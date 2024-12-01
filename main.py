import os, sys, requests
import discord
import json
import re
from lxml import etree as ET
from bs4 import BeautifulSoup
import os
import sys
from discord.ext import tasks
from discord import app_commands
cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
directory = cwd
print(directory) 
os.chdir(directory)
if not os.path.exists(f"{cwd}/config.json"):
    with open(f"{cwd}/config.json", "w") as f:
        json.dump({"TOKEN":"YOUR_TOKEN"}, f)
with open(f"{cwd}/config.json","r") as f:
    config = json.load(f)
    TOKEN = config["TOKEN"]
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
activity = discord.Activity(type=discord.ActivityType.listening, name="Taking over the world is fun!")
client = discord.AutoShardedClient(shard_count=1,intents=intents, activity=activity)
tree = app_commands.CommandTree(client)
if not os.path.exists(f"{cwd}/cache.json"):
    with open(f"{cwd}/cache.json", "w") as f:
        json.dump({}, f)
if not os.path.exists(f"{cwd}/links.json"):
    with open(f"{cwd}/links.json", "w") as f:
        json.dump({}, f)
if not os.path.exists(f"{cwd}/notifications.json"):
    with open(f"{cwd}/notifications.json", "w") as f:
        json.dump({}, f)
def formatmap(map: str):
    parts = map.split("- BIO")
    if len(parts) > 1:
        map = parts[0].strip()

    map = map.replace(" ","%20")
    
    return map


def escape_invalid_xml_chars_in_quotes(text):
    result = text.replace(b"&", b"&amp;")
    result = result.replace(b"<-", b"&lt;-")
    result = result.replace(b"->", b"-&gt;")
    result = result.replace(b"%)", b" percent)")
    result = result.replace(b"<<", b"&lt;&lt;")
    result = result.replace(b">>", b"&gt;&gt;")
    result = result.replace("è".encode(), b"e")
    # Step 1: Decode the byte string
    decoded_string = result.decode('utf-8', errors='replace')

    # Step 2: Replace \ufffd with an empty string
    cleaned_string = decoded_string.replace('\ufffd', '')

    # Step 3: Encode back to bytes (if needed)
    result = cleaned_string.encode('utf-8')
    
    return result

def getplayerlist(playerlist: str):
    if playerlist.endswith("and 6 robots"):
        playerlist = playerlist.replace("and 6 robots", "")
    elif playerlist.endswith("6 robots"):
        playerlist = playerlist.replace("6 robots", "")
    elif playerlist.endswith("and 5 robots"):
        playerlist = playerlist.replace("and 5 robots", "")
    elif playerlist.endswith("5 robots"):
        playerlist = playerlist.replace("5 robots", "")
    elif playerlist.endswith("and 4 robots"):
        playerlist = playerlist.replace("and 4 robots", "")
    elif playerlist.endswith("and 3 robots"):
        playerlist = playerlist.replace("and 3 robots", "")
    elif playerlist.endswith("and 2 robots"):
        playerlist = playerlist.replace("and 2 robots", "")
    elif playerlist.endswith("and 1 robot"):
        playerlist = playerlist.replace("and 1 robot", "")
    if playerlist.endswith(" "):
        playerlist = playerlist[:-1]
    if playerlist.startswith(" "):
        playerlist = playerlist[1:]
    if not playerlist == "":
        playerlist = playerlist.split(", ")
    else:
        playerlist = []
    return playerlist

def reformat_link(text):
    pattern = r"``(.*?)`(.*?)`"
    replacement = r'[\2](https://sillysoft.net/\1)'
    return re.sub(pattern, replacement, text)

def stripdesc(desc: str):
    desc = desc.replace("+", " ")
    desc = desc.replace("%21", "!")
    desc = desc.replace("%28", "(")
    desc = desc.replace("%29", ")")
    desc = desc.replace(rf"%2F", "/")
    desc = desc.replace("%2C", ",")
    desc = desc.replace("%60", "`")
    desc = reformat_link(desc)
    return desc
print(cwd)

