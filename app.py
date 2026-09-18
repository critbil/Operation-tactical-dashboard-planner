import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Operations Analytics & Performance Dashboard",
    layout="wide"
)

# Operational Standards Base Constants
FRESH_FOOD_BASE_CPH = 190.0
COLD_CHAIN_BASE_CPH = 185.0
MAX_SHIFT_HOURS = 11.0

# HEADER SECTION
st.title("🏭 Operations Analytics & Performance Dashboard")
st.caption("Interactive workforce planning and performance projection tool | Illustrative operational standards")

# MAIN CONTROLS
# Split the entire input zone into two clean side-by-side containers
col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown("### ⚙️ Performance & Labor Targets")
        
        target_active_hours = st.slider(
            "Target Active Production Run-Time (Hours)",
            min_value=4.0, max_value=float(MAX_SHIFT_HOURS), value=9.0, step=0.5,
            help="Adjust the intended active production window to estimate required staffing."
        )
        
        c1, c2 = st.columns(2)
        with c1:
            fresh_food_performance_pct = st.slider(
                "Fresh Expected Performance (%)",
                min_value=50, max_value=160, value=120, step=5
            )
            fresh_food_multiplier = fresh_food_performance_pct / 100.0
            
            fresh_indirect_pct = st.slider(
                "Fresh Indirect Time (%)",
                min_value=0, max_value=50, value=15, step=5,
                help="Non-productive time (meetings, clean-up, breaks)."
            )
            
        with c2:
            cold_chain_performance_pct = st.slider(
                "Cold Expected Performance (%)",
                min_value=50, max_value=160, value=100, step=5
            )
            cold_chain_multiplier = cold_chain_performance_pct / 100.0

            cold_indirect_pct = st.slider(
                "Cold Indirect Time (%)",
                min_value=0, max_value=50, value=20, step=5,
                help="Non-productive warm-up breaks, meetings, etc."
            )
            
        # New Interactive Target for Internal Logistics Pallet Moves Goal
        replenishment_mph_goal = st.slider(
            "Replenishment Target Rate (Pallet Moves/Hour)",
            min_value=5.0, max_value=30.0, value=14.0, step=0.5,
            help="Set the targeted engineering standard for internal logistics pallet handling speed."
        )

with col_right:
    with st.container(border=True):
        st.markdown("### 📊 Daily Volume Inputs")
        
        v1, v2 = st.columns(2)
        with v1:
            st.markdown("**Outbound Demand**")
            fresh_food_cases = st.number_input(
                "Fresh Food Cases", min_value=0, max_value=100000, value=25000, step=500
            )
            cold_chain_cases = st.number_input(
                "Cold Chain Cases", min_value=0, max_value=100000, value=15000, step=500
            )
        with v2:
            st.markdown("**Internal Logistics**")
            fresh_replen_moves = st.number_input(
                "Fresh Replenishment Moves", min_value=0, max_value=5000, value=250, step=25
            )
            cold_replen_moves = st.number_input(
                "Cold Replenishment Moves", min_value=0, max_value=5000, value=200, step=25
            )

# CALCULATIONS 
calculated_fresh_cph = FRESH_FOOD_BASE_CPH * fresh_food_multiplier
calculated_cold_cph = COLD_CHAIN_BASE_CPH * cold_chain_multiplier

# Split replenishment hours using user-defined slider metric
fresh_replen_hours = fresh_replen_moves / replenishment_mph_goal if replenishment_mph_goal > 0 else 0.0
cold_replen_hours = cold_replen_moves / replenishment_mph_goal if replenishment_mph_goal > 0 else 0.0
total_replen_hours = fresh_replen_hours + cold_replen_hours

fresh_gross_hours = fresh_direct_hours = fresh_food_cases / calculated_fresh_cph if calculated_fresh_cph > 0 else 0.0
cold_gross_hours = cold_direct_hours = cold_chain_cases / calculated_cold_cph if calculated_cold_cph > 0 else 0.0

