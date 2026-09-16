import math

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Operations Analytics & Performance Dashboard",
    layout="wide"
)

FRESH_FOOD_BASE_CPH = 190.0
COLD_CHAIN_BASE_CPH = 185.0
BASE_REPLENISHMENT_MPH = 14.0
MAX_SHIFT_HOURS = 11.0

st.title("🏭 Operations Analytics & Performance Dashboard")

st.caption(
    "Interactive workforce planning and performance projection tool | "
    "Illustrative operational standards and data"
)

st.markdown("---")

st.markdown("### ⚙️ Step 1: Set Performance & labor forecasting ")

col_time, col_fresh, col_cold = st.columns([1.2, 1, 1])

with col_time:

    target_active_hours = st.slider(
        "Target Active Production Run-Time (Hours)",
        min_value=4.0,
        max_value=float(MAX_SHIFT_HOURS),
        value=9.0,
        step=0.5,
        help=(
            "Adjust the intended active production window. "
            "The model uses this value to estimate required staffing."
        )
    )

with col_fresh:

    fresh_food_performance_pct = st.slider(
        "Fresh Food Expected Performance (%)",
        min_value=50,
        max_value=160,
        value=120,
        step=5,
        help=(
            "Adjust expected performance relative to the "
            "illustrative baseline standard."
        )
    )

    fresh_food_multiplier = fresh_food_performance_pct / 100.0

with col_cold:

    cold_chain_performance_pct = st.slider(
        "Cold Chain Expected Performance (%)",
        min_value=50,
        max_value=160,
        value=100,
        step=5,
        help=(
            "Adjust expected performance relative to the "
            "illustrative baseline standard."
        )
    )

    cold_chain_multiplier = cold_chain_performance_pct / 100.0

st.markdown("---")

st.markdown("### 📊 Step 2: Enter Daily Operational Inputs")

col_cases, col_moves, col_fresh_support, col_cold_support = st.columns(4)

with col_cases:

    st.markdown("#### 📦 Outbound Case Volumes")

    fresh_food_cases = st.number_input(
        "Fresh Food Cases",
        min_value=1000,
        max_value=250000,
        value=38500,
        step=1000
    )

    cold_chain_cases = st.number_input(
        "Cold Chain Cases",
        min_value=1000,
        max_value=250000,
        value=31500,
        step=1000
    )

with col_moves:

    st.markdown("#### 🚜 Replenishment Moves")

    meat_moves = st.number_input(
        "Meat Replenishment Moves",
        min_value=0,
        max_value=1000,
        value=330,
        step=10
    )

    produce_moves = st.number_input(
        "Produce Replenishment Moves",
        min_value=0,
        max_value=1000,
        value=410,
        step=10
    )

    dairy_deli_moves = st.number_input(
        "Dairy & Deli Replenishment Moves",
        min_value=0,
        max_value=1000,
        value=180,
        step=10
    )

    frozen_moves = st.number_input(
        "Frozen Replenishment Moves",
        min_value=0,
        max_value=1000,
        value=157,
        step=10
    )

with col_fresh_support:

    st.markdown("#### 🥩 Fresh Food Support Staff")

    fresh_food_loaders = st.number_input(
        "Fresh Food Dock Loaders",
        min_value=0,
        max_value=50,
        value=3,
        step=1
    )

    fresh_food_wrappers = st.number_input(
        "Fresh Food Pallet Wrappers",
        min_value=0,
        max_value=50,
        value=1,
        step=1
    )

    fresh_food_runners = st.number_input(
        "Fresh Food Support Runners",
        min_value=0,
        max_value=10,
        value=1,
        step=1
    )

    total_fresh_food_support = int(
        fresh_food_loaders
        + fresh_food_wrappers
        + fresh_food_runners
    )

with col_cold_support:

    st.markdown("#### ❄️ Cold Chain Support Staff")

    cold_chain_loaders = st.number_input(
        "Cold Chain Dock Loaders",
        min_value=0,
        max_value=50,
        value=1,
        step=1
    )

    cold_chain_wrappers = st.number_input(
        "Cold Chain Pallet Wrappers",
        min_value=0,
        max_value=50,
        value=1,
        step=1
    )

    cold_chain_runners = st.number_input(
        "Cold Chain Support Runners",
        min_value=0,
        max_value=10,
        value=1,
        step=1
    )

    total_cold_chain_support = int(
        cold_chain_loaders
        + cold_chain_wrappers
        + cold_chain_runners
    )

