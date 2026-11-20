# NEXORA SYSTEM
Open-source Discord bot starter with moderation, community safety, tickets, leveling and a Discord OAuth dashboard.

## Features
- Slash commands: `/kick`, `/ban`, `/timeout`, `/warn`, `/warnings`, `/suggest`, `/ticket`
- Moderation permissions and role-hierarchy checks
- Configurable AutoMod, Anti-Spam and Anti-Raid alerts
- Welcome/leave messages, AutoRole, suggestions and XP leveling
- Private tickets with close button
- Dark responsive web dashboard using Discord OAuth
- SQLite database shared by bot and dashboard

## Setup
1. Install Python 3.11+ and run `pip install -r requirements.txt`.
2. Create a Discord application and add a bot.
3. Enable **Server Members Intent** and **Message Content Intent** in Developer Portal > Bot.
4. Copy `.env.example` to `.env`; add your own bot token, client ID, client secret and a long random Flask secret.
5. Add the exact `DISCORD_REDIRECT_URI` to OAuth2 > Redirects in Developer Portal.
6. Invite the bot using scopes `bot` and `applications.commands`, with only required permissions.
7. Start bot: `python -m bot.main`
8. Start dashboard in a second process: `python -m dashboard.app`
9. Visit `http://127.0.0.1:5000` for local testing.

## Configuration
Select a server in the dashboard, enter channel/role/category IDs, then enable modules. Turn on Developer Mode in Discord to copy IDs. Keep bot and dashboard on the same host and database path.

## Notes
Anti-Raid sends alerts only; it does not mass-ban or lock down the server. Anti-Spam uses conservative detection and does not auto-timeout users. AutoMod deletes matching messages only when enabled. The included Flask server is for testing; use HTTPS and a production WSGI server for public hosting.

## Security
Never publish `.env`, bot tokens, OAuth client secrets or Flask secret keys. `.env` is ignored by Git. Do not share credentials in chat.

## License
MIT
