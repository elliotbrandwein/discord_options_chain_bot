import discord
from discord.ext import commands
import yahoo #our other file
from dotenv import load_dotenv
import os
from prettytable import PrettyTable
import pandas as pd

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>') #change character here

#####
# by default bot commands only accept one token, the first after the command
# can accept multiple tokens by using *args instead of ticka
# then query = " ".join(args[:]) >>> query = query.strip()


def danny_divito(rum_ham, ticka):
    ascii_table = PrettyTable()
    ascii_table.field_names = rum_ham.columns
    for i in range(len(rum_ham.index)):
        if i == 4:
            ascii_table.add_row(["TICKA:",ticka.upper(),"-","-","PRICE:", round(yahoo.price_cache[ticka],4)])
        ascii_table.add_row(rum_ham.iloc[i])
    return ascii_table

@bot.command(name='puts')
async def put_getter(ctx, ticka):
    data = ""
    try:
        data = yahoo.return_puts(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
            ascii_table = danny_divito(data, ticka)
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
    except:
      await ctx.send("There was an error please try again")
  

@bot.command(name='calls')
async def call_getter(ctx, ticka):
    data = ""
    try:
        data = yahoo.return_calls(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            data = data.drop(columns=['Contract Name', 'Last Trade Date', 'Change', 'Implied Volatility', '% Change', 'Open Interest'])
            ascii_table = danny_divito(data, ticka)
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
            data = data.reset_index()
            print(data)
            calls = yahoo.return_calls(tokens[1])
            calls = calls[['Contract Name', 'Strike']]
            offset = len(tokens[1]) # for indexing contract names for date
            calls['index'] = calls['Contract Name'].apply(lambda x: pd.to_datetime(x[4+offset:6+offset] + '-' + x[2+offset:4+offset] + '-' + x[offset:2+offset]))            
            print(calls)
            calls = calls.merge(data, how='left', on='index')
            calls = calls.dropna()
            calls['Safe'] = calls['Strike'] > calls['Upper']
            ascii_table = danny_divito(calls, tokens[1])
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
            return
        elif tokens[0] == 'put' or tokens[0] == 'puts':
            data = data[['MA','STD','Lower']]
    
    

    return
    
bot.run(TOKEN)