st.markdown("---")

fresh_food_cph = (
    FRESH_FOOD_BASE_CPH
    * fresh_food_multiplier
)

cold_chain_cph = (
    COLD_CHAIN_BASE_CPH
    * cold_chain_multiplier
)

fresh_food_replenishment_mph = (
    BASE_REPLENISHMENT_MPH
    * fresh_food_multiplier
)

cold_chain_replenishment_mph = (
    BASE_REPLENISHMENT_MPH
    * cold_chain_multiplier
)

fresh_food_pick_hours = (
    fresh_food_cases / fresh_food_cph
)

cold_chain_pick_hours = (
    cold_chain_cases / cold_chain_cph
)

total_required_pick_hours = (
    fresh_food_pick_hours
    + cold_chain_pick_hours
)

required_fresh_food_pickers = int(
    math.ceil(
        fresh_food_pick_hours
        / target_active_hours
    )
)

required_cold_chain_pickers = int(
    math.ceil(
        cold_chain_pick_hours
        / target_active_hours
    )
)

total_required_pickers = (
    required_fresh_food_pickers
    + required_cold_chain_pickers
)

meat_replenishment_hours = (
    meat_moves
    / fresh_food_replenishment_mph
)

produce_replenishment_hours = (
    produce_moves
    / fresh_food_replenishment_mph
)

dairy_deli_replenishment_hours = (
    dairy_deli_moves
    / cold_chain_replenishment_mph
)

frozen_replenishment_hours = (
    frozen_moves
    / cold_chain_replenishment_mph
)

total_required_replenishment_hours = (
    meat_replenishment_hours
    + produce_replenishment_hours
    + dairy_deli_replenishment_hours
    + frozen_replenishment_hours
)

required_meat_replenishment_staff = round(
    meat_replenishment_hours
    / target_active_hours,
    1
)

required_produce_replenishment_staff = round(
    produce_replenishment_hours
    / target_active_hours,
    1
)

required_dairy_deli_replenishment_staff = round(
    dairy_deli_replenishment_hours
    / target_active_hours,
    1
)

required_frozen_replenishment_staff = round(
    frozen_replenishment_hours
    / target_active_hours,
    1
)

total_required_replenishment_staff = round(
    total_required_replenishment_hours
    / target_active_hours,
    1
)

if total_required_pickers > 0:

    projected_shift_hours = (
        total_required_pick_hours
        / total_required_pickers
    ) + 1.0

else:

    projected_shift_hours = 0.0

projected_shift_hours = min(
    projected_shift_hours,
    MAX_SHIFT_HOURS
)

shift_hours = int(projected_shift_hours)

shift_minutes = int(
    (projected_shift_hours - shift_hours)
    * 60
)

active_run_hours = max(
    0.0,
    projected_shift_hours - 1.0
)

fresh_food_active_labor_hours = (
    required_fresh_food_pickers
    + total_fresh_food_support
) * active_run_hours

cold_chain_active_labor_hours = (
    required_cold_chain_pickers
    + total_cold_chain_support
) * active_run_hours

projected_fresh_food_cph = (
    fresh_food_cases
    / fresh_food_active_labor_hours
    if fresh_food_active_labor_hours > 0
    else 0.0
)

projected_cold_chain_cph = (
    cold_chain_cases
    / cold_chain_active_labor_hours
    if cold_chain_active_labor_hours > 0
    else 0.0
)

st.markdown("### 🧮 Step 3: Performance Projections")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

with kpi1:

    st.metric(
        label="Required Pickers",
        value=f"{total_required_pickers}"
    )

with kpi2:

    st.metric(
        label="Required Replenishment Staff",
        value=f"{total_required_replenishment_staff}"
    )

fresh_food_color = (
    "#15803d"
    if projected_fresh_food_cph >= FRESH_FOOD_BASE_CPH
    else "#9b1c1c"
)

fresh_food_background = (
    "#dcfce7"
    if projected_fresh_food_cph >= FRESH_FOOD_BASE_CPH
    else "#fde8e8"
)

