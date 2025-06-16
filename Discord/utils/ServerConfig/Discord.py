#                                https://safemarket.xyz/
#__| |_____________________________________________________________________________| |__
#__   _____________________________________________________________________________   __
#  | |                                                                             | |  
#  | | ____     _     _____  _____      __  __     _     ____   _  __ _____  _____ | |  
#  | |/ ___|   / \   |  ___|| ____|    |  \/  |   / \   |  _ \ | |/ /| ____||_   _|| |  
#  | |\___ \  / _ \  | |_   |  _|      | |\/| |  / _ \  | |_) || ' / |  _|    | |  | |  
#  | | ___) |/ ___ \ |  _|  | |___     | |  | | / ___ \ |  _ < | . \ | |___   | |  | |  
#  | ||____//_/   \_\|_|    |_____|    |_|  |_|/_/   \_\|_| \_\|_|\_\|_____|  |_|  | |  
#__| |_____________________________________________________________________________| |__
#__   _____________________________________________________________________________   __
#  | |                                                                             | |  
#                               https://github.com/Zhodisov                           

# Used in Safemarket V2



import os
import discord
from discord.ext import commands, tasks
import requests
import time
import asyncio
from quart import Quart, request, jsonify
from hypercorn.asyncio import serve
from hypercorn.config import Config
import hmac
import hashlib
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.invites = True
search_active = False
bot = commands.Bot(command_prefix="!", intents=intents)
API_KEY = '' # api.ipapi.is
WELCOME_CHANNEL_ID = 1267549906990792744 # Welcome Channel
WEBHOOK_CHANNEL_ID = 1267545989418319993 # Yapp Channel
INVITE_CHANNEL_ID = 950806890835755020 # Invite Receive Channel
HISTORY_CHANNEL_ID = 1267815938749890652 # History Channel
new_members = {}
last_invite = {} 
announced_members = {}
SECRET_KEY = "SafeMarket-23489756231156789743-SafeMarket"

def validate_token(token):
	try:
		token, timestamp = token.split(':')
		timestamp = int(timestamp)
		c_time = int(time.time())
		if c_time - timestamp > 300:
			return False
		m = f'{timestamp}'
		ex = hmac.new(SECRET_KEY.encode(), m.encode(), hashlib.sha256).hexdigest()
		return hmac.compare_digest(ex, token)
	except Exception as e:
		return False

@bot.event
async def on_ready():
	await update_invite()

async def update_invite():
    global invites
    invites = {}
    for guild in bot.guilds:
        invites[guild.id] = {invite.code: invite for invite in await guild.invites()}

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return
    try:
        new_invites = await member.guild.invites()
    except discord.Forbidden as e:
        await channel.send(f"@everyone {member.mention} присоединился к серверу, но у меня нет необходимых прав, чтобы проверить использованное приглашение.")
        return
    except Exception as e:
        return
    invite_used = None
    for invite in invites.get(member.guild.id, {}).values():
        for new_invite in new_invites:
            if invite.code == new_invite.code and invite.uses < new_invite.uses:
                inviter = new_invite.inviter
                invite_url = new_invite.url
                invite_code = new_invite.code
                uses = new_invite.uses
                invite_used = last_invite[member.guild.id] = {
                    'url': invite_url,
                    'code': invite_code,
                    'inviter': inviter,
                    'uses': uses,
                    'ip': last_invite.get(member.guild.id, {}).get('ip')
                }
                break
        if invite_used:
            break
    if invite_used and member.id not in announced_members:
        await channel.send(f"Все {member.mention} присоединились к серверу по приглашению {invite_used['url']} (IP: {invite_used['ip']})")
        announced_members[member.id] = invite_used['url']

        try:
            invite_to_delete = next((inv for inv in new_invites if inv.code == invite_used['code']), None)
            if invite_to_delete:
                await invite_to_delete.delete()
        except Exception as e:
            print(f"{invite_used['code']}: {e}")
    elif invite_used:
        print(f"Участник {member.name} уже объявлен для приглашения {invite_used['url']}")
    else:
        await channel.send(f"@everyone {member.mention} присоединился к серверу.")

    new_members[member.id] = {
        'username': str(member),
        'joined_at': time.time()
    }

    await update_invite()


