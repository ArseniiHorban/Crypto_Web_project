import pandas as pd
from utils import Utils
from historical_data_controller import HistoricalDataController


class Portfolio:
    def __init__(self, assets_with_weights, initial_investment = 10000, period=365):
        """
        assets with weights is a dictionary of shape
        {
        asset : weight,
        asset : weight,
        asset : weight
        }
        weights are in percents
        assets are symbols BTC, ETH etc.
        period is a period of time portfolio is held for, in days
        """
        total_weight = sum(assets_with_weights.values())
        if total_weight != 100:
            raise ValueError("Total weights must sum to 100.")
        
        self.assets_with_weights = assets_with_weights
        self.df = pd.DataFrame()
        self.initial_investment = initial_investment
        self.period = period

        self.utils = Utils()
        self.historical_data = HistoricalDataController()
        

    def load_prices(self, prices, coin):
        """
        prices is a dictionary is a shape 
        {
        date : price
        }
        coin is a coin symbol BTC, ETH etc.
        """
        
        if not self.utils.is_valid_coin(coin):
            raise ValueError("Cannot load prices for an invalid coin.")

        price_series = pd.Series(prices, name=coin)
        price_series.index = pd.to_datetime(price_series.index)
        
        # If df is empty, initialize with this coin's prices and set dates as the index
        if self.df.empty:
            self.df = price_series.to_frame()
        else:
            # Align with the existing DataFrame index (date alignment)
            self.df = pd.concat([self.df, price_series], axis=1)


    def calculate_portfolio_value(self):
        # Step 1: Calculate the amount of money allocated to each asset
        allocation = {
            coin: (self.initial_investment * weight / 100) 
            for coin, weight in self.assets_with_weights.items()
        }
        
        # Step 2: Calculate the number of units bought for each asset at the first available price
        units = {}
        for coin in self.assets_with_weights:
            first_price = self.df[coin].iloc[0]
            units[coin] = allocation[coin] / first_price

        # Step 3: Calculate the total value of the portfolio at each date
        portfolio_values = []
        for row in self.df.itertuples(index=False):
            total_value = sum(getattr(row, coin) * units[coin] for coin in self.assets_with_weights)
            portfolio_values.append(total_value)

        # Step 4: Create a DataFrame with the calculated portfolio values
        portfolio_df = pd.DataFrame({"Portfolio Value": portfolio_values}, index=self.df.index)
        
        return portfolio_df

    def calculate_volatility(self, df):
    # Calculate daily returns
        daily_returns = df['Portfolio Value'].pct_change().dropna()
        
        # Calculate daily volatility (standard deviation)
        daily_volatility = daily_returns.std()
        
        # Annualize volatility
        annual_volatility = daily_volatility * (365** 0.5)
        
        return annual_volatility
    

    def calculate_daily_returns(self, df):
        # Calculate the daily returns and add as a new column
        df['Daily Return'] = df['Portfolio Value'].pct_change()
        
        return df
    
    def calculate_monthly_returns(self, df):
        # Resample the data to monthly frequency (taking the last value for each month)
        df_monthly = df.resample('ME').last()

        # Calculate monthly returns and add as a new column
        df_monthly['Monthly Return'] = df_monthly['Portfolio Value'].pct_change()
        if 'Portfolio Value' in df_monthly.columns:
            df_monthly = df_monthly.drop(['Portfolio Value'], axis=1)

        if 'Daily Return' in df_monthly.columns:
            df_monthly = df_monthly.drop(['Daily Return'], axis=1)
        return df_monthly

    def calculate_sharpe_ratio(self, df, risk_free_rate=0.0):
        """
        Calculate the Sharpe Ratio to measure risk-adjusted returns.
        """
        daily_returns = df['Daily Return'].dropna()
        excess_returns = daily_returns - (risk_free_rate / self.period)
        sharpe_ratio = (excess_returns.mean() / daily_returns.std()) * (self.period ** 0.5)
        return sharpe_ratio

    def calculate_max_drawdown(self, df):
        """
        Calculate the Maximum Drawdown of the portfolio.
        """
        cumulative_max = df['Portfolio Value'].cummax()
        drawdown = (df['Portfolio Value'] - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        return max_drawdown
    
    def transform_df(self, df, columns):
        # Replace NaNs with 0
        df = df.fillna(0)

        for column in columns:
            # For each value in the column:
            # - First, convert it to a float (a number with a decimal point)
            # - Then, round the number to the specified decimal places
            for i in range(len(df[column])):
                # Convert the value to a float and round it to the required decimal places
                # df[column].iloc[i] = round(float(df[column].iloc[i]), 4)    # This one throws a warning that it might get disabled in next updates
                df.iloc[i, df.columns.get_loc(column)] = round(float(df.iloc[i, df.columns.get_loc(column)]), 4)

        
        return df

    def analyze(self):
        coins = list(self.assets_with_weights.keys())
        data = self.historical_data.process_historical_data_call(coins)

        for coin, data in data.items():
        # Create a dictionary where each date is a key and price is the value
            prices = {entry['date']: float(entry['price'].replace('$', '').strip()) for entry in data['data']}
            self.load_prices(prices, coin)
            print(prices)

        print(self.df)
        portfolio_value_df = self.calculate_portfolio_value()
        annual_volatility = float(portfolio.calculate_volatility(portfolio_value_df))
        portfolio_value_df = portfolio.calculate_daily_returns(portfolio_value_df)
        monthly_returns_df = portfolio.calculate_monthly_returns(portfolio_value_df).dropna()
        columns = ['Monthly Return']
        monthly_returns_df = self.transform_df(monthly_returns_df, columns)
        sharpe_ratio = float(self.calculate_sharpe_ratio(portfolio_value_df))
        max_drawdown = float(self.calculate_max_drawdown(portfolio_value_df))
        columns = ['Portfolio Value', 'Daily Return']
        portfolio_value_df = self.transform_df(portfolio_value_df,columns)

        portfolio_value_dict = {date.strftime('%Y-%m-%d'): value for date, value in zip(portfolio_value_df.index, portfolio_value_df['Portfolio Value'])}
        daily_returns_dict = {date.strftime('%Y-%m-%d'): value for date, value in zip(portfolio_value_df.index, portfolio_value_df['Daily Return'])}
        monthly_returns_dict = {date.strftime('%Y-%m-%d'): value for date, value in zip(monthly_returns_df.index, monthly_returns_df['Monthly Return'])}
        print(monthly_returns_dict)

        portfolio_analysis = {
        "data": {
            "assets": self.assets_with_weights, 
            "initial_investment": self.initial_investment,
            "period": self.period,
        },
        "performance": {
            "annual_volatility": annual_volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
        },
        "portfolio_value": portfolio_value_dict,
        "daily_returns": daily_returns_dict,
        "monthly_returns": monthly_returns_dict
        }
        return portfolio_analysis



# assets = {"BTC": 60, "ETH": 40}

# Create portfolio
# portfolio = Portfolio(assets)


# analysis = portfolio.analyze()
# print(analysis)