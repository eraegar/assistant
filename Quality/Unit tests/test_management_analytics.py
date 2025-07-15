#!/usr/bin/env python3
import unittest
from unittest.mock import MagicMock
import main
from main import models

class TestManagementAnalytics(unittest.IsolatedAsyncioTestCase):
    async def test_get_overview_analytics_direct(self):
        mock_manager = MagicMock()
        mock_manager.id = 1
        mock_manager.role = models.UserRole.manager
        
        mock_db = MagicMock()
        mock_db.query.return_value.count.side_effect = [
            100, 20, 30, 50, 15,
            25, 10, 20,
            200, 150, 5
        ]
        
        subscription_data = [
            (models.SubscriptionPlan.personal_2h, 50),
            (models.SubscriptionPlan.business_5h, 30)
        ]
        mock_db.query.return_value.filter.return_value.group_by.return_value.all.return_value = subscription_data
        
        response = await main.get_overview_analytics_direct(
            current_user=mock_manager, 
            db=mock_db
        )
        
        self.assertEqual(response["tasks"]["total"], 100)
        self.assertEqual(response["assistants"]["online_now"], 10)
        self.assertEqual(response["clients"]["active_subscribers"], 150)
        self.assertEqual(response["performance"]["monthly_revenue"], 
                         (50 * 15000) + (30 * 60000))

if __name__ == '__main__':
    unittest.main()