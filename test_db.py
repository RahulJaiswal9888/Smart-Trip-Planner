import mysql.connector

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Student123",  # Apna MySQL password yahan likho
        port=3306,
        database="smart_trip_planner"
    )

    if con.is_connected():
        print("MySQL connected successfully!")

    cur = con.cursor()
    cur.execute("SHOW TABLES")

    for table in cur.fetchall():
        print(table)

    cur.close()
    con.close()

except mysql.connector.Error as e:
    print("Database error:", e)