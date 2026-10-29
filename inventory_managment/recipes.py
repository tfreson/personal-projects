from helpers import get_inventory_item_id

def add_recipe(conn, name, weight_oz, price):
    if get_inventory_item_id(conn, name) is None:
        print(f"Add '{name}' to inventory_items first.")
        return
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO recipe (name, weight, price) VALUES (%s, %s, %s)",
        (name, weight_oz, price),
    )
    conn.commit()
    cur.close()