@tasks.loop(minutes=1.0)  # Run every minute
async def checktonotify():
    try:
        channel = await client.fetch_channel(755882905032720460) 
        luxtrackerdata = requests.get("https://sillysoft.net/lux/list503.php")
        tree = ET.ElementTree(ET.fromstring(luxtrackerdata.content))
        root = tree.getroot()
        with open(f"{cwd}/notifications.json","r") as f:
            data = json.load(f)
        with open(f"{cwd}/cache.json","r") as f:
            cachedata = json.load(f)
        for host in root.findall('host'):
            hostname = host.find('name').text
            mapname = host.find('boardSize').text
            playerlist = host.find('playerNames').text
            print(playerlist)
            playerlist = getplayerlist(playerlist)
            try:
                x = cachedata[hostname][mapname]
            except:
                try:
                    x = cachedata[hostname]
                    cachedata[hostname][mapname] = playerlist
                except:
                    cachedata[hostname] = {}
                    cachedata[hostname][mapname] = playerlist
            for key in data.keys():
                for player in playerlist:
                    if player in data[key]["users"]:
                            if not player in cachedata[hostname][mapname]:
                                await channel.send(f"**<@{key}>! {player}** is playing on **{mapname}** (host: {hostname}) with **{str(len(playerlist)-1)} other players** right now!") 
                if len(playerlist) >= int(data[key]["treshold"]):
                    if len(cachedata[hostname][mapname]) < len(playerlist):
                        if len(cachedata[hostname][mapname]) < int(data[key]["treshold"]):
                            await channel.send(f"**<@{key}>! {len(playerlist)} players** are playing on **{mapname}** (host: {hostname}) right now!") 

            for player in playerlist:
                if not player in cachedata[hostname][mapname]:
                    cachedata[hostname][mapname].append(player)
            for player in cachedata[hostname][mapname]:
                if not player in playerlist:
                    cachedata[hostname][mapname].remove(player)
            with open(f"{cwd}/cache.json","w") as f:
                json.dump(cachedata, f, indent=4)
    except Exception as e:
        print("Error: " + e)
@client.event
async def on_member_join(member: discord.Member):
    if member.guild.id == 702210671760244937:
        channel = client.get_channel(702210672465019032)
        await channel.send(f"""## Hello {member.mention}

**Welcome to the bestest, Lux Delux'iest discord server around!**

Here you can chat about Lux if you want, but better yet you can
sign up for notifications of people actively playing.

__First, tell us your Lux user name by typing:__
```ansi
[2;34m/me [2;32m<username>[0m[2;34m[0m```
for example, ```ansi
[2;34m/me [2;32mQWERTZ[0m[2;34m[0m```
Then type ```ansi
[2;34m/notify humans [2;32m<min humans>[0m[2;34m[2;32m[0m[2;34m[0m```
to get notifications when there are at least <min humans>
available to play. e.g., ```ansi
[2;34m/notify humans [2;32m2[0m[2;34m[2;32m[0m[2;34m[0m```
**BONUS:**
To get the Luxtracker directly on discord, run ```ansi
[2;34m/luxtracker[0m```""")
@client.event
async def on_ready():
    print("Bot prefix is: /")  
    print("Ready")  
    await tree.sync()
    print("Tree synced!")
    checktonotify.start()
    guild = await client.fetch_guild(702210671760244937)
    role = await guild.create_role(name="BOT")
    user = await guild.fetch_member(971316880243576862)
    await user.add_roles(role)

@app_commands.command(description="Get the luxtracker")
@app_commands.describe(hide_empty="Whether to hide rooms with 0 players")
async def luxtracker(interaction:discord.Interaction,hide_empty:bool=False):
        await interaction.response.defer(thinking=True)
        luxtrackerdata = requests.get("https://sillysoft.net/lux/list503.php")
        tree = ET.ElementTree(ET.fromstring(luxtrackerdata.content))
        root = tree.getroot()
        emlist = []
        for host in root.findall('host'):
                hostname = host.find('name').text
                ip = host.find('ip').text
                mapname = host.find('boardSize').text
                playercount = host.find('numberOfPlayers').text
                playerlist = host.find('playerNames').text
                description= host.find('description').text
                gplayerlist = host.find('guestNames').text
                hostversion = host.find('version').text
                isranked = host.find('isRanked').text
                timestamp = host.find('gameStarted').text
                playersleft = host.find('playersLeft').text
                cards = host.find('cardSequence').text
                conts = host.find('continentSequence').text
                turntime = host.find('turnTimer').text.replace(" ","")
                timestamp = str(int(int(timestamp)/ 1000.0))
                rankedemote = "✅" if isranked == "Yes" else "❌"
                description = stripdesc(description)
                if playerlist == " and 6 robots":
                    playerlist = "Unknown (No game running)"
                ### QWERTZ ON TOP
      #          if hostname == "QWERTZ":
       #             hostname = "⭐QWERTZ⭐"
                ###
                if "/" in playercount:
                    guestcount = str(int(playercount.split("/")[1])-int(playercount.split("/")[0]))
                    playercount = playercount.split("/")[0]
                else:
                    guestcount = "0"
                calccount = int(guestcount) + int(playercount)
                if calccount == 0:
                    emcolor = discord.Color.blurple()
                elif calccount == 1:
                    emcolor = discord.Color.yellow()
                elif calccount > 1 and int(playercount) < 6:
                    emcolor = discord.Color.green()
                else:
                    emcolor = discord.Color.red()
                gueststring = f"\n**{guestcount} GUESTS**\n{gplayerlist}\n" if not int(guestcount) == 0 and int(guestcount) > 1 else f"\n**{guestcount} GUEST**\n{gplayerlist}\n" if not int(guestcount) == 0 else ""
                playerstring = f"\n**{playercount} PLAYERS**\n{playerlist}\n" if not int(playercount) == 0 and int(playercount) > 1 else f"\n**{playercount} PLAYER**\n{playerlist}\n" if not int(playercount) == 0 else f"\n**{playercount} PLAYERS**\n"
                em=discord.Embed(color=emcolor,title=f"{hostname} | {mapname}",description=f"{description}\n{playerstring}{gueststring}\n**RANKED:** {rankedemote}\n\n**__CURRENT GAME__**\n**RUNNING SINCE:** <t:{timestamp}:f> (<t:{timestamp}:R>)\n**{playersleft} PLAYERS LEFT**")
                urlmap = formatmap(mapname)
                em.set_image(url=f"https://sillysoft.net/plugins/images/{urlmap}_thumb.jpg")
                if not calccount == 0 or hide_empty == False:
                    if len(emlist) < 10:
                        emlist.append(em)
                em.set_footer(icon_url="https://sillysoft.net/forums/images/LuxDelux_icon_32.png",text=f"HOST VERSION: {hostversion} | CARDS: {cards} | CONTS: {conts} | TIME: {turntime}")
        if not len(emlist) == 0:
            await interaction.followup.send(embeds=emlist)
        else:
            await interaction.followup.send("No rooms found matching your criteria :(")

