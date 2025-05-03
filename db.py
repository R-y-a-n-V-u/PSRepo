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

createTable(cursor)

import json

def insertJSON(cursor, conn, json_file):
    f = open(json_file, 'r')
    data = json.load(f)
    game_id = data["id"]
    json_text = json.dumps(data)
    elo = int(data["pre_battle"][2][-4:]) + int(data["pre_battle"][3][-4:])
    sql = "INSERT IGNORE INTO data (game_id, json, elo) VALUES (%s, %s, %s)"
    val = (game_id, json_text, elo)
    cursor.execute(sql, val)
    conn.commit()
    f.close()
    print("Successfully inserted row")


insertJSON(cursor, conn, "gen9ou-2172099392_clean.json")

def printRows(cursor):
    query = "SELECT * FROM data"
    cursor.execute(query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)

printRows(cursor)

cursor.close()
conn.close()