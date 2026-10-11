import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import os

# Načítanie tokenu z premenných prostredia
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
app = Flask(__name__)

# Databáza farieb pre slovenské tímy (použijú sa podľa toho, kto skóruje)
FARBY_TIMOV = {
    "Slovan Bratislava": 0x228B22, # Svetlomodrá/Zelená (prispôsob si hex kód)
    "Spartak Trnava": 0xE30613,    # Červená
    "Košice": 0xFFD700,             # Žltá
    "DAC 1904": 0x0000FF,           # Modrá
    "Podbrezová": 0x808080,         # Sivá/Zelená
    "MŠK Žilina": 0x7FFF00,         # Žlto-zelená
    "Zemplín": 0x00008B,            # Tmavomodrá
    "Trenčín": 0xFFFFFF            # Biela
}

@app.route('/gol', methods=['POST'])
def gol_prijaty():
    data = request.json
    strelec = data.get('strelec')
    tim_co_skoroval = data.get('tim')  # Názov tímu, ktorý dal gól (napr. "Slovan Bratislava")
    tim_proti = data.get('tim_proti')  # Názov súpera (napr. "Spartak Trnava")
    skoreA = data.get('skoreA')
    skoreB = data.get('skoreB')
    cas = data.get('cas')
    
    bot.loop.create_task(posli_gol_embed(strelec, tim_co_skoroval, tim_proti, skoreA, skoreB, cas))
    return jsonify({"status": "success"}), 200

async def posli_gol_embed(strelec, tim_co_skoroval, tim_proti, skoreA, skoreB, cas):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        # Zistenie farby tímu z databázy (ak tím nenájde, dá neutrálnu sivú 0x808080)
        farba = FARBY_TIMOV.get(tim_co_skoroval, 0x808080)
        
        # Vytvorenie Embed okienka prispôsobeného pre tvoj tím
        embed = discord.Embed(title=f"💥 {tim_co_skoroval}", color=farba)
        embed.description = "⚽ **GÓÓÓÓÓÓL!**"
        
        embed.add_field(name="Zápas", value=f"🏆 **{tim_co_skoroval}** vs **{tim_proti}**", inline=False)
        embed.add_field(name="Aktuálne skóre", value=f"🔢 **[{skoreA}] : {skoreB}**", inline=False)
        embed.add_field(name="Střelec Branky", value=f"👤 {strelec}", inline=True)
        embed.add_field(name="Čas", value=f"⏱️ {cas}", inline=True)
        
        embed.set_footer(text="Niké Liga - Virtual Roblox League")
        
        await channel.send(embed=embed)

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run(TOKEN)