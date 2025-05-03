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
        #database=database,
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

cursor.close()
conn.close()