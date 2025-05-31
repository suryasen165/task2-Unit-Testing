import unittest
import os
import tempfile
import pandas as pd
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from database import (
    initialize_db, insert_csv_data, fetch_records, 
    update_record, delete_record, get_record_by_id, create_table_from_df
)
from utils import process_csv

class TestDatabase(unittest.TestCase):
    """Test cases for database operations - 3 tests per function"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock the database engine for testing
        self.engine_patcher = patch('database.engine')
        self.mock_engine = self.engine_patcher.start()
        
    def tearDown(self):
        """Clean up after tests"""
        self.engine_patcher.stop()
    
    # Tests for initialize_db
    def test_initialize_db_success(self):
        """Test successful database initialization"""
        mock_conn = MagicMock()
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        try:
            initialize_db()
            mock_conn.execute.assert_called()
        except Exception:
            self.fail("initialize_db should not raise exception on success")
    
    def test_initialize_db_connection_failure(self):
        """Test database initialization with connection failure"""
        self.mock_engine.connect.side_effect = Exception("Connection failed")
        
        with self.assertRaises(Exception):
            initialize_db()
    
    @patch('builtins.print')
    def test_initialize_db_prints_success_message(self, mock_print):
        """Test that initialize_db prints success message"""
        mock_conn = MagicMock()
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        initialize_db()
        mock_print.assert_called_with("Database connection successful")
    
    # Tests for insert_csv_data
    @patch('database.create_table_from_df')
    @patch('database.Table')
    @patch('database.MetaData')
    def test_insert_csv_data_success(self, mock_metadata, mock_table, mock_create_table):
        """Test successful CSV data insertion"""
        df = pd.DataFrame({'name': ['John', 'Jane'], 'age': [30, 25]})
        
        mock_conn = MagicMock()
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        
        insert_csv_data(df)
        mock_create_table.assert_called_once_with(df)
        mock_conn.execute.assert_called_once()
    
    @patch('database.create_table_from_df')
    @patch('database.Table')
    @patch('database.MetaData')
    def test_insert_csv_data_empty_dataframe(self, mock_metadata, mock_table, mock_create_table):
        """Test inserting empty DataFrame"""
        df = pd.DataFrame()
        
        mock_conn = MagicMock()
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        
        insert_csv_data(df)
        mock_create_table.assert_called_once_with(df)
    
    @patch('database.create_table_from_df')
    def test_insert_csv_data_exception_handling(self, mock_create_table):
        """Test insert_csv_data handles exceptions properly"""
        df = pd.DataFrame({'name': ['John'], 'age': [30]})
        mock_create_table.side_effect = Exception("Table creation failed")
        
        with self.assertRaises(Exception):
            insert_csv_data(df)
    
    # Tests for fetch_records
    @patch('database.inspect')
    def test_fetch_records_all(self, mock_inspect):
        """Test fetching all records"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.keys.return_value = ['id', 'name']
        mock_result.__iter__.return_value = [(1, 'John'), (2, 'Jane')]
        mock_conn.execute.return_value = mock_result
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        result = fetch_records()
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'John')
    
    @patch('database.inspect')
    def test_fetch_records_filtered(self, mock_inspect):
        """Test fetching filtered records"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.keys.return_value = ['id', 'name']
        mock_result.__iter__.return_value = [(1, 'John')]
        mock_conn.execute.return_value = mock_result
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        result = fetch_records('name', 'John')
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['name'], 'John')
    
    @patch('database.inspect')
    def test_fetch_records_exception_handling(self, mock_inspect):
        """Test fetch_records handles exceptions"""
        mock_inspect.side_effect = Exception("Query failed")
        
        result = fetch_records()
        self.assertEqual(result, [])
    
    # Tests for update_record
    @patch('database.inspect')
    def test_update_record_success(self, mock_inspect):
        """Test successful record update"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_conn.execute.return_value = mock_result
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        result = update_record(1, {'name': 'Updated Name'})
        
        self.assertTrue(result)
        mock_conn.execute.assert_called_once()
    
    @patch('database.inspect')
    def test_update_record_no_rows_affected(self, mock_inspect):
        """Test update_record when no rows are affected"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_conn.execute.return_value = mock_result
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        result = update_record(999, {'name': 'Updated Name'})
        
        self.assertFalse(result)
    
    @patch('database.inspect')
    def test_update_record_exception_handling(self, mock_inspect):
        """Test update_record handles exceptions"""
        mock_inspect.side_effect = Exception("Update failed")
        
        result = update_record(1, {'name': 'Updated Name'})
        self.assertFalse(result)
    
    # Tests for delete_record
    @patch('database.inspect')
    def test_delete_record_success(self, mock_inspect):
        """Test successful record deletion"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 1
        mock_conn.execute.return_value = mock_result
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        result = delete_record(1)
        
        self.assertTrue(result)
        mock_conn.execute.assert_called_once()
    
    @patch('database.inspect')
    def test_delete_record_no_rows_affected(self, mock_inspect):
        """Test delete_record when no rows are affected"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.rowcount = 0
        mock_conn.execute.return_value = mock_result
        self.mock_engine.begin.return_value.__enter__.return_value = mock_conn
        
        result = delete_record(999)
        
        self.assertFalse(result)
    
    @patch('database.inspect')
    def test_delete_record_exception_handling(self, mock_inspect):
        """Test delete_record handles exceptions"""
        mock_inspect.side_effect = Exception("Delete failed")
        
        result = delete_record(1)
        self.assertFalse(result)
    
    # Tests for get_record_by_id
    @patch('database.inspect')
    def test_get_record_by_id_found(self, mock_inspect):
        """Test get_record_by_id when record exists"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.keys.return_value = ['id', 'name']
        mock_result.fetchone.return_value = (1, 'John')
        mock_conn.execute.return_value = mock_result
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        result = get_record_by_id(1)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'John')
    
    @patch('database.inspect')
    def test_get_record_by_id_not_found(self, mock_inspect):
        """Test get_record_by_id when record doesn't exist"""
        mock_inspector = MagicMock()
        mock_inspector.has_table.return_value = True
        mock_inspect.return_value = mock_inspector
        
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        self.mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        result = get_record_by_id(999)
        
        self.assertIsNone(result)
    
    @patch('database.inspect')
    def test_get_record_by_id_exception_handling(self, mock_inspect):
        """Test get_record_by_id handles exceptions"""
        mock_inspect.side_effect = Exception("Query failed")
        
        result = get_record_by_id(1)
        self.assertIsNone(result)

