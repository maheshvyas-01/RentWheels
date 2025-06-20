import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
import pyodbc
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import get_user_bookings, get_booking_details
from fpdf import FPDF


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

# ------------------ Database Connection ------------------
def get_db_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=ABCDE\\SQLEXPRESS;"  # Replace with your server name
            "DATABASE=RentWheels;"  # Replace with your database name
            "Trusted_Connection=yes;",
            autocommit=True
        )
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# ------------------ Home Route ------------------
@app.route('/')
def home():
    return render_template('index.html')

# ------------------ About Us Route ------------------
@app.route('/about')
def about():
    return render_template('about.html')

# ------------------ Car Listings Route ------------------
@app.route('/car_listings')
def car_listings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT car_id, car_name, brand, model, year, price_per_day, image_url FROM Cars")
    cars = cursor.fetchall()
    conn.close()

    car_list = [{
        "car_id": car[0],  
        "car_name": car[1],
        "brand": car[2],
        "model": car[3],
        "year": car[4],
        "price_per_day": car[5],
        "image_url": car[6]
    } for car in cars]

    return render_template('car_listings.html', cars=car_list)

# ------------------ FAQ Route ------------------
@app.route('/faq')
def faq():
    return render_template('faq.html')

# ------------------ Contact Us Route ------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        conn = get_db_connection()
        if not conn:
            flash("Database connection error!", "danger")
            return render_template('contact.html')

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ContactUs (name, email, message) VALUES (?, ?, ?)", (name, email, message))
            conn.commit()
            flash("Message sent successfully!", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('contact.html')

# ------------------ Login Route ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        conn = get_db_connection()
        if not conn:
            flash("Database connection error!", "danger")
            return render_template('login.html')

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, full_name, phone, password_hash, is_admin FROM Users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if user:
                if check_password_hash(user[3], password):
                    session['user_id'] = user[0]
                    session['full_name'] = user[1]
                    session['phone'] = user[2]
                    session['is_admin'] = bool(user[4])  # Convert to boolean
                    flash("Login successful!", "success")
                    return redirect(url_for('admin_panel') if session['is_admin'] else url_for('home'))
                else:
                    flash("Invalid email or password!", "danger")
            else:
                flash("User not found!", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# ------------------ Registration Route ------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        if not name or not email or not phone or not password:
            flash("All fields are required!", "danger")
            return render_template('register.html')

        conn = get_db_connection()
        if not conn:
            flash("Database connection error!", "danger")
            return render_template('register.html')

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM Users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email is already registered! Please log in.", "warning")
                return redirect(url_for('login'))

            hashed_password = generate_password_hash(password)
            cursor.execute("INSERT INTO Users (full_name, email, phone, password_hash, is_admin) VALUES (?, ?, ?, ?, 0)", 
                           (name, email, phone, hashed_password))
            conn.commit()
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

# ------------------ Logout Route ------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out!", "info")
    return redirect(url_for('home'))


# ------------------ My Bookings Route ------------------
@app.route('/book_car/<int:car_id>', methods=['GET', 'POST'])
def book_car(car_id):
    if 'user_id' not in session:
        flash("Please log in to book a car.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('car_listings'))

    cursor = conn.cursor()

    # Fetch car details
    cursor.execute("SELECT car_name, price_per_day, image_url FROM Cars WHERE car_id = ?", (car_id,))
    car = cursor.fetchone()

    if not car:
        flash("Car not found!", "danger")
        return redirect(url_for('car_listings'))

    if request.method == 'POST':
        user_id = session['user_id']
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')

        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

            if start_date_obj >= end_date_obj:
                flash("End date must be after start date.", "danger")
                return redirect(url_for('book_car', car_id=car_id))

            price_per_day = car[1]  # Fetch price from tuple
            rental_days = (end_date_obj - start_date_obj).days
            total_price = rental_days * price_per_day

            start_date_str = start_date_obj.strftime("%Y-%m-%d")
            end_date_str = end_date_obj.strftime("%Y-%m-%d")

            # Insert booking and get the new booking_id
            cursor.execute("""
                INSERT INTO Bookings (user_id, car_id, start_date, end_date, total_price, status) 
                OUTPUT INSERTED.booking_id
                VALUES (?, ?, ?, ?, ?, 'Pending')
            """, (user_id, car_id, start_date_str, end_date_str, total_price))
            
            booking_id = cursor.fetchone()[0]  # Get the generated booking_id

            conn.commit()
            flash("Booking successful! Redirecting to payment...", "success")

            #Redirect to Payment Summary Page
            return redirect(url_for('payment_summary', booking_id=booking_id))

        except Exception as e:
            flash(f"Database error: {e}", "danger")

    cursor.close()
    conn.close()

    return render_template('book_car.html', car_id=car_id, car=car)

# ------------------ Payment Summary Route ------------------
@app.route('/payment_summary/<int:booking_id>')
def payment_summary(booking_id):
    if 'user_id' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('car_listings'))

    cursor = conn.cursor()

    # Fetch booking details
    cursor.execute("""
        SELECT b.booking_id, c.car_name, c.image_url, c.price_per_day, b.start_date, b.end_date, b.total_price
        FROM Bookings b
        JOIN Cars c ON b.car_id = c.car_id
        WHERE b.booking_id = ? AND b.user_id = ?
    """, (booking_id, session['user_id']))

    booking = cursor.fetchone()
    if not booking:
        flash("Booking not found!", "danger")
        return redirect(url_for('car_listings'))

    cursor.close()
    conn.close()

    return render_template('payment_summary.html', booking=booking)

# ------------------ Confirm Payment  Route ------------------
@app.route('/confirm_payment/<int:booking_id>', methods=['POST'])
def confirm_payment(booking_id):
    if 'user_id' not in session:
        flash("Please log in to continue.", "warning")
        return redirect(url_for('login'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('car_listings'))

    cursor = conn.cursor()

    # Fetch booking details
    cursor.execute("SELECT total_price FROM Bookings WHERE booking_id = ?", (booking_id,))
    booking = cursor.fetchone()

    if not booking:
        flash("Booking not found!", "danger")
        return redirect(url_for('car_listings'))

    total_price = float(booking.total_price)  # Convert Decimal to float
    tax = round(total_price * 0.18, 2)  # 18% GST
    total_amount = total_price + tax

    # Insert dummy payment
    try:
        cursor.execute("""
            INSERT INTO Payments (booking_id, amount, tax, total_amount, payment_status) 
            VALUES (?, ?, ?, ?, 'Paid')
        """, (booking_id, total_price, tax, total_amount))
        conn.commit()
        flash("Payment successful!", "success")
    except Exception as e:
        flash(f"Database error: {e}", "danger")

    cursor.close()
    conn.close()

    return redirect(url_for('payment_success', booking_id=booking_id))

# ------------------ Payment Success Route ------------------
@app.route('/payment_success/<int:booking_id>')
def payment_success(booking_id):
    print(f"✅ payment_success route called with booking_id: {booking_id}")  # Debugging print
    return render_template('payment_success.html', booking_id=booking_id)

# ------------------ Generate Invoice Route ------------------
# Route to generate and download invoice PDF

@app.route('/download_invoice/<int:booking_id>')
def download_invoice(booking_id):
    # Fetch booking details from the database
    booking = get_booking_details(booking_id)

    if not booking:
        flash("Booking not found!", "error")
        return redirect(url_for('my_bookings'))

    # Create PDF invoice
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Use built-in fonts to avoid missing TTF errors
    pdf.set_font("Arial", "B", 16)

    # Title
    pdf.cell(200, 10, "RentWheels Invoice", ln=True, align="C")
    pdf.ln(10)
    
    # Booking details
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Booking ID: {booking['booking_id']}", ln=True, align="L")
    pdf.cell(200, 10, f"Customer: {booking['user_name']}", ln=True, align="L")
    pdf.cell(200, 10, f"Car: {booking['car_name']} ({booking['car_model']})", ln=True, align="L")
    pdf.cell(200, 10, f"Booking Dates: {booking['start_date']} to {booking['end_date']}", ln=True, align="L")
    pdf.cell(200, 10, f"Total Amount: Rs. {booking['total_price']}", ln=True, align="L")  # Changed ₹ to Rs.
    pdf.ln(10)

    pdf.cell(200, 10, "Thank you for choosing RentWheels!", ln=True, align="C")

    # Ensure the invoice folder exists
    invoice_folder = "static/invoices"
    os.makedirs(invoice_folder, exist_ok=True)  

    # Save PDF
    invoice_path = f"{invoice_folder}/invoice_{booking_id}.pdf"
    pdf.output(invoice_path)

    # Serve the PDF for download
    return send_file(invoice_path, as_attachment=True)

# ------------------ View Bookings Route ------------------
@app.route('/my_bookings')
def my_bookings():
    if 'user_id' not in session:
        flash("Please log in to view your bookings.", "danger")
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_id = session['user_id']
    bookings = get_user_bookings(user_id)  # Fetch bookings from DB

    return render_template('my_bookings.html', bookings=bookings)


# ------------------ Admin Panel Route ------------------
@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))
    
    return render_template('admin.html')

# ------------------ Manage Cars (Admin) ------------------
@app.route('/admin/manage-cars')
def manage_cars():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('admin_panel'))

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT car_id, car_name, brand, model, year, price_per_day, image_url FROM Cars")
        cars = cursor.fetchall()

        # Convert the result into a list of dictionaries
        car_list = []
        for car in cars:
            car_list.append({
                "car_id": car[0],
                "car_name": car[1],
                "brand": car[2],
                "model": car[3],
                "year": car[4],
                "price_per_day": car[5],
                "image_url": car[6]
            })

        return render_template('manage_cars.html', cars=car_list)

    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return render_template('manage_cars.html', cars=[])


