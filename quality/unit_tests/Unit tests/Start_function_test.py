import unittest
from unittest.mock import patch, MagicMock
import asyncio
from App.bot.bot1_simple import start


class TestBotStart(unittest.TestCase):
    def setUp(self):
        self.update = MagicMock()
        self.context = MagicMock()
        self.update.message.reply_text = asyncio.Future()
        self.update.message.reply_text.set_result(None)

    @patch("App.bot.bot1_simple.os.getenv")
    @patch("builtins.print")
    def test_start_command(self, mock_print, mock_getenv):
        mock_getenv.return_value = "https://some-url.com"

        async def run_test():
            await start(self.update, self.context)

        asyncio.run(run_test())
        self.update.message.reply_text.assert_called_once()


if __name__ == "__main__":
    unittest.main() 