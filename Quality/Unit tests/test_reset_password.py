#!/usr/bin/env python3
import unittest
from unittest.mock import patch, MagicMock
import main
from main import models

class TestResetPassword(unittest.IsolatedAsyncioTestCase):
    @patch('main.secrets')
    @patch('main.string')
    @patch('main.auth.get_password_hash')
    async def test_reset_assistant_password_direct(self, mock_password_hash, mock_string, mock_secrets):
        mock_secrets.choice.return_value = 'a'
        mock_string.ascii_letters = 'abc'
        mock_string.digits = '123'
        mock_password_hash.return_value = "new_hashed_password"
        
        mock_manager = MagicMock()
        mock_manager.id = 1
        mock_manager.role = models.UserRole.manager
        
        mock_assistant = MagicMock()
        mock_assistant.id = 2
        mock_assistant.role = models.UserRole.assistant
        mock_assistant.name = "Test Assistant"
        mock_assistant.password_hash = "old_hash"
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assistant
        
        response = await main.reset_assistant_password_direct(
            assistant_id=2,
            current_user=mock_manager,
            db=mock_db
        )
        
        self.assertTrue(response["success"])
        self.assertEqual(response["assistant_name"], "Test Assistant")
        self.assertEqual(len(response["new_password"]), 8)
        self.assertEqual(mock_assistant.password_hash, "new_hashed_password")
        mock_db.commit.assert_called()

if __name__ == '__main__':
    unittest.main()