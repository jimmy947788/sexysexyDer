# Module Imports
import mariadb
import sys
import os
from dotenv import load_dotenv

load_dotenv() 
# Connect to MariaDB Platform
try:
    passwd=os.getenv("MYSQL_ROOT_PASSWORD")
    print(f"passwd={passwd}")

    
    conn = mariadb.connect(
        user="root",
        password=passwd,
        host="192.168.0.150",
        port=3306,
        database="SexsexDer"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()