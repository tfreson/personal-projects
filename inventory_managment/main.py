from db import get_connection
from schema import reset_tables
from seed import load_test_data
import reports 

def main():
    conn = get_connection()
    try:
        reset_tables(conn)      # wipes data; remove once you stop testing
        load_test_data(conn)
        #reports.get_ci(conn, "2026-10-21")
        reports.inventory_stats(conn, "2026-10-20")
    finally:
        conn.close()

if __name__ == "__main__":
    main()