# ------------------ Add New Car (Admin) ------------------
@app.route('/admin/add-car', methods=['GET', 'POST'])
def add_car():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        car_name = request.form.get('car_name')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        price_per_day = request.form.get('price_per_day')
        image_url = request.form.get('image_url')  # Store image URL

        if not (car_name and brand and model and year and price_per_day and image_url):
            flash("All fields are required!", "danger")
            return render_template('add_car.html')

        conn = get_db_connection()
        if not conn:
            flash("Database connection error!", "danger")
            return render_template('add_car.html')

        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Cars (car_name, brand, model, year, price_per_day, image_url) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (car_name, brand, model, int(year), float(price_per_day), image_url))
            conn.commit()
            flash("Car added successfully!", "success")
            return redirect(url_for('manage_cars'))
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return render_template('add_car.html')


# ------------------ Edit Car (Admin) ------------------
@app.route('/admin/edit-car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('manage_cars'))

    cursor = conn.cursor()

    if request.method == 'POST':
        car_name = request.form.get('car_name')
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        price_per_day = request.form.get('price_per_day')
        image_url = request.form.get('image_url')

        if not (car_name and brand and model and year and price_per_day and image_url):
            flash("All fields are required!", "danger")
            return redirect(url_for('edit_car', car_id=car_id))

        try:
            cursor.execute("""
                UPDATE Cars
                SET car_name = ?, brand = ?, model = ?, year = ?, price_per_day = ?, image_url = ?
                WHERE car_id = ?
            """, (car_name, brand, model, int(year), float(price_per_day), image_url, car_id))
            conn.commit()
            flash("Car updated successfully!", "success")
            return redirect(url_for('manage_cars'))
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    # GET request - fetch car details to pre-fill form
    cursor.execute("SELECT * FROM Cars WHERE car_id = ?", (car_id,))
    car = cursor.fetchone()
    cursor.close()
    conn.close()

    if car is None:
        flash("Car not found!", "danger")
        return redirect(url_for('manage_cars'))

    return render_template('edit_car.html', car=car)


# ------------------ Delete Car (Admin) ------------------
@app.route('/admin/delete-car/<int:car_id>')
def delete_car(car_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('manage_cars'))

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Cars WHERE car_id = ?", (car_id,))
        conn.commit()
        flash("Car deleted successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('manage_cars'))


# ------------------ Manage Users (Admin) ------------------
# ------------------ Manage Users (Admin) ------------------ 
@app.route('/admin/manage-users')
def manage_users():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('admin_panel'))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, full_name, email, phone, is_admin
            FROM Users
        """)
        users = cursor.fetchall()

        # Convert result into a list of dictionaries for easier HTML rendering
        user_list = []
        for user in users:
            user_list.append({
                "user_id": user[0],
                "full_name": user[1],
                "email": user[2],
                "phone": user[3],
                "is_admin": user[4]
            })

        return render_template('manage_users.html', users=user_list)

    except Exception as e:
        flash(f"Error fetching users: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return render_template('manage_users.html', users=[])

# ------------------ Delete User (Admin) ------------------ 
@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Optional: Prevent deleting admin users
        cursor.execute("SELECT is_admin FROM Users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            flash("Cannot delete admin users!", "warning")
            return redirect(url_for('manage_users'))

        # Proceed with deletion
        cursor.execute("DELETE FROM Users WHERE user_id = ?", (user_id,))
        conn.commit()

        flash("User deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting user: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('manage_users'))


# ------------------ View Messages (Admin) ------------------
# ------------------ View Messages (Admin) ------------------ 
@app.route('/admin/view-messages')
def view_messages():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('admin_panel'))

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT message_id, name, email, message, created_at
            FROM ContactUs
        """)
        messages = cursor.fetchall()

        # Convert result into a list of dictionaries for easier HTML rendering
        message_list = []
        for message in messages:
            message_list.append({
                "message_id": message[0],
                "name": message[1],
                "email": message[2],
                "message_content": message[3],
                "created_at": message[4]
            })

        return render_template('view_messages.html', messages=message_list)

    except Exception as e:
        flash(f"Error fetching messages: {e}", "danger")
    finally:
        cursor.close()
        conn.close()

    return render_template('view_messages.html', messages=[])