class TestUtils(unittest.TestCase):
    """Test cases for utility functions - 3 tests per function"""
    
    def test_process_csv_valid_data(self):
        """Test processing valid CSV content"""
        csv_content = "name,age\nJohn,30\nJane,25"
        csv_bytes = csv_content.encode('utf-8')
        
        df = process_csv(csv_bytes)
        
        self.assertEqual(len(df), 2)
        self.assertIn('name', df.columns)
        self.assertIn('age', df.columns)
    
    def test_process_csv_empty_content(self):
        """Test processing empty CSV content"""
        csv_content = ""
        csv_bytes = csv_content.encode('utf-8')
        
        with self.assertRaises(Exception):
            process_csv(csv_bytes)
    
    def test_process_csv_malformed_data(self):
        """Test processing malformed CSV data"""
        csv_content = "name,age\nJohn,30,extra\nJane"
        csv_bytes = csv_content.encode('utf-8')
        
        # Should handle gracefully or raise appropriate exception
        try:
            df = process_csv(csv_bytes)
            self.assertIsNotNone(df)
        except Exception:
            pass  # Expected behavior for malformed data

class TestAPI(unittest.TestCase):
    """Test cases for FastAPI endpoints - 3 tests per endpoint"""
    
    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    # Tests for upload endpoint
    @patch('main.process_csv')
    @patch('main.insert_csv_data')
    def test_upload_csv_success(self, mock_insert, mock_process):
        """Test successful CSV upload"""
        mock_df = pd.DataFrame({'name': ['John'], 'age': [30]})
        mock_process.return_value = mock_df
        
        csv_content = "name,age\nJohn,30"
        response = self.client.post(
            "/upload/",
            files={"file": ("test.csv", csv_content, "text/csv")}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    @patch('main.process_csv')
    def test_upload_csv_processing_error(self, mock_process):
        """Test CSV upload with processing error"""
        mock_process.side_effect = Exception("Processing failed")
        
        response = self.client.post(
            "/upload/",
            files={"file": ("test.csv", "invalid,data", "text/csv")}
        )
        
        self.assertEqual(response.status_code, 500)
    
    def test_upload_csv_no_file(self):
        """Test CSV upload without file"""
        response = self.client.post("/upload/")
        
        self.assertEqual(response.status_code, 422)  # Validation error
    
    # Tests for get records endpoint
    @patch('main.fetch_records')
    def test_get_records_success(self, mock_fetch):
        """Test successful records retrieval"""
        mock_fetch.return_value = [{'id': 1, 'name': 'John'}]
        
        response = self.client.get("/records/")
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("records", response.json())
    
    @patch('main.fetch_records')
    def test_get_records_with_filter(self, mock_fetch):
        """Test records retrieval with filtering"""
        mock_fetch.return_value = [{'id': 1, 'name': 'John'}]
        
        response = self.client.get("/records/?column=name&value=John")
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["records"]), 1)
    
    @patch('main.fetch_records')
    def test_get_records_database_error(self, mock_fetch):
        """Test records retrieval with database error"""
        mock_fetch.side_effect = Exception("Database error")
        
        response = self.client.get("/records/")
        
        self.assertEqual(response.status_code, 500)

def run_tests():
    """Run all tests and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestUtils))
    suite.addTests(loader.loadTestsFromTestCase(TestAPI))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)