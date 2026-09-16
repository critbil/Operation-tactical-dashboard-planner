import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Shipping & Replen Command Center", layout="wide")

is_shared_view = st.query_params.get("mode") == "shared"

# --- GLOBAL STATIC OPERATIONAL PARAMETERS ---
MP_BASE_CPH = 190.0
FDD_BASE_CPH = 185.0
LIFT_BASE_MPH = 14.0
PAID_SHIFT_HOURS = 11.0

# --- TITLE ---
st.title("🏭 Shipping Department Labor & Capacity Command Center")
st.caption("Active Configurations: 11h Shifts Max | MP Standard: 190 CPH | FDD Standard: 185 CPH | Replen Standard: 14 Moves/Hour")

st.markdown("---")

# --- CONTROL ROOM: LIVE INPUT PANELS ---
col_in_time, col_in_contingency = st.columns(2)

with col_in_time:
    st.markdown("### ⏱️ Target Shift Plan")
    target_active_hours = st.slider(
        "Target Active Production Run-Time (Hours):",
        min_value=4.0, max_value=12.0, value=9.0, step=0.5,
        help="Adjust this parameter to see how changing your intended work duration window scales your required crew size."
    )

with col_in_contingency:
    st.markdown("### ⚡ Performance Contingency")
    team_perf_contingency = st.slider(
        "Expected Team Performance Pace (% Baseline Standard):",
        min_value=50, max_value=160, value=120, step=5,
        help="Standard pace = 100%. Shift 5 night crews typically clear lanes at a 120%+ velocity index."
    )
    performance_multiplier = team_perf_contingency / 100.0

st.markdown("---")

col_in_cases, col_in_moves, col_in_support = st.columns([1, 1, 1.2])

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

with col_in_support:
    st.markdown("### 🛠️ Standard Support Headcount")
    # MANAGERS INPUT THEIR OWN LIVE STAFFING FOR SUPPORT POSITIONS HERE
    loaders_count = st.number_input("Actual Scheduled Outbound Dock Loaders:", min_value=0, max_value=50, value=4, step=1)
    wrappers_count = st.number_input("Actual Scheduled Pallet Wrappers:", min_value=0, max_value=50, value=2, step=1)
    chase_count = st.number_input("Actual Scheduled Outbound Chase Runners:", min_value=0, max_value=10, value=1, step=1)
    total_fixed_support_headcount = loaders_count + wrappers_count + chase_count

st.markdown("---")

# --- SHIPPING WORKFORCE FORECAST MATH ENGINE ---
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
    expected_shift_length_hours = (total_required_pick_hours / total_scheduled_pickers) + 1.0 # 1 hr break
else:
    expected_shift_length_hours = 0.0
hours_int = int(expected_shift_length_hours)
mins_int = int((expected_shift_length_hours - hours_int) * 60)

# 4. Total Combined Building Burden Pool Compilation Math
total_building_headcount = total_scheduled_pickers + total_scheduled_lifts + total_fixed_support_headcount
# Total active working hours = Picker active hours + Lift active hours + Support active hours (paid hours minus 1hr break)
total_building_active_hours = (total_scheduled_pickers * (expected_shift_length_hours - 1.0)) + \
                               (total_scheduled_lifts * (expected_shift_length_hours - 1.0)) + \
                               (total_fixed_support_headcount * (expected_shift_length_hours - 1.0))

# 5. THE OUTPUT METRIC: True Burdened Expected Building CPH for the Day
if total_building_active_hours > 0:
    expected_building_cph = total_cases / total_building_active_hours
else:
    expected_building_cph = 0.0

# --- CORE SUMMARY KPI METRICS BAR ---
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:
    st.metric(label="Required Pickers", value=f"{total_scheduled_pickers} Crew")
with kpi2:
    st.metric(label="Required Drivers", value=f"{total_scheduled_lifts} Lifts")
