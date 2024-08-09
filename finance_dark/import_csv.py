import sqlite3
import pandas as pd

# Connect to the SQLite database (replace 'your_database.db' with your actual database file name)
conn = sqlite3.connect('finance.db')

# Specify the table name and the DataFrame
table_name = 'jobs'
df = pd.read_csv('output_csv_file_new.csv')  # Replace 'your_file.csv' with your actual CSV file name

# Remove any extra spaces in column names
df.columns = df.columns.str.strip()

# Append the DataFrame to the SQLite database
df.to_sql(table_name, conn, index=False, if_exists='append')

# Commit and close the connection
conn.commit()
conn.close()



