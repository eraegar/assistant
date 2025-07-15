import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio
from bot1_simple import handle_message


class TestHandleMessage(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.user = MagicMock()
        self.user.first_name = "TestUser"
        self.update.effective_user = self.user
        self.update.message = AsyncMock()
        self.update.message.text = "Обычная задача"

    async def run_async(self, test_func):
        await test_func()

    def run_test(self, test_func):
        asyncio.run(self.run_async(test_func))

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_normal_priority(self, mock_button, mock_markup):
        self.update.message.text = "Обычная задача"

        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertIn("📝 **Приоритет:** обычная", response_text)
        self.assertIn("Обычная задача", response_text)
        self.assertIn("#", response_text)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_fast_priority(self, mock_button, mock_markup):
        self.update.message.text = "Нужно быстро сделать"

        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertIn("⚡ **Приоритет:** быстрая (+50%)", response_text)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_urgent_priority(self, mock_button, mock_markup):
        self.update.message.text = "Срочно! Сделай немедленно!"

        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertIn("🔥 **Приоритет:** срочная (+100%)", response_text)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_english_priority(self, mock_button, mock_markup):
        self.update.message.text = "URGENT! Need it now!"

        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertIn("🔥 **Приоритет:** срочная (+100%)", response_text)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_keyboard_structure(self, mock_button, mock_markup):
        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        mock_markup.assert_called_once()
        keyboard_args = mock_markup.call_args[0][0]
        self.assertEqual(len(keyboard_args), 2)
        self.assertEqual(len(keyboard_args[0]), 2)
        self.assertEqual(len(keyboard_args[1]), 1)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_user_info_in_response(self, mock_button, mock_markup):
        self.user.first_name = "Иван"

        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertIn("👤 **Клиент:** Иван", response_text)

    @patch("bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("bot1_simple.telegram.InlineKeyboardButton")
    def test_task_id_format(self, mock_button, mock_markup):
        async def test():
            await handle_message(self.update, self.context)

        self.run_test(test)

        args, kwargs = self.update.message.reply_text.call_args
        response_text = kwargs.get('text', '')
        self.assertRegex(response_text, r"#\d{1,4}")


if __name__ == "__main__":
    unittest.main()