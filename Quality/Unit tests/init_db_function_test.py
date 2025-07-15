#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, inspect
import database 
import sys

sys.modules['models'] = MagicMock()
from init_db import init_database

class TestInitDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_engine = create_engine('sqlite:///:memory:')
        self.original_engine = database.engine
        database.engine = self.temp_engine

    def tearDown(self):
        database.engine = self.original_engine

    @patch('init_db.print')
    def test_successful_init(self, mock_print):
        """Тест успешной инициализации базы данных"""
        result = init_database()
        
        self.assertTrue(result)
        
        inspector = inspect(self.temp_engine)
        tables = inspector.get_table_names()
        self.assertIn('users', tables)
        self.assertIn('tasks', tables)
        
        mock_print.assert_any_call("🚀 Initializing database...")
        mock_print.assert_any_call("✅ Database tables created successfully!")
        mock_print.assert_any_call("🎉 Database is ready to use!")

    @patch('init_db.print')
    @patch('init_db.Base.metadata.create_all')
    def test_failed_init(self, mock_create_all, mock_print):
        """Тест обработки ошибки при инициализации"""
        mock_create_all.side_effect = Exception("Test DB error")
        
        result = init_database()
        
        self.assertFalse(result)
        
        mock_print.assert_any_call("❌ Error creating database: Test DB error")
        mock_print.assert_any_call("💥 Database initialization failed!")

if __name__ == '__main__':
    unittest.main()