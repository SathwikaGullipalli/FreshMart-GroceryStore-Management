
CREATE DATABASE IF NOT EXISTS grocery_store;

USE grocery_store;

-- 1. Units of Measurement
CREATE TABLE IF NOT EXISTS uom (
    uom_id INT NOT NULL AUTO_INCREMENT,
    uom_name VARCHAR(45) NOT NULL,
    PRIMARY KEY (uom_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default units
INSERT IGNORE INTO uom (uom_id, uom_name)
VALUES
(1, 'each'),
(2, 'kg');

-- 2. Products
CREATE TABLE IF NOT EXISTS products (
    product_id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    uom_id INT NOT NULL,
    price_per_unit DOUBLE NOT NULL,
    stock_quantity DOUBLE NOT NULL DEFAULT 0,
    PRIMARY KEY (product_id),
    KEY fk_uom_id_idx (uom_id),
    CONSTRAINT fk_uom_id
        FOREIGN KEY (uom_id)
        REFERENCES uom (uom_id)
        ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INT NOT NULL AUTO_INCREMENT,
    customer_name VARCHAR(100) NOT NULL,
    total DOUBLE NOT NULL,
    date_time DATETIME NOT NULL,
    PRIMARY KEY (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Order Details
CREATE TABLE IF NOT EXISTS order_details (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity DOUBLE NOT NULL,
    total_price DOUBLE NOT NULL,
    PRIMARY KEY (order_id, product_id),
    KEY fk_product_id_idx (product_id),
    CONSTRAINT fk_product_id
        FOREIGN KEY (product_id)
        REFERENCES products (product_id)
        ON UPDATE RESTRICT,
    CONSTRAINT fr_order_id
        FOREIGN KEY (order_id)
        REFERENCES orders (order_id)
        ON UPDATE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
