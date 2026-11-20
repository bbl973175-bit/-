import aiosqlite
from bot.config import DATABASE_PATH
DEFAULTS = {
"welcome_enabled":"0","welcome_channel":"","welcome_message":"Welcome {mention}!",
"leave_enabled":"0","leave_channel":"","log_channel":"",
"automod_enabled":"0","blocked_words":"","block_links":"0",
"antispam_enabled":"0","antispam_limit":"5","antispam_window":"7",
"antiraid_enabled":"0","raid_join_limit":"8","raid_window":"20",
"autorole_enabled":"0","autorole_id":"","suggestions_enabled":"0",
"suggestions_channel":"","tickets_enabled":"0","ticket_category":"","leveling_enabled":"0"
}
async def initialize_database():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("CREATE TABLE IF NOT EXISTS guild_settings(guild_id TEXT,key TEXT,value TEXT,PRIMARY KEY(guild_id,key))")
        await db.execute("CREATE TABLE IF NOT EXISTS warnings(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id TEXT,user_id TEXT,moderator_id TEXT,reason TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,guild_id TEXT,channel_id TEXT,user_id TEXT,status TEXT DEFAULT 'open',created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
        await db.execute("CREATE TABLE IF NOT EXISTS levels(guild_id TEXT,user_id TEXT,xp INTEGER DEFAULT 0,level INTEGER DEFAULT 0,PRIMARY KEY(guild_id,user_id))")
        await db.commit()
async def get_setting(guild_id,key,default=None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur=await db.execute("SELECT value FROM guild_settings WHERE guild_id=? AND key=?",(str(guild_id),key))
        row=await cur.fetchone()
    return row[0] if row else DEFAULTS.get(key,default)
async def set_setting(guild_id,key,value):
    if key not in DEFAULTS: raise ValueError("Unknown setting")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT INTO guild_settings VALUES(?,?,?) ON CONFLICT(guild_id,key) DO UPDATE SET value=excluded.value",(str(guild_id),key,str(value)))
        await db.commit()
async def get_all_settings(guild_id):
    result=dict(DEFAULTS)
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cur=await db.execute("SELECT key,value FROM guild_settings WHERE guild_id=?",(str(guild_id),))
        for k,v in await cur.fetchall():
            if k in result: result[k]=v
    return result
