from discord.ext import commands
from discord import File
import yfinance as yf
import yahoo
import io
import aiohttp


TOKEN = "TOKEN_GOES_HERE"
bot = commands.Bot(command_prefix='$', description="Stock market analysis Discord bot")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(name="overview", help="Get basic stock info for one ticker", cog='equities')
async def stock_overview(ctx, ticker: str):
    try:
        profile = yahoo.get_profile(ticker)
        summary = yahoo.get_quote_summary(ticker)
        price = yahoo.get_price(ticker)
    except Exception:
        return await ctx.send("Stock ticker not recognized.")

    # the problem child
    day_range = summary['Day\'s Range']
    msg = [
            f"**{profile['name']} | {price}**",
            f"*Open*: {summary['Open']} | Day\'s Range: {day_range} | Previous Close: {summary['Previous Close']} | Volume: {summary['Volume']}",
            f"*EPS*: {summary['EPS (TTM)']} | *PE*: {summary['PE Ratio (TTM)']} | *Beta*: {summary['Beta (5Y Monthly)']}"]

    await ctx.send('\n'.join(msg))


@bot.command(name='info', help="Display the description for a certain business")
async def stock_desc(ctx, ticker: str):
    try:
        profile = yahoo.get_profile(ticker)
    except ValueError:
        return await ctx.send("Stock ticker not recognized.")

    try:
        result = [
                f"**{profile['name']}** | {profile['phone']} | {profile['website']}",
                f"*Sector*: {profile['sector']}",
                f"*Industry*: {profile['industry']}",
                f"*Full Time Employees*: {profile['employees']}",
                f"{profile['desc']}"
                ]
    except KeyError:
        return ctx.send("Something seems to be wrong with the API.")

    await ctx.send('\n'.join(result))

    logo_url = f"https://logo.clearbit.com/{profile['website'][11:]}"
    async with aiohttp.ClientSession() as session:
        async with session.get(logo_url) as resp:
            data = io.BytesIO(await resp.read())
        await ctx.send(file=File(data, 'logo.png'))



@bot.command(name='recommend', help="Show professional firms' opinions on stocks")
async def stock_recs(ctx, ticker: str):
    try:
        return await ctx.send(f"```\n{yf.Ticker(ticker).recommendations.tail().to_string()}\n```")
    except Exception:
        return await ctx.send("Stock ticker not recognized.")


@bot.command(name='calendar', help="Display upcoming events (quarterly reports) for a certain stock")
async def stock_calendar(ctx, ticker: str):
    try:
        return await ctx.send(f"```\n{yf.Ticker(ticker).calendar}\n```")
    except Exception:
        return await ctx.send("Stock ticker not recognized.")

@bot.command(name='financials', help="Display brief overview of financial statements from last quarter")
async def financial_overview(ctx, ticker: str):
    try:
        stats = yahoo.get_statistics(ticker)
    except ValueError:
        return await ctx.send("Stock ticker not recognized.")
    
    result = [f"```\n{yahoo.make_table(stats['is'], 'Income Statement').to_string()}\n```",
              f"```\n{yahoo.make_table(stats['bs'], 'Balance Sheet').to_string()}\n```",
              f"```\n{yahoo.make_table(stats['cfs'], 'Cash Flow Statement').to_string()}\n```"]
    
    return await ctx.send('\n'.join(result))


@bot.command(name='valuation', help="Display valuation indicators for a certain stock")
async def valuation(ctx, ticker: str):
    try:
        value = yahoo.get_statistics(ticker)['valuation']
    except ValueError:
        return await ctx.send("Stock ticker not recognized.")

    return await ctx.send(f"```\n{yahoo.make_table(value, 'Valuation').to_string()}\n```")


@bot.command(name='ph', help="Display price history for a certain stock")
async def price_history(ctx, ticker: str):
    try:
        history = yahoo.get_statistics(ticker)['price_history']
    except ValueError:
        return await ctx.send("Stock ticker not recognized.")

    return await ctx.send(f"```\n{yahoo.make_table(history, 'Price History').to_string()}\n```")


@bot.command(name='crypto', help="Get basic cryptocurrency information for a certain crypto")
async def crypto(ctx, name: str):
    if name.lower() == 'bitcoin' or name.lower() == 'btc':
        cc = yf.Ticker('btc-usd')
    elif name.lower() == 'ethereum' or name.lower() == 'ether':
        cc = yf.Ticker('eth-usd')
    else:
        cc = yf.Ticker(name)

    try:
        info = cc.info
    except Exception:
        return await ctx.send('Crypto name not recognized (for vague ones used their Yahoo abbrieviations)')

    msg = [
            f"**{info['name']} | {info['regularMarketPrice']}**",
            f"*OHLC* | {info['open']} | {info['dayHigh']} | {info['dayLow']} | {info['previousClose']}",
            f"*Basic Price History* | 52-Week High: {info['fiftyTwoWeekHigh']} | 52-Week Low: {info['fiftyTwoWeekLow']}"
            ]

    return await ctx.send('\n'.join(msg))


bot.run(TOKEN)
