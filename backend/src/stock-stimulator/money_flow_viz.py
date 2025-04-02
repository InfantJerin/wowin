import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class MoneyFlowVisualizer:
    def __init__(self, simulation_data):
        self.data = simulation_data
        
    def plot_price_and_money_flow(self, stock_name):
        """Plot price and money flow for a specific stock"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 16), sharex=True)
        
        # Price chart
        self.data.plot(x='date', y=f'{stock_name}_price', ax=axes[0], 
                       color='black', linewidth=2)
        axes[0].set_title(f'{stock_name} Price', fontsize=16)
        axes[0].set_ylabel('Price ($)', fontsize=14)
        axes[0].grid(True)
        
        # Money flow chart
        self.data.plot(x='date', y=f'{stock_name}_inst_flow', ax=axes[1], 
                       color='blue', linewidth=2, label='Institutional Flow')
        self.data.plot(x='date', y=f'{stock_name}_retail_flow', ax=axes[1], 
                       color='green', linewidth=2, label='Retail Flow')
        axes[1].set_title(f'{stock_name} Daily Money Flow', fontsize=16)
        axes[1].set_ylabel('Flow Amount ($)', fontsize=14)
        axes[1].grid(True)
        axes[1].legend()
        
        # Cumulative flow
        inst_cum = self.data[f'{stock_name}_inst_flow'].cumsum()
        retail_cum = self.data[f'{stock_name}_retail_flow'].cumsum()
        
        axes[2].plot(self.data['date'], inst_cum, 
                    color='blue', linewidth=2, label='Institutional (Cumulative)')
        axes[2].plot(self.data['date'], retail_cum, 
                    color='green', linewidth=2, label='Retail (Cumulative)')
        axes[2].set_title(f'{stock_name} Cumulative Money Flow', fontsize=16)
        axes[2].set_ylabel('Cumulative Flow ($)', fontsize=14)
        axes[2].grid(True)
        axes[2].legend()
        
        plt.tight_layout()
        return fig
        
    def detect_pump_and_dump(self, stock_name, window=10):
        """Detect potential pump and dump patterns"""
        # Calculate indicators
        price = self.data[f'{stock_name}_price']
        inst_flow = self.data[f'{stock_name}_inst_flow']
        retail_flow = self.data[f'{stock_name}_retail_flow']
        
        # Smoothed price change
        price_pct_change = price.pct_change(window)
        
        # Calculate institutional sell-off after price increase
        inst_flow_ma = inst_flow.rolling(window=window).mean()
        price_ma = price.rolling(window=window).mean()
        
        # Conditions for pump and dump
        # 1. Significant price increase in the past
        # 2. Recent institutional selling
        # 3. Recent retail buying (getting dumped on)
        
        pump_periods = []
        dump_periods = []
        
        for i in range(window*2, len(self.data)):
            # Check for pump (price increase + institutional buying)
            if (price_pct_change.iloc[i-window] > 0.1 and  # 10% price increase
                inst_flow.iloc[i-window:i-1].mean() > 0):  # Institutional buying
                pump_periods.append(i-window)
            
            # Check for dump (institutional selling + retail buying)
            if (inst_flow.iloc[i-5:i+1].mean() < 0 and      # Recent institutional selling
                retail_flow.iloc[i-5:i+1].mean() > 0 and    # Recent retail buying
                price_pct_change.iloc[i-10:i].max() > 0.15): # After significant price rise
                dump_periods.append(i)
        
        return pump_periods, dump_periods
    
    def plot_pump_and_dump_detection(self, stock_name):
        """Plot price with detected pump and dump periods highlighted"""
        pump_periods, dump_periods = self.detect_pump_and_dump(stock_name)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot price
        ax.plot(self.data['date'], self.data[f'{stock_name}_price'], 
                color='black', linewidth=2, label='Price')
        
        # Highlight pump periods
        for p in pump_periods:
            if p < len(self.data):
                ax.axvspan(self.data['date'].iloc[p], 
                          self.data['date'].iloc[min(p+5, len(self.data)-1)], 
                          alpha=0.2, color='green', label='_Pump')
        
        # Highlight dump periods
        for d in dump_periods:
            if d < len(self.data):
                ax.axvspan(self.data['date'].iloc[d], 
                          self.data['date'].iloc[min(d+5, len(self.data)-1)], 
                          alpha=0.2, color='red', label='_Dump')
        
        # Create custom legend
        from matplotlib.patches import Patch
        legend_elements = [
            plt.Line2D([0], [0], color='black', lw=2, label='Price'),
            Patch(facecolor='green', alpha=0.2, label='Pump Phase'),
            Patch(facecolor='red', alpha=0.2, label='Dump Phase')
        ]
        ax.legend(handles=legend_elements)
        
        ax.set_title(f'{stock_name} Pump and Dump Detection', fontsize=16)
        ax.set_ylabel('Price ($)', fontsize=14)
        ax.grid(True)
        
        return fig
    
    def create_money_flow_dashboard(self, stock_name):
        """Create a comprehensive dashboard for money flow analysis"""
        # In a real app, this would be an interactive dashboard
        # Here we'll just return multiple plots
        fig1 = self.plot_price_and_money_flow(stock_name)
        fig2 = self.plot_pump_and_dump_detection(stock_name)
        
        return fig1, fig2
    
    def institutional_dominance_metric(self, stock_name):
        """Calculate how much institutional investors dominate price action"""
        inst_influence = np.abs(self.data[f'{stock_name}_inst_demand']).mean()
        retail_influence = np.abs(self.data[f'{stock_name}_retail_demand']).mean()
        
        if retail_influence > 0:
            return inst_influence / retail_influence
        else:
            return float('inf')  # Complete dominance
