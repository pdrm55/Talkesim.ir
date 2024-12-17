from flask import Flask, render_template, request, redirect, url_for , jsonify
from models import db, User
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask import session
from flask import flash
import requests
import sqlite3

app = Flask(__name__)
app.secret_key = 'GlobalKadro@2024'
# تنظیمات دیتابیس
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
# لینک واتساپ (شماره پشتیبانی)
WHATSAPP_LINK = "https://wa.me/905432138243"


@app.route('/')
def home():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # لیست کشورهای محبوب
    popular_countries = ["Turkey", "Germany", "France", "United Arab Emirates", "United States", "United Kingdom", "Australia", "Italy"]
    
    countries_data = []
    for country in popular_countries:
        # یافتن کمترین پکیج برای هر کشور
        cursor.execute("""
            SELECT name, MIN(price) AS price, validity
            FROM packages
            WHERE LOWER(edited_name) = ?
        """, (country.lower(),))
        package = cursor.fetchone()
        
        if package and package["price"] is not None:
            countries_data.append({
                "name": country,
                "image": country.lower() + ".png",
                "package": package["name"],
                "price": package["price"],
                "validity": package["validity"],
                "slug": country.lower()
            })
    conn.close()

    return render_template('home.html', countries=countries_data)


@app.route('/support')
def support():
    # ریدایرکت مستقیم به واتساپ
    return f"<script>window.location.href='{WHATSAPP_LINK}';</script>"

@app.route('/countries')
def countries():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # کوئری برای انتخاب کمترین قیمت هر کشور
    query = '''
        SELECT edited_name, MIN(price) AS min_price, translated_name, validity
        FROM packages
        GROUP BY edited_name
        ORDER BY translated_name ASC
    '''
    result = cursor.execute(query).fetchall()
    conn.close()

    countries = []
    for row in result:
        country_data = {
            'name': row[2] or row[0],  # استفاده از نام ترجمه‌شده در صورت وجود
            'data': "1GB",  # نمونه‌ای از دیتا
            'days': row[3],  # مدت زمان
            'price': row[1],  # قیمت
            'id': row[0].replace(' ', '-').lower()
        }
        countries.append(country_data)

    return render_template('countries.html', countries=countries)

