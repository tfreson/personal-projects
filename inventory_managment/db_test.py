from datetime import datetime, timedelta
import decimal
import json

import mysql.connector

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password="secret",
    database="testdb",
)
cur = conn.cursor()

#testing drops
cur.execute("DROP TABLE IF EXISTS recipe")
cur.execute("DROP TABLE IF EXISTS sales")
cur.execute("DROP TABLE IF EXISTS pizza")
cur.execute("DROP TABLE IF EXISTS inventory")
cur.execute("DROP TABLE IF EXISTS inventory_items")

#------------table set up----------------
#how much of each ingredient is used in a per recipe
cur.execute("""
    CREATE TABLE recipe(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        weight DECIMAL(10, 2),
        price DECIMAL(10, 2)
    ) engine=InnoDB
""")

#pizza table holds topings and id
cur.execute("""
    CREATE TABLE pizza(
        id INT AUTO_INCREMENT PRIMARY KEY,
        toppings JSON NOT NULL
    )engine=InnoDB
""")

#sales for a given day with pizza id and size and price and date
cur.execute("""
    CREATE TABLE sales(
        id INT AUTO_INCREMENT PRIMARY KEY,
        pizzaID INT,
        pizza_size VARCHAR(100),
        price DECIMAL(10, 2),
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pizzaID) REFERENCES pizza(id)    
    ) engine=InnoDB 
""")

#total inventory items table holds name id price and case weight because these dont change often
cur.execute("""
    CREATE TABLE inventory_items(
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        price DECIMAL(10, 2),
        full_case_weight DECIMAL(10, 2)
    )engine=InnoDB
""")


#inventory table holds the count of each item in inventory for a given date
cur.execute("""
    CREATE TABLE inventory(
        id INT AUTO_INCREMENT PRIMARY KEY,
        item_id INT NOT NULL,
        count_date DATE NOT NULL,
        qty INT NOT NULL,
        lbs decimal(10, 2) NOT NULL,
        FOREIGN KEY (item_id) REFERENCES inventory_items(id)
    )engine=InnoDB
""")


#---------functions---------------
#region   helper functions

def oz_to_lbs(oz):
    return oz / 16.0
def lbs_to_oz(lbs):
    return lbs * 16.0

def get_inventory_item_id(name):
    cur.execute("SELECT id FROM inventory_items WHERE name = %s", (name,))
    item_id = cur.fetchone()
    if item_id is None:
        print(f"Inventory item '{name}' not found.")
        return None
    return item_id[0]

def get_inventory_item_price(name):
    cur.execute("SELECT price FROM inventory_items WHERE name = %s", (name,))
    price = cur.fetchone()
    if price is None:
        print(f"Inventory item '{name}' not found.")
        return None
    return float(decimal.Decimal(str(price[0])))


def get_recipe_price(name):
    cur.execute("SELECT price FROM recipe WHERE name = %s", (name,))
    price = cur.fetchone()
    if price is None:
        print(f"Recipe '{name}' not found.")
        return None
    return float(decimal.Decimal(str(price[0])))

def get_recipe_weight(name):
    cur.execute("SELECT weight FROM recipe WHERE name = %s", (name,))
    weight = cur.fetchone()
    if weight is None:
        print(f"Recipe '{name}' not found.")
        return None
    return float(decimal.Decimal(str(weight[0])))

#endregion
#region main functions 


#weight in oz
def add_recipe(name, weight, price):
    #search inventory item 
    cur.execute("SELECT id FROM inventory_items WHERE name = %s", (name,))
    item_id = cur.fetchone()
    if item_id is None:
        print(f"Inventory item '{name}' not found. Please add it to inventory_items first.")
        return
    cur.execute("INSERT INTO recipe (name, weight, price) VALUES (%s, %s, %s)", (name, weight, price))
    conn.commit()

def add_sales(pizzaSize,toppings,date):
    #print("size: " + pizzaSize + " toppings: " + str(toppings))
    price = 0.00
    #calculate price based on toppings and size
    if pizzaSize == "Small":
        price = 10.00
    elif pizzaSize == "Medium":
        price = 15.00
    elif pizzaSize == "Large":
        price = 20.00
    elif pizzaSize == "Extra Large":
        price = 25.00

    #pull price of each topping and add to price
    for topping in toppings:
        cur.execute("SELECT price FROM recipe WHERE name = %s", (topping,))
        topping_price = cur.fetchone()
        #print(topping)
        #print(type(topping_price[0]))
        #print(topping_price[0])
        if topping_price:
            price += float(decimal.Decimal(str(topping_price[0])))
        else:
            print(f"Topping '{topping}' not found in inventory_items. Please add it first.")
            return
    #print(price)
    cur.execute("INSERT INTO pizza (toppings) VALUES (%s)", (json.dumps(toppings),))
    pizza_id = cur.lastrowid
    cur.execute("INSERT INTO sales (pizzaID, pizza_size, price, date) VALUES (%s, %s, %s, %s)", (pizza_id, pizzaSize,price,date)) 
    conn.commit()


#add a new item to count for inventory 
#weight in lbs
def add_inventory_item(name, price, full_case_weight):
    cur.execute("INSERT INTO inventory_items (name, price, full_case_weight) VALUES (%s, %s, %s)", (name, price, full_case_weight))
    conn.commit()



# Count inventory for a given date
#qty in full cases 
def count_inventory(items, count_date):
    #items is a list of tuples (name, qty)
    for name, qty,lb in items:  
        cur.execute("SELECT id FROM inventory_items WHERE name = %s", (name,))
        item_id = cur.fetchone()
        if item_id:
            cur.execute("INSERT INTO inventory (item_id, count_date, qty,lb) VALUES (%s, %s, %s,%s)", (item_id[0], count_date, qty,lb))
            conn.commit()

