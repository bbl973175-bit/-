from flask import Flask,redirect,request,session,render_template,url_for
import requests,asyncio,aiosqlite
from bot.config import CLIENT_ID,CLIENT_SECRET,REDIRECT_URI,FLASK_SECRET_KEY,DATABASE_PATH,DASHBOARD_HOST,DASHBOARD_PORT
from bot.database import DEFAULTS
app=Flask(__name__); app.secret_key=FLASK_SECRET_KEY
API="https://discord.com/api/v10"
def headers(): return {"Authorization":"Bearer "+session["access_token"]}
def manageable(g):
    p=int(g.get("permissions","0")); return bool(p&0x20 or p&0x8)
@app.get("/")
def home():
    if not session.get("access_token"): return render_template("login.html")
    try:
        u=requests.get(API+"/users/@me",headers=headers(),timeout=15)
        if u.status_code!=200: session.clear(); return redirect(url_for("home"))
        user=u.json(); gs=requests.get(API+"/users/@me/guilds",headers=headers(),timeout=15).json()
        return render_template("servers.html",user=user,guilds=[g for g in gs if manageable(g)])
    except requests.RequestException: return "Discord API unavailable.",503
@app.get("/login")
def login():
    if not CLIENT_ID or not CLIENT_SECRET: return "Configure Discord OAuth credentials in .env.",500
    from urllib.parse import urlencode
    q=urlencode({"client_id":CLIENT_ID,"redirect_uri":REDIRECT_URI,"response_type":"code","scope":"identify guilds"})
    return redirect("https://discord.com/oauth2/authorize?"+q)
@app.get("/callback")
def callback():
    code=request.args.get("code")
    if not code: return redirect(url_for("home"))
    try:
        r=requests.post(API+"/oauth2/token",data={"client_id":CLIENT_ID,"client_secret":CLIENT_SECRET,"grant_type":"authorization_code","code":code,"redirect_uri":REDIRECT_URI},headers={"Content-Type":"application/x-www-form-urlencoded"},timeout=15)
        r.raise_for_status(); session["access_token"]=r.json()["access_token"]
        return redirect(url_for("home"))
    except requests.RequestException: return "Discord OAuth failed. Check the redirect URL and credentials.",400
@app.get("/logout")
def logout(): session.clear(); return redirect(url_for("home"))
def authorized_guild(gid):
    if not session.get("access_token"): return None
    gs=requests.get(API+"/users/@me/guilds",headers=headers(),timeout=15).json()
    return next((g for g in gs if g["id"]==gid and manageable(g)),None)
@app.get("/server/<guild_id>")
def server(guild_id):
    if not session.get("access_token"): return redirect(url_for("home"))
    try:
        guild=authorized_guild(guild_id)
        if not guild: return "No Manage Server permission for this server.",403
        settings=dict(DEFAULTS)
        async def read():
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cur=await db.execute("SELECT key,value FROM guild_settings WHERE guild_id=?",(guild_id,))
                for k,v in await cur.fetchall():
                    if k in settings: settings[k]=v
        asyncio.run(read())
        return render_template("settings.html",guild=guild,settings=settings)
    except requests.RequestException: return "Discord API unavailable.",503
@app.post("/server/<guild_id>/save")
def save(guild_id):
    if not session.get("access_token"): return redirect(url_for("home"))
    try:
        if not authorized_guild(guild_id): return "Forbidden",403
        async def write():
            async with aiosqlite.connect(DATABASE_PATH) as db:
                for key in DEFAULTS:
                    value=request.form.get(key,"")
                    if key.endswith("_enabled") or key=="block_links": value="1" if key in request.form else "0"
                    if key in request.form or key.endswith("_enabled") or key=="block_links":
                        await db.execute("INSERT INTO guild_settings VALUES(?,?,?) ON CONFLICT(guild_id,key) DO UPDATE SET value=excluded.value",(guild_id,key,value[:1500]))
                await db.commit()
        asyncio.run(write())
        return redirect(url_for("server",guild_id=guild_id)+"?saved=1")
    except requests.RequestException: return "Discord API unavailable.",503
if __name__=="__main__": app.run(host=DASHBOARD_HOST,port=DASHBOARD_PORT,debug=False)
