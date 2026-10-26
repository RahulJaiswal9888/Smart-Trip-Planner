import os
import mysql.connector

# Defaults match your existing settings. Override with environment variables if needed:
#   $env:DB_PASSWORD="your_password"
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "Student123"),
    "port": int(os.getenv("DB_PORT", "3306")),
}
DB_NAME = os.getenv("DB_NAME", "smart_trip_planner")


def connect_db():
    return mysql.connector.connect(database=DB_NAME, **DB_CONFIG)


def initialize_database():
    # Create the database only if it does not exist (nothing is dropped).
    server = mysql.connector.connect(**DB_CONFIG)
    try:
        cur = server.cursor()
        cur.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        server.commit()
        cur.close()
    finally:
        server.close()

    con = connect_db()
    try:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INT AUTO_INCREMENT PRIMARY KEY,
                traveler_name VARCHAR(100) NOT NULL,
                start_city VARCHAR(100) NOT NULL,
                destination VARCHAR(100) NOT NULL,
                start_date DATE NOT NULL,
                duration_days INT NOT NULL,
                travelers INT NOT NULL,
                budget DECIMAL(12,2) NOT NULL,
                travel_style VARCHAR(50) NOT NULL,
                estimated_total DECIMAL(12,2) NOT NULL,
                itinerary_json LONGTEXT NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'Planned',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("SHOW COLUMNS FROM trips LIKE 'status'")
        if not cur.fetchone():
            cur.execute(
                "ALTER TABLE trips ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'Planned'"
            )
        con.commit()
        cur.close()
    finally:
        con.close()


def save_trip(trip):
    con = connect_db()
    try:
        cur = con.cursor()
        cur.execute("""
            INSERT INTO trips (
                traveler_name, start_city, destination,
                start_date, duration_days, travelers,
                budget, travel_style, estimated_total,
                itinerary_json
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            trip["traveler_name"],
            trip["start_city"],
            trip["destination"],
            trip["start_date"],
            trip["duration_days"],
            trip["travelers"],
            trip["budget"],
            trip["travel_style"],
            trip["estimated_total"],
            trip["itinerary_json"],
        ))
        con.commit()
        trip_id = cur.lastrowid
        cur.close()
        return trip_id
    finally:
        con.close()


def get_trips():
    con = connect_db()
    try:
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT * FROM trips ORDER BY created_at DESC, id DESC")
        trips = cur.fetchall()
        cur.close()
        return trips
    finally:
        con.close()


def delete_trip(trip_id):
    con = connect_db()
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM trips WHERE id = %s", (trip_id,))
        deleted = cur.rowcount > 0
        if deleted:
            cur.execute("SELECT id FROM trips ORDER BY id")
            existing_ids = [row[0] for row in cur.fetchall()]

            for existing_id in existing_ids:
                cur.execute("UPDATE trips SET id = %s WHERE id = %s", (-existing_id, existing_id))
            for new_id, existing_id in enumerate(existing_ids, start=1):
                cur.execute("UPDATE trips SET id = %s WHERE id = %s", (new_id, -existing_id))

            con.commit()
            cur.execute(f"ALTER TABLE trips AUTO_INCREMENT = {len(existing_ids) + 1}")
        else:
            con.commit()
        cur.close()
        return deleted
    finally:
        con.close()


def cancel_trip(trip_id):
    return delete_trip(trip_id)