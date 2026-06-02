-- ============================================
-- Star Schema DDL: Online Retail Sales DW
-- Database: MySQL
-- ============================================

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_invoice;

-- ── Dimension: Date ──────────────────────────
CREATE TABLE dim_date (
    date_key        INT AUTO_INCREMENT PRIMARY KEY,
    full_date       DATE NOT NULL,
    day             TINYINT NOT NULL,
    month           TINYINT NOT NULL,
    month_name      VARCHAR(10) NOT NULL,
    quarter         TINYINT NOT NULL,
    year            SMALLINT NOT NULL,
    day_of_week     TINYINT NOT NULL,
    day_name        VARCHAR(10) NOT NULL,
    is_weekend      BOOLEAN NOT NULL,
    CONSTRAINT uq_dim_date UNIQUE (full_date)
);

-- ── Dimension: Product ───────────────────────
CREATE TABLE dim_product (
    product_key     INT AUTO_INCREMENT PRIMARY KEY,
    stock_code      VARCHAR(20) NOT NULL,
    description     VARCHAR(255),
    CONSTRAINT uq_dim_product UNIQUE (stock_code)
);

-- ── Dimension: Customer ──────────────────────
CREATE TABLE dim_customer (
    customer_key    INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     VARCHAR(20) NOT NULL,
    country         VARCHAR(100),
    CONSTRAINT uq_dim_customer UNIQUE (customer_id)
);

-- ── Dimension: Invoice ───────────────────────
CREATE TABLE dim_invoice (
    invoice_key     INT AUTO_INCREMENT PRIMARY KEY,
    invoice_no      VARCHAR(20) NOT NULL,
    is_cancelled    BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT uq_dim_invoice UNIQUE (invoice_no)
);

-- ── Fact: Sales ──────────────────────────────
CREATE TABLE fact_sales (
    sales_key       INT AUTO_INCREMENT PRIMARY KEY,
    date_key        INT NOT NULL,
    product_key     INT NOT NULL,
    customer_key    INT NOT NULL,
    invoice_key     INT NOT NULL,
    quantity        INT NOT NULL,
    unit_price      DECIMAL(10, 2) NOT NULL,
    total_amount    DECIMAL(12, 2) NOT NULL,
    FOREIGN KEY (date_key)     REFERENCES dim_date(date_key),
    FOREIGN KEY (product_key)  REFERENCES dim_product(product_key),
    FOREIGN KEY (customer_key) REFERENCES dim_customer(customer_key),
    FOREIGN KEY (invoice_key)  REFERENCES dim_invoice(invoice_key)
);

-- ── Indexes ──────────────────────────────────
CREATE INDEX idx_fact_date     ON fact_sales(date_key);
CREATE INDEX idx_fact_product  ON fact_sales(product_key);
CREATE INDEX idx_fact_customer ON fact_sales(customer_key);