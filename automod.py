import discord
from discord.ext import commands
from bot.database import get_setting
class AutoMod(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @commands.Cog.listener()
    async def on_message(self,m):
        if not m.guild or m.author.bot or m.author.guild_permissions.manage_messages: return
        if await get_setting(m.guild.id,"automod_enabled","0")!="1": return
        words=[w.strip().lower() for w in (await get_setting(m.guild.id,"blocked_words","")).split(",") if w.strip()]
        text=m.content.lower()
        blocked=any(w in text for w in words)
        links=await get_setting(m.guild.id,"block_links","0")=="1" and any(x in text for x in ("http://","https://","discord.gg/"))
        if blocked or links:
            try:
                await m.delete()
                await m.channel.send(f"{m.author.mention}, your message was removed by AutoMod.",delete_after=5)
            except discord.Forbidden: pass
async def setup(bot): await bot.add_cog(AutoMod(bot))
