# Sales Data Star Schema — Online Retail II

> End-to-end dimensional model built on real UK retail transactional data (541K+ records) using a Star Schema with MySQL.

## Architecture

```
Online Retail II Dataset (UCI)
        ↓
  Python ETL Script
        ↓
┌─────────────────────────────────┐
│         MySQL Database          │
│                                 │
│  dim_date    dim_product        │
│      ↘           ↙              │
│       fact_sales                │
│      ↗           ↘              │
│  dim_customer  dim_invoice      │
└─────────────────────────────────┘
```

## Tech Stack

| Layer         | Technology              |
|---------------|-------------------------|
| Dataset       | Online Retail II (UCI)  |
| Processing    | Python, Pandas          |
| Database      | MySQL                   |
| ORM/Connector | SQLAlchemy, PyMySQL     |
| Schema Design | Star Schema (Kimball)   |

## Schema Design

**Fact Table**
- `fact_sales` — 397,885 rows (quantity, unit_price, total_amount)

**Dimension Tables**
- `dim_date` — 305 unique dates (day, month, quarter, year, is_weekend)
- `dim_product` — 3,665 unique products
- `dim_customer` — 4,338 unique customers
- `dim_invoice` — 18,532 unique invoices

## Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/ASD-17/cdf-star-schema.git
cd cdf-star-schema
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up MySQL database
```sql
CREATE DATABASE cdf_sales_dw;
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env with your MySQL credentials
```

### 5. Download dataset
- Download from: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Place `online_retail_II.xlsx` in the `data/` folder

### 6. Run the ETL pipeline
```bash
python3 python/load_data.py
```

### 7. Run sample queries
Open `sql/sample_queries.sql` in MySQL Workbench and execute.

## Sample Query Output

**Monthly Revenue Trend:**

| Year | Month | Revenue (GBP) | Invoices |
|------|-------|---------------|----------|
| 2010 | 12    | 572,713.89    | 1,400    |
| 2011 | 1     | 569,445.04    | 987      |
| 2011 | 9     | 952,838.38    | 1,755    |
| 2011 | 10    | 1,039,318.79  | 1,929    |

## Project Structure

```
cdf-star-schema/
├── data/               ← dataset (not tracked in git)
├── python/
│   └── load_data.py    ← ETL pipeline
├── sql/
│   ├── ddl.sql         ← Star schema DDL
│   └── sample_queries.sql
├── .env.example
├── requirements.txt
└── README.md
```