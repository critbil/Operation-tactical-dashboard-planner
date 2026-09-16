import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Split-Commodity Command Center", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# GLOBAL STATIC OPERATIONAL GOALS
MP_BASE_CPH = 190.0
FDD_BASE_CPH = 185.0
LIFT_BASE_MPH = 14.0
PAID_SHIFT_HOURS = 11.0

st.title("🏭 Shipping Department Commodity-Isolated Command Center")
st.caption("Active Configurations: 11h Shifts Max | MP Picker Standard: 190 CPH | FDD Picker Standard: 185 CPH | Lift: 14 MPH")

st.markdown("---")

# --- CONTROL ROOM: LIVE INPUT PANELS ---
st.markdown("### ⚙️ Step 1: Configure Shift Run & Pacing Contingencies")
col_in_time, col_in_contingency = st.columns(2)

with col_in_time:
    target_active_hours = st.slider(
        "Target Active Production Run-Time (Hours):",
        min_value=4.0, max_value=12.0, value=9.0, step=0.5,
        help="Adjust this parameter to see how changing your intended work duration window scales your required crew size."
    )

with col_in_contingency:
    team_perf_contingency = st.slider(
        "Expected Team Performance Pace (% Baseline Standard):",
        min_value=50, max_value=160, value=120, step=5,
        help="Standard pace = 100%. Shift 5 night crews typically clear lanes at a 120%+ velocity index."
    )
    performance_multiplier = team_perf_contingency / 100.0

st.markdown("---")

# lIVE FREIGHT & MANPOWER
st.markdown("### 📊 Step 2: Input Daily Freight Drops & Split Support Headcounts")
col_in_cases, col_in_moves, col_in_support_mp, col_in_support_fdd = st.columns([1, 1, 1, 1])

with col_in_cases:
    st.markdown("#### 📦 Outbound Case Volumes")
    mp_cases = st.number_input("Meat & Produce (MP) Total Shift Cases:", min_value=1000, max_value=250000, value=38500, step=1000)
    fdd_cases = st.number_input("Freezer, Dairy, Deli (FDD) Total Shift Cases:", min_value=1000, max_value=250000, value=31500, step=1000)
    total_cases = mp_cases + fdd_cases

with col_in_moves:
    st.markdown("#### 🚜 Replenishment Moves")
    meat_moves = st.number_input("Expected Meat Lift Moves:", min_value=0, max_value=1000, value=330, step=10)
    produce_moves = st.number_input("Expected Produce Lift Moves:", min_value=0, max_value=1000, value=410, step=10)
    dairy_deli_moves = st.number_input("Expected Dairy/Deli Lift Moves:", min_value=0, max_value=1000, value=120, step=10)
    freezer_moves = st.number_input("Expected Freezer Lift Moves:", min_value=0, max_value=1000, value=157, step=10)
    total_moves = meat_moves + produce_moves + dairy_deli_moves + freezer_moves

