import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import numpy as np
import logging

import sqldb as db

logger = logging.getLogger(__name__)

import os

from dotenv import load_dotenv

load_dotenv()

def connect_to_database():
    """create connectiont to DB"""
    try:
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "postgres")

        engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")

        conn = psycopg2.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_name
        )  

        print("Successfully connected to Postgresql")
        return conn, engine
    except Exception as e:
        print("error connecting to DB")
        return None, None
    

def generate_sample_csv():
    """Generate a sample CSV file if one doesn't exist"""
    csv_path = 'sample_students.csv'
    
    if not os.path.exists(csv_path):
        # Create sample data
        import numpy as np
        
        np.random.seed(42)
        n_samples = 100
        
        data = {
            'name': [f"Student_{i}" for i in range(1, n_samples+1)],
            'age': np.random.randint(18, 25, n_samples),
            'grade': np.random.normal(75, 15, n_samples),
            'active': np.random.choice([True, False], n_samples)
        }
        
        sample_df = pd.DataFrame(data)
        sample_df['grade'] = sample_df['grade'].clip(0, 100).round(2)
        sample_df.to_csv(csv_path, index=False)
        print(f"Generated sample CSV file: {csv_path}")
    
    return csv_path

def process_csv(conn, engine):
    csv_path = input("Enter path to csv file: ")
    if csv_path == "":
        csv_path = generate_sample_csv()
    


    df = db.load_csv_to_df(csv_path)
    if df is None:
        logger.error("No CSV found")
        conn.close()
        return
    
    table_name = os.path.splitext(os.path.basename(csv_path))[0]
    db.create_table_automatically(conn, df, table_name)

    db.insert_df_to_sql(df, "sample_students", engine)

    conn.close()


def main():

    try:

        conn, engine = connect_to_database()
        if conn is None or engine is None:
            return 
        
        while True:
            print("\n=== PostgreSQL CSV Operations ===")
            print("1. Process CSV file (create table & insert data)")
            print("2. List available tables")
            print("3. View sample data from a table")
            print("4. Run SQL query")
            print("5. Export table to CSV")
            print("6. Ask in plain english")
            print("7. Exit")

            choice = input("\nEnter choice: ")

            if choice == "1":
                # process CSV
                process_csv(conn, engine)
                continue
            elif choice == "2":
                # list tables
                db.list_tables(conn)
                continue
            elif choice == "3":
                # view sample data
                continue
            elif choice == "4":
                # run sql query
                print("\n--- SQL Query Execution ---")
                print("Enter SQL Query (exit to cancel): ")
                query_lines = []

                while True:
                    line = input()
                    if line.lower() == "exit":
                        break
                    query_lines.append(line)

                    if line.strip().endswith(";"):
                        break

                logger.debug(query_lines)

                if query_lines:
                    query = ' '.join(query_lines)
                    db.execute_query(conn, query)
                continue
            elif choice == "5":
                continue
            elif choice == "6":
                # plain english using AI
                print("\n--- Ask in Plain English")
                print("Exit to cancel")

                user_query = input("What would you like to do: ")
                if user_query.lower() != "exit":
                    db.natural_language_query(conn, user_query)

                continue
            elif choice == "7":
                print("\nExiting program")
                break
            else:
                print("\nInvalid choice")

    except Exception as e:
        logger.error(e)

    finally:
        if conn:
            conn.close()
            print("Connection closed")

if __name__ == "__main__":
    main()