@bot.event
async def on_guild_join(guild):
	invites[guild.id] = {invite.code: invite for invite in await guild.invites()}

@bot.event
async def on_guild_remove(guild):
	invites.pop(guild.id, None)
	last_invite.pop(guild.id, None)

@bot.event
async def on_invite_create(invite):
	if invite.guild.id in invites:
		invites[invite.guild.id][invite.code] = invite

	ip_address = last_invite.get(invite.guild.id, {}).get('ip')
	
	last_invite[invite.guild.id] = {
		'url': invite.url,
		'ip': ip_address,
		'uses': invite.uses
	}

@bot.event
async def on_invite_delete(invite):
	if invite.guild.id in invites:
		invites[invite.guild.id].pop(invite.code, None)

def count_code(country_code):
    country_code = country_code.upper()
    flag_offset = ord('🇦') - ord('A')
    flag = chr(ord(country_code[0]) + flag_offset) + chr(ord(country_code[1]) + flag_offset)
    return flag
flask_app = Quart(__name__)

@flask_app.route("/d", methods=["POST"])
async def create_invite():
    # token = request.args.get('safemarket')
    # if not validate_token(token):
    #     return jsonify({"status": "error", "message": "Недопустимый маркер источника"}), 403
    data = await request.json
    ip_address = data.get('_____')
    if not ip_address:
        return jsonify({"status": "error", "message": "Необходим IP-адрес"}), 400
    url = f'https://api.ipapi.is?q={ip_address}&key={API_KEY}'
    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"status": "error", "message": "Не удалось получить информацию об IP-адресе"}), 500
    ip_info = response.json()
    invite_channel = bot.get_channel(INVITE_CHANNEL_ID)
    if not invite_channel:
        return jsonify({"status": "error", "message": "Канал приглашения не найден"}), 500
    invite = await invite_channel.create_invite(max_age=60, max_uses=2)
    guild_id = invite.guild.id
    if guild_id not in invites:
        invites[guild_id] = {}
    if guild_id not in last_invite:
        last_invite[guild_id] = {}
    invites[guild_id][invite.code] = invite
    last_invite[guild_id] = {
        'url': invite.url,
        'ip': ip_address,
        'uses': invite.uses
    }
    ip_details = {
        "ip": ip_info.get("ip", "Unknown"),
        "rir": ip_info.get("rir", "Unknown"),
        "is_bogon": ip_info.get("is_bogon", "Unknown"),
        "is_mobile": ip_info.get("is_mobile", "Unknown"),
        "is_crawler": ip_info.get("is_crawler", "Unknown"),
        "is_datacenter": ip_info.get("is_datacenter", "Unknown"),
        "is_tor": ip_info.get("is_tor", "Unknown"),
        "is_proxy": ip_info.get("is_proxy", "Unknown"),
        "is_vpn": ip_info.get("is_vpn", "Unknown"),
        "is_abuser": ip_info.get("is_abuser", "Unknown"),
        "datacenter": ip_info.get("datacenter", {}).get("datacenter", "Unknown"),
        "country": ip_info.get("location", {}).get("country", "Unknown"),
        "city": ip_info.get("location", {}).get("city", "Unknown")
    }
    location = ip_info.get('location', {})
    location_details = {
        "continent": location.get("continent", "Unknown"),
        "country": location.get("country", "Unknown"),
        "country_code": location.get("country_code", "Unknown"),
        "state": location.get("state", "Unknown"),
        "city": location.get("city", "Unknown"),
        "latitude": location.get("latitude", "Unknown"),
        "longitude": location.get("longitude", "Unknown"),
        "zip": location.get("zip", "Unknown"),
        "timezone": location.get("timezone", "Unknown"),
        "local_time": location.get("local_time", "Unknown"),
        "local_time_unix": location.get("local_time_unix", "Unknown"),
        "is_dst": location.get("is_dst", "Unknown")
    }
    invite_embed = discord.Embed(
        title="🎟️ Создано новое приглашение",
        description=f"Приглашение, созданное для IP `{ip_address}` (`{location_details['country']}`, `{location_details['city']}`).\nКод приглашения : - `{invite.code}`",
        color=0xA64D79
    )
    invite_embed.add_field(name="🌐 IP", value=f"`{ip_details['ip']}`", inline=True)
    invite_embed.add_field(name="🏢 RIR", value=f"`{ip_details['rir']}`", inline=True)
    invite_embed.add_field(name="🚫 Bogon", value=f"`{ip_details['is_bogon']}`", inline=True)
    invite_embed.add_field(name="📱 Mobile", value=f"`{ip_details['is_mobile']}`", inline=True)
    invite_embed.add_field(name="🤖 Crawler", value=f"`{ip_details['is_crawler']}`", inline=True)
    invite_embed.add_field(name="🏬 Datacenter", value=f"`{ip_details['is_datacenter']}`", inline=True)
    invite_embed.add_field(name="🕵️ TOR", value=f"`{ip_details['is_tor']}`", inline=True)
    invite_embed.add_field(name="🛡️ Proxy", value=f"`{ip_details['is_proxy']}`", inline=True)
    invite_embed.add_field(name="🔒 VPN", value=f"`{ip_details['is_vpn']}`", inline=True)
    invite_embed.add_field(name="🚨 Abuser", value=f"`{ip_details['is_abuser']}`", inline=True)
    invite_embed.add_field(name="🏢 Datacenter", value=f"`{ip_details['datacenter']}`", inline=True)
    invite_embed.add_field(name="🌍 Continent", value=f"`{location_details['continent']}`", inline=True)
    country_flag = count_code(location_details['country_code'])
    invite_embed.add_field(name=f"{country_flag} Pays", value=f"`{location_details['country']}`", inline=True)
    invite_embed.add_field(name=f"{country_flag} Code Pays", value=f"`{location_details['country_code']}`", inline=True)
    invite_embed.add_field(name="🏙️ Status", value=f"`{location_details['state']}`", inline=True)
    invite_embed.add_field(name="🌆 City", value=f"`{location_details['city']}`", inline=True)
    invite_embed.add_field(name="📍 Latitude", value=f"`{location_details['latitude']}`", inline=True)
    invite_embed.add_field(name="📍 Longitude", value=f"`{location_details['longitude']}`", inline=True)
    invite_embed.add_field(name="🏤 Postal code", value=f"`{location_details['zip']}`", inline=True)
    invite_embed.add_field(name="🕰️ Time Zone", value=f"`{location_details['timezone']}`", inline=True)
    invite_embed.add_field(name="🕒 Local time", value=f"`{location_details['local_time']}`", inline=True)
    invite_embed.add_field(name="🕒 Local time Unix", value=f"`{location_details['local_time_unix']}`", inline=True)
    invite_embed.add_field(name="☀️ DST", value=f"`{location_details['is_dst']}`", inline=True)

    invite_channel_msg = bot.get_channel(WELCOME_CHANNEL_ID)
    if invite_channel_msg:
        await invite_channel_msg.send(embed=invite_embed)

    history_embed = discord.Embed(
        title="📜 История приглашений",
        description=(
            f"Приглашение, созданное PI `{ip_address}` \n- `{location_details['country']}`, `{location_details['country_code']}`, `{location_details['city']}`"
            f"\n- Latitude: `{location_details['latitude']}`\n- Longitude: `{location_details['longitude']}`\n- Code Postal: `{location_details['zip']}`"
            f"\n- Код приглашения: `{invite.code}`"
        ),
        color=0xFF9900
    )
    history_channel = bot.get_channel(HISTORY_CHANNEL_ID)
    if history_channel:
        await history_channel.send(embed=history_embed)

    return jsonify({"api_url": invite.url})

async def run_flask_app():
	config = Config()
	config.bind = ["0.0.0.0:7813"]
	await serve(flask_app, config)

def run_discord_bot():
	loop = asyncio.get_event_loop()
	flask_task = loop.create_task(run_flask_app())
	bot_task = loop.create_task(bot.start("")) # Token
	loop.run_until_complete(asyncio.gather(flask_task, bot_task))
