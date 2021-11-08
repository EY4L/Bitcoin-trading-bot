import gym
from gym import spaces
import pandas as pd
import numpy as np
import random
import gym
from gym import spaces
import pandas as pd
import numpy as np
import random
class trading_env(gym.Env):
    """Single Stock Trading Environment"""
    def __init__(self,df, init_capital=10000):
        #instance attributes
        self.df = df
        self.initial_capital = init_capital
        self.current_step = None
        #Porfolio Information
        self.no_stocks_bought = None
        self.no_stocks_sold = None
        self.portfolio_value = None
        self.current_stocks_held = None
        self.current_capital = None
        self.avg_cost = None
        self.buy_cost = None
        self.returns = None
        self.max_steps = None
        self.previous_portfolio_value = None
    
        #Values for normalising data
        self.max_stock_price = max(self.df["Close"])
        self.max_volume = max(self.df["Volume_(BTC)"])
        self.max_capital = 1000000
        self.max_no_shares = 10000
    
    

    
    
    def observation(self):
        obs = np.array([self.df.loc[self.current_step,"3D_return_norm"], self.df.loc[self.current_step,"MACD_status"],self.df.loc[self.current_step,"RSI_status"],self.df.loc[self.current_step,"EMA_status"]])
        
        return obs
    
    def step(self,a):
        self.action(a)
        self.current_step += 1
        
        if self.current_step > len(self.df.loc[:,"Open"].values):
            self.current_step = 0 # Sanity check ensuring that current step isn't greater than 6 steps ahead
        
        delay = self.current_step/self.max_steps
        
        reward = (self.portfolio_value-self.previous_portfolio_value)/self.previous_portfolio_value
        
        if self.current_step == len(self.df):
            self.done = True
        elif self.portfolio_value == 0:
            self.done = True
        
        obs = self.observation()
        
        return obs,float(reward), self.done
        
    def action(self,a):
        self.amount = 0
        current_price = random.uniform(self.df.loc[self.current_step,"Open"],self.df.loc[self.current_step,"Close"])
        #Buy at the low and sell high
        if self.df.loc[self.current_step,"3D_return"] < -0.19:
            self.amount = random.uniform(0.3,0.5)
        elif (self.df.loc[self.current_step,"3D_return"] > -0.19) & (self.df.loc[self.current_step,"3D_return"]<-0.02):
            self.amount = random.uniform(0.1,0.3)
        elif self.df.loc[self.current_step,"3D_return"] > 0.3:
            self.amount = random.uniform(0.3,0.5)
        elif (self.df.loc[self.current_step,"3D_return"] >0.1) & (self.df.loc[self.current_step,"3D_return"]<0.3):
            self.amount = random.uniform(0.1,0.3)
        
        
        action_taken = a

        
        if action_taken == 2: # Buy
            total_possible = self.current_capital/current_price
            amount_stocks_bought = total_possible * self.amount
            current_cost = amount_stocks_bought * current_price
            self.buy_cost += current_cost
            self.no_stocks_bought += amount_stocks_bought
            self.current_stocks_held += amount_stocks_bought
            self.avg_cost = float(self.buy_cost) / float(self.current_stocks_held)
            self.current_capital -= current_cost #attemps to incentivise buying behaviour at prices lower than the average cost
            self.previous_portfolio_value = self.portfolio_value 
            self.portfolio_value = self.current_capital + (self.current_stocks_held*current_price)
            
        elif action_taken == 0: #Sell
            #can probably do and if else statement to check if there is any stocks bought if not do nothing
            #if self.current_stocks_held <= 0.000001:
             #   self.previous_portfolio_value = self.portfolio_value 
              #  self.portfolio_value -= self.portfolio_value *0.1
           # else:
                shares_sell = self.current_stocks_held * self.amount
                profit = shares_sell * current_price
                self.no_stocks_sold += shares_sell
                self.current_stocks_held -= shares_sell
                self.current_capital += profit
                self.returns = profit - (shares_sell * self.avg_cost)
                self.buy_cost -= shares_sell * self.avg_cost
                self.previous_portfolio_value = self.portfolio_value 
                self.portfolio_value = self.current_capital + (self.current_stocks_held*current_price)
            
            
        elif action_taken == 1:
            self.previous_portfolio_value = self.portfolio_value 
            self.portfolio_value -= self.portfolio_value *0.1 #holding should only be considered beneficial if current price of all assets > average price of assets, besides that selling is better
            
        if self.current_capital > self.max_capital:
            self.max_capital = self.current_capital
        if self.current_stocks_held <= 0:
            self.avg_cost == 0 
            
    def reset(self):
        self.no_stocks_bought = 0.00000001 #to avoid double scalar problems
        self.no_stocks_sold = 0.0000001   #to avoid double scalar problems
        self.current_stocks_held = 0.000001
        self.portfolio_value = self.initial_capital
        self.current_capital = self.initial_capital
        self.avg_cost = 0
        self.returns = 0 
        self.max_steps = len(self.df)
        self.current_step = 0
        self.buy_cost = 0
        self.previous_portfolio_value = 0
        self.done = False
        
        return self.observation()
        
    def render(self):
        current_price = random.uniform(self.df.loc[self.current_step, "Open"],self.df.loc[self.current_step,"Close"])
        self.portfolio_value = self.current_capital + (self.current_stocks_held*current_price)
        return_perc = (self.portfolio_value-self.initial_capital)/self.initial_capital * 100
        
        print(f"Current Porfolio Value:{self.portfolio_value}; Available Capital: {self.current_capital}; Current Stocks Held: {self.current_stocks_held}")
        print(f"No. Stocks Bought:{self.no_stocks_bought}; No. Stocks Sold:{self.no_stocks_sold}; Average Cost:{self.avg_cost} ")
        print(f"Return:{return_perc}%; {self.portfolio_value-self.initial_capital}")
        print(f"Termination date: {self.df.loc[self.current_step,'Timestamp']}")
        
    def reward_output(self):
        return_value = self.portfolio_value-self.initial_capital
        return_perc = (self.portfolio_value/self.initial_capital) * 100
        return return_perc, return_value, self.no_stocks_bought,self.no_stocks_sold,  self.current_stocks_held
