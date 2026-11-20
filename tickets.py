import asyncio, aiosqlite, discord
from discord.ext import commands
from discord import app_commands
from bot.database import get_setting
from bot.config import DATABASE_PATH
class TicketView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Close ticket",style=discord.ButtonStyle.danger,custom_id="nexora:ticket_close")
    async def close(self,i:discord.Interaction,button:discord.ui.Button):
        ch=i.channel
        if not isinstance(ch,discord.TextChannel): return await i.response.send_message("Not a ticket channel.",ephemeral=True)
        owner=(ch.topic or "").replace("ticket-owner:","")
        if str(i.user.id)!=owner and not i.user.guild_permissions.manage_channels:
            return await i.response.send_message("Only the ticket owner or a moderator can close this ticket.",ephemeral=True)
        await i.response.send_message("Ticket closing...")
        await asyncio.sleep(2)
        try: await ch.delete(reason=f"Closed by {i.user}")
        except discord.Forbidden: pass
class Tickets(commands.Cog):
    def __init__(self,bot): self.bot=bot
    async def cog_load(self): self.bot.add_view(TicketView())
    @app_commands.command(name="ticket",description="Create a private support ticket")
    @app_commands.guild_only()
    async def ticket(self,i:discord.Interaction):
        if await get_setting(i.guild_id,"tickets_enabled","0")!="1": return await i.response.send_message("Tickets are disabled.",ephemeral=True)
        existing=next((c for c in i.guild.text_channels if c.topic==f"ticket-owner:{i.user.id}"),None)
        if existing: return await i.response.send_message(f"You already have a ticket: {existing.mention}",ephemeral=True)
        cid=await get_setting(i.guild_id,"ticket_category",""); cat=i.guild.get_channel(int(cid)) if cid.isdigit() else None
        overwrites={i.guild.default_role:discord.PermissionOverwrite(view_channel=False),i.user:discord.PermissionOverwrite(view_channel=True,send_messages=True,read_message_history=True)}
        if i.guild.me: overwrites[i.guild.me]=discord.PermissionOverwrite(view_channel=True,send_messages=True,manage_channels=True,read_message_history=True)
        try:
            ch=await i.guild.create_text_channel(f"ticket-{i.user.name}"[:90],category=cat if isinstance(cat,discord.CategoryChannel) else None,overwrites=overwrites,topic=f"ticket-owner:{i.user.id}")
            async with aiosqlite.connect(DATABASE_PATH) as db:
                await db.execute("INSERT INTO tickets(guild_id,channel_id,user_id) VALUES(?,?,?)",(str(i.guild_id),str(ch.id),str(i.user.id))); await db.commit()
            await ch.send(f"{i.user.mention} Support team will be with you soon.",view=TicketView())
            await i.response.send_message(f"Ticket created: {ch.mention}",ephemeral=True)
        except discord.Forbidden: await i.response.send_message("Bot needs Manage Channels permission.",ephemeral=True)
async def setup(bot): await bot.add_cog(Tickets(bot))
