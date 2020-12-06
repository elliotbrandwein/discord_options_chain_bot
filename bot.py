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
    data = ""
    try:
        data = yahoo.return_puts(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
            ascii_table.field_names = data.columns
            for i in range(len(data.index)):
                if i == 4:
                    ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","PRICE:", round(yahoo.price_cache[ticka],4)])
                ascii_table.add_row(data.iloc[i])
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
    except:
      await ctx.send("There was an error please try again")
  

@bot.command(name='calls')
async def call_getter(ctx, ticka):
    ascii_table = PrettyTable()
    data = ""
    try:
        data = yahoo.return_calls(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
            ascii_table.field_names = data.columns
            for i in range(len(data.index)):
                if i == 4:
                    ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","PRICE:", round(yahoo.price_cache[ticka],4)])
                ascii_table.add_row(data.iloc[i])
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
    except:
      await ctx.send("There was an error please try again")
    
bot.run(TOKEN)
