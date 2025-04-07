import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="login"
)

cursor = conn.cursor()


conn.commit()
conn.close()