with kpi3:

    st.html(
        f"""
        <div style="
            background-color: {fresh_food_background};
            border: 2px solid {fresh_food_color};
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        ">
            <p style="
                margin: 0;
                font-size: 13px;
                color: #4b5563;
                font-weight: 500;
            ">
                Projected Fresh Food CPH
            </p>

            <h2 style="
                margin: 4px 0 0 0;
                color: {fresh_food_color};
                font-size: 24px;
                font-weight: 700;
            ">
                {projected_fresh_food_cph:.1f} CPH
            </h2>
        </div>
        """
    )

cold_chain_color = (
    "#15803d"
    if projected_cold_chain_cph >= COLD_CHAIN_BASE_CPH
    else "#9b1c1c"
)

cold_chain_background = (
    "#dcfce7"
    if projected_cold_chain_cph >= COLD_CHAIN_BASE_CPH
    else "#fde8e8"
)

with kpi4:

    st.html(
        f"""
        <div style="
            background-color: {cold_chain_background};
            border: 2px solid {cold_chain_color};
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        ">
            <p style="
                margin: 0;
                font-size: 13px;
                color: #4b5563;
                font-weight: 500;
            ">
                Projected Cold Chain CPH
            </p>

            <h2 style="
                margin: 4px 0 0 0;
                color: {cold_chain_color};
                font-size: 24px;
                font-weight: 700;
            ">
                {projected_cold_chain_cph:.1f} CPH
            </h2>
        </div>
        """
    )

with kpi5:

    st.metric(
        label="Projected Shift Length",
        value=f"{shift_hours}h {shift_minutes}m"
    )

st.markdown("---")

st.subheader("📋 Operational Production Analysis")

fresh_food_meat_cases = int(
    fresh_food_cases * 0.55
)

fresh_food_produce_cases = int(
    fresh_food_cases * 0.45
)

cold_chain_dairy_deli_cases = int(
    cold_chain_cases * 0.55
)

cold_chain_frozen_cases = int(
    cold_chain_cases * 0.45
)

production_matrix = [

    {
        "Operational Area": "Meat",

        "Performance Standard":
            f"{round(fresh_food_cph)} CPH / "
            f"{round(fresh_food_replenishment_mph, 1)} MPH",

        "Outbound Case Load":
            f"{fresh_food_meat_cases:,} Cases",

        "Order Fillers Needed":
            f"{math.ceil((fresh_food_pick_hours * 0.55) / target_active_hours)} Staff",

        "Replenishment Moves":
            f"{meat_moves} Moves",

        "Replenishment Staff":
            f"{required_meat_replenishment_staff} Staff"
    },

    {
        "Operational Area": "Produce",

        "Performance Standard":
            f"{round(fresh_food_cph)} CPH / "
            f"{round(fresh_food_replenishment_mph, 1)} MPH",

        "Outbound Case Load":
            f"{fresh_food_produce_cases:,} Cases",

        "Order Fillers Needed":
            f"{math.ceil((fresh_food_pick_hours * 0.45) / target_active_hours)} Staff",

        "Replenishment Moves":
            f"{produce_moves} Moves",

        "Replenishment Staff":
            f"{required_produce_replenishment_staff} Staff"
    },

    {
        "Operational Area": "Dairy & Deli",

        "Performance Standard":
            f"{round(cold_chain_cph)} CPH / "
            f"{round(cold_chain_replenishment_mph, 1)} MPH",

        "Outbound Case Load":
            f"{cold_chain_dairy_deli_cases:,} Cases",

        "Order Fillers Needed":
            f"{math.ceil((cold_chain_pick_hours * 0.55) / target_active_hours)} Staff",

        "Replenishment Moves":
            f"{dairy_deli_moves} Moves",

        "Replenishment Staff":
            f"{required_dairy_deli_replenishment_staff} Staff"
    },

    {
        "Operational Area": "Frozen",

        "Performance Standard":
            f"{round(cold_chain_cph)} CPH / "
            f"{round(cold_chain_replenishment_mph, 1)} MPH",

        "Outbound Case Load":
            f"{cold_chain_frozen_cases:,} Cases",

        "Order Fillers Needed":
            f"{math.ceil((cold_chain_pick_hours * 0.45) / target_active_hours)} Staff",

        "Replenishment Moves":
            f"{frozen_moves} Moves",

        "Replenishment Staff":
            f"{required_frozen_replenishment_staff} Staff"
    }
]

st.dataframe(
    pd.DataFrame(production_matrix),
    use_container_width=True,
    hide_index=True
)
