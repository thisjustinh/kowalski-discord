from discord.ext import commands
from discord import File
import yfinance as yf
import io
import aiohttp

TOKEN = "NzQzOTkxMTgzMzgyMTUxMjQ4.XzctyA.-viZ2iJPZ2S5S1VM2tD4gfHXPuc"

bot = commands.Bot(command_prefix='$', description="Stock market analysis Discord bot")

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(name="stock", help="Get basic stock info for one ticker", cog='equities')
async def stock_ind(ctx, ticker: str):
  stock = yf.Ticker(ticker)

  try:
    info = stock.info
  except Exception:
    return await ctx.send("Stock ticker not recognized.")

  msg = [
    f"**{ info['longName']} | {info['regularMarketPrice']}**",
    f"*OHLC*: {info['open']} | {info['dayHigh']} | {info['dayLow']} | { info['previousClose'] }",
    f"*Basic Technicals* | EPS: {info['trailingEps']} | PE: {info['trailingPE']} | Beta: {info['beta']} | EV/EBITDA: {info['enterpriseToEbitda']}",
    f"*Basic Pric History* | 52-Week High: {info['fiftyTwoWeekHigh']} | 52-Week Low: {info['fiftyTwoWeekLow']} | 52-Week Change: {info['52WeekChange']}"
  ]

  await ctx.send('\n'.join(msg))

  if info['logo_url'] is not None:
    async with aiohttp.ClientSession() as session:
      async with session.get(info['logo_url']) as resp:
          data = io.BytesIO(await resp.read())
          await ctx.send(file=File(data, 'logo.png'))

  
@bot.command(name='info', help="Display the description for a certain business")
async def stock_desc(ctx, ticker: str):
  try: 
    await ctx.send(yf.Ticker(ticker).info['longBusinessSummary'])
  except Exception:
    await ctx.send("Stock ticker not recognized.")

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
    return await ctx.send("Stock ticker not recognized")

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