@app.route('/guide')
def guide():
    return render_template('guide.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

# مسیر لاگین
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash('با موفقیت وارد شدید!', 'success')
            return redirect('/')
        else:
            flash('ایمیل یا رمز عبور اشتباه است.', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()  # پاک کردن تمام اطلاعات سشن
    flash('شما با موفقیت خارج شدید.', 'info')
    return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('این ایمیل قبلاً ثبت شده است.', 'error')
            return redirect('/signup')

        # Hash the password and save user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(name=name, email=email, password=hashed_password, phone=phone)
        db.session.add(new_user)
        db.session.commit()

        # Flash success message
        flash('ثبت‌نام با موفقیت انجام شد! لطفاً وارد شوید.', 'success')
        return redirect('/login')
    return render_template('signup.html')

@app.route('/packages/<country_name>')
def packages(country_name):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # دریافت اطلاعات پکیج‌ها برای کشور انتخاب‌شده
    query = """
    SELECT id, name, validity, price
    FROM packages
    WHERE LOWER(edited_name) = ?
    ORDER BY price ASC
    """
    cursor.execute(query, (country_name.lower(),))
    packages = cursor.fetchall()
    conn.close()

    print("پکیج‌های مربوط به", country_name, ":", packages)

    # تبدیل داده‌ها برای ارسال به صفحه HTML
    package_data = [{
        "id": row["id"],
        "name": row["name"],
        "validity": row["validity"],
        "price": row["price"]
    } for row in packages]

    return render_template(
        'packages.html',
        country_name=country_name.title(),
        packages=package_data
    )



def add_to_cart(user_id, package_id, quantity=1):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # بررسی اینکه آیا این پکیج از قبل در سبد خرید کاربر وجود دارد
        cursor.execute('''
            SELECT id, quantity FROM cart
            WHERE user_id = ? AND package_id = ?
        ''', (user_id, package_id))
        result = cursor.fetchone()

        if result:
            # اگر پکیج قبلاً موجود است، تعداد آن را افزایش می‌دهیم
            cart_id, current_quantity = result
            new_quantity = current_quantity + quantity
            cursor.execute('''
                UPDATE cart SET quantity = ?
                WHERE id = ?
            ''', (new_quantity, cart_id))
        else:
            # اگر پکیج وجود ندارد، یک رکورد جدید ایجاد می‌کنیم
            cursor.execute('''
                INSERT INTO cart (user_id, package_id, quantity)
                VALUES (?, ?, ?)
            ''', (user_id, package_id, quantity))

        conn.commit()
    except sqlite3.Error as e:
        print(f"خطا در افزودن به سبد خرید: {e}")
    finally:
        conn.close()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart_route():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # اگر لاگین نکرده به صفحه لاگین منتقل شود.

    user_id = session['user_id']
    package_id = request.form.get('package_id')

    if package_id:
        add_to_cart(user_id, package_id)  # اضافه کردن پکیج به سبد خرید
        flash('پکیج با موفقیت به سبد خرید اضافه شد!', 'success')
    else:
        flash('خطا: پکیج انتخاب‌شده معتبر نیست.', 'danger')

    return redirect(url_for('countries'))  # بازگشت به صفحه لیست کشورها




@app.route('/cart')
def view_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # دریافت محتویات سبد خرید کاربر
        cursor.execute('''
            SELECT cart.id, packages.name, packages.price, cart.quantity
            FROM cart
            JOIN packages ON cart.package_id = packages.id
            WHERE cart.user_id = ?
        ''', (user_id,))
        cart_items = cursor.fetchall()

        # محاسبه مجموع قیمت کل سبد خرید
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)

        return render_template('cart.html', cart_items=cart_items, total_price=total_price)
    finally:
        conn.close()


# مسیر نمایش سبد خرید
def get_cart_items(user_id):
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute('''
            SELECT cart.id, packages.name, cart.quantity, packages.price, (cart.quantity * packages.price) AS total_price
            FROM cart
            JOIN packages ON cart.package_id = packages.id
            WHERE cart.user_id = ?
        ''', (user_id,))
        items = cursor.fetchall()

        for item in items:
            print(f"پکیج: {item[1]}, تعداد: {item[2]}, قیمت واحد: {item[3]}€, قیمت کل: {item[4]}€")

        return items
    except sqlite3.Error as e:
        print(f"خطا در دریافت سبد خرید: {e}")
    finally:
        conn.close()


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    cart_id = request.form.get('cart_id')
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart WHERE id = ?', (cart_id,))
        conn.commit()
        flash('پکیج از سبد خرید حذف شد.', 'success')
    except Exception as e:
        flash('خطایی در حذف پکیج رخ داد.', 'danger')
    finally:
        conn.close()
    return redirect(url_for('view_cart'))

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    try:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        conn.commit()
        flash('سبد خرید با موفقیت خالی شد.', 'success')
    except Exception as e:
        flash('خطایی در پاک کردن سبد خرید رخ داد.', 'danger')
    finally:
        conn.close()
    return redirect(url_for('view_cart'))




@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # بررسی وضعیت لاگین
    if 'user' not in session:
        flash('Please log in to proceed to checkout.', 'warning')
        return redirect(url_for('login'))

    # ادامه فرایند ثبت سفارش
    if request.method == 'POST':
        cart = session.get('cart', [])
        total_price = sum(float(item['price']) for item in cart)

        # اطلاعات مشتری (در صورت نیاز)
        customer_info = {
            "name": session['user']['name'],
            "email": session['user']['email']
        }

        # شبیه‌سازی پرداخت
        if cart:
            session.pop('cart', None)  # پاک کردن سبد خرید پس از پرداخت
            return render_template('success.html', customer_info=customer_info, total_price=total_price)
        else:
            return redirect(url_for('view_cart'))

    cart = session.get('cart', [])
    total_price = sum(float(item['price']) for item in cart)
    return render_template('checkout.html', cart=cart, total_price=total_price)

@app.route('/search_countries', methods=['GET'])
def search_countries():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify([])  # در صورت خالی بودن ورودی هیچ نتیجه‌ای برنگردان

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # جستجو در ستون‌های edited_name و translated_name
    cursor.execute("""
        SELECT DISTINCT edited_name, translated_name
        FROM packages
        WHERE LOWER(edited_name) LIKE ? OR LOWER(translated_name) LIKE ?
        LIMIT 10
    """, (f"{query}%", f"{query}%"))

    results = cursor.fetchall()
    conn.close()

    # تبدیل داده‌ها به فرمت JSON
    countries = [{"english": row["edited_name"], "persian": row["translated_name"]} for row in results]
    return jsonify(countries)


if __name__ == '__main__':
    app.run(debug=True)
