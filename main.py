import discord
from discord.ext import commands
from bot.config import BOT_TOKEN, validate_bot_config
from bot.database import initialize_database
EXTENSIONS=["bot.systems.moderation","bot.systems.automod","bot.systems.antispam","bot.systems.antiraid","bot.systems.community","bot.systems.tickets"]
class NexoraBot(commands.Bot):
    def __init__(self):
        intents=discord.Intents.default()
        intents.guilds=True
        intents.members=True
        intents.message_content=True
        super().__init__(command_prefix="!",intents=intents)
    async def setup_hook(self):
        await initialize_database()
        for ext in EXTENSIONS:
            await self.load_extension(ext)
            print("Loaded:",ext)
        await self.tree.sync()
        print("NEXORA slash commands synchronized.")
    async def on_ready(self):
        print(f"NEXORA SYSTEM online as {self.user} | servers: {len(self.guilds)}")
bot=NexoraBot()
if __name__=="__main__":
    validate_bot_config()
    bot.run(BOT_TOKEN)