def get_sales_by_item(date):
    cur.execute("""SELECT p.toppings, s.pizza_size, s.price
    FROM sales s 
    JOIN pizza p ON s.pizzaID = p.id
    WHERE date = %s""", (date,))
    sales = cur.fetchall()
    sales_by_item = {}
    for toppings, pizza_size, price in sales:
        for topping in json.loads(toppings):
            if topping not in sales_by_item:
                sales_by_item[topping] = 0
            sales_by_item[topping] += 1
    return sales_by_item


def get_diff_in_ci(previnv, curinv,date):
    #get the difference between the two inventories according to sales 
    diff = []
    for i in range(len(previnv)):
        prev_item = previnv[i]
        cur_item = curinv[i]
        name = prev_item[0]
        prev_qty = prev_item[3]
        cur_qty = cur_item[3]
        diff_qty = cur_qty - prev_qty
        diff.append((name, diff_qty))
    #diffrence in inventorys 
    #expected diffrence is previnv - sales = curinv
    sales_amount = get_sales_by_item(date)
    for item, qty in sales_amount.items():
        price = get_recipe_price(item)
        weightoz = get_recipe_weight(item)
        weightlbs = oz_to_lbs(weightoz)
        print(f"Item: {item}, Quantity: {qty}, Price: {price}, Weight (oz): {weightoz}, Weight (lbs): {weightlbs}")

        
def get_ci(count_date):
    #get most expensive item in inventory along with their qty price weight name
    #privious date is the day before the count date
    prev_date = (datetime.strptime(count_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")

    # get the current inventory 
    cur.execute("""
        SELECT ii.name, ii.price, ii.full_case_weight, i.qty
        FROM inventory_items ii
        JOIN inventory i ON ii.id = i.item_id
        WHERE i.count_date = %s
        ORDER BY ii.price DESC LIMIT 5""", (count_date,))
    curinv = cur.fetchall()
    #get previous date
    cur.execute("""
        SELECT ii.name, ii.price, ii.full_case_weight, i.qty
        FROM inventory_items ii
        JOIN inventory i ON ii.id = i.item_id
        WHERE i.count_date = %s
        ORDER BY ii.price ASC LIMIT 5""", (prev_date,))
    previnv = cur.fetchall()
    print("Current inventory: " + str(count_date))
    for item in curinv:
        print(item)
    print("Previous inventory:" + str(prev_date))
    for item in previnv:
        print(item)

    print("ci stats")
    #dif per item based off sales 
    # previouse inventory - sales = current 
    #get diffrence then - current to get what we are gaining or losing
    # inventory then display the difference 
    get_diff_in_ci(previnv, curinv,prev_date)
    


#endregion 



#----------------testing ---------------------


#region setup inventory and sales for testing
#region add inventory items
#add inventory items 
add_inventory_item("Pepperoni", 10.99, 20.00)
add_inventory_item("Mushrooms", 8.99, 15.00)
add_inventory_item("Onions", 6.99, 12.00)
add_inventory_item("Sausage", 12.99, 25.00)
add_inventory_item("Bacon", 14.99, 30.00)
add_inventory_item("cheese", 9.99, 18.00)
add_inventory_item("green peppers", 7.99, 14.00)
add_inventory_item("black olives", 11.99, 22.00)
add_inventory_item("tomatoes", 5.99, 10.00)

#endregion

#region add inventory 

count_inventory([("Pepperoni", 10,0.00), ("Mushrooms", 5,0.00), ("Onions", 8,0.00), ("Sausage", 12,0.00), ("Bacon", 6,0.00), ("cheese", 15,0.00), ("green peppers", 7,0.00), ("black olives", 4,0.00), ("tomatoes", 9,0.00)], "2026-10-21")
count_inventory([("Pepperoni", 15,0.00), ("Mushrooms", 10,0.00), ("Onions", 8,0.00), ("Sausage", 12,0.00), ("Bacon", 6,0.00), ("cheese", 30,0.00), ("green peppers", 7,0.00), ("black olives", 4,0.00), ("tomatoes", 9,0.00)], "2026-10-20")

#endregion

#region add recipe
#add_recipe
add_recipe("Pepperoni", 2, 3.00)
add_recipe("Mushrooms", 3, 2.00)
add_recipe("Onions", 1, 1.00)
add_recipe("Sausage", 4, 3.00)
add_recipe("Bacon", 4, 3.00)
add_recipe("cheese", 6, 0.00)
add_recipe("green peppers", 1, 1.00)
add_recipe("black olives", 1, 2.00)
add_recipe("tomatoes", 3, 2.00)

#endregion

#region add sales 
add_sales("Large", ["Pepperoni", "Mushrooms","Bacon"], "2026-10-20")
add_sales("Medium", ["Onions", "Sausage", "Bacon"], "2026-10-20")
add_sales("Small", ["cheese", "green peppers", "black olives", "tomatoes"], "2026-10-20")
add_sales("Extra Large", ["Pepperoni", "Mushrooms", "Onions", "Sausage", "Bacon", "cheese", "green peppers", "black olives", "tomatoes"], "2026-10-20")
add_sales("Large", ["Pepperoni", "Mushrooms", "Onions", "Sausage", "Bacon", "cheese", "green peppers", "black olives", "tomatoes"], "2026-10-20")

#endregion

#endregion

get_ci("2026-10-21")

cur.close()
conn.close()