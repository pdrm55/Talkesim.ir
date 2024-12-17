import requests
import sqlite3

# آدرس‌های احراز هویت و API پکیج‌ها
AUTH_URL = "https://admin.talkesim.com/api/auth/local"
PACKAGES_URL = "https://admin.talkesim.com/api/package"
API_KEY = "513b375a-110a-4846-aeff-dde14591f392"

# اطلاعات ورود
CREDENTIALS = {
    "identifier": "talkesim.ir@gmail.com",
    "password": "akbarhassantalkesim"
}

def get_jwt_token():
    """دریافت توکن JWT"""
    headers = {"x-api-key": API_KEY, "Content-Type": "application/json"}
    try:
        response = requests.post(AUTH_URL, json=CREDENTIALS, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("jwt")
    except requests.exceptions.RequestException as e:
        print(f"خطا در دریافت توکن جدید: {e}")
        return None

def get_packages(token):
    """دریافت لیست پکیج‌ها با استفاده از توکن JWT"""
    headers = {"Authorization": f"Bearer {token}", "x-api-key": API_KEY}
    try:
        response = requests.get(PACKAGES_URL, headers=headers)
 #       print(f"وضعیت پاسخ API: {response.status_code}")
        if response.status_code != 200:
            print(f"وضعیت پاسخ API: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        
        # دسترسی به بخش درست از ساختار JSON
        packages = data.get("listPrepaidPackageTemplate", {}).get("template", [])
        return packages
    except Exception as e:
        print(f"خطا در دریافت پکیج‌ها: {e}")
        return None


def save_packages_to_db(packages):
    """ذخیره پکیج‌ها در دیتابیس SQLite"""
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # حذف داده‌های قدیمی
        cursor.execute("DELETE FROM packages")

        # ایجاد جدول در صورت عدم وجود
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


        # بررسی فرمت داده‌ها
        if not isinstance(packages, list):
            print("داده‌ها در فرمت لیست نیستند:", type(packages))
            return

        for package in packages:
            try:
                if isinstance(package, dict):  # بررسی نوع داده هر آیتم
                    cursor.execute('''
                        INSERT INTO packages (id, provider, name, country, price, validity, additional_info)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        package.get("prepaidpackagetemplateid"),
                        package.get("reseller", {}).get("resellername", "N/A"),  # مثال برای فیلدهای تو در تو
                        package.get("prepaidpackagetemplatename"),
                        package.get("rdbLocationZones", {}).get("locationzonename", "Unknown"),
                        package.get("cost"),
                        package.get("perioddays", 0),
                        package.get("uiStartAvailablePeriod", "No Info")  # مقدار پیش‌فرض
                    ))
                else:
                    print("فرمت نادرست برای پکیج:", package)
            except Exception as e:
                print(f"خطا در پردازش پکیج: {package}: {e}")

        conn.commit()
        print("پکیج‌ها با موفقیت ذخیره شدند.")
    except Exception as e:
        print(f"خطای عمومی: {e}")
    finally:
        conn.close()

def main():
    token = get_jwt_token()
    if not token:
        print("دریافت توکن ناموفق بود.")
        return

    print(f"توکن JWT: {token}")
    packages = get_packages(token)
    if not packages:
        print("دریافت پکیج‌ها ناموفق بود.")
        return

    save_packages_to_db(packages)

if __name__ == "__main__":
    main()
