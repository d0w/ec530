import unittest
import sys
import os
import pandas as pd
import numpy as np
import psycopg2
from sqlalchemy import create_engine
from unittest.mock import MagicMock, patch
import logging

# Add parent directory to path so we can import sqldb
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sqldb

class TestSQLDB(unittest.TestCase):
    """Test cases for the sqldb.py module"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database connection"""
        # Use test database settings - these can be different from your main DB
        db_user = os.getenv("TEST_DB_USER", "postgres")
        db_password = os.getenv("TEST_DB_PASSWORD", "postgres")
        db_host = os.getenv("TEST_DB_HOST", "localhost")
        db_port = os.getenv("TEST_DB_PORT", "5432")
        db_name = os.getenv("TEST_DB_NAME", "postgres_test")
        
        # Try to connect to test DB, if it fails use mock
        try:
            cls.engine = create_engine(f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
            cls.conn = psycopg2.connect(
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                database=db_name
            )
            cls.using_real_db = True
            print("Using real PostgreSQL database for tests")
        except Exception as e:
            print(f"Could not connect to test database: {e}")
            print("Using mock database for tests")
            cls.conn = MagicMock()
            cls.engine = MagicMock()
            cls.using_real_db = False
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        if cls.using_real_db:
            # Drop test tables if we created any
            try:
                cursor = cls.conn.cursor()
                # First check if tables exist
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema='public' AND 
                          table_name IN ('test_students', 'test_courses');
                """)
                tables = cursor.fetchall()
                
                # Drop each test table
                for table in tables:
                    cursor.execute(f"DROP TABLE {table[0]};")
                
                cls.conn.commit()
                cursor.close()
            except Exception as e:
                print(f"Error cleaning up test database: {e}")
            
            # Close connection
            cls.conn.close()
    
    def setUp(self):
        """Set up before each test"""
        # Create test data for each test
        self.test_df = pd.DataFrame({
            'name': ['Student_1', 'Student_2', 'Student_3'],
            'age': [20, 22, 19],
            'grade': [85.5, 92.3, 78.9],
            'active': [True, True, False]
        })
        
        # Skip DB tests if we're using mocks
        if not self.using_real_db:
            self.skipTest("Skipping test that requires real database connection")
    
    def test_list_tables(self):
        """Test listing tables from database"""
        # Mock the cursor and its methods
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [('table1',), ('table2',)]
        
        # Mock the connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function with our mock
        result = sqldb.list_tables(mock_conn)
        
        # Verify the results
        self.assertEqual(result, ['table1', 'table2'])
        mock_cursor.execute.assert_called_once()
    
    def test_execute_query_select(self):
        """Test executing a SELECT query"""
        # Mock the cursor and its methods
        mock_cursor = MagicMock()
        mock_cursor.description = [('col1',), ('col2',)]
        mock_cursor.fetchall.return_value = [(1, 'a'), (2, 'b')]
        
        # Mock the connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function with our mock
        result = sqldb.execute_query(mock_conn, "SELECT * FROM test;")
        
        # Verify the results
        self.assertTrue(result)
        mock_cursor.execute.assert_called_with("SELECT * FROM test;")
        mock_conn.commit.assert_not_called()  # SELECT doesn't need commit
    
    def test_execute_query_update(self):
        """Test executing an UPDATE query"""
        # Mock the cursor and its methods
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 2  # Simulate 2 rows affected
        
        # Mock the connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function with our mock
        result = sqldb.execute_query(mock_conn, "UPDATE test SET col1=1;")
        
        # Verify the results
        self.assertTrue(result)
        mock_cursor.execute.assert_called_with("UPDATE test SET col1=1;")
        mock_conn.commit.assert_called_once()  # UPDATE needs commit
    
    def test_execute_query_error(self):
        """Test error handling in execute_query"""
        # Mock the cursor that raises an exception
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("SQL Error")
        
        # Mock the connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function with our mock
        result = sqldb.execute_query(mock_conn, "INVALID SQL;")
        
        # Verify the results
        self.assertFalse(result)
    
    @unittest.skipIf(not hasattr(sqldb, 'create_table_automatically'), "create_table_automatically not implemented")
    def test_create_table_automatically(self):
        """Test creating a table automatically from DataFrame"""
        if not self.using_real_db:
            self.skipTest("Skipping test that requires real database")
        
        # Create a table from our test DataFrame
        table_name = 'test_students'
        sqldb.create_table_automatically(self.conn, self.test_df, table_name)
        
        # Check if table was created by querying it
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 0;")
        
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        cursor.close()
        
        # Verify the columns match our DataFrame (plus maybe an ID column)
        for col in self.test_df.columns:
            self.assertIn(col, col_names)
    
    @unittest.skipIf(not hasattr(sqldb, 'load_csv_to_df'), "load_csv_to_df not implemented")
    def test_load_csv_to_df(self):
        """Test loading a CSV file to DataFrame"""
        # Create a temporary CSV file
        temp_csv = 'temp_test.csv'
        self.test_df.to_csv(temp_csv, index=False)
        
        try:
            # Load the CSV
            result_df = sqldb.load_csv_to_df(temp_csv)
            
            # Verify the DataFrame was loaded correctly
            self.assertIsNotNone(result_df)
            self.assertEqual(len(result_df), len(self.test_df))
            self.assertEqual(list(result_df.columns), list(self.test_df.columns))
        finally:
            # Clean up
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
    
    @unittest.skipIf(not hasattr(sqldb, 'insert_df_to_sql'), "insert_df_to_sql not implemented")
    def test_insert_df_to_sql(self):
        """Test inserting DataFrame to SQL table"""
        if not self.using_real_db:
            self.skipTest("Skipping test that requires real database")
        
        # Create a test table
        table_name = 'test_insert'
        if hasattr(sqldb, 'create_table_automatically'):
            sqldb.create_table_automatically(self.conn, self.test_df, table_name)
        
        # Insert data
        sqldb.insert_df_to_sql(self.test_df, table_name, self.engine)
        
        # Check if data was inserted by querying it
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        cursor.close()
        
        # Verify the count matches our DataFrame
        self.assertEqual(count, len(self.test_df))
    
    # @unittest.skipIf(not hasattr(sqldb, 'natural_language_query'), "natural_language_query not implemented")
    # @patch('sqldb.generate_sql_with_openai')
    # def test_natural_language_query(self, mock_generate_sql):
    #     """Test natural language query with mocked OpenAI"""
    #     # Mock the SQL generation
    #     mock_generate_sql.return_value = ("SELECT * FROM test_students LIMIT 5;", "This query selects 5 students.")
        
    #     # Mock environment variable
    #     with patch.dict(os.environ, {'OPENAI_API_KEY': 'fake_key'}):
    #         # Mock execute_query to return True
    #         with patch('sqldb.execute_query', return_value=True):
    #             # Mock input to return 'y'
    #             with patch('builtins.input', return_value='y'):
    #                 # Call the function
    #                 mock_conn = MagicMock()
    #                 result = sqldb.natural_language_query(mock_conn, "Show me 5 students")
                    
    #                 # Verify the result
    #                 self.assertTrue(result)
    #                 mock_generate_sql.assert_called_once()

    @unittest.skipIf(not hasattr(sqldb, 'get_table_schema_info'), "get_table_schema_info not implemented")
    def test_get_table_schema_info(self):
        """Test getting schema information"""
        # Create mock cursor with schema information
        mock_cursor = MagicMock()
        # Mock table list
        mock_cursor.fetchall.side_effect = [
            [('table1',)],  # First call returns tables
            [('col1', 'integer', 'NO'), ('col2', 'text', 'YES')],  # Second call returns columns
            [(1, 'test')],  # Third call returns sample data
        ]
        
        # Mock connection
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        if hasattr(sqldb, 'get_table_schema_info'):
            result = sqldb.get_table_schema_info(mock_conn)
            
            # Verify the result
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['table_name'], 'table1')
            self.assertEqual(len(result[0]['columns']), 2)

if __name__ == '__main__':
    unittest.main()