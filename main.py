import os
import discord
import requests
from discord.ext import commands
from requests.auth import HTTPBasicAuth
import openai
import asyncio
import logging
from openai import OpenAIError, RateLimitError, APIConnectionError, AuthenticationError

# Load secrets from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EBAY_CLIENT_ID = os.getenv("EBAY_CLIENT_ID")
EBAY_CLIENT_SECRET = os.getenv("EBAY_CLIENT_SECRET")

# Setup OpenAI client
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# Setup Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True  # Allow reading message content
bot = commands.Bot(command_prefix="!", intents=intents)

# eBay OAuth token function
def get_ebay_oauth_token():
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope"
    }

    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=HTTPBasicAuth(EBAY_CLIENT_ID, EBAY_CLIENT_SECRET)
    )
    response.raise_for_status()
    return response.json()["access_token"]

# OpenAI prompt handler
async def ask_gpt(message):
    while True:
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                temperature=0.3,
                max_tokens=100
            )
            return response.choices[0].message.content

        except RateLimitError:
            logging.warning("Rate limited, retrying in 5 seconds...")
            await asyncio.sleep(5)
        except APIConnectionError:
            logging.warning("API connection error, retrying in 5 seconds...")
            await asyncio.sleep(5)
        except AuthenticationError:
            logging.error("Authentication error: check your OpenAI API key.")
            return "Authentication error. Check your API key."
        except OpenAIError as e:
            logging.error(f"OpenAI error: {e}")
            await asyncio.sleep(5)

# Discord command to ask GPT
@bot.command()
async def ask(ctx, *, query):
    reply = await ask_gpt(query)
    await ctx.send(reply)

# Run the bot
bot.run(DISCORD_TOKEN)

    await ctx.send(reply)

# Run bot
bot.run(DISCORD_TOKEN)
