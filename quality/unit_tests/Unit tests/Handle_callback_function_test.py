import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from App.bot.bot1_simple import handle_callback
import telegram
from unittest import mock


class TestHandleCallback(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.callback_query = MagicMock()
        self.update.callback_query.from_user.id = 123
        self.update.callback_query.message.reply_text = AsyncMock()
        self.update.callback_query.edit_message_text = AsyncMock()

    @patch("builtins.print")
    @patch("App.bot.bot1_simple.os.getenv", return_value="https://google.com")
    async def test_pricing_callback(self, mock_getenv, mock_print):
        self.update.callback_query.data = "pricing"
        await handle_callback(self.update, self.context)
        self.update.callback_query.message.reply_text.assert_called_once()
        call_args = self.update.callback_query.message.reply_text.call_args
        self.assertIn("У нас есть 2 тарифа", call_args[0][0])

    @patch("builtins.print")
    @patch("App.bot.bot1_simple.os.getenv", return_value="https://google.com")
    async def test_task_examples_callback(self, mock_getenv, mock_print):
        self.update.callback_query.data = "task_examples"
        await handle_callback(self.update, self.context)
        self.update.callback_query.message.reply_text.assert_called_once()
        call_args = self.update.callback_query.message.reply_text.call_args
        self.assertIn("Примеры задач", call_args[0][0])

    @patch("builtins.print")
    async def test_documents_callback(self, mock_print):
        self.update.callback_query.data = "documents"
        await handle_callback(self.update, self.context)
        self.update.callback_query.message.reply_text.assert_called_once()
        self.update.callback_query.message.reply_text.assert_called_with(
            "Для получения документов, пожалуйста, свяжитесь с нашей службой поддержки.",
            reply_markup=mock.ANY,
        )

    @patch("builtins.print")
    async def test_support_callback(self, mock_print):
        self.update.callback_query.data = "support"
        await handle_callback(self.update, self.context)
        self.update.callback_query.message.reply_text.assert_called_once()
        self.update.callback_query.message.reply_text.assert_called_with(
            "Наша служба поддержки готова помочь вам. Пожалуйста, напишите нам @трунь.",
            reply_markup=mock.ANY,
        )

    @patch("builtins.print")
    @patch("App.bot.bot1_simple.os.getenv", return_value="https://google.com")
    async def test_create_task_callback(self, mock_getenv, mock_print):
        self.update.callback_query.data = "create_task"
        await handle_callback(self.update, self.context)
        self.update.callback_query.edit_message_text.assert_called_once()
        call_args = self.update.callback_query.edit_message_text.call_args
        self.assertIn("Напишите ваше задание", call_args[0][0])

    @patch("builtins.print")
    @patch("App.bot.bot1_simple.os.getenv", return_value="https://google.com")
    async def test_back_to_main_callback(self, mock_getenv, mock_print):
        self.update.callback_query.data = "back_to_main"
        await handle_callback(self.update, self.context)
        self.update.callback_query.edit_message_text.assert_called_once()
        call_args = self.update.callback_query.edit_message_text.call_args
        self.assertIn("Чем я могу помочь?", call_args[0][0])

    @patch("builtins.print")
    async def test_unknown_callback(self, mock_print):
        self.update.callback_query.data = "unknown_callback"
        await handle_callback(self.update, self.context)
        self.update.callback_query.message.reply_text.assert_called_once()
        self.update.callback_query.message.reply_text.assert_called_with(
            "Извините, я не понимаю эту команду."
        )

    @patch("builtins.print")
    async def test_no_callback_query(self, mock_print):
        self.update.callback_query = None
        await handle_callback(self.update, self.context)
        mock_print.assert_called_with("Update does not contain a callback query.")

    @patch("builtins.print")
    @patch("App.bot.bot1_simple.traceback.print_exc")
    async def test_exception_handling(self, mock_print_exc, mock_print):
        self.update.callback_query.message.reply_text.side_effect = Exception("Test error")
        self.update.callback_query.data = "pricing"
        await handle_callback(self.update, self.context)
        mock_print.assert_any_call("An error occurred in handle_callback:")
        mock_print_exc.assert_called_once()


if __name__ == "__main__":
    unittest.main() 