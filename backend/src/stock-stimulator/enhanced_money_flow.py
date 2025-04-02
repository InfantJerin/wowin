import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.patches import Patch

class EnhancedMoneyFlowAnalyzer:
    def __init__(self, simulation_data):
        self.data = simulation_data
        self.calculate_wealth_transfer_metrics()
        
    def calculate_wealth_transfer_metrics(self):
        """Calculate metrics related to wealth transfer from retail to institutional investors"""
        # Process each stock in the dataset
        stock_columns = [col.split('_')[0] for col in self.data.columns 
                         if col.endswith('_price')]
        
        for stock_name in stock_columns:
            # 1. Calculate the strategic timing advantage
            # When institutions sell and retailers buy at the same time
            self.data[f'{stock_name}_wealth_transfer'] = (
                -1 * self.data[f'{stock_name}_inst_flow'] * 
                np.where(self.data[f'{stock_name}_retail_flow'] > 0, 1, 0) *
                np.where(self.data[f'{stock_name}_inst_flow'] < 0, 1, 0)
            )
            
            # 2. Calculate cumulative wealth transfer
            self.data[f'{stock_name}_cum_wealth_transfer'] = self.data[f'{stock_name}_wealth_transfer'].cumsum()
            
            # 3. Calculate retail buying at institutional selling peaks
            # Get top 10% of institutional selling days
            inst_sell_threshold = np.percentile(
                self.data[self.data[f'{stock_name}_inst_flow'] < 0][f'{stock_name}_inst_flow'], 10)
            
            # Flag days with heavy institutional selling
            self.data[f'{stock_name}_heavy_inst_selling'] = np.where(
                self.data[f'{stock_name}_inst_flow'] <= inst_sell_threshold, 1, 0)
            
            # Calculate retail buying during heavy institutional selling
            self.data[f'{stock_name}_retail_buying_into_selling'] = (
                self.data[f'{stock_name}_retail_flow'] * 
                self.data[f'{stock_name}_heavy_inst_selling']
            )
            
            # 4. Calculate value capture/loss 5 and 10 days after heavy institutional selling
            window_sizes = [5, 10, 20]
            for window in window_sizes:
                # Calculate price change N days after each point
                self.data[f'{stock_name}_price_change_{window}d'] = self.data[f'{stock_name}_price'].pct_change(periods=window).shift(-window)
                
                # Calculate retail value change after institutional selling
                self.data[f'{stock_name}_retail_value_change_{window}d'] = (
                    self.data[f'{stock_name}_retail_buying_into_selling'] * 
                    self.data[f'{stock_name}_price_change_{window}d']
                )
    
    def plot_wealth_transfer(self, stock_name):
        """Plot wealth transfer dynamics for a specific stock"""
        fig, axes = plt.subplots(3, 1, figsize=(12, 18), sharex=True)
        
        # 1. Price chart with institutional selling highlighted
        axes[0].plot(self.data['date'], self.data[f'{stock_name}_price'], 
                    color='black', linewidth=2, label='Price')
        
        # Highlight periods of heavy institutional selling
        sell_periods = self.data[self.data[f'{stock_name}_heavy_inst_selling'] == 1]
        if not sell_periods.empty:
            axes[0].scatter(sell_periods['date'], sell_periods[f'{stock_name}_price'], 
                           color='red', s=50, alpha=0.7, label='Heavy Institutional Selling')
        
        axes[0].set_title(f'{stock_name} Price with Institutional Selling Markers', fontsize=16)
        axes[0].set_ylabel('Price ($)', fontsize=14)
        axes[0].grid(True)
        axes[0].legend()
        
        # 2. Daily wealth transfer
        axes[1].plot(self.data['date'], self.data[f'{stock_name}_wealth_transfer'], 
                   color='purple', linewidth=2)
        axes[1].axhline(y=0, color='gray', linestyle='--')
        axes[1].set_title(f'{stock_name} Daily Wealth Transfer (Retail to Institutional)', fontsize=16)
        axes[1].set_ylabel('Transfer Amount ($)', fontsize=14)
        axes[1].grid(True)
        
        # 3. Cumulative wealth transfer
        axes[2].plot(self.data['date'], self.data[f'{stock_name}_cum_wealth_transfer'], 
                    color='darkred', linewidth=2)
        axes[2].axhline(y=0, color='gray', linestyle='--')
        axes[2].set_title(f'{stock_name} Cumulative Wealth Transfer', fontsize=16)
        axes[2].set_ylabel('Cumulative Transfer ($)', fontsize=14)
        axes[2].grid(True)
        
        plt.tight_layout()
        return fig
        
    def plot_retail_fate_after_inst_selling(self, stock_name):
        """Plot what happens to retail investments after institutional selling"""
        # Filter to days with heavy institutional selling
        sell_days = self.data[self.data[f'{stock_name}_heavy_inst_selling'] == 1].copy()
        
        if sell_days.empty:
            # Create a figure with a message if no selling days
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'No heavy institutional selling detected', 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=16)
            return fig
            
        fig, axes = plt.subplots(2, 1, figsize=(12, 12))
        
        # 1. Price change after institutional selling
        window_sizes = [5, 10, 20]
        colors = ['#ff9999', '#ff6666', '#cc0000']
        
        # Price changes X days after institutional selling
        for i, window in enumerate(window_sizes):
            avg_change = sell_days[f'{stock_name}_price_change_{window}d'].mean() * 100
            axes[0].bar(i, avg_change, color=colors[i], 
                      label=f'{window} Days Later: {avg_change:.2f}%')
        
        axes[0].axhline(y=0, color='black', linestyle='-')
        axes[0].set_title('Average Price Change After Heavy Institutional Selling', fontsize=16)
        axes[0].set_ylabel('Price Change (%)', fontsize=14)
        axes[0].set_xticks(range(len(window_sizes)))
        axes[0].set_xticklabels([f'{w} Days' for w in window_sizes])
        axes[0].grid(axis='y')
        
        # 2. Retail money flow and subsequent value
        retail_flow_during_selling = sell_days[f'{stock_name}_retail_buying_into_selling'].sum()
        
        # Value of these investments after X days
        value_after = []
        for window in window_sizes:
            col = f'{stock_name}_retail_value_change_{window}d'
            value = sell_days[f'{stock_name}_retail_buying_into_selling'].sum() * (
                1 + sell_days[f'{stock_name}_price_change_{window}d'].mean())
            value_after.append(value)
        
        # Calculate gain/loss percentage
        pct_changes = [(v / retail_flow_during_selling - 1) * 100 if retail_flow_during_selling else 0 
                      for v in value_after]
        
        # Plot initial investment vs value after X days
        x_positions = np.arange(len(window_sizes) + 1)
        bars = axes[1].bar(x_positions, [retail_flow_during_selling] + value_after, 
                         color=['green'] + colors)
        
        # Add percentage labels
        axes[1].text(0, retail_flow_during_selling * 1.05, 
                   'Initial', ha='center', fontsize=12)
        
        for i, pct in enumerate(pct_changes):
            axes[1].text(i+1, value_after[i] * 1.05, 
                       f'{pct:.1f}%', ha='center', fontsize=12, 
                       color='green' if pct >= 0 else 'red')
        
        axes[1].set_title('Retail Investment Value After Institutional Selling', fontsize=16)
        axes[1].set_ylabel('Value ($)', fontsize=14)
        axes[1].set_xticks(x_positions)
        axes[1].set_xticklabels(['Initial'] + [f'{w} Days' for w in window_sizes])
        axes[1].grid(axis='y')
        
        plt.tight_layout()
        return fig
    
    def create_wealth_transfer_summary(self, stock_name):
        """Create a comprehensive summary of wealth transfer dynamics"""
        # Filter to days with heavy institutional selling
        sell_days = self.data[self.data[f'{stock_name}_heavy_inst_selling'] == 1]
        
        # Summary stats
        total_wealth_transfer = self.data[f'{stock_name}_wealth_transfer'].sum()
        retail_investment_during_inst_selling = self.data[f'{stock_name}_retail_buying_into_selling'].sum()
        
        # Calculate post-selling returns
        returns_after = {}
        for window in [5, 10, 20]:
            avg_change = sell_days[f'{stock_name}_price_change_{window}d'].mean() * 100
            returns_after[window] = avg_change
        
        # Count distribution phases
        phases = 0
        threshold = np.percentile(
            self.data[self.data[f'{stock_name}_inst_flow'] < 0][f'{stock_name}_inst_flow'], 25)
        
        in_phase = False
        for i in range(1, len(self.data)):
            if not in_phase and self.data[f'{stock_name}_inst_flow'].iloc[i] <= threshold:
                in_phase = True
                phases += 1
            elif in_phase and self.data[f'{stock_name}_inst_flow'].iloc[i] > threshold:
                in_phase = False
        
        return {
            'total_wealth_transfer': total_wealth_transfer,
            'retail_caught_buying': retail_investment_during_inst_selling,
            'number_of_distribution_phases': phases,
            'returns_after_5d': returns_after[5],
            'returns_after_10d': returns_after[10],
            'returns_after_20d': returns_after[20],
            'avg_wealth_transfer_per_phase': total_wealth_transfer / max(1, phases)
        }