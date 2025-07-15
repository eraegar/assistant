#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import main

class TestAssistantLogin(unittest.IsolatedAsyncioTestCase):
    @patch('main.auth.verify_password')
    @patch('main.auth.create_access_token')
    async def test_login_assistant_direct(self, mock_create_token, mock_verify_password):
        mock_verify_password.return_value = True
        mock_create_token.return_value = "test_token"
        
        mock_request = MagicMock()
        mock_request.json = AsyncMock(return_value={
            "phone": "+1234567890",
            "password": "password123"
        })
        
        mock_db = MagicMock()
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.password_hash = "hashed_password"
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        response = await main.login_assistant_direct(mock_request, mock_db)
        
        self.assertEqual(response["access_token"], "test_token")
        self.assertEqual(response["token_type"], "bearer")

if __name__ == '__main__':
    unittest.main()