#! /usr/bin/python3

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from joblib import load
import discord
from discord.ext import commands
import yahoo  # our other file
from dotenv import load_dotenv
import os
from prettytable import PrettyTable
import pandas as pd
import datetime as datetime
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='>')  # change character here

#####
# by default bot commands only accept one token, the first after the command
# can accept multiple tokens by using *args instead of ticka
# then query = " ".join(args[:]) >>> query = query.strip()


def danny_divito(rum_ham, ticka=None):
    ascii_table = PrettyTable()
    ascii_table.field_names = rum_ham.columns
    for i in range(len(rum_ham.index)):
        if i == 4 and ticka != None:
            ascii_table.add_row(["TICKA:", ticka.upper(
            ), "-", "-", "PRICE:", round(yahoo.price_cache[ticka], 4)])
        ascii_table.add_row(rum_ham.iloc[i])
    return ascii_table


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
            await ctx.send(f"```\n{ascii_table.get_string()}\n```")
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
        async with ctx.typing():
            data = yahoo.get_band(tokens[1], start_date=datetime.date.today(), band_age=20)
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


# load classifier once on launch
rf_classifier = load('models/rf_classifier.ai')


def get_prediction(strike, std, ma, adjclose):
    x = std/ma
    y = abs((adjclose/ma)-1)
    z = abs((strike/adjclose)-1)
    return int(rf_classifier.predict(np.array([x, y, z]).reshape(1, -1))[0])


@bot.command(name='classifier')
async def classifier_dumb(ctx, *args):
    tokens = args[:]
    if len(tokens) < 2:
        await ctx.send("funtionality is >classifier [call/put] [ticka]")
        return
    elif len(tokens) == 2:
        async with ctx.typing():
            data = yahoo.get_band(tokens[1], start_date=datetime.date.today(), band_age=20)

        if tokens[0] == 'call' or tokens[0] == 'calls':
            async with ctx.typing():
                calls = yahoo.return_calls(tokens[1])
                calls = calls[['Contract Name', 'Strike']]
                calls = calls.dropna()
                calls['Safe'] = calls['Strike'] > data['Upper'][0]
                for idx in calls.index:
                    strike = calls.loc[idx,'Strike']
                    std = data['STD'][0]
                    ma = data['MA'][0]
                    adjclose = data['adjclose'][0]
                    pred = get_prediction(strike, std, ma, adjclose)
                    calls.loc[idx, 'Prediction'] = pred
                ascii_table = danny_divito(calls)
                data = data.apply(lambda x: round(x, 4), axis=1)
                await ctx.send(f"```\n{ascii_table.get_string()}\n{danny_divito(data).get_string()}\n```")
                return


bot.run(TOKEN)
