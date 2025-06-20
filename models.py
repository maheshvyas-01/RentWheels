import pyodbc

# Database connection function
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=MAHESH\\SQLEXPRESS;"
        "DATABASE=RentWheels;"
        "Trusted_Connection=yes;"
    )
    return conn

# ✅ Function to fetch all cars
def get_all_cars():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cars")  # Ensure the table exists
    cars = cursor.fetchall()
    conn.close()
    return cars

# ✅ Function to add a booking
def add_booking(user_id, car_id, start_date, end_date, total_cost):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Bookings (user_id, car_id, start_date, end_date, total_cost) VALUES (?, ?, ?, ?, ?)",
        (user_id, car_id, start_date, end_date, total_cost),
    )
    conn.commit()
    conn.close()
    return True

# ✅ Function to fetch all bookings
def get_user_bookings(user_id):
    conn = get_db_connection()  # Establish connection
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.booking_id, c.car_name, b.start_date, b.end_date, b.total_price, b.status, b.created_at
        FROM Bookings b
        JOIN Cars c ON b.car_id = c.car_id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (user_id,))
    bookings = cursor.fetchall()  # Fetch results
    conn.close()  # Close connection
    return bookings  # Return results

# ✅ Function to update booking status
def get_booking_details(booking_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT 
        b.booking_id, 
        u.full_name AS user_name, 
        c.car_name, 
        c.model AS car_model, 
        b.start_date, 
        b.end_date, 
        b.total_price, 
        b.status 
    FROM Bookings b
    JOIN Users u ON b.user_id = u.user_id
    JOIN Cars c ON b.car_id = c.car_id
    WHERE b.booking_id = ?
    """
    cursor.execute(query, (booking_id,))
    result = cursor.fetchone()
    
    conn.close()

    if result:
        return {
            "booking_id": result[0],
            "user_name": result[1],
            "car_name": result[2],
            "car_model": result[3],
            "start_date": result[4],
            "end_date": result[5],
            "total_price": result[6],
            "status": result[7]
        }
    return None
