import sqlite3
import re
from deep_translator import GoogleTranslator

def extract_country_from_name(package_name):
    """
    استخراج نام کشور از نام پکیج.
    تمام بخش‌های متنی تا قبل از برخورد با اعداد یا سایر مشخصات به عنوان نام کشور استخراج می‌شود.
    """
    match = re.match(r"^[^\d]+", package_name)
    if match:
        return match.group(0).strip()
    return None

def translate_and_save_to_db():
    """ترجمه نام کشورها و ذخیره آن‌ها در دیتابیس"""
    translator = GoogleTranslator(source='en', target='fa')
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # دریافت رکوردهایی که ترجمه نشده‌اند
        cursor.execute("SELECT id, edited_name FROM packages WHERE translated_name IS NULL")
        rows = cursor.fetchall()

        for row in rows:
            package_id, package_name = row
            country_name = extract_country_from_name(package_name)
            if country_name:
                try:
                    translated_name = translator.translate(country_name)
                    print(f"ترجمه: {country_name} -> {translated_name}")

                    # ذخیره ترجمه در دیتابیس
                    cursor.execute(
                        "UPDATE packages SET translated_name = ? WHERE id = ?",
                        (translated_name, package_id)
                    )
                except Exception as e:
                    print(f"خطا در ترجمه: {country_name} - {e}")
                    continue

        conn.commit()
        print("ترجمه‌ها با موفقیت ذخیره شدند.")
    except Exception as e:
        print(f"خطای عمومی: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    translate_and_save_to_db()
