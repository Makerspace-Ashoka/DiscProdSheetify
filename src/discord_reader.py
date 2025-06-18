import discord
from urllib.parse import urlparse

# We need a reference to our orchestrator to pass the work to.
from .orchestrator import BotOrchestrator

class DiscordReader:
    """
    This class is responsible for connecting to Discord, listening for messages,
    and delegating valid product links to the BotOrchestrator.
    """
    def __init__(self, bot_token: str, orchestrator: BotOrchestrator):
        if not bot_token:
            raise ValueError("Discord bot token cannot be empty.")
        
        self._token = bot_token
        self._orchestrator = orchestrator
        
        # We need to tell the discord.py client which events we want to listen to.
        intents = discord.Intents.default()
        intents.message_content = True
        self._client = discord.Client(intents=intents)

        # Register our event handlers
        self._client.event(self.on_ready)
        self._client.event(self.on_message)

    def run(self):
        """Starts the bot."""
        print("Discord bot is starting...")
        self._client.run(self._token)

    async def on_ready(self):
        """Called when the bot successfully connects to Discord."""
        print(f'Bot logged in as {self._client.user}')

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
                    print(f"Found URL: {word} from user {message.author}")
                    # This is the handoff! The reader's job is done.
                    # It calls the orchestrator, which is completely unaware of Discord.
                    self._orchestrator.process_single_url(word)
            except ValueError:
                continue # Not a valid URL, ignore