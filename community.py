import random, aiosqlite, discord
from discord.ext import commands
from discord import app_commands
from bot.database import get_setting
from bot.config import DATABASE_PATH
class Community(commands.Cog):
    def __init__(self,bot): self.bot=bot
    @commands.Cog.listener()
    async def on_member_join(self,m):
        if await get_setting(m.guild.id,"welcome_enabled","0")=="1":
            cid=await get_setting(m.guild.id,"welcome_channel",""); ch=m.guild.get_channel(int(cid)) if cid.isdigit() else None
            if ch:
                msg=await get_setting(m.guild.id,"welcome_message","Welcome {mention}!")
                try: await ch.send(msg.replace("{mention}",m.mention).replace("{server}",m.guild.name))
                except discord.Forbidden: pass
        if await get_setting(m.guild.id,"autorole_enabled","0")=="1":
            rid=await get_setting(m.guild.id,"autorole_id",""); role=m.guild.get_role(int(rid)) if rid.isdigit() else None
            if role and m.guild.me and role<m.guild.me.top_role:
                try: await m.add_roles(role,reason="NEXORA AutoRole")
                except discord.Forbidden: pass
    @commands.Cog.listener()
    async def on_member_remove(self,m):
        if await get_setting(m.guild.id,"leave_enabled","0")=="1":
            cid=await get_setting(m.guild.id,"leave_channel",""); ch=m.guild.get_channel(int(cid)) if cid.isdigit() else None
            if ch:
                try: await ch.send(f"👋 {m} left the server.")
                except discord.Forbidden: pass
    @commands.Cog.listener()
    async def on_message(self,m):
        if not m.guild or m.author.bot or len(m.content.strip())<4: return
        if await get_setting(m.guild.id,"leveling_enabled","0")!="1": return
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cur=await db.execute("SELECT xp,level FROM levels WHERE guild_id=? AND user_id=?",(str(m.guild.id),str(m.author.id)))
            row=await cur.fetchone(); xp,level=row if row else (0,0); xp+=random.randint(5,12); new=int((xp/100)**0.5)
            await db.execute("INSERT INTO levels VALUES(?,?,?,?) ON CONFLICT(guild_id,user_id) DO UPDATE SET xp=excluded.xp,level=excluded.level",(str(m.guild.id),str(m.author.id),xp,new)); await db.commit()
        if new>level:
            try: await m.channel.send(f"🎉 {m.author.mention} reached level **{new}**!")
            except discord.Forbidden: pass
    @app_commands.command(name="suggest",description="Submit a server suggestion")
    @app_commands.guild_only()
    async def suggest(self,i:discord.Interaction,suggestion:str):
        if await get_setting(i.guild_id,"suggestions_enabled","0")!="1": return await i.response.send_message("Suggestions are disabled.",ephemeral=True)
        cid=await get_setting(i.guild_id,"suggestions_channel",""); ch=i.guild.get_channel(int(cid)) if cid.isdigit() else None
        if not ch: return await i.response.send_message("Suggestions channel is not configured.",ephemeral=True)
        e=discord.Embed(title="New suggestion",description=suggestion[:1800],color=discord.Color.purple()); e.set_footer(text=f"By {i.user}")
        msg=await ch.send(embed=e); await msg.add_reaction("👍"); await msg.add_reaction("👎")
        await i.response.send_message("Suggestion submitted.",ephemeral=True)
async def setup(bot): await bot.add_cog(Community(bot))
