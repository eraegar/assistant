#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import main

class TestCreateAssistant(unittest.IsolatedAsyncioTestCase):
    @patch('main.auth.get_password_hash')
    async def test_create_assistant_direct(self, mock_password_hash):
        mock_password_hash.return_value = "hashed_password"
        mock_request = MagicMock()
        mock_request.json = AsyncMock(return_value={
            "name": "New Assistant",
            "phone": "+1987654321",
            "password": "newpassword",
            "email": "new@example.com",
            "specialization": "personal_only"
        })
        
        mock_manager = MagicMock()
        mock_manager.id = 1
        mock_manager.role = main.models.UserRole.manager
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        response = await main.create_assistant_direct(
            mock_request, 
            current_user=mock_manager, 
            db=mock_db
        )
        
        self.assertEqual(response["name"], "New Assistant")
        self.assertEqual(response["email"], "new@example.com")
        self.assertEqual(response["password"], "newpassword")
        self.assertEqual(response["specialization"], "personal_only")
        mock_db.add.assert_called()
        mock_db.commit.assert_called()

if __name__ == '__main__':
    unittest.main()