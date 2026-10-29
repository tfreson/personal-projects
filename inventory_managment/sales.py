import json
from decimal import Decimal
import helpers

SIZE_PRICES = {
    "Small": Decimal("10.00"),
    "Medium": Decimal("15.00"),
    "Large": Decimal("20.00"),
    "Extra Large": Decimal("25.00"),
}

def add_sales(conn, pizza_size, toppings, date):
    price = SIZE_PRICES.get(pizza_size, Decimal("0.00"))

    for topping in toppings:
        topping_price = helpers.get_recipe_price(conn, topping)
        if topping_price is None:
            print(f"Topping '{topping}' has no recipe. Add it first.")
            return
        price += topping_price

    cur = conn.cursor()
    cur.execute("INSERT INTO pizza (toppings) VALUES (%s)", (json.dumps(toppings),))
    pizza_id = cur.lastrowid
    cur.execute(
        "INSERT INTO sales (pizzaID, pizza_size, price, date) VALUES (%s, %s, %s, %s)",
        (pizza_id, pizza_size, price, date),
    )
    conn.commit()
    cur.close()

def total_sales_by_item(conn, date):
    items = helpers.get_inventory_item_names(conn) 
    sales = helpers.get_sales_by_item(conn, date)
    print(items)
    print(sales)
    counts = {}

    for item in items:
        counts[item] = sales.get(item, 0)

    return counts
