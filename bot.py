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

@bot.command(name='bands')
async def safe_contracts(ctx, *args):
    tokens = args[:]
    if len(tokens) < 2:
        await ctx.send("funtionality is >bands [call/put] [ticka]")
        return
    elif len(tokens) == 2:
        data = yahoo.get_band(tokens[1])
        if tokens[0] == 'call' or tokens[0] == 'calls':
            data = data[['MA','STD','Upper']]
        elif tokens[0] == 'put' or tokens[0] == 'puts':
            data = data[['MA','STD','Lower']]
    
    

    return
    
bot.run(TOKEN)
