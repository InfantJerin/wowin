import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from market_simulator import MarketSimulator, create_sample_simulation
from enhanced_money_flow import EnhancedMoneyFlowAnalyzer

def main():
    st.set_page_config(layout="wide", page_title="Stock Market Wealth Transfer Simulator")
    
    st.title("Stock Market Wealth Transfer Analyzer")
    st.subheader("Track how institutional investors extract money from retail traders")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Simulation Controls")
        
        # Simulation parameters
        st.subheader("Market Parameters")
        num_inst = st.slider("Number of Institutional Investors", 1, 20, 5)
        num_retail = st.slider("Number of Retail Investors", 10, 200, 50)
        simulation_days = st.slider("Simulation Days", 30, 365, 120)
        
        # Stock parameters
        st.subheader("Stock Parameters")
        num_stocks = st.slider("Number of Stocks", 1, 10, 3)
        avg_volatility = st.slider("Average Volatility", 0.005, 0.05, 0.015, format="%.3f")
        
        # Behavior parameters
        st.subheader("Investor Behavior")
        inst_aggression = st.slider("Institutional Aggression", 0.1, 2.0, 1.0)
        retail_fomo = st.slider("Retail FOMO Factor", 0.1, 2.0, 0.7)
        
        simulate_button = st.button("Run Simulation")
    
    # Main panel - initially show explanation
    if 'simulation_run' not in st.session_state:
        st.session_state.simulation_run = False
        st.session_state.sim_data = None
        
        # Show explanation
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("""
            ## How Wealth Transfer Works in Markets
            
            This application simulates how wealth gets transferred from retail to institutional investors through market timing advantages.
            
            ### The Three-Phase Cycle:
            
            1. **Accumulation Phase**
               - Institutional investors quietly buy shares
               - Prices rise gradually, avoiding attention
               - Retail investors largely unaware
            
            2. **Markup Phase (Pump)**
               - Prices rise more rapidly
               - Media coverage and social buzz increase
               - Retail investors experience FOMO (Fear Of Missing Out)
               - Retail buying accelerates near price peaks
            
            3. **Distribution Phase (Dump)**
               - Institutional investors begin selling shares
               - Selling occurs into retail buying demand
               - Retail investors continue buying as prices peak
               - After distribution, prices fall, leaving retail investors with losses
            
            ### Wealth Transfer Mechanics
            
            The simulation tracks specifically:
            - When institutions sell to retail at market peaks
            - How much retail investors lose after buying during distribution phases
            - Cumulative wealth transfer from retail to institutional investors
            """)
        
        with col2:
            st.image("https://via.placeholder.com/400x300.png?text=Wealth+Transfer+Cycle", 
                     caption="The market cycle of wealth transfer")
            st.markdown("""
            ### Key Metrics Tracked:
            1. **Direct Wealth Transfer** - When institutions sell directly to retail
            2. **Value Decay** - How much value retail purchases lose after institutional exit
            3. **Distribution Detection** - Identification of institutional selling phases
            4. **Return Differential** - How returns differ between investor classes
            """)
    
    # Run simulation when button is clicked
    if simulate_button:
        with st.spinner("Running simulation..."):
            # Create and run simulation
            sim = MarketSimulator()
            
            # Add stocks with slightly different volatilities
            stock_names = ["TECH", "ENERGY", "FINANCE", "HEALTH", "RETAIL", 
                          "CRYPTO", "TELECOM", "AUTO", "DEFENSE", "FOOD"]
            for i in range(min(num_stocks, len(stock_names))):
                vol = avg_volatility * (0.8 + np.random.random() * 0.4)  # ±20% of avg_volatility
                price = 25 + np.random.random() * 175  # $25-$200
                sim.add_stock(stock_names[i], price, vol)
            
            # Add institutional investors with adjusted aggression
            for i in range(num_inst):
                capital = 5000000 + np.random.random() * 15000000  # $5M-$20M
                strategy = "pump_and_dump"  # Use more aggressive strategy
                sim.add_institutional_investor(f"Inst_{i}", capital, strategy)
            
            # Add retail investors with FOMO factors
            for i in range(num_retail):
                capital = 10000 + np.random.random() * 90000  # $10K-$100K
                fomo = retail_fomo * (0.7 + np.random.random() * 0.6)  # Variation in FOMO
                sim.add_retail_investor(f"Retail_{i}", capital, fomo)
            
            # Run simulation
            data = sim.run_simulation(simulation_days)
            
            # Store in session state
            st.session_state.simulation_run = True
            st.session_state.sim_data = data
            st.session_state.stock_names = list(sim.stocks.keys())
    
    # Display simulation results if available
    if st.session_state.simulation_run and st.session_state.sim_data is not None:
        stock_tabs = st.tabs(st.session_state.stock_names)
        
        # Create enhanced analyzer
        analyzer = EnhancedMoneyFlowAnalyzer(st.session_state.sim_data)
        
        for i, stock_name in enumerate(st.session_state.stock_names):
            with stock_tabs[i]:
                # Get wealth transfer summary
                summary = analyzer.create_wealth_transfer_summary(stock_name)
                
                # Overview metrics
                st.header(f"{stock_name}: Wealth Transfer Analysis")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Total wealth transfer
                    st.metric("Total Wealth Transfer", 
                             f"${summary['total_wealth_transfer']:,.2f}",
                             delta=None)
                    
                with col2:
                    # Retail caught buying
                    st.metric("Retail Caught Buying During Distribution", 
                             f"${summary['retail_caught_buying']:,.2f}",
                             delta=None)
                    
                with col3:
                    # Number of distribution phases
                    st.metric("Distribution Phases Detected", 
                             f"{summary['number_of_distribution_phases']}",
                             delta=None)
                
                # Post-selling returns
                st.subheader("Retail Investment Returns After Institutional Selling")
                ret_col1, ret_col2, ret_col3 = st.columns(3)
                
                with ret_col1:
                    delta_color = "inverse" if summary['returns_after_5d'] < 0 else "normal"
                    st.metric("5 Days Later", 
                             f"{summary['returns_after_5d']:.2f}%",
                             delta=None)
                
                with ret_col2:
                    delta_color = "inverse" if summary['returns_after_10d'] < 0 else "normal"
                    st.metric("10 Days Later", 
                             f"{summary['returns_after_10d']:.2f}%",
                             delta=None)
                
                with ret_col3:
                    delta_color = "inverse" if summary['returns_after_20d'] < 0 else "normal"
                    st.metric("20 Days Later", 
                             f"{summary['returns_after_20d']:.2f}%",
                             delta=None)
                
                # Charts
                st.subheader("Wealth Transfer Visualization")
                
                # Create and display the charts
                wealth_transfer_fig = analyzer.plot_wealth_transfer(stock_name)
                st.pyplot(wealth_transfer_fig)
                
                st.subheader("Retail Fate After Institutional Selling")
                retail_fate_fig = analyzer.plot_retail_fate_after_inst_selling(stock_name)
                st.pyplot(retail_fate_fig)
                
                # Distribution phase explanation
                st.subheader("Distribution Phase Analysis")
                
                st.markdown(f"""
                During the simulation, we detected **{summary['number_of_distribution_phases']}** distinct distribution phases 
                where institutional investors sold their holdings while retail investors were still buying.
                
                The average wealth transfer per distribution phase was **${summary['avg_wealth_transfer_per_phase']:,.2f}**.
                
                This means that on average, each time institutional investors initiated a selling phase:
                1. Retail investors continued to buy the stock
                2. Prices typically fell after institutional selling
                3. Retail investors were left holding declining assets
                """)
                
                # Interpretation
                st.subheader("Interpretation")
                
                negative_return_20d = summary['returns_after_20d'] < 0
                high_transfer = summary['total_wealth_transfer'] > 10000
                
                if negative_return_20d and high_transfer:
                    st.error("""
                    **Strong Wealth Transfer Pattern Detected**
                    
                    This simulation shows a classic pattern of wealth transfer from retail to institutional investors.
                    Institutions successfully timed their exit near market peaks, selling to retail investors who
                    subsequently experienced significant losses.
                    """)
                elif negative_return_20d:
                    st.warning("""
                    **Moderate Wealth Transfer Pattern**
                    
                    The simulation shows some evidence of wealth transfer, primarily through poor timing
                    by retail investors who bought near market peaks while institutions were exiting.
                    """)
                else:
                    st.success("""
                    **Weak Wealth Transfer Pattern**
                    
                    In this simulation, retail investors performed relatively well even after institutional selling.
                    This can happen in strong bull markets or when retail panic selling doesn't materialize.
                    """)
                
                # Trading opportunities explanation
                st.subheader("Using This Information in Trading")
                
                st.markdown("""
                To avoid becoming the retail investor who buys during institutional distribution phases:
                
                1. **Watch for divergence** between price action and institutional buying/selling
                2. **Track unusual volume** which may indicate institutional activity
                3. **Be cautious of media hype** around stocks that have already made significant moves
                4. **Consider contrarian timing** - be more cautious when retail sentiment is extremely bullish
                5. **Use relative strength analysis** to identify when momentum is weakening despite continuing price increases
                """)

if __name__ == "__main__":
    main()