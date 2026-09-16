import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Outbound Dock Command Center", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- GLOBAL STATIC OPERATIONAL PARAMETERS ---
MP_CPH_GOAL = 190
FDD_CPH_GOAL = 185
PAID_SHIFT_HOURS = 11.0
ACTIVE_SHIFT_HOURS = 10.0

# --- TITLE ---
st.title("🏭 Shipping & Replenishment Roster Planner")
st.caption("Active Configurations: 11h Shifts Max | MP Target: 190 CPH | FDD Target: 185 CPH | Replen Target: 14 Moves/Hour")

st.markdown("---")

# --- CONTROL ROOM: LIVE INPUT CONFIGURATION PANELS ---
col_in_time, col_in_contingency = st.columns(2)

with col_in_time:
    st.markdown("### ⏱️ Target Shift Duration")
    target_active_hours = st.slider(
        "Target Active Production Run-Time (Hours):",
        min_value=4.0, max_value=12.0, value=9.0, step=0.5,
        help="Adjust this parameter to see how changing your intended work duration window scales your required crew size."
    )

with col_in_contingency:
    st.markdown("### ⚡ Live Team Performance Contingency")
    team_perf_contingency = st.slider(
        "Expected Team Performance Pace (% Baseline Standard):",
        min_value=50, max_value=160, value=120, step=5,
        help="Standard pace = 100%. Shift 5 night crews typically clear lanes at a 120%+ velocity index."
    )
    performance_multiplier = team_perf_contingency / 100.0

st.markdown("---")

col_in_cases, col_in_moves = st.columns(2)

with col_in_cases:
    st.markdown("### 📦 Outbound Case Volumes")
    mp_cases = st.number_input("Meat & Produce (MP) Total Shift Cases:", min_value=1000, max_value=250000, value=38500, step=1000)
    fdd_cases = st.number_input("Freezer, Dairy, Deli (FDD) Total Shift Cases:", min_value=1000, max_value=250000, value=31500, step=1000)
    total_cases = mp_cases + fdd_cases

with col_in_moves:
    st.markdown("### 🚜 Stock Replenishment Moves")
    meat_moves = st.number_input("Expected Meat Lift Moves:", min_value=0, max_value=1000, value=330, step=10)
    produce_moves = st.number_input("Expected Produce Lift Moves:", min_value=0, max_value=1000, value=410, step=10)
    dairy_deli_moves = st.number_input("Expected Dairy/Deli Lift Moves:", min_value=0, max_value=1000, value=120, step=10)
    freezer_moves = st.number_input("Expected Freezer Lift Moves:", min_value=0, max_value=1000, value=157, step=10)
    total_moves = meat_moves + produce_moves + dairy_deli_moves + freezer_moves

st.markdown("---")

# --- SHIPPING WORKFORCE FORECAST MATH ENGINE WITH VARIABLE DURATION ---
live_mp_cph = 190.0 * performance_multiplier
live_fdd_cph = 185.0 * performance_multiplier
live_replen_mph = 14.0 * performance_multiplier

mp_pick_hours_needed = mp_cases / live_mp_cph
fdd_pick_hours_needed = fdd_cases / live_fdd_cph
total_required_pick_hours = mp_pick_hours_needed + fdd_pick_hours_needed

# Keep orderfillers as whole numbers for physical staffing count allocations
scheduled_mp_pickers = math.ceil(mp_pick_hours_needed / target_active_hours)
scheduled_fdd_pickers = math.ceil(fdd_pick_hours_needed / target_active_hours)
total_scheduled_pickers = scheduled_mp_pickers + scheduled_fdd_pickers

meat_replen_hours = meat_moves / live_replen_mph
produce_replen_hours = produce_moves / live_replen_mph
dairy_deli_replen_hours = dairy_deli_moves / live_replen_mph
freezer_replen_hours = freezer_moves / live_replen_mph
total_required_replen_hours = total_moves / live_replen_mph

# REMOVED math.ceil() TO ALLOW EXACT DECIMALS FOR LIFT OPERATIONS SHARE TRACKING
scheduled_meat_lifts = round(meat_replen_hours / target_active_hours, 1)
scheduled_produce_lifts = round(produce_replen_hours / target_active_hours, 1)
scheduled_dairy_deli_lifts = round(dairy_deli_replen_hours / target_active_hours, 1)
scheduled_freezer_lifts = round(freezer_replen_hours / target_active_hours, 1)
total_scheduled_lifts = round(total_required_replen_hours / target_active_hours, 1)

if total_scheduled_pickers > 0:
    expected_shift_length_hours = (total_required_pick_hours / total_scheduled_pickers) + 1.0
else:
    expected_shift_length_hours = 0.0
hours_int = int(expected_shift_length_hours)
mins_int = int((expected_shift_length_hours - hours_int) * 60)

# --- CORE SUMMARY KPI METRICS BAR ---
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Required Pickers", value=f"{total_scheduled_pickers} Orderfillers")
with kpi2:
    st.metric(label="Required Drivers", value=f"{total_scheduled_lifts} Lift Drivers", help="Total exact decimal headcount required for direct replenishment moves.")
with kpi3:
    st.metric(label="Total Expected Moves", value=f"{total_moves} Pallets")
with kpi4:
    st.metric(label="Calculated Roster Run-Time", value=f"{hours_int}h {mins_int}m")
with kpi5:
    st.metric(label="Total Operational Pick Hours", value=f"{round(total_required_pick_hours, 1)} Hours")

st.markdown("---")

# --- CONSOLIDATED CROSS-COMMODITY ROSTER TARGETS ---
st.subheader("📋 Floor Management Deployment Blueprint")
blueprint_matrix = [
    {"Commodity Zone Area": "Meat (M)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{meat_moves} Moves", "Replen Drivers Needed": f"{scheduled_meat_lifts} Lifts"},
    {"Commodity Zone Area": "Produce (P)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{produce_moves} Moves", "Replen Drivers Needed": f"{scheduled_produce_lifts} Lifts"},
    {"Commodity Zone Area": "Dairy & Deli (DD)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{dairy_deli_moves} Moves", "Replen Drivers Needed": f"{scheduled_dairy_deli_lifts} Lifts"},
    {"Commodity Zone Area": "Freezer (F)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{freezer_moves} Moves", "Replen Drivers Needed": f"{scheduled_freezer_lifts} Lifts"},
    {"Commodity Zone Area": "📊 TOTAL ACTIVE FACILITY", "Pacing Target Standard": "Synchronized Speed Matrix", "Outbound Case Load": f"{int(total_cases):,} Cases", "Orderfillers Needed": f"{total_scheduled_pickers} Pickers", "Replen Moves Count": f"{total_moves} Moves", "Replen Drivers Needed": f"{total_scheduled_lifts} Lift Drivers"}
]
st.dataframe(pd.DataFrame(blueprint_matrix), use_container_width=True, hide_index=True)
