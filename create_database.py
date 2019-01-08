import sqlite3
sqlite_file = 'Data/configuration.sqlite'    # name of the sqlite database file
table_name1 = 'Camera'  # name of the table to be created
table_name2 = 'Triggerers'  # name of the table to be created

# Connecting to the database file
conn = sqlite3.connect(sqlite_file)
c = conn.cursor()

# Creating a new SQLite table with required columns
c.execute('''CREATE TABLE {tn}
          (ID INT PRIMARY KEY NOT NULL,
          DEVICE TEXT NOT NULL,
          STATUS TEXT,
          DEFAULT_SENSITIVITY INTEGER NOT NULL,
          CURRENT_SENSITIVITY INTEGER NOT NULL)'''.format(tn=table_name1))
          
# Creating a new SQLite table with required columns
c.execute('''CREATE TABLE {tn}
          (ID INT PRIMARY KEY NOT NULL,
          INPUT_DEVICE TEXT NOT NULL,
          STATUS TEXT,
          ALARM1 INTEGER,
          ALARM2 INTEGER,
          ALARM3 INTEGER,
          ALARM4 INTEGER
          ALARM5 INTEGER)'''.format(tn=table_name2))





# Committing changes and closing the connection to the database file
conn.commit()
conn.close()
