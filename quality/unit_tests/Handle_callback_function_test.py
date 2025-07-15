import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import asyncio
from bot1_simple import handle_callback


class TestHandleCallback(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.query = AsyncMock()
        self.update.callback_query = self.query
        self.query.data = None
        self.query.from_user.first_name = "TestUser"
        self.query.message.message_id = 123

    @patch("builtins.print")
    @patch("bot1_simple.os.getenv", return_value="https://google.com")
    async def test_pricing_callback(self, mock_getenv, mock_print):
        self.query.data = 'pricing'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Тарифные планы", kwargs['text'])
        self.assertIn("Базовый - 15,000₽/мес", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 2)
        self.assertEqual(markup.inline_keyboard[0][0].text, "📞 Связаться с поддержкой")
        self.assertEqual(markup.inline_keyboard[1][0].text, "🔙 Назад")

    @patch("builtins.print")
    @patch("bot1_simple.os.getenv", return_value="https://google.com")
    async def test_task_examples_callback(self, mock_getenv, mock_print):
        self.query.data = 'task_examples'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Примеры задач", kwargs['text'])
        self.assertIn("Личные задачи", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 3)
        self.assertEqual(markup.inline_keyboard[0][0].text, "🚀 Создать задачу в приложении")
        self.assertEqual(markup.inline_keyboard[0][0].url, "https://google.com")
        self.assertEqual(markup.inline_keyboard[1][0].text, "✍️ Написать задачу в чат")

    @patch("builtins.print")
    async def test_documents_callback(self, mock_print):
        self.query.data = 'documents'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Соглашение об обработке", kwargs['text'])
        self.assertIn("ФЗ-152", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 3)
        self.assertEqual(markup.inline_keyboard[0][0].text, "📧 Написать на Malina2701@mail.ru")
        self.assertEqual(markup.inline_keyboard[1][0].text, "📞 Связаться по вопросам данных")

    @patch("builtins.print")
    async def test_support_callback(self, mock_print):
        self.query.data = 'support'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Служба поддержки", kwargs['text'])
        self.assertIn("Malina2701@mail.ru", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 2)
        self.assertEqual(markup.inline_keyboard[0][0].text, "💬 Написать в поддержку")

    @patch("builtins.print")
    @patch("bot1_simple.os.getenv", return_value="https://google.com")
    async def test_create_task_callback(self, mock_getenv, mock_print):
        self.query.data = 'create_task'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Создание задачи", kwargs['text'])
        self.assertIn("срочно", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 2)
        self.assertEqual(markup.inline_keyboard[0][0].text, "🚀 Открыть приложение")
        self.assertEqual(markup.inline_keyboard[0][0].url, "https://google.com")

    @patch("builtins.print")
    @patch("bot1_simple.os.getenv", return_value="https://google.com")
    async def test_back_to_main_callback(self, mock_getenv, mock_print):
        self.query.data = 'back_to_main'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        self.query.edit_message_text.assert_awaited_once()

        args, kwargs = self.query.edit_message_text.call_args
        self.assertIn("Привет, TestUser", kwargs['text'])
        self.assertIn("Assistant-for-Rent", kwargs['text'])

        markup = kwargs['reply_markup']
        self.assertEqual(len(markup.inline_keyboard), 3)
        self.assertEqual(markup.inline_keyboard[0][0].text, "🚀 Открыть приложение")
        self.assertEqual(markup.inline_keyboard[1][0].text, "💡 Примеры задач")

    @patch("builtins.print")
    async def test_unknown_callback(self, mock_print):
        self.query.data = 'unknown_command'

        await handle_callback(self.update, self.context)

        self.query.answer.assert_awaited_once()
        mock_print.assert_any_call("DEBUG: Unknown callback data: unknown_command")

    @patch("builtins.print")
    async def test_no_callback_query(self, mock_print):
        self.update.callback_query = None

        await handle_callback(self.update, self.context)

        mock_print.assert_called_with("DEBUG: No callback_query in update!")
        self.query.answer.assert_not_called()

    @patch("builtins.print")
    @patch("bot1_simple.traceback.print_exc")
    async def test_exception_handling(self, mock_print_exc, mock_print):
        self.query.data = 'pricing'
        self.query.edit_message_text.side_effect = Exception("Test error")

        await handle_callback(self.update, self.context)

        # Проверки обработки ошибок
        mock_print.assert_any_call("ERROR in handle_callback: Test error")
        mock_print_exc.assert_called_once()


if __name__ == "__main__":
    unittest.main()