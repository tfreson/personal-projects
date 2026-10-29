from decimal import Decimal

def oz_to_lbs(oz):
    return Decimal(oz) / Decimal(16)

def lbs_to_oz(lbs):
    return Decimal(lbs) * Decimal(16)

def _lookup(conn, query, name, label):
    cur = conn.cursor()
    cur.execute(query, (name,))
    row = cur.fetchone()
    cur.close()
    if row is None:
        print(f"{label} '{name}' not found.")
        return None
    return row[0]


#------getters
def get_inventory_item_id(conn, name):
    return _lookup(conn, "SELECT id FROM inventory_items WHERE name = %s", name, "Inventory item")

def get_inventory_item_price(conn, name):
    return _lookup(conn, "SELECT price FROM inventory_items WHERE name = %s", name, "Inventory item")

def get_recipe_price(conn, name):
    return _lookup(conn, "SELECT price FROM recipe WHERE name = %s", name, "Recipe")

def get_recipe_weight(conn, name):
    return _lookup(conn, "SELECT weight FROM recipe WHERE name = %s", name, "Recipe")

def get_inventory_item_weight(conn, name):
    return _lookup(conn, "SELECT weight FROM inventory_items WHERE name = %s", name, "Inventory item")

def get_inventory_item_full_case_weight(conn, name):
    return _lookup(conn, "SELECT full_case_weight FROM inventory_items WHERE name = %s", name, "Inventory item")

def get_inventory_item_qty(conn, name, count_date):
    return _lookup(conn, "SELECT qty FROM inventory WHERE item_id = (SELECT id FROM inventory_items WHERE name = %s) AND count_date = %s", (name, count_date), "Inventory item")


def get_inventory_item_lbs(conn, name, count_date):
    return _lookup(conn, "SELECT lbs FROM inventory WHERE item_id = (SELECT id FROM inventory_items WHERE name = %s) AND count_date = %s", (name, count_date), "Inventory item")

def get_inventory_item_names(conn):
    cur = conn.cursor()
    cur.execute("SELECT name FROM inventory_items")
    names = [row[0] for row in cur.fetchall()]
    cur.close()
    return names

def get_sales_by_item(conn, date):
    cur = conn.cursor()
    cur.execute("""
        SELECT r.name, COUNT(s.id) AS sales_count
        FROM sales s
        JOIN pizza p ON s.pizzaID = p.id
        JOIN JSON_TABLE(p.toppings, '$[*]' COLUMNS (topping VARCHAR(100) PATH '$')) AS t ON 1=1
        JOIN recipe r ON t.topping = r.name
        WHERE DATE(s.date) = %s
        GROUP BY r.name
    """, (date,))
    sales = {row[0]: row[1] for row in cur.fetchall()}
    cur.close()
    return sales

#------setters
def set_inventory_item_qty(conn, name, count_date, qty):
    return _lookup(conn, "UPDATE inventory SET qty = %s WHERE item_id = (SELECT id FROM inventory_items WHERE name = %s) AND count_date = %s", (qty, name, count_date), "Inventory item")

def set_inventory_item_lbs(conn, name, count_date, lbs):
    return _lookup(conn, "UPDATE inventory SET lbs = %s WHERE item_id = (SELECT id FROM inventory_items WHERE name = %s) AND count_date = %s", (lbs, name, count_date), "Inventory item")

