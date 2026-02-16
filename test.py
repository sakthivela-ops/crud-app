# file: show_tables.py
import mysql.connector
from mysql.connector import Error

def show_tables(
    user="sakthivel",
    password="Qwerty@1234",  # <-- change this
    host="127.0.0.1",
    port=3306,
    database="sports"
):
    conn = None
    try:
        conn = mysql.connector.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database=database,
        )
        cur = conn.cursor()
        cur.execute("SHOW TABLES;")
        tables = [row[0] for row in cur.fetchall()]
        if tables:
            print(f"Tables in '{database}':")
            for t in tables:
                print("-", t)
        else:
            print(f"No tables found in '{database}'.")
    except Error as e:
        print("MySQL error:", e)
    finally:
        try:
            cur.close()
        except:
            pass
        if conn:
            conn.close()

if __name__ == "__main__":
    show_tables()