fresh_gross_hours = fresh_direct_hours / (1 - (fresh_indirect_pct / 100.0))
cold_gross_hours = cold_direct_hours / (1 - (cold_indirect_pct / 100.0))
total_gross_labor_hours = fresh_gross_hours + cold_gross_hours + total_replen_hours

fresh_required_hc = math.ceil(fresh_gross_hours / target_active_hours) if target_active_hours > 0 else 0
cold_required_hc = math.ceil(cold_gross_hours / target_active_hours) if target_active_hours > 0 else 0
fresh_replen_hc = math.ceil(fresh_replen_hours / target_active_hours) if target_active_hours > 0 else 0
cold_replen_hc = math.ceil(cold_replen_hours / target_active_hours) if target_active_hours > 0 else 0
total_required_hc = fresh_required_hc + cold_required_hc + fresh_replen_hc + cold_replen_hc

# ANALYTICS AND OUTPUTS 
# Display metrics and data grid in a single clean analytics card
with st.container(border=True):
    st.markdown("### 📈 Labor Requirements & Performance Analytics")
    
    # KPI Row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric(
            label="Total Required Headcount", 
            value=f"{total_required_hc} FTEs", 
            delta=f"{fresh_required_hc + fresh_replen_hc} Fresh | {cold_required_hc + cold_replen_hc} Cold",
            delta_color="off"
        )
    with metric_col2:
        st.metric(label="Total Gross Labor Hours", value=f"{total_gross_labor_hours:.1f} Hrs")
    with metric_col3:
        st.metric(label="Fresh Targeted CPH", value=f"{calculated_fresh_cph:.1f}", delta=f"{(fresh_food_multiplier - 1.0)*100:+.0f}% vs Base")
    with metric_col4:
        st.metric(label="Cold Targeted CPH", value=f"{calculated_cold_cph:.1f}", delta=f"{(cold_chain_multiplier - 1.0)*100:+.0f}% vs Base")

    # Detailed Table
    summary_data = {
        "Department": [
            "Fresh Food Outbound", 
            "Cold Chain Outbound", 
            "Fresh Replenishment Logistics", 
            "Cold Replenishment Logistics", 
            "Total Operation"
        ],
        "Volume / Units": [
            f"{fresh_food_cases:,} Cases", 
            f"{cold_chain_cases:,} Cases", 
            f"{fresh_replen_moves:,} Moves", 
            f"{cold_replen_moves:,} Moves", 
            "-"
        ],
        "Target Rate": [
            f"{calculated_fresh_cph:.1f} CPH", 
            f"{calculated_cold_cph:.1f} CPH", 
            f"{replenishment_mph_goal:.1f} MPH", 
            f"{replenishment_mph_goal:.1f} MPH", 
            "-"
        ],
        "Direct Hours": [
            f"{fresh_direct_hours:.1f}", 
            f"{cold_direct_hours:.1f}", 
            f"{fresh_replen_hours:.1f}", 
            f"{cold_replen_hours:.1f}", 
            f"{fresh_direct_hours + cold_direct_hours + total_replen_hours:.1f}"
        ],
        "Indirect Allowance": [
            f"{fresh_indirect_pct}%", 
            f"{cold_indirect_pct}%", 
            "0%", 
            "0%", 
            "-"
        ],
        "Gross Hours Required": [
            f"{fresh_gross_hours:.1f}", 
            f"{cold_gross_hours:.1f}", 
            f"{fresh_replen_hours:.1f}", 
            f"{cold_replen_hours:.1f}", 
            f"{total_gross_labor_hours:.1f}"
        ],
        "Estimated Staffing (FTEs)": [
            fresh_required_hc, 
            cold_required_hc, 
            fresh_replen_hc, 
            cold_replen_hc, 
            total_required_hc
        ]
    }
    
    st.markdown("---") 
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
