from datetime import datetime, timedelta
import sales
import helpers

def inventory_stats(conn, count_date):

    usage =sales.total_sales_by_item(conn, count_date)
    print("usage", usage)
    theo_usage = {}
    unit_variance = {}
    unit_cost = {}
    dollar_value = {}
    variance_percent = {}

    #usage 
    

    #theo usage 


    #unit varience 

    #unit cost

    #dolar value 

    #varience %




def get_counts(conn, count_date):
    cur = conn.cursor()
    cur.execute("""
        SELECT ii.name, ii.price, ii.full_case_weight, i.qty
        FROM inventory_items ii
        JOIN inventory i ON ii.id = i.item_id
        WHERE i.count_date = %s
        ORDER BY ii.name
    """, (count_date,))
    rows = cur.fetchall()
    cur.close()
    return rows

def get_diff_in_ci(conn, previnv, curinv, date):
    prev_qty = {row[0]: row[3] for row in previnv}
    print("Change in count (current - previous):")
    for name, _, _, qty in curinv:
        if name in prev_qty:
            print(f"  {name}: {qty - prev_qty[name]:+d}")

    print("Sales for", date)
    for item, qty in get_sales_by_item(conn, date).items():
        price = get_recipe_price(conn, item)
        weight_oz = get_recipe_weight(conn, item)
        print(f"  {item}: sold {qty}, price {price}, "
              f"{weight_oz} oz ({oz_to_lbs(weight_oz):.2f} lbs)")

def get_ci(conn, count_date):
    prev_date = (datetime.strptime(count_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
    curinv = get_counts(conn, count_date)
    previnv = get_counts(conn, prev_date)

    print("Current inventory:", count_date)
    for item in curinv:
        print(item)
    print("Previous inventory:", prev_date)
    for item in previnv:
        print(item)

    print("ci stats")
    get_diff_in_ci(conn, previnv, curinv, prev_date)