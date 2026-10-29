from helpers import get_inventory_item_id

def add_inventory_item(conn, name, price, full_case_weight):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventory_items (name, price, full_case_weight) VALUES (%s, %s, %s)",
        (name, price, full_case_weight),
    )
    conn.commit()
    cur.close()

def count_inventory(conn, items, count_date):
    """items is a list of (name, qty, lbs) tuples."""
    cur = conn.cursor()
    for name, qty, lbs in items:
        item_id = get_inventory_item_id(conn, name)
        if item_id is None:
            continue
        cur.execute(
            "INSERT INTO inventory (item_id, count_date, qty, lbs) VALUES (%s, %s, %s, %s)",
            (item_id, count_date, qty, lbs),
        )
    conn.commit()
    cur.close()