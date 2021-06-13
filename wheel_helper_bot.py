#! /usr/bin/python3

import discord
from discord.ext import commands
import yahoo  # our other file
from dotenv import load_dotenv
import os
from prettytable import PrettyTable
import pandas as pd
import datetime as datetime
import csv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>')  # change character here

#####
# by default bot commands only accept one token, the first after the command
# can accept multiple tokens by using *args instead of ticka
# then query = " ".join(args[:]) >>> query = query.strip()
"""
weekly_stinks = []
with open('weekly_stonks.csv', 'r') as f: 
    read_deez_nutz = csv.reader(f)
    for row in read_deez_nutz:
        if row[0] == 'ticka':
            continue
        weekly_stinks.append(row[0])
"""


def danny_divito(rum_ham, ticka=None):
    ascii_table = PrettyTable()
    ascii_table.field_names = rum_ham.columns
    for i in range(len(rum_ham.index)):
        if i == 4 and ticka != None:
            ascii_table.add_row(["TICKA:", ticka.upper(
            ), "-", "-", "PRICE:", round(yahoo.price_cache[ticka], 4)])
        ascii_table.add_row(rum_ham.iloc[i])
    return ascii_table


@bot.command(name="safe")
async def safe_getter(ctx, *args):
    tokens = args[:]
    if len(tokens) != 2:
        await ctx.send("funtionality is >safe [call/put] [ticka]")
        return
    else:
        try:
            async with ctx.typing():
                data = yahoo.get_todays_safe_options(
                    tokens[1], option=tokens[0])
                ascii_table = danny_divito(data)
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
        except:
            await ctx.send("There was an error please try again")


@bot.command(name='puts')
async def put_getter(ctx, ticka):
    data = ""
    try:
        async with ctx.typing():
            data = yahoo.return_puts(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            async with ctx.typing():
                data = data.drop(columns=['Contract Name', 'Last Trade Date',
                                          'Change', 'Implied Volatility', '% Change', 'Open Interest'])
                ascii_table = danny_divito(data, ticka)
            await ctx.send(f"```\n{ascii_table.get_string()}\n{yahoo.stock_expiry_cache[ticka]}\n```")
    except:
        await ctx.send("There was an error please try again")


@bot.command(name='calls')
async def call_getter(ctx, ticka):
    data = ""
    try:
        async with ctx.typing():
            data = yahoo.return_calls(ticka)
        if len(data) == 0:
            await ctx.send(f"```\nThere was no weekly options chain for the ticka {ticka}\n```")
        else:
            async with ctx.typing():
                data = data.drop(columns=['Contract Name', 'Last Trade Date',
                                          'Change', 'Implied Volatility', '% Change', 'Open Interest'])
                ascii_table = danny_divito(data, ticka)
            await ctx.send(f"```\n{ascii_table.get_string()}\n{yahoo.stock_expiry_cache[ticka]}\n```")
    except:
        await ctx.send("There was an error please try again")


@bot.command(name="meme")
async def get_memes(ctx, *args):
    try:
        async with ctx.typing():
            tokens = args[:]
            if len(tokens) == 0:
                ascii_table = PrettyTable()
                ascii_table.field_names = [
                    'Ticka', "Opening Price", "Current Price", "Change", "Percent Change"]
                ascii_table.add_rows(yahoo.get_memes())
                await ctx.send(f"```\n {ascii_table.get_string()}```\n")
            elif len(tokens) == 2:
                if tokens[0].lower() == "add":
                    yahoo.add_meme(tokens[1].upper())
                    await ctx.send("added")
                elif tokens[0].lower() == "remove" or tokens[0] == "delete":
                    yahoo.remove_meme(tokens[1].upper())
                    await ctx.send("removed")
            else:
                await ctx.send("I don't know how to do that", args, tokens)
        return
    except:
        await ctx.send("something went very very wrong", [args[:]])


@bot.command(name="memes")
async def get_memes(ctx):
    ascii_table = PrettyTable()
    ascii_table.field_names = ['Ticka', "Opening Price",
                               "Current Price", "Change", "Percent Change"]
    ascii_table.add_rows(yahoo.get_memes())
    await ctx.send(f"```\n {ascii_table.get_string()}```\n")


@bot.command(name="vix")
async def vix_up(ctx, *args):
    try:
        async with ctx.typing():
            tokens = args[:]
            if len(tokens) == 0:
                await ctx.send(f"```\n {yahoo.check_vxx()}```\n")
            elif len(tokens) == 2:
                if tokens[0].lower() == "up":
                    await ctx.send(f"```\n {yahoo.get_vxx(up=True)}```\n")
                elif tokens[0].lower() == "down":
                    await ctx.send(f"```\n {yahoo.get_vxx(up=False)}```\n")
            else:
                await ctx.send("I don't know how to do that", args, tokens)
        return
    except:
        await ctx.send("something went very very wrong", [args[:]])


@bot.command(name='bands')
async def safe_contracts(ctx, *args):
    tokens = args[:]
    if len(tokens) < 2:
        await ctx.send("functionality is >bands [call/put] [ticka]")
        return
    elif len(tokens) == 2:
        async with ctx.typing():
            data = yahoo.get_band(
                tokens[1], start_date=datetime.date.today(), band_age=20)
        if tokens[0] == 'call' or tokens[0] == 'calls':
            async with ctx.typing():
                calls = yahoo.return_calls(tokens[1])
                calls = calls[['Contract Name', 'Strike']]
                calls = calls.dropna()
                calls['Safe'] = calls['Strike'] > data['Upper'][0]
                ascii_table = danny_divito(calls)
                data = data.apply(lambda x: round(x, 4), axis=1)
            await ctx.send(f"```\n{ascii_table.get_string()}\n{danny_divito(data).get_string()}\n```")
            return
        elif tokens[0] == 'put' or tokens[0] == 'puts':
            async with ctx.typing():
                puts = yahoo.return_puts(tokens[1])
                puts = puts[['Contract Name', 'Strike']]
                puts = puts.dropna()
                puts['Safe'] = puts['Strike'] < data['Lower'][0]
                ascii_table = danny_divito(puts)
                data = data.apply(lambda x: round(x, 4), axis=1)
            await ctx.send(f"```\n{ascii_table.get_string()}\n{danny_divito(data).get_string()}\n```")
            return
    await ctx.send("borked")
    return

####
# the below MUST be run in conjuction with the IV scraper, located in the other repo
# that lil dude will check the puts of all weeklies on a strict schedule, and output the current highest IV
#    to a file, wich is read here
####
# using the static weekly stinks
# runtime too long
"""
@bot.command(name='high-v')
async def read_iv(ctx):
    async with ctx.typing():
        chains = [yahoo.check_iv(ticka) for ticka in weekly_stinks]
        chains = [chain for chain in chains if isinstance(chain, pd.DataFrame)]
        to_concat = [chain for chain in chains if not chain.empty]
    if not to_concat:
        await ctx.send('Sorry bud, none this time')
        return
    all_options = pd.concat(to_concat, ignore_index=True)
    
    message = danny_divito(all_options)
    dropped_counter = 0
    message = message + f'\nDropped {dropped_counter} records.'
    async with ctx.typing():
        while len(message) > 2000:
            all_options = all_options[:-1]
            message = danny_divito(all_options)
            message = message + f'\nDropped {dropped_counter} records.'
    await ctx.send(message)
    return
"""
bot.run(TOKEN)
