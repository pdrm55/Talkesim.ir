import re
import sqlite3

def extract_country_names():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # انتخاب تمام رکوردها
    cursor.execute('SELECT id, name FROM packages')
    rows = cursor.fetchall()

    for row in rows:
        package_id = row[0]
        full_name = row[1]

        # استخراج نام کشور تا قبل از اولین عدد یا اطلاعات اضافی
        match = re.match(r'([a-zA-Z\s]+)', full_name)
        if match:
            country_name = match.group(1).strip()

            # ذخیره در ستون جدید
            cursor.execute('UPDATE packages SET edited_name = ? WHERE id = ?', (country_name, package_id))

    conn.commit()
    conn.close()

extract_country_names()
