import sqlite3

def create_cart_table():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # ایجاد جدول سبد خرید
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            package_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (package_id) REFERENCES packages (id)
        )
    ''')

    conn.commit()
    conn.close()
    print("جدول سبد خرید با موفقیت ایجاد شد.")

if __name__ == "__main__":
    create_cart_table()
