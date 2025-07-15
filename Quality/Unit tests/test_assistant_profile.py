#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock
import main

class TestAssistantProfile(unittest.IsolatedAsyncioTestCase):
    async def test_get_assistant_profile_direct(self):
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.role = main.models.UserRole.assistant
        mock_user.name = "Test Assistant"
        mock_user.telegram_username = "@test"
        
        mock_profile = MagicMock()
        mock_profile.email = "test@example.com"
        mock_profile.status = "online"
        mock_profile.current_active_tasks = 3
        mock_profile.total_tasks_completed = 10
        mock_profile.average_rating = 4.5
        mock_profile.specialization = main.models.AssistantSpecialization.personal_only
        mock_user.assistant_profile = mock_profile
        
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_user
        
        response = await main.get_assistant_profile_direct(
            current_user=mock_user, 
            db=mock_db
        )
        
        self.assertEqual(response["name"], "Test Assistant")
        self.assertEqual(response["email"], "test@example.com")
        self.assertEqual(response["status"], "online")
        self.assertEqual(response["current_active_tasks"], 3)

if __name__ == '__main__':
    unittest.main()