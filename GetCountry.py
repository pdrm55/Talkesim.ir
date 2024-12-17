import sqlite3

def extract_clean_countries():
    try:
        # اتصال به دیتابیس
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        
        # اجرای کوئری برای استخراج نام کشورها
        cursor.execute("SELECT DISTINCT country FROM packages")
        raw_countries = [row[0] for row in cursor.fetchall()]
        
        # پاک‌سازی نام کشورها (حذف بخش‌های اضافی بعد از '_')
        clean_countries = list({country.split('_')[0] for country in raw_countries})
        
        # نمایش لیست کشورها
        print("لیست کشورها:")
        for country in clean_countries:
            print(country)
        
        return clean_countries
    except Exception as e:
        print(f"خطا در استخراج کشورها: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    countries = extract_clean_countries()
