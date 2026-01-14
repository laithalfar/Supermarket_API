import sqlite3

def dump_products():
    conn = sqlite3.connect('supermarket.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    print("PRODUCTS TABLE:")
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    dump_products()
