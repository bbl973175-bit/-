import time
from collections import defaultdict,deque
from discord.ext import commands
from bot.database import get_setting
class AntiSpam(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.history=defaultdict(deque); self.alerted={}
    @commands.Cog.listener()
    async def on_message(self,m):
        if not m.guild or m.author.bot or m.author.guild_permissions.manage_messages: return
        if await get_setting(m.guild.id,"antispam_enabled","0")!="1": return
        limit=max(3,min(12,int(await get_setting(m.guild.id,"antispam_limit","5"))))
        window=max(4,min(30,int(await get_setting(m.guild.id,"antispam_window","7"))))
        now=time.monotonic(); key=(m.guild.id,m.author.id); q=self.history[key]; q.append((now,m.content))
        while q and now-q[0][0]>window: q.popleft()
        repeats=sum(1 for _,content in q if content and content==m.content)
        if len(q)>=limit or repeats>=3:
            if now-self.alerted.get(key,0)<30: return
            self.alerted[key]=now
            try:
                await m.channel.send(f"{m.author.mention}, slow down — Anti-Spam detected repeated messages.",delete_after=6)
                if m.guild.me and m.guild.me.guild_permissions.manage_messages: await m.delete()
            except Exception: pass
            q.clear()
async def setup(bot): await bot.add_cog(AntiSpam(bot))
