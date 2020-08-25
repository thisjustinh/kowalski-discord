from datetime import datetime
from bs4 import BeautifulSoup
from requests import get
import pandas as pd

DEBUG = True

def yfin_bs4(ticker: str, tab=None):
    """
    BeautifulSoup gateway for Yahoo Finance requests.
    ticker = Requested stock/commodity/asset
    tab = Requested Yahoo Finance tab. Defaults to the main quote summary.
    """
    if tab is None:
        yfin = get(f'https://finance.yahoo.com/quote/{ticker}')
    else:
        yfin = get(f'https://finance.yahoo.com/quote/{ticker}/{tab}')
    if yfin.status_code != 200:
        raise ValueError("Ticker not recognized.")

    return BeautifulSoup(yfin.content, 'html.parser')

def get_historical_data(ticker: str, start, end):
    """
    Uses Yahoo Finance csv endpoint to get historical data.
    ticker: str = Requested stock/commodity/asset
    start: datetime = Start date for data
    end: datetime = End date for data. 
    """
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={int(start.timestamp())}&period2={int(end.timestamp())}&interval=1d&events=history'
    
    try:
        table = pd.read_csv(url)
    except:
        raise ValueError("Invalid parameters supplied. Check that ticker, start and end dates are correct.")
    return pd.read_csv(url)

def get_price(ticker: str):
    """
    Gets current price of requested ticker. Methods differ based on market hours.
    """
    yfin_soup = yfin_bs4(ticker)
    quotes = yfin_soup.find(id='quote-header-info')
    
    return quotes.find('span', class_=['Trsdu(0.3s)', 'Fw(b)', 'Fz(36px)', 'Mb(-4px)', 'D(ib)']).get_text()

def get_quote_summary(ticker: str):
    """
    Get basic summary information for requested ticker.
    """
    yfin_soup = yfin_bs4(ticker)
    summary = yfin_soup.find(id='quote-summary').find_all('td')
    summary = [td.get_text() for td in summary]
    
    quote_summary = {}
    for i in range(0, len(summary) - 1, 2):
        quote_summary[summary[i]] = summary[i + 1]
    return quote_summary

def get_statistics(ticker: str):
    """
    Get statistic numbers for stock
    """
    yfin_soup = yfin_bs4(ticker, tab='key-statistics')
    tables = yfin_soup.find_all('table', class_=['W(100%)', 'Bdcl(c)'])
    tdata = []
    
    for table in tables:
        tdata.append([td.get_text() for td in table.find_all('td')])
    
    statistics = {}
    titles = ['valuation', 'price_history', 'share_statistics', 'dividends_splits', 'fiscal_year', 'profitability', 'management', 'is', 'bs', 'cfs']
    # Design valuation table (only keep current values)
    valuation_td = tdata[0]
    valuation = {}
    for i in range(len(valuation_td)):
        entry = valuation_td[i]
        if not is_float(entry[:-1]):
            # clean up superscripts
            if entry[-1].isdecimal():
                entry = entry[:-2]
            valuation[entry] = valuation_td[i + 1]
    statistics[titles[0]] = valuation

    # Add the other tables
    table = {}
    for i in range(1, len(tdata)):
        tdatum = tdata[i]
        for j in range(0, len(tdatum) - 1, 2):
            # Clean up superscripts
            entry = tdatum[j]
            if entry[-1].isdecimal():
                entry = entry[:-2]
            table[entry] = tdatum[j + 1]
        statistics[titles[i]] = table
        table = {}

    return statistics

def get_profile(ticker: str):
    """
    Gets profile information for the requested ticker.
    """
    yfin_soup = yfin_bs4(ticker, tab='profile')
    profile = {}
    asset_keys = ['sector', 'industry', 'employees']

    overview = yfin_soup.find(class_='asset-profile-container')
    profile['name'] = overview.find('h3').get_text()

    contact = overview.find('p').find_all('a')
    profile['phone'] = contact[0].get_text()
    profile['website'] = contact[1].get_text()

    asset_profile = overview.find_all('p')[1].find_all('span')
    asset_profile = [p.get_text() for p in asset_profile]

    for i in range(0, len(asset_profile) - 1, 2):
        profile[asset_keys[i // 2]] = asset_profile[i + 1]

    profile['desc'] = yfin_soup.find(class_='quote-sub-section').find('p').get_text()

    return profile

########### Helper Functions ###########

def is_float(x: str):
    try:
        float(x)
        return True
    except ValueError:
        return False

def make_table(d: dict, title: str):
    return pd.DataFrame(
        data={f"{title}": list(d.values())},
        index=list(d.keys())
    )

if __name__ == '__main__' and DEBUG:
    ticker = 'tsla'
    print(get_statistics(ticker))
