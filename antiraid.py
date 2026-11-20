import time
from collections import defaultdict,deque
from discord.ext import commands
from bot.database import get_setting
class AntiRaid(commands.Cog):
    def __init__(self,bot): self.bot=bot; self.joins=defaultdict(deque); self.last_alert={}
    @commands.Cog.listener()
    async def on_member_join(self,member):
        if await get_setting(member.guild.id,"antiraid_enabled","0")!="1": return
        limit=max(4,min(30,int(await get_setting(member.guild.id,"raid_join_limit","8"))))
        window=max(10,min(120,int(await get_setting(member.guild.id,"raid_window","20"))))
        now=time.monotonic(); q=self.joins[member.guild.id]; q.append(now)
        while q and now-q[0]>window: q.popleft()
        if len(q)>=limit and now-self.last_alert.get(member.guild.id,0)>60:
            self.last_alert[member.guild.id]=now
            cid=await get_setting(member.guild.id,"log_channel","")
            channel=member.guild.get_channel(int(cid)) if cid.isdigit() else None
            if channel:
                await channel.send(f"🚨 Possible join raid: {len(q)} members joined in {window}s. Review joins and server verification.")
            q.clear()
async def setup(bot): await bot.add_cog(AntiRaid(bot))
