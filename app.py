import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Commodity-Isolated Command Center", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- GLOBAL STATIC OPERATIONAL PARAMETERS ---
MP_BASE_CPH = 190.0
FDD_BASE_CPH = 185.0
LIFT_BASE_MPH = 14.0
PAID_SHIFT_HOURS = 11.0

st.title("🏭 Shipping Department Commodity-Isolated Command Center")
st.caption("Active Configurations: 11h Shifts Max | Base Standards: MP = 190 CPH, FDD = 185 CPH | Replen Standard: 14 Moves/Hour")

st.markdown("---")

# --- CONTROL ROOM: STEP 1 PERFORMANCE & TIMING SLIDERS AT THE TOP ---
st.markdown("### ⚙️ Step 1: Configure Shift Run-Time Plan & Commodity Performance Sliders")
col_slider_time, col_slider_mp, col_slider_fdd = st.columns([1.2, 1, 1])

with col_slider_time:
    target_active_hours = st.slider(
        "Target Active Production Run-Time (Hours):",
        min_value=4.0, max_value=12.0, value=9.0, step=0.5,
        help="Adjust this parameter to see how changing your intended work duration window scales your required crew size."
    )

with col_slider_mp:
    mp_perf_contingency = st.slider(
        "Expected MP Team Pace (%):",
        min_value=50, max_value=160, value=120, step=5,
        help="Standard = 100%. Shift 5 fresh lines typically trend at a higher 120%+ velocity index."
    )
    mp_multiplier = mp_perf_contingency / 100.0

with col_slider_fdd:
    fdd_perf_contingency = st.slider(
        "Expected FDD Team Pace (%):",
        min_value=50, max_value=160, value=100, step=5,
        help="Standard = 100%. Heavy cube cold-chain zones typically run closer to baseline limits."
    )
    fdd_multiplier = fdd_perf_contingency / 100.0

st.markdown("---")

# --- LIVE FREIGHT & MANPOWER ENTRY GRID ---
st.markdown("### 📊 Step 2: Input Daily Outbound Case Volumes, Replenishment Moves, & Split Support Headcounts")
col_in_cases, col_in_moves, col_in_support_mp, col_in_support_fdd = st.columns(4)

with col_in_cases:
    st.markdown("#### 📦 Outbound Case Volumes")
    mp_cases = st.number_input("Meat & Produce (MP) Cases:", min_value=1000, max_value=250000, value=38500, step=1000)
    fdd_cases = st.number_input("Freezer, Dairy, Deli (FDD) Cases:", min_value=1000, max_value=250000, value=31500, step=1000)
    total_cases = mp_cases + fdd_cases

with col_in_moves:
    st.markdown("#### 🚜 Stock Replenishment Moves")
    meat_moves = st.number_input("Expected Meat Lift Moves:", min_value=0, max_value=1000, value=330, step=10)
    produce_moves = st.number_input("Expected Produce Lift Moves:", min_value=0, max_value=1000, value=410, step=10)
    dairy_deli_moves = st.number_input("Expected Dairy/Deli Lift Moves:", min_value=0, max_value=1000, value=180, step=10)
    freezer_moves = st.number_input("Expected Freezer Lift Moves:", min_value=0, max_value=1000, value=157, step=10)
    total_moves = meat_moves + produce_moves + dairy_deli_moves + freezer_moves