# ------------------ View Bookings (Admin) ------------------
# ------------------ View Bookings & Payments (Admin) ------------------
@app.route('/admin/view-bookings', methods=['GET', 'POST'])
def view_bookings():
    if 'user_id' not in session or not session.get('is_admin'):
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('home'))

    conn = get_db_connection()
    if not conn:
        flash("Database connection error!", "danger")
        return redirect(url_for('admin_panel'))

    try:
        cursor = conn.cursor()

        # Handle status update via POST request
        if request.method == 'POST':
            booking_id = request.form.get('booking_id')
            new_status = request.form.get('status')
            if new_status not in ['Confirmed', 'Cancelled']:
                flash("Invalid status update!", "danger")
            else:
                cursor.execute("UPDATE Bookings SET status = ? WHERE booking_id = ?", (new_status, booking_id))
                conn.commit()
                flash(f"Booking #{booking_id} status updated to {new_status}.", "success")

        cursor.execute("""
            SELECT 
                B.booking_id,
                U.full_name,
                C.car_name,
                B.start_date,
                B.end_date,
                B.status AS booking_status,
                B.created_at AS booking_created_at,
                P.payment_status,
                P.amount,
                P.tax,
                P.total_amount,
                P.created_at AS payment_created_at
            FROM Bookings B
            JOIN Users U ON B.user_id = U.user_id
            JOIN Cars C ON B.car_id = C.car_id
            LEFT JOIN Payments P ON B.booking_id = P.booking_id
            ORDER BY B.created_at DESC
        """)
        results = cursor.fetchall()

        booking_list = []
        for row in results:
            booking_list.append({
                "booking_id": row[0],
                "user_name": row[1],
                "car_name": row[2],
                "start_date": row[3],
                "end_date": row[4],
                "booking_status": row[5],
                "booking_created_at": row[6],
                "payment_status": row[7] or "Not Available",
                "amount": row[8],
                "tax": row[9],
                "total_amount": row[10],
                "payment_created_at": row[11]
            })

        return render_template('view_bookings.html', bookings=booking_list)

    except Exception as e:
        flash(f"Error fetching bookings: {e}", "danger")
        return render_template('view_bookings.html', bookings=[])
    finally:
        cursor.close()
        conn.close()

# ------------------ Run the App ------------------
if __name__ == '__main__':
    app.run(debug=True)
