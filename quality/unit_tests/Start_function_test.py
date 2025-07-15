import unittest
from unittest.mock import MagicMock, patch
import os
import telegram
from bot1_simple import start


class TestBotStart(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()

        self.user_mock = MagicMock()
        self.user_mock.first_name = "TestUser"
        self.update.effective_user = self.user_mock

        self.message_mock = MagicMock()
        self.update.message = self.message_mock

    @patch("bot1_simple.os.getenv")
    @patch("builtins.print")
    def test_start_command(self, mock_print, mock_getenv):
        mock_getenv.return_value = "https://google.com"

        import asyncio
        asyncio.run(start(self.update, self.context))

        mock_print.assert_any_call(f"DEBUG: START command received from user TestUser")
        mock_print.assert_any_call(f"DEBUG: Sending start message with 3 rows of buttons")
        mock_print.assert_any_call(f"DEBUG: Start message sent successfully")

        self.message_mock.reply_text.assert_called_once()

        args, kwargs = self.message_mock.reply_text.call_args
        welcome_text = kwargs.get('text', args[0] if args else "")
        reply_markup = kwargs.get('reply_markup')

        self.assertIn("TestUser", welcome_text)
        self.assertIn("Assistant-for-Rent", welcome_text)

        self.assertIsNotNone(reply_markup)
        keyboard = reply_markup.inline_keyboard
        self.assertEqual(len(keyboard), 3)

        self.assertEqual(len(keyboard[0]), 1)
        self.assertEqual(keyboard[0][0].text, "🚀 Открыть приложение")
        self.assertEqual(keyboard[0][0].url, "https://google.com")

        self.assertEqual(len(keyboard[1]), 2)
        self.assertEqual(keyboard[1][0].text, "💡 Примеры задач")
        self.assertEqual(keyboard[1][0].callback_data, "task_examples")
        self.assertEqual(keyboard[1][1].text, "💰 Тарифы")
        self.assertEqual(keyboard[1][1].callback_data, "pricing")

        self.assertEqual(len(keyboard[2]), 2)
        self.assertEqual(keyboard[2][0].text, "📄 Документы")
        self.assertEqual(keyboard[2][0].callback_data, "documents")
        self.assertEqual(keyboard[2][1].text, "📞 Поддержка")
        self.assertEqual(keyboard[2][1].callback_data, "support")


if __name__ == "__main__":
    unittest.main()