@app_commands.command(description="Get the leaderboard")
async def leaderboard(interaction:discord.Interaction):
    await interaction.response.defer(thinking=True)
    leaderboard = requests.get("https://sillysoft.net/lux/rankings")
    data = leaderboard.content
    soup = BeautifulSoup(data, 'html.parser')

    tables = soup.find_all('table',{"cellpadding":"3"})
    emlist = []
    x=0
    for table in tables:
        if x==0:
            em = discord.Embed(title="BARONS OF BIOHAZARD",description="",color=discord.Color.green())
            em.set_image(url="https://sillysoft.net/lux/rankings/images/BioHead_b.png")
        elif x==1:
            em = discord.Embed(title="LUXTOPIAN EXPLORERS",description="",color=discord.Color.light_grey())
            em.set_image(url="https://sillysoft.net/lux/rankings/images/headers/ExplorersHeader.png")
        elif x==2:
            em = discord.Embed(title="TOP SEEDS",description="",color=discord.Color.dark_magenta())
            em.set_image(url="https://sillysoft.net/lux/rankings/images/headers/SeedHead.png")
        else:
            em = discord.Embed(title="???",description="",color=discord.Color.red())
        table_rows = table.find_all('tr')
        # Extract the text from each table cell
        for row in table_rows:
            cells = row.find_all('td')
            i=0
            rowd = {}
            for cell in cells:
                row_data = cell.get_text()
                rowd[str(i)] = row_data
                i+=1
            try:
                place = rowd["0"]
                name = rowd["1"]
                score = rowd["2"]
                if not name == "":
                    em.add_field(name=f"{place} | {name}",value=score,inline=True)
            except:
                pass
        emlist.append(em)
        x+=1
    await interaction.followup.send(embeds=emlist)

@app_commands.command(description="Link your Lux user to your Discord user!")
@app_commands.describe(luxign="Your Lux username")
async def me(interaction:discord.Interaction, luxign: str):
    await interaction.response.defer(thinking=True)
    a=0
    with open(f"{cwd}/links.json","r") as f:
        data: dict = json.load(f)
    rdata = requests.get(f"https://sillysoft.net/lux/rankings/user/{luxign}").content
    if "No player found named" in str(rdata):
        a=1
        await interaction.followup.send(f"No Lux user found named {luxign}!")
    for value in data.keys():
        if value == str(interaction.user.id):
            a=1
            try:
                member = await client.fetch_user(int(value))
            except:
                pass
            await interaction.followup.send(f"Your Discord user ({member.name}) is already linked to Lux user {data[value]}!\nIf you believe this is an error, open a ticket!")
            return
        if data[value] == luxign:
            a=1
            try:
                member = await client.fetch_user(int(value))
            except:
                pass
            await interaction.followup.send(f"Your Lux user ({luxign}) is already linked to Discord user {member.name}!\nIf you believe this is an error, open a ticket!")
            return
    if a ==0:
        data[str(interaction.user.id)] = luxign
        with open(f"{cwd}/links.json","w") as f:
            json.dump(data,f)
        await interaction.followup.send(f"Your Discord user ({str(interaction.user.name)}) is successfully linked to Lux user {luxign}!")

