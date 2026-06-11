import json
import aiohttp
import discord
import os
from dotenv import load_dotenv
from discord.ext import tasks

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
NOTIFY_USER_ID = os.getenv("NOTIFY_USER_ID")

with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.default()
client = discord.Client(intents=intents)

@tasks.loop(seconds=60)
async def check_stock():
    for i in range(len(config["items"])):
        item = config["items"][i]
        url = f"{item['base_shop_url']}/products.json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        products = data["products"]
        for p in products:
            p.get("handle")
            if p["handle"] == item["product_handle"]:
                variants = p["variants"]
        
        in_stock = any(v.get("available") for v in variants)
        if (in_stock) and (item["notified"] == False):
            user = await client.fetch_user(NOTIFY_USER_ID)
            await user.send(f"Item is back in stock! {item['product_url']}")
            config["items"][0]["notified"] = True
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)

@client.event
async def on_ready():
    print("Connected to Discord!")
    check_stock.start()

client.run(DISCORD_TOKEN)