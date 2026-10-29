def reset_tables(conn):
    """Test-only: drops everything (children first) and recreates it."""
    cur = conn.cursor()
    for table in ("recipe", "sales", "pizza", "inventory", "inventory_items"):
        cur.execute(f"DROP TABLE IF EXISTS {table}")

    cur.execute("""
        CREATE TABLE recipe(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            weight DECIMAL(10, 2),
            price DECIMAL(10, 2)
        ) ENGINE=InnoDB
    """)
    cur.execute("""
        CREATE TABLE pizza(
            id INT AUTO_INCREMENT PRIMARY KEY,
            toppings JSON NOT NULL
        ) ENGINE=InnoDB
    """)
    cur.execute("""
        CREATE TABLE sales(
            id INT AUTO_INCREMENT PRIMARY KEY,
            pizzaID INT,
            pizza_size VARCHAR(100),
            price DECIMAL(10, 2),
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pizzaID) REFERENCES pizza(id)
        ) ENGINE=InnoDB
    """)
    cur.execute("""
        CREATE TABLE inventory_items(
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            price DECIMAL(10, 2),
            full_case_weight DECIMAL(10, 2)
        ) ENGINE=InnoDB
    """)
    cur.execute("""
        CREATE TABLE inventory(
            id INT AUTO_INCREMENT PRIMARY KEY,
            item_id INT NOT NULL,
            count_date DATE NOT NULL,
            qty INT NOT NULL,
            lbs DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (item_id) REFERENCES inventory_items(id)
        ) ENGINE=InnoDB
    """)
    conn.commit()
    cur.close()