with col_in_support_mp:
    st.markdown("#### 🛠️ MP Support Headcount")
    mp_loaders = st.number_input("MP Outbound Dock Loaders:", min_value=0, max_value=50, value=3, step=1)
    mp_wrappers = st.number_input("MP Pallet Wrappers:", min_value=0, max_value=50, value=1, step=1)
    mp_chase = st.number_input("MP Outbound Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_mp_support = int(mp_loaders + mp_wrappers + mp_chase)

with col_in_support_fdd:
    st.markdown("#### ❄️ FDD Support Headcount")
    fdd_loaders = st.number_input("FDD Cold-Chain Loaders:", min_value=0, max_value=50, value=1, step=1)
    fdd_wrappers = st.number_input("FDD Cold-Chain Wrappers:", min_value=0, max_value=50, value=1, step=1)
    fdd_chase = st.number_input("FDD Cold-Chain Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_fdd_support = int(fdd_loaders + fdd_wrappers + fdd_chase)

st.markdown("---")

# --- SHIPPING WORKFORCE FORECAST MATH ENGINE ---
live_mp_cph = MP_BASE_CPH * mp_multiplier
live_fdd_cph = FDD_BASE_CPH * fdd_multiplier

live_mp_replen_mph = LIFT_BASE_MPH * mp_multiplier
live_fdd_replen_mph = LIFT_BASE_MPH * fdd_multiplier

# 1. Direct Picking Labor Calculations
mp_pick_hours_needed = mp_cases / live_mp_cph
fdd_pick_hours_needed = fdd_cases / live_fdd_cph
total_required_pick_hours = mp_pick_hours_needed + fdd_pick_hours_needed

scheduled_mp_pickers = int(math.ceil(mp_pick_hours_needed / target_active_hours))
scheduled_fdd_pickers = int(math.ceil(fdd_pick_hours_needed / target_active_hours))
total_scheduled_pickers = int(scheduled_mp_pickers + scheduled_fdd_pickers)

# 2. Lift Replenishment Labor Calculations (Exact Decimal Capacities)
meat_replen_hours = meat_moves / live_mp_replen_mph
produce_replen_hours = produce_moves / live_mp_replen_mph
dairy_deli_replen_hours = dairy_deli_moves / live_fdd_replen_mph
freezer_replen_hours = freezer_moves / live_fdd_replen_mph
total_required_replen_hours = meat_replen_hours + produce_replen_hours + dairy_deli_replen_hours + freezer_replen_hours

scheduled_meat_lifts = round(float(meat_replen_hours / target_active_hours), 1)
scheduled_produce_lifts = round(float(produce_replen_hours / target_active_hours), 1)
scheduled_dairy_deli_lifts = round(float(dairy_deli_replen_hours / target_active_hours), 1)
scheduled_freezer_lifts = round(float(freezer_replen_hours / target_active_hours), 1)
total_scheduled_lifts = round(float(total_required_replen_hours / target_active_hours), 1)

# 3. Calculate Projected Shift Length
if total_scheduled_pickers > 0:
    expected_shift_length_hours = (total_required_pick_hours / total_scheduled_pickers) + 1.0 
else:
    expected_shift_length_hours = 0.0
hours_int = int(expected_shift_length_hours)
mins_int = int((expected_shift_length_hours - hours_int) * 60)

# 4. REFINED COMMODITY CPH MATHEMATICS
active_run_hours = max(0.0, expected_shift_length_hours - 1.0)

mp_active_labor_hours = (scheduled_mp_pickers + total_mp_support) * active_run_hours
fdd_active_labor_hours = (scheduled_fdd_pickers + total_fdd_support) * active_run_hours

expected_mp_cph = mp_cases / mp_active_labor_hours if mp_active_labor_hours > 0 else 0.0
expected_fdd_cph = fdd_cases / fdd_active_labor_hours if fdd_active_labor_hours > 0 else 0.0

# --- CORE SUMMARY KPI METRICS BAR ---
st.markdown("### 🧮 Step 3: Core Performance Projections")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Total Required Pickers", value=f"{total_scheduled_pickers} Crew")
with kpi2:
    st.metric(label="Total Required Lifts", value=f"{total_scheduled_lifts} Drivers")

# DYNAMIC HTML CONTAINER COLORS BASED ON PERFORMANCE GOALS
# MP Threshold Check (Standard: 190 CPH)
if expected_mp_cph >= 190.0:
    mp_bg, mp_border, mp_text = "#dcfce7", "#22c55e", "#15803d" # Green Alert
else:
    mp_bg, mp_border, mp_text = "#fde8e8", "#f87171", "#9b1c1c" # Red Alert

# FDD Threshold Check (Standard: 185 CPH)
if expected_fdd_cph >= 185.0:
    fdd_bg, fdd_border, fdd_text = "#dcfce7", "#22c55e", "#15803d" # Green Alert
else:
    fdd_bg, fdd_border, fdd_text = "#fde8e8", "#f87171", "#9b1c1c" # Red Alert

with kpi3:
    st.markdown(f"""
        <div style="background-color:{mp_bg}; border: 2px solid {mp_border}; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #4b5563; font-weight: 500;">Expected MP Shipping CPH</p>
            <h2 style="margin: 5px 0 0 0; color: {mp_text}; font-size: 26px; font-weight: 700;">{round(expected_mp_cph, 1)} CPH</h2>
        </div>
    """, unsafe_html=True)

with kpi4:
    st.markdown(f"""
        <div style="background-color:{fdd_bg}; border: 2px solid {fdd_border}; border-radius: 8px; padding: 15px; text-align: center;">
            <p style="margin: 0; font-size: 14px; color: #4b5563; font-weight: 500;">Expected FDD Shipping CPH</p>
            <h2 style="margin: 5px 0 0 0; color: {fdd_text}; font-size: 26px; font-weight: 700;">{round(expected_fdd_cph, 1)} CPH</h2>
        </div>
    """, unsafe_html=True)

with kpi5:
    st.metric(label="Projected Shift Length", value=f"{hours_int}h {mins_int}m")

st.markdown("---")

# --- CONSOLIDATED CROSS-COMMODITY ROSTER TARGETS ---
st.subheader("📋 Floor Management Deployment Blueprint")
blueprint_matrix = [
    {"Commodity Zone Area": "Meat (M)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_mp_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{meat_moves} Moves", "Replen Drivers Needed": f"{scheduled_meat_lifts} Lifts"},
    {"Commodity Zone Area": "Produce (P)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_mp_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{produce_moves} Moves", "Replen Drivers Needed": f"{scheduled_produce_lifts} Lifts"},
    {"Commodity Zone Area": "Dairy & Deli (DD)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_fdd_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{dairy_deli_moves} Moves", "Replen Drivers Needed": f"{scheduled_dairy_deli_lifts} Lifts"},
    {"Commodity Zone Area": "Freezer (F)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_fdd_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{freezer_moves} Moves", "Replen Drivers Needed": f"{scheduled_freezer_lifts} Lifts"},
]
