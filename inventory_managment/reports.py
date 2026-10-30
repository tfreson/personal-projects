from datetime import datetime, timedelta
import sales
import helpers

def inventory_stats(conn, count_date):
    #agrigation fuction 

    usage = get_diff_in_counts(conn, get_counts(conn, (datetime.strptime(count_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")), get_counts(conn, count_date), count_date)
    theo_usage = sales.total_sales_by_item(conn, count_date)
    unit_variance = unit_variance_func(conn, usage, theo_usage)
    unit_cost = unit_cost_func(conn, unit_variance)
    dollar_value = dollar_value_func(conn, unit_variance)
    variance_percent = variance_percent_func(conn, dollar_value, unit_cost)
    #stats as dict with item name as a key then usage, theo_usage, unit_variance, unit_cost, dollar_value, variance_percent as values
    print("usage: ", usage)
    print()
    stats = {
        
        item: {
            "usage": usage[item],
            "theo_usage": theo_usage.get(item, 0),
            "unit_variance": unit_variance[item],
            "unit_cost": unit_cost[item],
            "dollar_value": dollar_value[item],
            "variance_percent": variance_percent[item],
        }
        for item in usage
    }
   
    for item, data in stats.items():
        print(f"{item}: {data}")
    return stats




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

def get_diff_in_counts(conn, previnv, curinv, date):
    #find the difference in the counts between the two dates, return a dict with the item name as the key and the difference as the value
    #for all items in the inventory, if an item is not in the previous inventory, assume the previous count was 0
    
    prev_dict = {item[0]: item for item in previnv}
    cur_dict = {item[0]: item for item in curinv}

    diff = {}

    for item in cur_dict:
        prev_qty = prev_dict.get(item, (None, None, None, 0))[3]
        cur_qty = cur_dict[item][3]
        diff[item] = prev_qty - cur_qty

    print(f"Inventory difference for {date}: {diff}")

    return diff

def unit_variance_func(conn, usage, theo_usage):
    unit_variance = {}
    for item in usage:
        unit_variance[item] = usage[item] - theo_usage.get(item, 0)
    return unit_variance

def unit_cost_func(conn, unit_variance):
    unit_cost = {}
    for item in unit_variance:
        unit_cost[item] = helpers.get_inventory_item_price(conn, item)
    return unit_cost

def dollar_value_func(conn, unit_variance):
    dollar_value = {}
    for item in unit_variance:
        dollar_value[item] = unit_variance[item] * helpers.get_inventory_item_price(conn, item)
    return dollar_value

def variance_percent_func(conn, dollar_value, unit_cost):
    variance_percent = {}
    for item in dollar_value:
        if dollar_value[item] != 0:
            variance_percent[item] = (unit_cost[item] / dollar_value[item]) * 100
        else:
            variance_percent[item] = 0
    return variance_percent