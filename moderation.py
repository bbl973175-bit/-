import discord, aiosqlite
from datetime import timedelta
from discord.ext import commands
from discord import app_commands
from bot.config import DATABASE_PATH
class Moderation(commands.Cog):
    def __init__(self,bot): self.bot=bot
    async def can_moderate(self,i):
        if not (i.user.guild_permissions.moderate_members or i.user.guild_permissions.administrator):
            await i.response.send_message("You need Moderate Members permission.",ephemeral=True); return False
        return True
    @app_commands.command(name="kick",description="Kick a member")
    @app_commands.guild_only()
    async def kick(self,i:discord.Interaction,member:discord.Member,reason:str="No reason provided"):
        if not (i.user.guild_permissions.kick_members or i.user.guild_permissions.administrator):
            return await i.response.send_message("You need Kick Members permission.",ephemeral=True)
        if member==i.guild.owner or member.top_role>=i.user.top_role and i.user!=i.guild.owner:
            return await i.response.send_message("Role hierarchy prevents this action.",ephemeral=True)
        try:
            await member.kick(reason=reason[:400])
            await i.response.send_message(f"✅ Kicked {member}. Reason: {reason}",ephemeral=True)
        except discord.Forbidden: await i.response.send_message("Bot lacks Kick Members permission or role position.",ephemeral=True)
    @app_commands.command(name="ban",description="Ban a member")
    @app_commands.guild_only()
    async def ban(self,i:discord.Interaction,member:discord.Member,reason:str="No reason provided"):
        if not (i.user.guild_permissions.ban_members or i.user.guild_permissions.administrator):
            return await i.response.send_message("You need Ban Members permission.",ephemeral=True)
        if member==i.guild.owner or member.top_role>=i.user.top_role and i.user!=i.guild.owner:
            return await i.response.send_message("Role hierarchy prevents this action.",ephemeral=True)
        try:
            await member.ban(reason=reason[:400])
            await i.response.send_message(f"✅ Banned {member}.",ephemeral=True)
        except discord.Forbidden: await i.response.send_message("Bot lacks Ban Members permission or role position.",ephemeral=True)
    @app_commands.command(name="timeout",description="Timeout a member for up to 28 days")
    @app_commands.guild_only()
    async def timeout(self,i:discord.Interaction,member:discord.Member,minutes:app_commands.Range[int,1,40320],reason:str="No reason provided"):
        if not await self.can_moderate(i): return
        if member==i.guild.owner or member.top_role>=i.user.top_role and i.user!=i.guild.owner:
            return await i.response.send_message("Role hierarchy prevents this action.",ephemeral=True)
        try:
            await member.timeout(discord.utils.utcnow()+timedelta(minutes=minutes),reason=reason[:400])
            await i.response.send_message(f"✅ Timeout applied for {minutes} minutes.",ephemeral=True)
        except discord.Forbidden: await i.response.send_message("Bot lacks Moderate Members permission or role position.",ephemeral=True)
    @app_commands.command(name="warn",description="Record a warning")
    @app_commands.guild_only()
    async def warn(self,i:discord.Interaction,member:discord.Member,reason:str):
        if not await self.can_moderate(i): return
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("INSERT INTO warnings(guild_id,user_id,moderator_id,reason) VALUES(?,?,?,?)",(str(i.guild_id),str(member.id),str(i.user.id),reason[:500]))
            await db.commit()
        await i.response.send_message(f"⚠️ Warning recorded for {member.mention}.",ephemeral=True)
    @app_commands.command(name="warnings",description="View a member's recent warnings")
    @app_commands.guild_only()
    async def warnings(self,i:discord.Interaction,member:discord.Member):
        if not await self.can_moderate(i): return
        async with aiosqlite.connect(DATABASE_PATH) as db:
            cur=await db.execute("SELECT reason,created_at FROM warnings WHERE guild_id=? AND user_id=? ORDER BY id DESC LIMIT 10",(str(i.guild_id),str(member.id)))
            rows=await cur.fetchall()
        desc="\n".join(f"• {r[0]} — {r[1]}" for r in rows) or "No warnings."
        await i.response.send_message(embed=discord.Embed(title=f"Warnings: {member}",description=desc),ephemeral=True)
async def setup(bot): await bot.add_cog(Moderation(bot))
