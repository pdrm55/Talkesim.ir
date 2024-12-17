import sqlite3

def check_table_structure():
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(packages)")
        columns = cursor.fetchall()

        print("ساختار جدول packages:")
        for column in columns:
            print(f"ستون: {column[1]}, نوع داده: {column[2]}")

    except Exception as e:
        print(f"خطای عمومی: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_structure()
