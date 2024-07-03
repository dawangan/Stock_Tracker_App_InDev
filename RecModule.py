#GetInitialCategories
import json
import yfinance as yf 
import pandas as pd
import numpy as np
import scipy.spatial.distance
from scipy.stats import pearsonr
import robin_stocks as rh
need_download = False

def download_1y_data(ticker):
    data = yf.download(ticker, period="1y", interval="1d")
    return pd.DataFrame(data)
#TODO:
def return_my_assets(): 
    rh.robinhood.login('YOUREMAIL', 'YOURPASSWORD')
    my_stocks = rh.robinhood.account.build_holdings()
    stock_symbols = list(my_stocks.keys())
    return stock_symbols
def fetch_stock_info(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info


def update_stock_info():
    file_path = 'company_tickers_mod.json'
    stocks_info = []
    with open(file_path, 'r') as file:
        data = json.load(file)

    for i in data:
        ticker = data[i]["ticker"]
        info = fetch_stock_info(ticker)
        if info is not None:
            stock_data = {'Ticker': ticker}
            columns = ['open', 'dayLow', 'dayHigh', 'dividendRate', 'dividendYield', 'beta',
                'trailingPE', 'forwardPE', 'volume', 'fiftyDayAverage', 'twoHundredDayAverage',
                'priceToBook', 'trailingEps', 'forwardEps', 'pegRatio', 'ebitda']
            for field in columns:
                stock_data[field] = info.get(field, 'N/A')  # Use 'N/A' if the field is missing
            stocks_info.append(stock_data)
        else:
            stocks_info.append({'Ticker': ticker, 'currentPrice': 'N/A', 'marketCap': 'N/A', 'volume': 'N/A', 'trailingPE': 'N/A', 'pegRatio': 'N/A'})

    df = pd.DataFrame(stocks_info)
    df.to_excel('stocks_info.xlsx', index=False)
    
#math suite 
def normalize_data(df): 
    df1 = df/df.mean(axis='index')
    return df1
def cosine_similarity_function(d1, d2): 
    dot_product = np.dot(d1, d2)
    norm_d1 = np.linalg.norm(d1)
    norm_d2 = np.linalg.norm(d2)
    if norm_d1 == 0 or norm_d2 == 0:
        return -999999999999  
    return dot_product / (norm_d1 * norm_d2)
def manhattan_distance(d1, d2):
    return np.sum(np.abs(d1 - d2))
def pearson_correlation(d1, d2):
    if len(d1) != len(d2):
        raise ValueError("Input arrays must have the same length")
    if np.all(d1 == 0) or np.all(d2 == 0):
        return 0 
    corr, _ = pearsonr(d1, d2)
    return corr
def jaccard_similarity(d1,d2): 
    if len(d1) != len(d2):
        raise ValueError("Input arrays must have the same length")
    return 1-scipy.spatial.distance.jaccard(d1,d2)
def hamming_distance(d1,d2): 
    return scipy.spatial.distance.hamming(d1,d2) 
def minkowski_distance(d1,d2): 
    return scipy.spatial.distance.minkowski(d1,d2, p = 2)
def chebyshev_distance(d1, d2):
    return scipy.spatial.distance.chebyshev(d1, d2)
def spearman_correlation(d1, d2):
    return scipy.spatial.distance.spearmanr(d1, d2)[0]
def kl(d1,d2): 
    d1 = d1+1e-10
    d2 = d2+1e-10
    return np.sum(d1*np.log(d1/d2))
def canberra_distance(d1, d2):
    return np.sum(np.abs(d1 - d2) / (np.abs(d1) + np.abs(d2)))
def bray_curtis_dissimilarity(d1, d2):
    return np.sum(np.abs(d1 - d2)) / np.sum(d1 + d2)


def create_similar(Ticker, all_stock_data):
    new_cat = Ticker + 'Similarity'
    selected_row = all_stock_data.loc[all_stock_data['Ticker'] == Ticker].iloc[0]
    
    numeric_columns = all_stock_data.select_dtypes(include=[np.number]).columns
    #accesses all numeric columns names

    selected_data = selected_row[numeric_columns].values
    #accesses the ticker row's data 

    for index, row in all_stock_data.iterrows():
        row_data = row[numeric_columns].values
        similarity_val = (cosine_similarity_function(selected_data, row_data) +
                          manhattan_distance(selected_data, row_data)) * pearson_correlation(selected_data, row_data)
        all_stock_data.at[index, new_cat] = similarity_val
 
    sorted_data = all_stock_data.sort_values(by=new_cat, ascending=False)
    top_5 = sorted_data.head()
    top_5_tickers = top_5['Ticker'].tolist()
    similarity_scores = top_5[new_cat].tolist()
    print(similarity_scores)
    return top_5_tickers

def prep_data():

    my_assets = return_my_assets()
    all_stock_data = pd.read_excel('stocks_info.xlsx')
    #edge case testing:
    all_stock_data.loc[all_stock_data['Ticker'] == 'GOOGL', 'Ticker'] = 'GOOG'
    all_stock_data.replace(['N/A', pd.NA, np.nan, np.inf, -np.inf], 0, inplace=True)

    one_year_data = pd.read_csv('out.csv', index_col=0, parse_dates=True)
    one_year_data = pd.DataFrame(one_year_data)
    
    for i in my_assets:
        data = yf.download(i, period="1y", interval="1d")
        data = pd.DataFrame(data)
        data.index = pd.to_datetime(data.index)
        data.sort_index(inplace=True)
        one_year_data = one_year_data.reindex(data.index)
        one_year_data[i] = data['Close']      
    my_asset_DataFrame = all_stock_data[all_stock_data['Ticker'].isin(my_assets)]
    similar_stocks = {}

    for ticker in my_asset_DataFrame['Ticker']:
        similar_stocks[ticker] = create_similar(Ticker=ticker, all_stock_data=all_stock_data)
        for similar_ticker in similar_stocks[ticker]:
            if similar_ticker not in one_year_data.columns:
                data = yf.download(similar_ticker, period="1y", interval="1d")
                data = pd.DataFrame(data)
                data.index = pd.to_datetime(data.index)
                data.sort_index(inplace=True)
                one_year_data = one_year_data.reindex(data.index)
                one_year_data[similar_ticker] = data['Close']
            
    one_year_data.dropna(how='all', inplace=True)  
    one_year_data.fillna(method='ffill', inplace=True)
    one_year_data.fillna(method='bfill', inplace=True)
    one_year_data.to_csv('out.csv', index=True)   
    return similar_stocks    


def the_whole_shabang(): 
    a = prep_data()
    print(a)


the_whole_shabang()
