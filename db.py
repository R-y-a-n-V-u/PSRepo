import mysql.connector

HOST = "pokemonshowdowndb.cbiwcoou81sx.us-east-2.rds.amazonaws.com"
USER = "admin"
PASSWORD = "PSMVP2025!"
DATABASE = "pokemonshowdowndb"
PORT = 3306

def connectToDB(host, user, password, database, port):
    # Connect without specifying a database first
    print("Connecting to cloud service")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=port
    )
    print("Done connecting")

    cursor = conn.cursor()

    # Create a new database
    #cursor.execute("CREATE DATABASE IF NOT EXISTS mytestdb;")
    #print("Database created or already exists.")

    return cursor, conn


print("Attempting to connect to cloud service")
cursor, conn = connectToDB(HOST, USER, PASSWORD, DATABASE, PORT)
print("Out of connection function")

def createDatabase(cursor, database):
    # Create a new database
    queryString = "CREATE DATABASE IF NOT EXISTS " + database
    cursor.execute(queryString)
    print("Database created or already exists")

createDatabase(cursor, DATABASE)

def createTable(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS data (
        id INT AUTO_INCREMENT PRIMARY KEY,
        game_id VARCHAR(255) UNIQUE,
        json TEXT,
        elo INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    """)
    print("Table created successfully or table already created")


import json

def insertJSON(cursor, conn, data):
    try:
        game_id = data["id"]
        json_text = json.dumps(data)
        
        # Safely extract ELO values
        try:
            # New format handling
            p1_elo = data["pre_battle"][0].split('|')[-1]  # Gets the last part after |
            p2_elo = data["pre_battle"][1].split('|')[-1]  # Gets the last part after |
            
            elo = (int(p1_elo) + int(p2_elo)) / 2
            print(f"ELO  = ${elo}, elo 1 = ${p1_elo} elo 2 = ${p2_elo}")
            print(f"data[pre_battle][2] = ${data['pre_battle'][2].split('|')} ")
        except (IndexError, ValueError):
            # Fallback if ELO data isn't available
            elo = 0
        
        sql = "INSERT IGNORE INTO data (game_id, json, elo) VALUES (%s, %s, %s)"
        val = (game_id, json_text, elo)
        
        cursor.execute(sql, val)
        conn.commit()
        print(f"Successfully inserted row for {game_id}")
        return True
    except Exception as e:
        print(f"Error inserting data for {data.get('id', 'unknown')}: {str(e)}")
        return False

def printRows(cursor):
    query = "SELECT * FROM data"
    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)


cursor.close()
conn.close()

