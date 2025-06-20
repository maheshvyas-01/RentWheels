import pyodbc

def get_db_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=MAHESH\\SQLEXPRESS;"  # Your SQL Server name
            "DATABASE=RentWheels;"
            "Trusted_Connection=yes;"
        )
        print("✅ Database connected successfully!")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None
