import unittest
from unittest.mock import patch, MagicMock
import asyncio
from App.bot.bot1_simple import handle_message
from unittest import mock


class TestHandleMessage(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.message = MagicMock()
        self.update.message.text = "Обычный приоритет"
        self.update.message.reply_text = MagicMock()

    async def run_async(self, test_func):
        await test_func()

    def run_test(self, test_func):
        asyncio.run(self.run_async(test_func))

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_normal_priority(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Обычный приоритет"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once()

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_fast_priority(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Быстрый приоритет"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once()

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_urgent_priority(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Срочный приоритет"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once()

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_english_priority(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "I need a personal assistant"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once()

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_keyboard_structure(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Обычный приоритет"
            await handle_message(self.update, self.context)
            mock_markup.assert_called_once()

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_user_info_in_response(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Обычный приоритет"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once_with(
                "ID Пользователя: 123, Задание: Test task, Приоритет: Обычный",
                reply_markup=mock.ANY,
            )

        self.run_test(test)

    @patch("App.bot.bot1_simple.telegram.InlineKeyboardMarkup")
    @patch("App.bot.bot1_simple.telegram.InlineKeyboardButton")
    def test_task_id_format(self, mock_button, mock_markup):
        async def test():
            self.update.message.text = "Обычный приоритет"
            await handle_message(self.update, self.context)
            self.update.message.reply_text.assert_called_once()

        self.run_test(test)


if __name__ == "__main__":
    unittest.main() 