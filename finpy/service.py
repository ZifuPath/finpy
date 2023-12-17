from constants import OPTION_CHAIN_URL,CLOUD_HEADER,HEADERS,BASE_URL
from model import ChainData, CandleInput, EquityData
import requests
import json
import os
import urllib.parse
import pandas as pd
import datetime

class FINPY:
    """
    A Python package for financial data analysis and fetching using NSE APIs.

    Args:
        cloud (bool): Set to True if using the cloud version of NSE API.

    Attributes:
        cloud (bool): Indicates whether the cloud version of NSE API is used.

    Methods:
        generate_session(): Generates and returns a session for making API requests.
        get_response(data): Sends an API request and returns the response data.
        modify_symbol(symbol): Modifies the symbol to handle special characters.
        option_chain(symbol): Retrieves option chain data for a given symbol.
        option_chain_data_prep(response, df): Prepares option chain data for analysis.
        get_equity_list(): Retrieves the list of equities from NSE.
        search_symbol(symbol): Checks if a symbol is valid and exists in the NSE equity list.
        get_candle_data(symbol, start_date, end_date): Retrieves candlestick data for a given symbol and date range.
        get_data(symbol, start_date, end_date): Retrieves historical equity data for a given symbol and date range.
        get_equity_data(kwargs): Retrieves and concatenates equity data for a given symbol and date range.
    """

    def __init__(self, cloud: bool = False):
        """
        Initializes the FINPY object.
        Args:
        :param cloud (bool): Set to True if using the cloud version of NSE API.
        """
        if isinstance(cloud, bool):
            self.cloud = cloud
        else:
            raise ValueError('Incorrect Type Error')

    def generate_session(self):
        """
        Generates and returns a session for making API requests.
        :return  requests.Session: A session object for making HTTP requests.
        """
        session = requests.session()
        session.get(url=BASE_URL, headers=HEADERS)
        return session

    def get_response(self, data: str) -> json:
        """
        Sends an API request and returns the response data.
        :param data :str: The URL or data for the API request.
        :return dict: The response data in JSON format.
        """
        try:
            if self.cloud:
                if (("%26" in data) or ("%20" in data)):
                    ENCODED_URL = data
                else:
                    ENCODED_URL = urllib.parse.quote(data, safe=':/?&=')
                payload_var = 'curl -b cookies.txt "' + ENCODED_URL + '"' + CLOUD_HEADER + ''
                try:
                    response = os.popen(payload_var).read()
                    response = json.loads(response)
                except ValueError:
                    output2 = os.popen('curl -c cookies.txt "' + BASE_URL + '"' + CLOUD_HEADER + '').read()
                    response = os.popen(payload_var).read()
                    response = json.loads(response)
            else:
                session = self.generate_session()
                response = session.get(data, headers=HEADERS).json()
            return response
        except BaseException as e:
            raise ValueError(f'Error in Fetching Data : Reason : {e}')

    @staticmethod
    def modify_symbol(symbol:str) -> str:
        """
        Converts symbol if & is present e.g. M&M - M%26M
        :param symbol:
        :return: symbol (str)
        """
        return symbol.replace('&', '%26')

    def option_chain(self, symbol: str) ->pd.DataFrame:
        """
        Get the Option Chain Data
        :type symbol: str
        :return df: pd.DataFrame | None
        """
        symbol = self.modify_symbol(symbol)
        URL = OPTION_CHAIN_URL + symbol
        response = self.get_response(URL)
        try:
            option_data = ChainData(response=response['filtered']['data'])
            df = pd.json_normalize(option_data.model_dump()['response'])
            df = self.option_chain_data_prep(response, df)
            return df
        except BaseException as e:
            print('Not able to Fetch Correct Data')
            return None

    @staticmethod
    def option_chain_data_prep(response: dict, df) -> pd.DataFrame:
        """
        Prepare data for the option chain
        :type response: json
        :return df: pd.DataFrame
        """
        df['PE.sum'] = df['PE.openInterest'].sum()
        df['CE.sum'] = df['CE.openInterest'].sum()
        df['PCR'] = df['PE.sum'] / df['CE.sum']
        df['datetime'] = response['records']['timestamp']
        df['underlying'] = float(response['records']['underlyingValue'])
        df = df.sort_values(by='strikePrice')
        return df.reset_index(drop=True)

    @staticmethod
    def get_equity_list() -> list:
        """
        Get the equity symbols from nse archives
        :return equity symbol list: list
        """
        eq_list_pd = pd.read_csv('https://archives.nseindia.com/content/equities/EQUITY_L.csv')
        eq_list_pd.columns = eq_list_pd.columns.str.strip()
        eq_list_pd = eq_list_pd[eq_list_pd.SERIES == "EQ"]
        eq_list_pd['DATE OF LISTING'] = eq_list_pd['DATE OF LISTING'].apply(
            lambda x: datetime.datetime.strptime(x, '%d-%b-%Y'))
        return eq_list_pd['SYMBOL'].tolist()

    def search_symbol(self, symbol: str) -> str:
        """
        Search the equity Symbol
        :param symbol: str
        :return symbol or raise Error
        """
        symbol_list = self.get_equity_list()
        if symbol in symbol_list:
            return symbol
        else:
            raise ValueError('Symbol is  Incorrect')

    def get_candle_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get the Historical Data
        :param symbol: equity symbol
        :param start_date: date format "%d-%m-%Y" in string
        :param end_date: date format "%d-%m-%Y" in string
        :return: dataframe with ohlc data
        """
        candle_input = CandleInput(symbol=symbol, start_date=start_date, end_date=end_date)
        candle_input = candle_input.model_dump()
        symbol = self.search_symbol(candle_input['symbol'])
        candle_input['symbol'] = self.modify_symbol(symbol)
        df = self.get_equity_data(candle_input)
        return df

    def get_data(self, symbol, start_date, end_date):
        URL = f"{BASE_URL}/api/historical/cm/equity?symbol={symbol}&from={start_date}&to={end_date}"
        response = self.get_response(URL)
        if 'data' in response:
            response = EquityData(response=response['data'])
            df = pd.json_normalize(response.model_dump()['response'])
            return df
        else:
            raise ValueError('No Data Found')

    def get_equity_data(self, kwargs:dict) -> pd.DataFrame:
        """
        Performs Operation to Get Historical data
        :type kwargs: dict
        :return dataframe
        """
        symbol = kwargs['symbol']
        start_date = datetime.datetime.strptime(kwargs['start_date'], "%d-%m-%Y")
        end_date = datetime.datetime.strptime(kwargs['end_date'], "%d-%m-%Y")
        diff = end_date - start_date
        diff_days = int(diff.days / 40)
        temp_dates = [(start_date + datetime.timedelta(days=(40 * (i + 1)))) for i in range(diff_days)]
        start_dates = [(start_date + datetime.timedelta(days=(40 * i))) for i in range(diff_days)]
        total = [self.get_data(symbol, datetime.datetime.strftime(start_d, "%d-%m-%Y"),
                               datetime.datetime.strftime(temp_d, "%d-%m-%Y"))
                 for start_d, temp_d in zip(start_dates, temp_dates)]
        start_date = temp_dates[-1] if len(temp_dates) > 0 else start_date
        total.append(self.get_data(symbol,
                                   datetime.datetime.strftime(start_date, "%d-%m-%Y"),
                                   datetime.datetime.strftime(end_date, "%d-%m-%Y")))
        data = pd.concat(total, ignore_index=True)
        data['datetime'] = pd.to_datetime(data['datetime'])
        data = data.sort_values(by='datetime')
        return data.reset_index(drop=True)


if __name__ == '__main__':
    fin = FINPY()
    # symbol = "INFY"
    # start_date = "01-01-2021"
    # end_date = "30-01-2021"
    # df = fin.get_candle_data(symbol=symbol,start_date=start_date,end_date=end_date)
    # print(df.head())
    df = fin.option_chain('FINNIFTY')
    print(df.head())