with kpi3:
    st.metric(label="Total Expected Moves", value=f"{total_moves} Pallets")
with kpi4:
    # EXPECTED BUILDING CPH METRIC CARD OUTPUT
    st.metric(
        label="Expected Daily Building CPH", 
        value=f"{round(expected_building_cph, 1)} CPH",
        help="Efficiency Index: Total Outbound Cases divided by Total Active Department Hours Pool (Pickers + Lift Drivers + Loaders + Wrappers + Chase Runners)."
    )
with kpi5:
    st.metric(label="Projected Roster Run-Time", value=f"{hours_int}h {mins_int}m")

st.markdown("---")

# --- CONSOLIDATED CROSS-COMMODITY ROSTER TARGETS ---
st.subheader("📋 Floor Management Deployment Blueprint")
blueprint_matrix = [
    {"Commodity Zone Area": "Meat (M)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{meat_moves} Moves", "Replen Drivers Needed": f"{scheduled_meat_lifts} Lifts"},
    {"Commodity Zone Area": "Produce (P)", "Pacing Target Standard": f"{round(live_mp_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(mp_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((mp_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{produce_moves} Moves", "Replen Drivers Needed": f"{scheduled_produce_lifts} Lifts"},
    {"Commodity Zone Area": "Dairy & Deli (DD)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.55):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.55) / target_active_hours)} Staff", "Replen Moves Count": f"{dairy_deli_moves} Moves", "Replen Drivers Needed": f"{scheduled_dairy_deli_lifts} Lifts"},
    {"Commodity Zone Area": "Freezer (F)", "Pacing Target Standard": f"{round(live_fdd_cph)} CPH / {round(live_replen_mph, 1)} MPH", "Outbound Case Load": f"{int(fdd_cases * 0.45):,} Cases*", "Orderfillers Needed": f"{math.ceil((fdd_pick_hours_needed * 0.45) / target_active_hours)} Staff", "Replen Moves Count": f"{freezer_moves} Moves", "Replen Drivers Needed": f"{scheduled_freezer_lifts} Lifts"},
    {"Commodity Zone Area": "📊 TOTAL DIRECT POOL", "Pacing Target Standard": "Synchronized Speed Matrix", "Outbound Case Load": f"{int(total_cases):,} Cases", "Orderfillers Needed": f"{total_scheduled_pickers} Pickers", "Replen Moves Count": f"{total_moves} Moves", "Replen Drivers Needed": f"{total_scheduled_lifts} Lift Drivers"}
]
st.dataframe(pd.DataFrame(blueprint_matrix), use_container_width=True, hide_index=True)

st.markdown("---")

# --- CONSOLIDATED DEPARTMENT POOL OVERHEAD LEDGER ---
st.subheader("📋 Total Shipping Department Roster Pool Ledger")
roster_matrix = [
    {"Shipping Department Role Block": "Orderfillers (Direct Pickers)", "Scheduled Headcount Pool": f"{total_scheduled_pickers} Staff", "Paid Hours Burden Pool": f"{total_scheduled_pickers * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Variable (Picker-Gated Timeline)"},
    {"Shipping Department Role Block": "Forklift Operators (Replen Drivers)", "Scheduled Headcount Pool": f"{total_scheduled_lifts} Staff", "Paid Hours Burden Pool": f"{total_scheduled_lifts * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Variable (Exact Decimal Capacities)"},
    {"Shipping Department Role Block": "Outbound Dock Loaders", "Scheduled Headcount Pool": f"{loaders_count} Staff", "Paid Hours Burden Pool": f"{loaders_count * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Shift Standard (Manager Manual Input)"},
    {"Shipping Department Role Block": "Pallet Wrappers", "Scheduled Headcount Pool": f"{wrappers_count} Staff", "Paid Hours Burden Pool": f"{wrappers_count * PAID_SHIFT_HOURS} Hrs", "Role Allocation Type": "Shift Standard (Manager Manual Input)"},
