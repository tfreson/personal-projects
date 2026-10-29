from inventory import add_inventory_item, count_inventory
from recipes import add_recipe
from sales import add_sales

def load_test_data(conn):
    for args in [
        ("Pepperoni", 10.99, 20.00), ("Mushrooms", 8.99, 15.00),
        ("Onions", 6.99, 12.00), ("Sausage", 12.99, 25.00),
        ("Bacon", 14.99, 30.00), ("cheese", 9.99, 18.00),
        ("green peppers", 7.99, 14.00), ("black olives", 11.99, 22.00),
        ("tomatoes", 5.99, 10.00),( "pineapple", 6.99, 12.00),( "spinach", 7.99, 14.00),( "feta cheese", 8.99, 16.00),
    ]:
        add_inventory_item(conn, *args)

    count_inventory(conn, [("Pepperoni", 10, 0.00), ("Mushrooms", 5, 0.00), ("Onions", 8, 0.00),
                           ("Sausage", 12, 0.00), ("Bacon", 6, 0.00), ("cheese", 15, 0.00),
                           ("green peppers", 7, 0.00), ("black olives", 4, 0.00),
                           ("tomatoes", 9, 0.00)], "2026-10-21")
    count_inventory(conn, [("Pepperoni", 15, 0.00), ("Mushrooms", 10, 0.00), ("Onions", 8, 0.00),
                           ("Sausage", 12, 0.00), ("Bacon", 6, 0.00), ("cheese", 30, 0.00),
                           ("green peppers", 7, 0.00), ("black olives", 4, 0.00),
                           ("tomatoes", 9, 0.00)], "2026-10-20")

    for args in [
        ("Pepperoni", 2, 3.00), ("Mushrooms", 3, 2.00), ("Onions", 1, 1.00),
        ("Sausage", 4, 3.00), ("Bacon", 4, 3.00), ("cheese", 6, 0.00),
        ("green peppers", 1, 1.00), ("black olives", 1, 2.00), ("tomatoes", 3, 2.00),
    ]:
        add_recipe(conn, *args)

    all_toppings = ["Pepperoni", "Mushrooms", "Onions", "Sausage", "Bacon",
                    "cheese", "green peppers", "black olives", "tomatoes"]
    d = "2026-10-20"
    add_sales(conn, "Large", ["Pepperoni", "Mushrooms", "Bacon"], d)
    add_sales(conn, "Medium", ["Onions", "Sausage", "Bacon"], d)
    add_sales(conn, "Small", ["cheese", "green peppers", "black olives", "tomatoes"], d)
    add_sales(conn, "Extra Large", all_toppings, d)
    add_sales(conn, "Large", all_toppings, d)