with col_in_support_mp:
    st.markdown("#### 🛠️ MP Support Headcount")
    mp_loaders = st.number_input("MP Dock Loaders:", min_value=0, max_value=50, value=2, step=1)
    mp_wrappers = st.number_input("MP Pallet Wrappers:", min_value=0, max_value=50, value=1, step=1)
    mp_chase = st.number_input("MP Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_mp_support = mp_loaders + mp_wrappers + mp_chase

with col_in_support_fdd:
    st.markdown("#### ❄️ FDD Support Headcount")
    fdd_loaders = st.number_input("FDD Dock Loaders:", min_value=0, max_value=50, value=2, step=1)
    fdd_wrappers = st.number_input("FDD Pallet Wrappers:", min_value=0, max_value=50, value=1, step=1)
    fdd_chase = st.number_input("FDD Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_fdd_support = fdd_loaders + fdd_wrappers + fdd_chase

st.markdown("---")

# SHIPPING WORKFORCE FORECAST ENGINE
live_mp_cph = MP_BASE_CPH * performance_multiplier
live_fdd_cph = FDD_BASE_CPH * performance_multiplier
live_replen_mph = LIFT_BASE_MPH * performance_multiplier

# 1. Direct Picking Labor Calculations
mp_pick_hours_needed = mp_cases / live_mp_cph
fdd_pick_hours_needed = fdd_cases / live_fdd_cph
total_required_pick_hours = mp_pick_hours_needed + fdd_pick_hours_needed

scheduled_mp_pickers = math.ceil(mp_pick_hours_needed / target_active_hours)
scheduled_fdd_pickers = math.ceil(fdd_pick_hours_needed / target_active_hours)
total_scheduled_pickers = scheduled_mp_pickers + scheduled_fdd_pickers

# 2. Lift Replenishment Labor Calculations (Exact Decimal Capacities)
meat_replen_hours = meat_moves / live_replen_mph
produce_replen_hours = produce_moves / live_replen_mph
dairy_deli_replen_hours = dairy_deli_moves / live_replen_mph
freezer_replen_hours = freezer_moves / live_replen_mph
total_required_replen_hours = total_moves / live_replen_mph

scheduled_meat_lifts = round(meat_replen_hours / target_active_hours, 1)
scheduled_produce_lifts = round(produce_replen_hours / target_active_hours, 1)
scheduled_dairy_deli_lifts = round(dairy_deli_replen_hours / target_active_hours, 1)
scheduled_freezer_lifts = round(freezer_replen_hours / target_active_hours, 1)
total_scheduled_lifts = round(total_required_replen_hours / target_active_hours, 1)

# 3. Calculate Projected Shift Length (Picker-gated runtime timeline)
if total_scheduled_pickers > 0:
    expected_shift_length_hours = (total_required_pick_hours / total_scheduled_pickers) + 1.0 
else:
    expected_shift_length_hours = 0.0
hours_int = int(expected_shift_length_hours)
mins_int = int((expected_shift_length_hours - hours_int) * 60)

# 4. REFINED COMMODITY CPH MATHEMATICS (Lifts Completely Excluded)
active_run_hours = max(0.0, expected_shift_length_hours - 1.0)

mp_active_labor_hours = (scheduled_mp_pickers + total_mp_support) * active_run_hours
fdd_active_labor_hours = (scheduled_fdd_pickers + total_fdd_support) * active_run_hours

expected_mp_cph = mp_cases / mp_active_labor_hours if mp_active_labor_hours > 0 else 0.0
expected_fdd_cph = fdd_cases / fdd_active_labor_hours if fdd_active_labor_hours > 0 else 0.0

# --- CORE SUMMARY KPI METRICS BAR ---
st.markdown("### 🧮 Step 3: Core Performance Projections")
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Total Required Order-Fillers", value=f"{total_scheduled_pickers} Crew")
with kpi2:
    st.metric(label="Total Required Lifts", value=f"{total_scheduled_lifts} Drivers")
with kpi3:
    st.metric(label="Expected MP Shipping CPH", value=f"{round(expected_mp_cph, 1)} CPH", help="MP Cases divided by (MP Pickers + MP Loaders + MP Wrappers + MP Chase) active hours pool.")
with kpi4:
    st.metric(label="Expected FDD Shipping CPH", value=f"{round(expected_fdd_cph, 1)} CPH", help="FDD Cases divided by (FDD Pickers + FDD Loaders + FDD Wrappers + FDD Chase) active hours pool.")
with kpi5:
    st.metric(label="Projected Shift Length", value=f"{hours_int}h {mins_int}m")

st.markdown("---")

# CONSOLIDATED CROSS-COMMODITY TARGETS
st.subheader("📋 Floor Management Blueprint")
blueprint_matrix = [
    {"Commodity Zone Area": "Meat (M)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{meat_moves} Moves", "Replen Drivers Needed": f"{scheduled_meat_lifts} Lifts"},
    {"Commodity Zone Area": "Produce (P)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{produce_moves} Moves", "Replen Drivers Needed": f"{scheduled_produce_lifts} Lifts"},
    {"Commodity Zone Area": "Dairy & Deli (DD)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{dairy_deli_moves} Moves", "Replen Drivers Needed": f"{scheduled_dairy_deli_lifts} Lifts"},
    {"Commodity Zone Area": "Freezer (F)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{freezer_moves} Moves", "Replen Drivers Needed": f"{scheduled_freezer_lifts} Lifts"},
    {"Commodity Zone Area": "📊 TOTAL ACTIVE POOL", "Pacing Target Standard": "Synchronized Matrix", "Outbound Case Load": f"{int(total_cases):,} Cases", "Orderfillers Needed": f"{total_scheduled_pickers} Pickers", "Replen Moves Count": f"{total_moves} Moves", "Replen Drivers Needed": f"{total_scheduled_lifts} Lift Drivers"}
]
st.dataframe(pd.DataFrame(blueprint_matrix), use_container_width=True, hide_index=True)

st.markdown("---")

# CONSOLIDATED DEPARTMENT
st.subheader("📋 Total Shipping Department Roster")
total_all_staff = total_scheduled_pickers + total_scheduled_lifts + total_mp_support + total_fdd_support
roster_matrix = [
    {"Shipping Department Role ": "Orderfillers (Direct Pickers)", "Scheduled Headcount": f"{total_scheduled_pickers} Staff", "Paid Hours Pool": f"{total_scheduled_pickers * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Variable (Picker-Gated)"},
    {"Shipping Department Role ": "Forklift Operators (Replen Drivers)", "Scheduled Headcount": f"{total_scheduled_lifts} Staff", "Paid Hours Pool": f"{total_scheduled_lifts * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Variable (Exact Decimals)"},
    {"Shipping Department Role ": "MP Outbound Support (Load/Wrap/Chase)", "Scheduled Headcount": f"{total_mp_support} Staff", "Paid Hours Pool": f"{total_mp_support * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Shift Standard (MP Dock)"},
]
