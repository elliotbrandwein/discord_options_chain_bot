import discord
from discord.ext import commands
import yahoo #our other file
from dotenv import load_dotenv
import os
from prettytable import PrettyTable

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>') #change character here

#####
# by default bot commands only accept one token, the first after the command
# can accept multiple tokens by using *args instead of ticka
# then query = " ".join(args[:]) >>> query = query.strip()


@bot.command(name='puts')
async def put_getter(ctx, ticka):
    ascii_table = PrettyTable()
    price = yahoo.price_cache[ticka]
    data = yahoo.return_puts(ticka)
    data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
    for col in data.columns:
        ascii_table.add_column(col, data[col].to_list())
    await ctx.send(f"```\n{ascii_table.get_string()}\n```")

@bot.command(name='calls')
async def call_getter(ctx, ticka):
    ascii_table = PrettyTable()
    data = yahoo.return_calls(ticka)
    data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
    for col in data.columns:
        ascii_table.add_column(col, data[col].to_list())
    await ctx.send(f"```\n{ascii_table.get_string()}\n```")


bot.run(TOKEN)
