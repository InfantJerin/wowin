import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class Stock:
    def __init__(self, name, initial_price, volatility):
        self.name = name
        self.price = initial_price
        self.volatility = volatility
        self.price_history = [initial_price]
        self.volume_history = [0]
        self.institutional_holdings = 0
        self.retail_holdings = 0
        
    def update_price(self, institutional_demand, retail_demand):
        # Calculate new price based on combined demand and volatility
        demand_factor = (institutional_demand * 2 + retail_demand) / 3  # Institutional has more impact
        price_change = self.price * (demand_factor * self.volatility + 
                                    np.random.normal(0, self.volatility/2))
        self.price += price_change
        self.price = max(0.01, self.price)  # Ensure price stays positive
        self.price_history.append(self.price)
        return self.price

class InstitutionalInvestor:
    def __init__(self, name, capital, strategy="pump_and_dump"):
        self.name = name
        self.capital = capital
        self.strategy = strategy
        self.holdings = {}
        self.transaction_history = []
        self.phase = "accumulation"  # accumulation, pump, distribution
        self.phase_counter = 0
        self.target_stock = None
        
    def decide_action(self, market):
        if self.strategy == "pump_and_dump":
            return self._pump_and_dump_strategy(market)
        return 0, None
        
    def _pump_and_dump_strategy(self, market):
        if not self.target_stock and random.random() < 0.1:
            # Select a new target occasionally
            self.target_stock = random.choice(list(market.stocks.keys()))
            self.phase = "accumulation"
            self.phase_counter = 0
            
        if not self.target_stock:
            return 0, None
            
        stock = market.stocks[self.target_stock]
        action = 0  # Demand: -1 to +1
        
        if self.phase == "accumulation":
            # Quietly accumulate shares
            action = 0.3 + random.random() * 0.2
            self.phase_counter += 1
            if self.phase_counter > 20:  # After sufficient accumulation
                self.phase = "pump"
                self.phase_counter = 0
                
        elif self.phase == "pump":
            # Aggressively push prices up
            action = 0.7 + random.random() * 0.3
            self.phase_counter += 1
            if self.phase_counter > 10:  # After sufficient pumping
                self.phase = "distribution"
                self.phase_counter = 0
                
        elif self.phase == "distribution":
            # Sell holdings to retail investors
            action = -0.8 - random.random() * 0.2
            self.phase_counter += 1
            if self.phase_counter > 15:  # After distribution
                self.target_stock = None
        
        return action, self.target_stock

class RetailInvestor:
    def __init__(self, name, capital, fomo_factor=0.5):
        self.name = name
        self.capital = capital
        self.fomo_factor = fomo_factor  # How easily influenced by rising prices
        self.panic_factor = 0.7  # How easily scared by falling prices
        self.holdings = {}
        self.transaction_history = []
        
    def decide_action(self, market):
        # Simple strategy: buy on rising prices (FOMO), sell on falling prices
        actions = {}
        for stock_name, stock in market.stocks.items():
            if len(stock.price_history) < 5:
                actions[stock_name] = 0
                continue
                
            # Calculate recent price trend
            recent_trend = (stock.price_history[-1] / stock.price_history[-5]) - 1
            
            if recent_trend > 0.05:  # Price rising
                # FOMO buying - stronger as trend grows
                actions[stock_name] = min(recent_trend * self.fomo_factor, 1.0)
            elif recent_trend < -0.05:  # Price falling
                # Panic selling - stronger as trend worsens
                actions[stock_name] = max(recent_trend * self.panic_factor, -1.0)
            else:
                actions[stock_name] = recent_trend * 0.2  # Small action on small trends
                
        # Pick one stock to focus on
        if actions:
            focus_stock = max(actions.items(), key=lambda x: abs(x[1]))
            return focus_stock[1], focus_stock[0]
        return 0, None

class MarketSimulator:
    def __init__(self):
        self.stocks = {}
        self.institutional_investors = []
        self.retail_investors = []
        self.current_day = 0
        self.dates = []
        self.money_flow_data = []
        
    def add_stock(self, name, price, volatility):
        self.stocks[name] = Stock(name, price, volatility)
        
    def add_institutional_investor(self, name, capital, strategy="pump_and_dump"):
        self.institutional_investors.append(InstitutionalInvestor(name, capital, strategy))
        
    def add_retail_investor(self, name, capital, fomo_factor=0.5):
        self.retail_investors.append(RetailInvestor(name, capital, fomo_factor))
        
    def simulate_day(self):
        self.current_day += 1
        self.dates.append(datetime.now() + timedelta(days=self.current_day))
        
        # Process institutional investors first
        institutional_demands = {stock: 0 for stock in self.stocks}
        for investor in self.institutional_investors:
            demand, stock_name = investor.decide_action(self)
            if stock_name:
                institutional_demands[stock_name] += demand
        
        # Then process retail investors
        retail_demands = {stock: 0 for stock in self.stocks}
        for investor in self.retail_investors:
            demand, stock_name = investor.decide_action(self)
            if stock_name:
                retail_demands[stock_name] += demand
        
        # Update prices and record money flow
        day_data = {'date': self.dates[-1]}
        for stock_name, stock in self.stocks.items():
            inst_demand = institutional_demands[stock_name] / len(self.institutional_investors) if self.institutional_investors else 0
            retail_demand = retail_demands[stock_name] / len(self.retail_investors) if self.retail_investors else 0
            
            new_price = stock.update_price(inst_demand, retail_demand)
            
            # Track money flow
            inst_flow = inst_demand * stock.price * 100000  # Approximate dollar value
            retail_flow = retail_demand * stock.price * 10000
            
            day_data[f'{stock_name}_price'] = new_price
            day_data[f'{stock_name}_inst_flow'] = inst_flow
            day_data[f'{stock_name}_retail_flow'] = retail_flow
            day_data[f'{stock_name}_inst_demand'] = inst_demand
            day_data[f'{stock_name}_retail_demand'] = retail_demand
            
            # Update holdings
            stock.institutional_holdings += inst_flow
            stock.retail_holdings += retail_flow
            
        self.money_flow_data.append(day_data)
        
    def get_data_frame(self):
        return pd.DataFrame(self.money_flow_data)
    
    def run_simulation(self, days):
        for _ in range(days):
            self.simulate_day()
        return self.get_data_frame()

# Example usage
def create_sample_simulation():
    sim = MarketSimulator()
    
    # Add stocks
    sim.add_stock("TECH", 100.0, 0.02)
    sim.add_stock("ENERGY", 50.0, 0.015)
    sim.add_stock("FINANCE", 75.0, 0.01)
    
    # Add institutional investors
    for i in range(5):
        sim.add_institutional_investor(f"Inst_{i}", 10000000)
    
    # Add retail investors with varying FOMO factors
    for i in range(50):
        fomo = 0.3 + random.random() * 0.7  # Between 0.3 and 1.0
        sim.add_retail_investor(f"Retail_{i}", 100000, fomo)
    
    return sim

if __name__ == "__main__":
    sim = create_sample_simulation()
    data = sim.run_simulation(100)  # Simulate 100 days
    print(data.head())
