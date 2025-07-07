import discord
import asyncio
import logging
from urllib.parse import urlparse
from .data_models import WorkItem

logger = logging.getLogger(__name__)

class DiscordReader:
    """
    This class is responsible for connecting to Discord, listening for messages,
    and delegating valid product links to the BotOrchestrator.
    """
    def __init__(self, bot_token: str, work_queue: asyncio.Queue):
        if not bot_token:
            raise ValueError("Discord bot token cannot be empty.")
        
        self._token = bot_token
        self._queue = work_queue
        
        # We need to tell the discord.py client which events we want to listen to.
        intents = discord.Intents.default()
        intents.message_content = True
        self._client = discord.Client(intents=intents)

        # Register our event handlers
        self._client.event(self.on_ready)
        self._client.event(self.on_message)
        logger.info("DiscordReader initialized.")

    async def start(self):
        """Starts the bot using the non-blocking start method."""
        logger.info("Discord bot is starting...")
        await self._client.start(self._token)

    async def on_ready(self):
        """Called when the bot successfully connects to Discord."""
        logger.info(f'Bot logged in as {self._client.user}')

    async def on_message(self, message: discord.Message):
        """Called every time a message is sent in a channel the bot can see."""
        # Ignore messages sent by the bot itself to prevent loops
        if message.author == self._client.user:
            return

        # Simple URL extraction logic
        for word in message.content.split():
            try:
                result = urlparse(word)
                # A simple check if it looks like a real URL
                if all([result.scheme, result.netloc]):
                    logger.info(f"Found URL: {word} from user {message.author}, adding to work queue.")
                    # Create a complete WorkItem
                    item = WorkItem(
                        url=word,
                        message_content=message.content,
                        user_name=message.author.name
                    )

                    # --- DEBUGGING LOG ---
                    logger.info(f"Putting object of type {type(item).__name__} onto queue for URL: {item.url}")

                    await self._queue.put(item)
                    logger.info(f"Work item for {word} added to queue.")
            except ValueError:
                continue # Not a valid URL, ignore