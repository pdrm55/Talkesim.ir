import sqlite3

# اتصال به دیتابیس و ایجاد جدول
def create_packages_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS packages")
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY,
        provider TEXT,
        name TEXT,
        country TEXT,
        price REAL,
        validity INTEGER,
        additional_info TEXT
    )
''')

    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_packages_table()
