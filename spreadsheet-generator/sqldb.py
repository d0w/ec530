import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import numpy as np
import logging
import requests
import json

logger = logging.getLogger(__name__)

import os

def list_tables(conn):

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        cursor.close()

        if tables:
            for i, (table,) in enumerate(tables, 1):
                print(f"{i}: {table}")
        else:
            print("No tables found in DB")

        return [table[0] for table in tables]
    except Exception as e:
        logger.error(e)
        return []
    
def execute_query(conn, query):
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        logger.debug("Executed query")

        # check if query is a SELECT
        if query.strip().upper().startswith("SELECT"):
            col_names = [description[0] for description in cursor.description]

            results = cursor.fetchall()

            if results:
                header = " | ".join(col_names)
                separator = "-" * len(header)
                print(f"\n{header}")
                print(separator)

                for row in results:
                    formatted_row = " | ".join(str(val) for val in row)
                    print(formatted_row)
                
                print(f"\n{len(results)} rows returned.")

            else:
                print("\nNo results from query")
        else:
            rows_affected = cursor.rowcount
            conn.commit()
            print(f"Query affected {rows_affected} rows")
        
        cursor.close()
        return True

    except Exception as e:
        logger.error(e)
        return False


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



def create_table_automatically(conn, df, table_name):
    def generate_schema_from_df(df):
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
            elif np.issubdtype(dtype, np.datetime64):
                schema[column] = f"TIMESTAMP {nullable}"
            elif np.issubdtype(dtype, np.bool_):
                schema[column] = f"BOOLEAN {nullable}"
            else:
                schema[column] = f"TEXT {nullable}"

        return schema
    
    try:
        cursor = conn.cursor()

        schema = generate_schema_from_df(df)

        columns_def = []
        primary_key = None

        if "id" in schema:
            columns_def.append(f"id {schema["id"]} PRIMARY KEY")
            primary_key = "id"
        else:
            columns_def.append("id SERIAL PRIMARY KEY")

        for column, data_type in schema.items():
            if column != primary_key:
                columns_def.append(f"{column} {data_type}")

        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {",".join(columns_def)}
            );
        """

        print(f"SQL: {create_table_query}")
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table {table_name} created")

        for column, data_type in schema.items():
            print(f"    {column}: {data_type}")

        cursor.close()

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        

def load_csv_to_df(csv_path):
    try:
        df = pd.read_csv(csv_path)

        return df
    except Exception as e:
        print(f"Error loading DF: {e}")
        return None

# --------- AI Integration ----------
def get_table_schema_info(conn):
    """Get detailed schema information for all tables in the database"""
    schema_info = []
    
    try:
        cursor = conn.cursor()
        
        # Get list of all tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # Get column information for each table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            # Get sample data (first row) to understand content
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1;")
                sample = cursor.fetchone()
                sample_data = "No data available"
                if sample:
                    sample_data = ", ".join([f"{col}: {val}" for col, val in zip([c[0] for c in columns], sample)])
            except:
                sample_data = "Error retrieving sample data"
            
            # Format table schema information
            table_info = {
                "table_name": table_name,
                "columns": [{"name": col[0], "type": col[1], "nullable": col[2]} for col in columns],
                "sample_data": sample_data
            }
            
            schema_info.append(table_info)
        
        cursor.close()
        return schema_info
    
    except Exception as e:
        logger.error(f"Error getting schema info: {e}")
        return []


def insert_df_to_sql(df, table_name, engine, if_exists="replace"):
    try:
        df.to_sql(table_name, engine, if_exists=if_exists)
        print(f"Successful insertion into: {table_name}")

    except Exception as e:
        print(f"Error inserting data: {e}")

def generate_sql_with_ollama(schema_info, user_query, model):
    """Generate SQL using OpenAI's API from natural language query"""
    try:
        # Create a prompt with schema information and user query
        schema_text = ""
        for table in schema_info:
            schema_text += f"Table: {table['table_name']}\n"
            schema_text += "Columns:\n"
            for col in table['columns']:
                schema_text += f"  - {col['name']} ({col['type']}, {'NULL' if col['nullable'] == 'YES' else 'NOT NULL'})\n"
            schema_text += f"Sample data: {table['sample_data']}\n\n"
        
        prompt = f"""You are an AI assistant tasked with converting user queries into SQL statements. 
The database uses PostgreSQL and contains the following tables:

{schema_text}

User Query: "{user_query}"

Your task is to:
1. Generate a SQL query that accurately answers the user's question.
2. Ensure the SQL is compatible with PostgreSQL syntax.
3. Provide a short comment explaining what the query does.

Output Format:
- SQL Query (enclosed in ```sql code blocks)
- Explanation
"""
        
        ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")

        data = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }

        res = requests.post(
            ollama_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(data)
        )
        
        result = res.json()
        response_text = result.get("response", "")

        if "```sql" in response_text:
            sql_start = response_text.find("```sql") + 6
            sql_end = response_text.find("```", sql_start)
            sql_query = response_text[sql_start:sql_end].strip()
        else:
            lines = response_text.split("\n")
            sql_query = ""
            for line in lines:
                if line.strip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP")):
                    sql_query = line
                    break

        explanation = response_text.split("Explanation:", 1)[-1].strip() if "Explanation:" in response_text else "No explanation provided"

        return sql_query, explanation
        
    except Exception as e:
        logger.error(f"Error generating SQL: {e}")
        return None, f"Error generating SQL: {str(e)}"

# uses Ollama for local LLM usage
def natural_language_query(conn, user_query):
    """Process a natural language query and execute the generated SQL"""
    try:
        # # Get API key from environment variable
        # api_key = os.getenv("OPENAI_API_KEY")
        # if not api_key:
        #     print("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        #     return False
        
        # Get schema information
        print("Analyzing database schema...")
        schema_info = get_table_schema_info(conn)
        
        if not schema_info:
            print("No schema information available. Make sure you have tables in your database.")
            return False
        
        model = os.getenv("OLLAMA_MODEL", "deepseek-r1:1.5b")
        print(f"Generating SQL using Ollama ({model})")
        sql_query, explanation = generate_sql_with_ollama(schema_info, user_query, model)

        if not sql_query:
            print(f"Failed to generate SQL: {explanation}")
            return False
        
        # Show the generated SQL and explanation
        print("\n=== Generated SQL Query ===")
        print(sql_query)
        print("\n=== Explanation ===")
        print(explanation)
        
        # Ask user if they want to execute the query
        execute = input("\nDo you want to execute this query? (y/n): ").lower() == 'y'
        if execute:
            # Execute the query
            return execute_query(conn, sql_query)
        else:
            print("Query execution cancelled.")
            return False
    
    except Exception as e:
        logger.error(f"Error in natural language query: {e}")
        print(f"Error processing your query: {str(e)}")
        return False
