from db_connection import get_db_connection

conn = get_db_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sys.tables")  # Check if tables exist
    tables = cursor.fetchall()
    
    print("📌 Tables in the database:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()
else:
    print("⚠️ Connection failed.")
