import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Perishable Shipping Performance Planner", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- GLOBAL STATIC OPERATIONAL PARAMETERS ---
MP_BASE_CPH = 190.0
FDD_BASE_CPH = 185.0
LIFT_BASE_MPH = 14.0
PAID_SHIFT_HOURS = 11.0

st.title("🏭 Shipping Department Performance Forcasting")
st.caption("Active Configurations: 11h Shifts Max | Base Standards: MP = 190 CPH, FDD = 185 CPH | Replen Standard: 14 Moves/Hour")

st.markdown("---")

# --- CONTROL ROOM: STEP 1 PERFORMANCE & TIMING SLIDERS AT THE TOP ---
st.markdown("### ⚙️ Step 1: Forecast Shift Run-Time Plan & Commodity Performance ")
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
    st.markdown("#### 🚜 Replenishment Moves")
    meat_moves = st.number_input("Expected Meat Lift Moves:", min_value=0, max_value=1000, value=330, step=10)
    produce_moves = st.number_input("Expected Produce Lift Moves:", min_value=0, max_value=1000, value=410, step=10)
    dairy_deli_moves = st.number_input("Expected Dairy/Deli Lift Moves:", min_value=0, max_value=1000, value=180, step=10)
    freezer_moves = st.number_input("Expected Freezer Lift Moves:", min_value=0, max_value=1000, value=157, step=10)
    total_moves = meat_moves + produce_moves + dairy_deli_moves + freezer_moves

with col_in_support_mp:
    st.markdown("#### 🥩 MP Support Headcount")
    mp_loaders = st.number_input("MP Outbound Dock Loaders:", min_value=0, max_value=50, value=3, step=1)
    mp_wrappers = st.number_input("MP Pallet Wrappers:", min_value=0, max_value=50, value=1, step=1)
    mp_chase = st.number_input("MP Outbound Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_mp_support = int(mp_loaders + mp_wrappers + mp_chase)

with col_in_support_fdd:
    st.markdown("#### ❄️ FDD Support Headcount")
    fdd_loaders = st.number_input("FDD OutBound Dock Loaders:", min_value=0, max_value=50, value=1, step=1)
    fdd_wrappers = st.number_input("FDD Pallet Wrappers:", min_value=0, max_value=50, value=1, step=1)
    fdd_chase = st.number_input("FDD Chase Runners:", min_value=0, max_value=10, value=1, step=1)
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
st.markdown("### 🧮 Step 3: Performance Projections")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Total Required Pickers", value=f"{total_scheduled_pickers} Order-Fillers")
with kpi2:
    st.metric(label="Total Required Lifts", value=f"{total_scheduled_lifts} Drivers")

# Color setups
mp_color = "#15803d" if expected_mp_cph >= 190.0 else "#9b1c1c"
mp_bg = "#dcfce7" if expected_mp_cph >= 190.0 else "#fde8e8"

fdd_color = "#15803d" if expected_fdd_cph >= 185.0 else "#9b1c1c"
fdd_bg = "#dcfce7" if expected_fdd_cph >= 185.0 else "#fde8e8"

final_mp_val = str(round(expected_mp_cph, 1))
final_fdd_val = str(round(expected_fdd_cph, 1))

with kpi3:
    st.html(
        f'<div style="background-color: {mp_bg}; border: 2px solid {mp_color}; border-radius: 8px; padding: 12px; text-align: center;">'
        f'<p style="margin: 0; font-size: 13px; color: #4b5563; font-weight: 500;">Expected MP Shipping CPH</p>'
        f'<h2 style="margin: 4px 0 0 0; color: {mp_color}; font-size: 24px; font-weight: 700;">{final_mp_val} CPH</h2>'
        f'</div>'
    )

with kpi4:
    st.html(
        f'<div style="background-color: {fdd_bg}; border: 2px solid {fdd_color}; border-radius: 8px; padding: 12px; text-align: center;">'
        f'<p style="margin: 0; font-size: 13px; color: #4b5563; font-weight: 500;">Expected FDD Shipping CPH</p>'
        f'<h2 style="margin: 4px 0 0 0; color: {fdd_color}; font-size: 24px; font-weight: 700;">{final_fdd_val} CPH</h2>'
        f'</div>'
    )

with kpi5:
    st.metric(label="Projected Shift Length", value=f"{hours_int}h {mins_int}m")

st.markdown("---")

# --- CONSOLIDATED CROSS-COMMODITY ROSTER TARGETS ---
st.subheader("📋 Floor Management Production Analysis")

# CLEAN RE-MAPPED COMPILING DICTIONARY MATRIX
blueprint_matrix = [
    {"Commodity Zone Area": "Meat (M)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_mp_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.55):,} Cases", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{meat_moves} Moves", "Replen Drivers Needed": f"{scheduled_meat_lifts} Lifts"},
    {"Commodity Zone Area": "Produce (P)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_mp_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.45):,} Cases", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{produce_moves} Moves", "Replen Drivers Needed": f"{scheduled_produce_lifts} Lifts"},
    {"Commodity Zone Area": "Dairy & Deli (DD)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_fdd_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.55):,} Cases", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{dairy_deli_moves} Moves", "Replen Drivers Needed": f"{scheduled_dairy_deli_lifts} Lifts"},
    {"Commodity Zone Area": "Freezer (F)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_fdd_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.45):,} Cases", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{freezer_moves} Moves", "Replen Drivers Needed": f"{scheduled_freezer_lifts} Lifts"},
]
st.dataframe(pd.DataFrame(blueprint_matrix), use_container_width=True, hide_index=True)
