#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import main

class TestAssistantRegistration(unittest.IsolatedAsyncioTestCase):
    @patch('main.auth.get_password_hash')
    async def test_register_assistant_direct(self, mock_password_hash):
        mock_password_hash.return_value = "hashed_password"
        mock_request = MagicMock()
        mock_request.json = AsyncMock(return_value={
            "name": "Test Assistant",
            "phone": "+1234567890",
            "password": "password123",
            "email": "test@example.com"
        })
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = await main.register_assistant_direct(mock_request, mock_db)
        
        self.assertEqual(response["name"], "Test Assistant")
        self.assertEqual(response["email"], "test@example.com")
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

if __name__ == '__main__':
    unittest.main()