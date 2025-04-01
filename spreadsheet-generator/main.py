import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import numpy as np

import os

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
    

def create_table_manually(conn):
    try:
        cursor = conn.cursor()

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INTEGER,
                grade FLOAT,
                active BOOLEAN
            );
        '''

        cursor.execute(create_table_query)
        conn.commit()
        print("Students table created")
    except Exception as e:
        print(f"Error: {e}")

def create_table(conn, df):
    schema = {}

    for column in df.columns:
        # get type of each column
        dtype = df[column].dtype

        # if column has nulls, then make type null
        has_nulls = df[column].isnull().any()
        nullable = "" if has_nulls else "NOT NULL"

        if np.issubdtype(dtype, np.integer):
            schema[column] = f"INTEGER {nullable}"
        elif np.issubdtype(dtype, np.floating):
            schema[column] = f"REAL {nullable}"
        elif np.issubdtype(dtype, np.floating):
            schema[column] = f"REAL {nullable}"
        elif np.issubdtype(dtype, np.floating):
            schema[column] = f"REAL {nullable}"
        elif np.issubdtype(dtype, np.floating):
            schema[column] = f"REAL {nullable}"



def load_csv_to_df(csv_path):
    try:
        df = pd.read_csv(csv_path)

        return df
    except Exception as e:
        print(f"Error loading DF: {e}")
        return None
    
def insert_df_to_sql(df, table_name, engine, if_exists="replace"):
    try:
        df.to_sql(table_name, engine, if_exists=if_exists)
        print(f"Successful insertion into: {table_name}")

    except Exception as e:
        print(f"Error inserting data: {e}")

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


def main():
    csv_path = generate_sample_csv()

    conn, engine = connect_to_database()
    if conn is None or engine is None:
        return 
    
    create_table(conn)

    df = load_csv_to_df(csv_path)
    if df is None:
        conn.close()
        return
    
    insert_df_to_sql(df, "students", engine)

    conn.close()
    print("Connection closed")

if __name__ == "__main__":
    main()