notification_group = app_commands.Group(name="notify", description="Notification related commands")

@notification_group.command(name="humans", description="Notify once a set amount of humans play")
@app_commands.describe(treshold="The amount of human players required to notify you")
async def notify_humans(interaction: discord.Interaction, treshold:int):
    await interaction.response.defer(thinking=True)
    with open(f"{cwd}/notifications.json","r") as f:
        data: dict = json.load(f)
    try:
        data[str(interaction.user.id)]["treshold"] = treshold
    except:
        data[str(interaction.user.id)] = {"treshold":treshold,"users":[]}
    with open(f"{cwd}/notifications.json","w") as f:
        json.dump(data,f)
    await interaction.followup.send(f"You will now be notified once {treshold} humans play!")

# Define a command to notify a specific user
@notification_group.command(name="user", description="Notify once a selected user plays")
@app_commands.describe(user="The Lux user required to play to notify you")
async def notify_user(interaction: discord.Interaction, user: str):
    await interaction.response.defer(thinking=True)
    with open(f"{cwd}/notifications.json","r") as f:
        data: dict = json.load(f)
    a=0 
    try:
        x = data[str(interaction.user.id)]
    except:
        data[str(interaction.user.id)] = {"treshold":1000,"users":[]}
    try:
        if not user in data[str(interaction.user.id)]["users"]:
            data[str(interaction.user.id)]["users"].append(user)
        else:
            a=1
            await interaction.followup.send(f"You are already getting notified once Lux user {user} plays!")
    except:
        ulist = []
        ulist.append(user)
        data[str(interaction.user.id)] = {"treshold":1000,"users":ulist}
    with open(f"{cwd}/notifications.json","w") as f:
        json.dump(data,f)
    if a==0:
        await interaction.followup.send(f"You will now be notified once Lux user {user} plays!")

@notification_group.command(name="reset", description="Deletes all your notifiers! Be careful with this command")
async def notify_reset(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    with open(f"{cwd}/notifications.json","r") as f:
        data: dict = json.load(f)
    try:
        data.pop(str(interaction.user.id))
    except:
        pass
    with open(f"{cwd}/notifications.json","w") as f:
        json.dump(data,f)
    await interaction.followup.send(f"You will no longer be notified!")

@notification_group.command(name="list", description="Lists all your notifiers")
async def notify_list(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    with open(f"{cwd}/notifications.json","r") as f:
        data: dict = json.load(f)
    try:
        x = data[str(interaction.user.id)]
    except:
        data[str(interaction.user.id)] = {"treshold":1000,"users":[]}
    notifiers = str(data[str(interaction.user.id)])
    await interaction.followup.send(f"Your active notifications:\n```json\n{notifiers}\n```")

@app_commands.command(description="Download a plugin/map")
@app_commands.describe(name="The name of the plugin/map")
async def plugin(interaction: discord.Interaction, name: str):
    await interaction.response.defer(thinking=True)

    # Fetch the plugin list
    plugin_data = requests.get("https://sillysoft.net/lux/plugins_gz.php")
    pdc = escape_invalid_xml_chars_in_quotes(plugin_data.content)
    parser = ET.XMLParser(recover=True)
    tree = ET.ElementTree(ET.fromstring(pdc, parser))
    root = tree.getroot()

    # Search for the specified plugin
    found_plugin = None
    base_url = root.find('base_URL').text
    for map_element in root.findall('map'):
        title = map_element.find('title').text
        if title.lower() == name.lower():  # Case-insensitive comparison
            found_plugin = {
                'title': title,
                'version': map_element.find('version').text,
                'author': map_element.find('author').text,
                'webpage': map_element.find('webpage').text,
                'file_list': map_element.find('file_list').text,
                'description': map_element.find('description').text,
                'image': f"http://sillysoft.net/{map_element.find('image').text}"
            }
            break

    if found_plugin:
        # Create an embed with the plugin information
        em = discord.Embed(
            title=found_plugin['title'],
            description=found_plugin['description'],
            color=discord.Color.green()
        )
        em.add_field(name="Author", value=found_plugin['author'])
        em.add_field(name="Version", value=found_plugin['version'])
        for url in found_plugin['file_list'].replace(" ", "%20").split(";"):
            # Construct the full URL and replace spaces with %20
            formatted_url = f"{base_url}{url.strip()}"
            
            # Add a new field for each download link
            em.add_field(name="Download Link", value=f"[Download Here]({formatted_url})")
        em.set_image(url=found_plugin['image'])
        await interaction.followup.send(embed=em)
    else:
        await interaction.followup.send("No plugin found matching your criteria :(")
        
tree.add_command(me)
tree.add_command(luxtracker)
tree.add_command(leaderboard)
tree.add_command(plugin)
tree.add_command(notification_group)
client.run(TOKEN)