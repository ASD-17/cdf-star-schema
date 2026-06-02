import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def get_engine():
    url = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url)


def run_ddl(engine):
    ddl_path = os.path.join(os.path.dirname(__file__), "../sql/ddl.sql")
    with open(ddl_path, "r") as f:
        ddl = f.read()
    with engine.connect() as conn:
        for statement in ddl.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
        conn.commit()
    print("DDL executed successfully.")


def load_raw_data(filepath: str) -> pd.DataFrame:
    print("Loading raw dataset...")
    df = pd.read_excel(filepath, sheet_name="Year 2010-2011", engine="openpyxl")
    print(f"Raw records: {len(df)}")

    df = df.dropna(subset=["Customer ID", "Description"])
    df["is_cancelled"] = df["Invoice"].astype(str).str.startswith("C")
    df = df[~df["is_cancelled"]].copy()
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    df["Customer ID"]  = df["Customer ID"].astype(int).astype(str).str.strip()
    df["StockCode"]    = df["StockCode"].astype(str).str.strip()
    df["Invoice"]      = df["Invoice"].astype(str).str.strip()
    df["InvoiceDate"]  = pd.to_datetime(df["InvoiceDate"])
    df["date_str"]     = df["InvoiceDate"].dt.strftime("%Y-%m-%d")
    df["total_amount"] = (df["Quantity"] * df["Price"]).round(2)

    print(f"Clean records: {len(df)}")
    return df


def build_dim_date(df: pd.DataFrame, engine) -> pd.DataFrame:
    print("Loading dim_date...")
    unique_dates = df["date_str"].unique()

    dim = pd.DataFrame({"date_str": sorted(unique_dates)})
    dim["date_key"]    = range(1, len(dim) + 1)
    dt                 = pd.to_datetime(dim["date_str"])
    dim["full_date"]   = dt.dt.date
    dim["day"]         = dt.dt.day.astype("int8")
    dim["month"]       = dt.dt.month.astype("int8")
    dim["month_name"]  = dt.dt.strftime("%B")
    dim["quarter"]     = dt.dt.quarter.astype("int8")
    dim["year"]        = dt.dt.year.astype("int16")
    dim["day_of_week"] = dt.dt.dayofweek.astype("int8")
    dim["day_name"]    = dt.dt.strftime("%A")
    dim["is_weekend"]  = dt.dt.dayofweek.isin([5, 6])

    dim.drop(columns=["date_str"]).to_sql(
        "dim_date", engine, if_exists="append", index=False,
        method="multi", chunksize=500
    )
    return dim[["date_key", "date_str"]]


def build_dim_product(df: pd.DataFrame, engine) -> pd.DataFrame:
    print("Loading dim_product...")
    dim = df[["StockCode", "Description"]].drop_duplicates(subset=["StockCode"]).copy()
    dim.columns = ["stock_code", "description"]
    dim["product_key"] = range(1, len(dim) + 1)
    dim["description"] = dim["description"].str.strip().str[:255]

    dim[["product_key", "stock_code", "description"]].to_sql(
        "dim_product", engine, if_exists="append", index=False,
        method="multi", chunksize=500
    )
    return dim[["product_key", "stock_code"]]


def build_dim_customer(df: pd.DataFrame, engine) -> pd.DataFrame:
    print("Loading dim_customer...")
    dim = df[["Customer ID", "Country"]].drop_duplicates(subset=["Customer ID"]).copy()
    dim.columns = ["customer_id", "country"]
    dim["customer_key"] = range(1, len(dim) + 1)

    dim[["customer_key", "customer_id", "country"]].to_sql(
        "dim_customer", engine, if_exists="append", index=False,
        method="multi", chunksize=500
    )
    return dim[["customer_key", "customer_id"]]


def build_dim_invoice(df: pd.DataFrame, engine) -> pd.DataFrame:
    print("Loading dim_invoice...")
    dim = df[["Invoice", "is_cancelled"]].drop_duplicates(subset=["Invoice"]).copy()
    dim.columns = ["invoice_no", "is_cancelled"]
    dim["invoice_key"] = range(1, len(dim) + 1)

    dim[["invoice_key", "invoice_no", "is_cancelled"]].to_sql(
        "dim_invoice", engine, if_exists="append", index=False,
        method="multi", chunksize=500
    )
    return dim[["invoice_key", "invoice_no"]]


def build_fact_sales(df, engine, dim_date, dim_product, dim_customer, dim_invoice):
    print("Loading fact_sales...")

    fact = df.merge(dim_date,    on="date_str",              how="left")
    fact = fact.merge(dim_product,  left_on="StockCode",   right_on="stock_code",  how="left")
    fact = fact.merge(dim_customer, left_on="Customer ID", right_on="customer_id", how="left")
    fact = fact.merge(dim_invoice,  left_on="Invoice",     right_on="invoice_no",  how="left")

    fact_final = fact[[
        "date_key", "product_key", "customer_key",
        "invoice_key", "Quantity", "Price", "total_amount"
    ]].copy()
    fact_final.columns = [
        "date_key", "product_key", "customer_key",
        "invoice_key", "quantity", "unit_price", "total_amount"
    ]

    before = len(fact_final)
    fact_final = fact_final.dropna()
    fact_final[["date_key", "product_key", "customer_key", "invoice_key"]] = \
        fact_final[["date_key", "product_key", "customer_key", "invoice_key"]].astype(int)

    dropped = before - len(fact_final)
    if dropped > 0:
        print(f"Rows dropped due to unresolved keys: {dropped}")

    fact_final.to_sql(
        "fact_sales", engine, if_exists="append",
        index=False, method="multi", chunksize=1000
    )
    print(f"fact_sales loaded: {len(fact_final)} rows")


def main():
    data_path = os.path.join(os.path.dirname(__file__), "../data/online_retail_II.xlsx")

    engine = get_engine()
    run_ddl(engine)

    df = load_raw_data(data_path)

    dim_date     = build_dim_date(df, engine)
    dim_product  = build_dim_product(df, engine)
    dim_customer = build_dim_customer(df, engine)
    dim_invoice  = build_dim_invoice(df, engine)

    build_fact_sales(df, engine, dim_date, dim_product, dim_customer, dim_invoice)

    print("\n Star schema fully populated.")


if __name__ == "__main__":
    main()