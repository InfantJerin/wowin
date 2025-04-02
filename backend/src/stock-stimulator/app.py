import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from market_simulator import MarketSimulator, create_sample_simulation
from money_flow_viz import MoneyFlowVisualizer

def main():
    st.set_page_config(layout="wide", page_title="Stock Market Money Flow Simulator")
    
    st.title("Stock Market Money Flow Analyzer")
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
            ## How This Simulator Works
            
            This application simulates stock market dynamics with a focus on the flow of money between institutional and retail investors.
            
            ### Key Components:
            
            1. **Institutional Investors**
               - Deploy sophisticated strategies
               - Often work in coordination
               - Have large capital bases
               - Can influence market prices significantly
            
            2. **Retail Investors**
               - Typically react to price movements
               - Exhibit FOMO (Fear Of Missing Out) behavior
               - Have smaller individual impact
               - Often buy near tops and sell near bottoms
            
            3. **Money Flow Analysis**
               - Tracks capital movement between investor classes
               - Identifies accumulation and distribution phases
               - Highlights potential pump-and-dump patterns
               - Shows when smart money is entering or exiting
            """)
        
        with col2:
            st.image("https://via.placeholder.com/400x300.png?text=Money+Flow+Concept", 
                     caption="Conceptual illustration of money flow between investor classes")
            st.markdown("""
            ### How to Use:
            1. Adjust parameters in the sidebar
            2. Click "Run Simulation"
            3. Analyze the resulting patterns
            4. Identify potential pump-and-dump cycles
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
            
            # Add institutional investors
            for i in range(num_inst):
                capital = 5000000 + np.random.random() * 15000000  # $5M-$20M
                sim.add_institutional_investor(f"Inst_{i}", capital)
            
            # Add retail investors
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
        
        visualizer = MoneyFlowVisualizer(st.session_state.sim_data)
        
        for i, stock_name in enumerate(st.session_state.stock_names):
            with stock_tabs[i]:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.subheader(f"{stock_name} Price and Money Flow")
                    
                    # Convert matplotlib figures to Streamlit
                    fig1, fig2 = visualizer.create_money_flow_dashboard(stock_name)
                    st.pyplot(fig1)
                    st.pyplot(fig2)
                
                with col2:
                    st.subheader("Analysis")
                    
                    # Calculate key metrics
                    final_price = st.session_state.sim_data[f'{stock_name}_price'].iloc[-1]
                    initial_price = st.session_state.sim_data[f'{stock_name}_price'].iloc[0]
                    price_change_pct = ((final_price / initial_price) - 1) * 100
                    
                    inst_total_flow = st.session_state.sim_data[f'{stock_name}_inst_flow'].sum()
                    retail_total_flow = st.session_state.sim_data[f'{stock_name}_retail_flow'].sum()
                    
                    # Display metrics
                    st.metric("Current Price", f"${final_price:.2f}", f"{price_change_pct:.1f}%")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.metric("Institutional Net Flow", f"${inst_total_flow:,.0f}")
                    with col_b:
                        st.metric("Retail Net Flow", f"${retail_total_flow:,.0f}")
                    
                    # Detect patterns
                    pump_periods, dump_periods = visualizer.detect_pump_and_dump(stock_name)
                    
                    st.subheader("Detected Patterns")
                    if len(pump_periods) > 0 or len(dump_periods) > 0:
                        st.write(f"✅ Found {len(pump_periods)} accumulation phases")
                        st.write(f"⚠️ Found {len(dump_periods)} distribution phases")
                        
                        # Show most recent pattern
                        if dump_periods:
                            latest_dump = st.session_state.sim_data['date'].iloc[dump_periods[-1]]
                            st.warning(f"Recent distribution detected around {latest_dump.strftime('%Y-%m-%d')}")
                    else:
                        st.write("No clear patterns detected in this time period")
                    
                    # Money flow dominance
                    dominance = visualizer.institutional_dominance_metric(stock_name)
                    st.subheader("Institutional Dominance")
                    st.progress(min(dominance / 3, 1.0))  # Scale to 0-1
                    st.write(f"Score: {dominance:.2f}x (higher means stronger institutional control)")

if __name__ == "__main__":
    main()