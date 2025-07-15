import unittest
from unittest.mock import patch, MagicMock
import asyncio
from App.bot.bot1_simple import handle_keywords


class TestHandleKeywords(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.message = MagicMock()
        self.update.message.reply_text = MagicMock()

    async def run_async(self, test_func):
        await test_func()

    def run_test(self, test_func):
        asyncio.run(self.run_async(test_func))

    def test_manager_keyword(self):
        async def test():
            self.update.message.text = "менеджер"
            await handle_keywords(self.update, self.context)
            self.update.message.reply_text.assert_called_once()
            self.assertIn("менеджер", self.update.message.reply_text.call_args[0][0])
        self.run_test(test)

    def test_assistant_keyword(self):
        async def test():
            self.update.message.text = "ассистент"
            await handle_keywords(self.update, self.context)
            self.update.message.reply_text.assert_called_once()
            self.assertIn("ассистент", self.update.message.reply_text.call_args[0][0])
        self.run_test(test)

    def test_no_keyword(self):
        async def test():
            self.update.message.text = "простое сообщение"
            await handle_keywords(self.update, self.context)
            self.update.message.reply_text.assert_not_called()
        self.run_test(test)

if __name__ == "__main__":
    unittest.main() 