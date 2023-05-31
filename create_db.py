import sqlite3

# Function to create the table booking database
def create_table():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT,
                사번 TEXT,
                name TEXT,
                table_number INTEGER,
                booking_date TEXT,
                status TEXT)''')
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    create_table()