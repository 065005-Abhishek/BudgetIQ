import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from groq import Groq


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="BudgetIQ",
    page_icon="💰",
    layout="wide"
)

# =========================================================
# BUDGETIQ BACKGROUND THEME
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #eef4ff 0%,
        #f7f2ff 50%,
        #eefaff 100%
    );
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# COLORFUL CHART CARDS
# =========================================================

st.markdown("""
<style>

div[data-testid="stPlotlyChart"] {
    background: linear-gradient(
        135deg,
        #eef4ff 0%,
        #f6efff 100%
    );

    border: 1px solid #d8def0;

    border-radius: 16px;

    padding: 10px;

    box-shadow: 0 5px 18px rgba(70, 90, 140, 0.10);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# BUDGETIQ PROFESSIONAL DASHBOARD STYLING
# =========================================================

st.markdown("""
<style>



    /* -----------------------------------------------------
       MAIN PAGE
    ----------------------------------------------------- */

    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }


    /* -----------------------------------------------------
       SIDEBAR
    ----------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background-color: #f5f6f8;
    }

    section[data-testid="stSidebar"] h1 {
        font-size: 1.55rem;
        font-weight: 700;
    }

    section[data-testid="stSidebar"] h2 {
        font-size: 1.15rem;
    }


    /* -----------------------------------------------------
       HEADINGS
    ----------------------------------------------------- */

    h1 {
        font-weight: 750 !important;
        letter-spacing: -0.5px;
    }

    h2 {
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
    }

    h3 {
        font-weight: 650 !important;
    }


/* -----------------------------------------------------
   KPI / METRIC CARDS
----------------------------------------------------- */

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e6e8ec;
    border-radius: 12px;
    padding: 14px 12px 12px 12px;
    min-height: 105px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

div[data-testid="stMetricLabel"] {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    white-space: normal !important;
    line-height: 1.2 !important;
}

div[data-testid="stMetricValue"] {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    white-space: nowrap !important;
}

div[data-testid="stMetricDelta"] {
    font-size: 0.75rem !important;
}


    /* -----------------------------------------------------
       BUTTONS
       ----------------------------------------------------- */

    .stButton > button {
        border-radius: 9px;
        font-weight: 600;
        min-height: 42px;
    }


    /* -----------------------------------------------------
       INFORMATION / SUCCESS / WARNING BOXES
       ----------------------------------------------------- */

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }


    /* -----------------------------------------------------
       DATA TABLES
       ----------------------------------------------------- */

    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        border: 1px solid #e6e8ec;
        overflow: hidden;
    }


    /* -----------------------------------------------------
       AI BOX
       ----------------------------------------------------- */

    .ai-box {
        background: #f7f9fc;
        border: 1px solid #dfe4ea;
        border-left: 5px solid #ff4b4b;
        border-radius: 10px;
        padding: 20px 24px;
        margin-top: 12px;
        margin-bottom: 20px;
        line-height: 1.65;
    }


    /* -----------------------------------------------------
       SECTION SPACING
       ----------------------------------------------------- */

    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
        border: none;
        border-top: 1px solid #e5e7eb;
    }


    /* -----------------------------------------------------
       FILE UPLOADER
       ----------------------------------------------------- */

    section[data-testid="stFileUploader"] {
        border-radius: 10px;
    }


    /* -----------------------------------------------------
       CAPTIONS
       ----------------------------------------------------- */

    .stCaption {
        color: #6b7280;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.title("BudgetIQ")

st.caption(
    "AI-Powered Budget Decision Support Dashboard"
)


# =========================================================
# HEADER
# =========================================================



# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("BudgetIQ")

st.sidebar.caption("Dashboard Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload Budget Dataset",
    type=["xlsx", "csv"]
)


# =========================================================
# DATA LOADING
# =========================================================

if uploaded_file is None:

    st.info(
        "👈 Upload your BudgetIQ Excel or CSV dataset from the sidebar to begin."
    )

    st.markdown("""
    ### What BudgetIQ does

    **BudgetIQ** helps managers understand:

    - Budget vs Actual spending
    - Variance and overspending
    - Unusual spending patterns
    - Department and category performance
    - Future spending trends
    - AI-generated business recommendations
    """)

    st.stop()


# =========================================================
# READ FILE
# =========================================================

try:

    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

except Exception as e:

    st.error(f"Unable to read the uploaded file: {e}")
    st.stop()


# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [
    "Date",
    "Department",
    "Category",
    "Budget",
    "Actual"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:

    st.error(
        "The uploaded file is missing these required columns: "
        + ", ".join(missing_columns)
    )

    st.stop()


# =========================================================
# DATA CLEANING
# =========================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce"
)

df["Budget"] = pd.to_numeric(
    df["Budget"],
    errors="coerce"
)

df["Actual"] = pd.to_numeric(
    df["Actual"],
    errors="coerce"
)


# Remove rows with invalid essential values

df = df.dropna(
    subset=[
        "Date",
        "Department",
        "Category",
        "Budget",
        "Actual"
    ]
).copy()


# =========================================================
# CALCULATE VARIANCE
# =========================================================

df["Variance"] = df["Actual"] - df["Budget"]

df["Variance %"] = np.where(
    df["Budget"] != 0,
    (df["Variance"] / df["Budget"]) * 100,
    0
)


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.markdown("---")

st.sidebar.subheader("Filters")


departments = sorted(
    df["Department"].dropna().unique().tolist()
)

selected_departments = st.sidebar.multiselect(
    "Department",
    departments,
    default=departments
)


categories = sorted(
    df["Category"].dropna().unique().tolist()
)

selected_categories = st.sidebar.multiselect(
    "Category",
    categories,
    default=categories
)


min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

selected_dates = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered_df = df[
    df["Department"].isin(selected_departments)
    &
    df["Category"].isin(selected_categories)
].copy()


if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

    start_date = pd.Timestamp(selected_dates[0])
    end_date = pd.Timestamp(selected_dates[1])

    filtered_df = filtered_df[
        (filtered_df["Date"] >= start_date)
        &
        (filtered_df["Date"] <= end_date)
    ]


if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# =========================================================
# KPI CALCULATIONS
# =========================================================

total_budget = filtered_df["Budget"].sum()

total_actual = filtered_df["Actual"].sum()

total_variance = filtered_df["Variance"].sum()

overall_variance_pct = (
    total_variance / total_budget * 100
    if total_budget != 0
    else 0
)

over_budget_records = (
    filtered_df["Actual"] > filtered_df["Budget"]
).sum()


# =========================================================
# KPI CARDS
# =========================================================

st.markdown(
    '<div class="section-title">📊 Budget Overview</div>',
    unsafe_allow_html=True
)

col1, col2, col3, col4, col5 = st.columns(
    [1, 1, 1, 1, 1]
)

with col1:
    st.metric(
        "Total Budget",
        f"₹{total_budget:,.0f}"
    )

with col2:
    st.metric(
        "Actual Spending",
        f"₹{total_actual:,.0f}"
    )

with col3:

    st.metric(
        "Total Variance",
        f"₹{total_variance:,.0f}"
    )

with col4:

    st.metric(
        "Variance %",
        f"{overall_variance_pct:.2f}%"
    )

with col5:

    st.metric(
        "Over-Budget",
        int(over_budget_records)
    )


# =========================================================
# OVERALL STATUS
# =========================================================

if total_variance > 0:

    st.warning(
        f"⚠️ Overall spending is ₹{total_variance:,.0f} "
        f"above the selected budget."
    )

else:

    st.success(
        f"✅ Spending is ₹{abs(total_variance):,.0f} "
        f"below the selected budget."
    )


# =========================================================
# BUDGET VS ACTUAL
# =========================================================

st.markdown(
    '<div class="section-title">Budget vs Actual</div>',
    unsafe_allow_html=True
)

overall_chart_df = pd.DataFrame({
    "Metric": [
        "Budget",
        "Actual"
    ],
    "Amount": [
        total_budget,
        total_actual
    ]
})

fig = px.bar(
    overall_chart_df,
    x="Metric",
    y="Amount",
    text_auto=".2s",
    title="Overall Budget vs Actual Spending"
)

fig.update_layout(
    yaxis_title="Amount",
    xaxis_title=""
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# MONTHLY ANALYSIS
# =========================================================

monthly_df = (
    filtered_df
    .assign(
        Month=filtered_df["Date"].dt.to_period("M").astype(str)
    )
    .groupby("Month", as_index=False)
    .agg(
        Budget=("Budget", "sum"),
        Actual=("Actual", "sum")
    )
)

monthly_df["Variance"] = (
    monthly_df["Actual"] -
    monthly_df["Budget"]
)

monthly_fig = px.line(
    monthly_df,
    x="Month",
    y=["Budget", "Actual"],
    markers=True,
    title="Monthly Budget vs Actual"
)

st.plotly_chart(
    monthly_fig,
    use_container_width=True
)


# =========================================================
# DEPARTMENT ANALYSIS
# =========================================================

st.markdown(
    '<div class="section-title">Department Analysis</div>',
    unsafe_allow_html=True
)

department_df = (
    filtered_df
    .groupby("Department", as_index=False)
    .agg(
        Budget=("Budget", "sum"),
        Actual=("Actual", "sum")
    )
)

department_df["Variance"] = (
    department_df["Actual"] -
    department_df["Budget"]
)

department_df["Variance %"] = np.where(
    department_df["Budget"] != 0,
    department_df["Variance"] /
    department_df["Budget"] * 100,
    0
)


col1, col2 = st.columns(2)

with col1:

    fig_department = px.bar(
        department_df.sort_values(
            "Variance",
            ascending=False
        ),
        x="Department",
        y="Variance",
        title="Department-wise Variance",
        text_auto=".2s"
    )

    st.plotly_chart(
        fig_department,
        use_container_width=True
    )


with col2:

    fig_department_pct = px.bar(
        department_df.sort_values(
            "Variance %",
            ascending=False
        ),
        x="Department",
        y="Variance %",
        title="Department-wise Variance %",
        text_auto=".2f"
    )

    st.plotly_chart(
        fig_department_pct,
        use_container_width=True
    )


# =========================================================
# CATEGORY ANALYSIS
# =========================================================

category_df = (
    filtered_df
    .groupby("Category", as_index=False)
    .agg(
        Budget=("Budget", "sum"),
        Actual=("Actual", "sum")
    )
)

category_df["Variance"] = (
    category_df["Actual"] -
    category_df["Budget"]
)

category_df["Variance %"] = np.where(
    category_df["Budget"] != 0,
    category_df["Variance"] /
    category_df["Budget"] * 100,
    0
)

category_top10 = (
    category_df
    .sort_values(
        "Variance",
        ascending=False
    )
    .head(10)
)


fig_category = px.bar(
    category_top10,
    x="Variance",
    y="Category",
    orientation="h",
    title="Top 10 Categories by Unfavorable Variance"
)

st.plotly_chart(
    fig_category,
    use_container_width=True
)


# =========================================================
# TOP OUTLIERS
# =========================================================

st.markdown(
    '<div class="section-title">🔎 Top Budget Variances</div>',
    unsafe_allow_html=True
)

top_variances = (
    filtered_df
    .sort_values(
        "Variance",
        ascending=False
    )
    .head(10)
)

st.dataframe(
    top_variances[
        [
            "Date",
            "Department",
            "Category",
            "Budget",
            "Actual",
            "Variance",
            "Variance %"
        ]
    ],
    use_container_width=True
)


# =========================================================
# ANOMALY DETECTION
# =========================================================

st.markdown(
    '<div class="section-title">🚨 Anomaly Detection</div>',
    unsafe_allow_html=True
)

q1 = filtered_df["Variance %"].quantile(0.25)

q3 = filtered_df["Variance %"].quantile(0.75)

iqr = q3 - q1

upper_limit = q3 + (1.5 * iqr)

lower_limit = q1 - (1.5 * iqr)

filtered_df["Anomaly"] = (
    (filtered_df["Variance %"] > upper_limit)
    |
    (filtered_df["Variance %"] < lower_limit)
)


anomaly_df = filtered_df[
    filtered_df["Anomaly"]
].copy()


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Anomalies Detected",
        len(anomaly_df)
    )

with col2:
    st.metric(
        "Normal Records",
        len(filtered_df) - len(anomaly_df)
    )

with col3:
    st.metric(
        "Upper Anomaly Limit",
        f"{upper_limit:.2f}%"
    )


if not anomaly_df.empty:

    st.dataframe(
        anomaly_df[
            [
                "Date",
                "Department",
                "Category",
                "Budget",
                "Actual",
                "Variance",
                "Variance %",
                "Anomaly"
            ]
        ].sort_values(
            "Variance %",
            ascending=False
        ),
        use_container_width=True
    )

else:

    st.success(
        "No statistical anomalies were detected."
    )


# =========================================================
# FORECAST
# =========================================================

st.markdown(
    '<div class="section-title">📈 Spending Forecast</div>',
    unsafe_allow_html=True
)


if len(monthly_df) >= 3:

    monthly_values = monthly_df["Actual"].values

    x = np.arange(len(monthly_values))

    coefficients = np.polyfit(
        x,
        monthly_values,
        1
    )

    trend = np.poly1d(coefficients)

    future_x = np.arange(
        len(monthly_values),
        len(monthly_values) + 3
    )

    forecast_values = trend(future_x)

    forecast_values = np.maximum(
        forecast_values,
        0
    )

    last_month = pd.Period(
        monthly_df["Month"].iloc[-1],
        freq="M"
    )

    forecast_months = [
        str(last_month + i)
        for i in range(1, 4)
    ]

    forecast_df = pd.DataFrame({
        "Month": forecast_months,
        "Forecast": forecast_values
    })


    forecast_chart_df = pd.concat(
        [
            monthly_df[
                ["Month", "Actual"]
            ].rename(
                columns={
                    "Actual": "Amount"
                }
            ),
            forecast_df.rename(
                columns={
                    "Forecast": "Amount"
                }
            )
        ],
        ignore_index=True
    )

    forecast_fig = px.line(
        forecast_chart_df,
        x="Month",
        y="Amount",
        markers=True,
        title="Historical Spending + 3-Month Forecast"
    )

    st.plotly_chart(
        forecast_fig,
        use_container_width=True
    )


    average_monthly_spending = (
        monthly_df["Actual"].mean()
    )

    next_month_forecast = forecast_values[0]

    three_month_forecast = forecast_values.sum()

    average_monthly_budget = (
        monthly_df["Budget"].mean()
    )


    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Avg Monthly Spending",
            f"₹{average_monthly_spending:,.0f}"
        )

    with col2:
        st.metric(
            "Next Month Forecast",
            f"₹{next_month_forecast:,.0f}"
        )

    with col3:
        st.metric(
            "Next 3 Months Forecast",
            f"₹{three_month_forecast:,.0f}"
        )

    with col4:
        st.metric(
            "Avg Monthly Budget",
            f"₹{average_monthly_budget:,.0f}"
        )

else:

    st.info(
        "At least 3 months of data are required for forecasting."
    )

    forecast_values = np.array([])

    forecast_months = []


# =========================================================
# AI INSIGHTS
# =========================================================

st.markdown(
    '<div class="section-title">🤖 AI Budget Insights</div>',
    unsafe_allow_html=True
)

st.write(
    "Use AI to interpret the calculated results and generate "
    "practical management recommendations."
)


# =========================================================
# PREPARE INFORMATION FOR AI
# =========================================================

top_department = (
    department_df
    .sort_values(
        "Variance",
        ascending=False
    )
    .iloc[0]
)

top_category = (
    category_df
    .sort_values(
        "Variance",
        ascending=False
    )
    .iloc[0]
)


# Top 5 anomalies

if not anomaly_df.empty:

    ai_anomalies = anomaly_df[
        [
            "Date",
            "Department",
            "Category",
            "Budget",
            "Actual",
            "Variance",
            "Variance %"
        ]
    ].sort_values(
        "Variance %",
        ascending=False
    ).head(5)

    anomaly_text = ai_anomalies.to_string(
        index=False
    )

else:

    anomaly_text = "No anomalies detected."


# Forecast text

if len(forecast_values) > 0:

    forecast_text = "\n".join(
        [
            f"{month}: ₹{value:,.0f}"
            for month, value
            in zip(
                forecast_months,
                forecast_values
            )
        ]
    )

else:

    forecast_text = "Forecast unavailable."


# =========================================================
# AI BUTTON
# =========================================================

if st.button(
    "✨ Generate AI Insights",
    type="primary",
    use_container_width=True
):

    try:

        groq_client = Groq(
            api_key=st.secrets["GROQ_API_KEY"]
        )


        system_prompt = """
You are BudgetIQ, a business budgeting and financial
analysis assistant.

Your job is to interpret already-calculated budget analytics.

IMPORTANT RULES:

1. Do not invent numbers.
2. Do not recalculate or change the supplied figures.
3. Use only the information provided in the prompt.
4. Clearly distinguish facts from interpretations.
5. Do not claim a specific cause unless the data supports it.
6. If the data is insufficient to determine a cause, say so.
7. Give practical business recommendations.
8. Keep the language simple and suitable for an MBA management presentation.
9. Do not provide investment advice.
10. Focus on cost control, budgeting, resource allocation and management action.

Structure your response with these headings:

### Executive Summary

### Key Areas Requiring Attention

### Anomaly Interpretation

### Forecast Interpretation

### Recommended Actions

### Management Takeaway
"""


        user_prompt = f"""
Analyze the following BudgetIQ results.

OVERALL RESULTS

Total Budget:
₹{total_budget:,.0f}

Total Actual Spending:
₹{total_actual:,.0f}

Total Variance:
₹{total_variance:,.0f}

Overall Variance:
{overall_variance_pct:.2f}%

Number of Over-Budget Records:
{over_budget_records}


TOP DEPARTMENT BY VARIANCE

Department:
{top_department["Department"]}

Budget:
₹{top_department["Budget"]:,.0f}

Actual:
₹{top_department["Actual"]:,.0f}

Variance:
₹{top_department["Variance"]:,.0f}

Variance %:
{top_department["Variance %"]:.2f}%


TOP CATEGORY BY VARIANCE

Category:
{top_category["Category"]}

Budget:
₹{top_category["Budget"]:,.0f}

Actual:
₹{top_category["Actual"]:,.0f}

Variance:
₹{top_category["Variance"]:,.0f}

Variance %:
{top_category["Variance %"]:.2f}%


STATISTICAL ANOMALIES

{anomaly_text}


FORECAST

{forecast_text}


Provide a concise but useful management interpretation.
"""


        with st.spinner(
            "BudgetIQ is generating AI insights..."
        ):

            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1200
            )


        ai_response = (
            response
            .choices[0]
            .message
            .content
        )


        st.markdown(
            '<div class="ai-box">',
            unsafe_allow_html=True
        )

        st.markdown(ai_response)

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    except Exception as e:

        st.error(
            "Unable to generate AI insights."
        )

        st.caption(
            f"Technical details: {e}"
        )

# =========================================================
# WHAT-IF BUDGET SIMULATOR
# =========================================================

# =========================================================
# WHAT-IF BUDGET SIMULATOR
# =========================================================

st.markdown(
    '<div class="section-title">🧮 What-If Budget Simulator</div>',
    unsafe_allow_html=True
)

st.write(
    "Test a possible spending decision and see how it could "
    "change the budget position using the current filtered data."
)

st.info(
    "Example: If Marketing spending is reduced by 10%, "
    "how does it affect the department and overall budget?"
)


# ---------------------------------------------------------
# SIMULATOR INPUTS
# ---------------------------------------------------------

sim_col1, sim_col2, sim_col3 = st.columns(3)


with sim_col1:

    simulator_department = st.selectbox(
        "Select Department",
        sorted(
            filtered_df["Department"]
            .dropna()
            .unique()
            .tolist()
        ),
        help="Choose the department whose current spending you want to simulate."
    )


with sim_col2:

    simulator_action = st.selectbox(
        "Scenario",
        [
            "Reduce current spending by",
            "Increase current spending by"
        ],
        help="The percentage will be applied to the department's current actual spending."
    )


with sim_col3:

    simulator_percentage = st.slider(
        "Adjustment (%)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="This percentage is applied to the current actual spending of the selected department."
    )


st.caption(
    f"The {simulator_percentage}% adjustment will be applied to "
    f"current actual spending for {simulator_department}."
)


# ---------------------------------------------------------
# RUN SIMULATION
# ---------------------------------------------------------

if st.button(
    "🔮 Run What-If Simulation",
    type="primary",
    use_container_width=True
):

    simulator_data = filtered_df[
        filtered_df["Department"] == simulator_department
    ].copy()


    if simulator_data.empty:

        st.warning(
            "No data is available for the selected department."
        )

    else:

        # -------------------------------------------------
        # CURRENT VALUES
        # -------------------------------------------------

        current_budget = simulator_data["Budget"].sum()

        current_actual = simulator_data["Actual"].sum()

        current_variance = (
            current_actual -
            current_budget
        )


        # -------------------------------------------------
        # SCENARIO CALCULATION
        # -------------------------------------------------

        adjustment_amount = (
            current_actual *
            simulator_percentage /
            100
        )


        if simulator_action == "Reduce current spending by":

            new_actual = (
                current_actual -
                adjustment_amount
            )

        else:

            new_actual = (
                current_actual +
                adjustment_amount
            )


        new_variance = (
            new_actual -
            current_budget
        )


        # Positive value = improvement
        variance_improvement = (
            current_variance -
            new_variance
        )


        # -------------------------------------------------
        # OVERALL COMPANY IMPACT
        # -------------------------------------------------

        overall_new_actual = (
            total_actual
            - current_actual
            + new_actual
        )

        overall_new_variance = (
            overall_new_actual -
            total_budget
        )


        # -------------------------------------------------
        # STORE RESULT FOR LATER AI EXPLANATION
        # -------------------------------------------------

        st.session_state["simulation_result"] = {

            "department": simulator_department,

            "action": simulator_action,

            "percentage": simulator_percentage,

            "current_budget": current_budget,

            "current_actual": current_actual,

            "current_variance": current_variance,

            "adjustment_amount": adjustment_amount,

            "new_actual": new_actual,

            "new_variance": new_variance,

            "variance_improvement": variance_improvement,

            "overall_new_actual": overall_new_actual,

            "overall_new_variance": overall_new_variance,

            "total_budget": total_budget,

            "total_actual": total_actual
        }


# ---------------------------------------------------------
# DISPLAY STORED SIMULATION
# ---------------------------------------------------------

if "simulation_result" in st.session_state:

    result = st.session_state["simulation_result"]


    st.markdown("### 🔮 Simulation Result")


    st.caption(
        f"Scenario: {result['action']} "
        f"{result['percentage']}% of "
        f"{result['department']} current spending"
    )


    # -----------------------------------------------------
    # RESULT METRICS
    # -----------------------------------------------------

    result_col1, result_col2, result_col3, result_col4 = (
        st.columns(4)
    )


    with result_col1:

        st.metric(
            "Current Spending",
            f"₹{result['current_actual']:,.0f}"
        )


    with result_col2:

        adjustment_display = result["adjustment_amount"]

        if result["action"] == "Reduce current spending by":
            adjustment_display = -adjustment_display

        st.metric(
            f"Adjustment ({result['percentage']}%)",
            f"₹{adjustment_display:,.0f}"
        )


    with result_col3:

        st.metric(
            "New Estimated Spending",
            f"₹{result['new_actual']:,.0f}"
        )


    with result_col4:

        st.metric(
            "New Variance",
            f"₹{result['new_variance']:,.0f}"
        )


    # -----------------------------------------------------
    # STATUS MESSAGE
    # -----------------------------------------------------

    if result["variance_improvement"] > 0:

        st.success(
            f"✅ The scenario improves the budget position by "
            f"₹{result['variance_improvement']:,.0f}."
        )

    elif result["variance_improvement"] < 0:

        st.warning(
            f"⚠️ The scenario worsens the budget position by "
            f"₹{abs(result['variance_improvement']):,.0f}."
        )

    else:

        st.info(
            "The scenario does not change the budget variance."
        )


    # -----------------------------------------------------
    # OVERALL IMPACT
    # -----------------------------------------------------

    st.markdown("### 📊 Impact on Overall Budget")


    impact_col1, impact_col2, impact_col3 = st.columns(3)


    with impact_col1:

        st.metric(
            "Current Overall Spending",
            f"₹{result['total_actual']:,.0f}"
        )


    with impact_col2:

        overall_change = (
            result["overall_new_actual"] -
            result["total_actual"]
        )

        st.metric(
            "New Overall Spending",
            f"₹{result['overall_new_actual']:,.0f}",
            delta=f"₹{overall_change:,.0f}"
        )


    with impact_col3:

        st.metric(
            "New Overall Variance",
            f"₹{result['overall_new_variance']:,.0f}"
        )


    # -----------------------------------------------------
    # BEFORE VS AFTER
    # -----------------------------------------------------

    st.markdown(
        f"### 📋 Before vs After — {result['department']}"
    )


    current_variance_pct = (
        result["current_variance"] /
        result["current_budget"] * 100
        if result["current_budget"] != 0
        else 0
    )


    new_variance_pct = (
        result["new_variance"] /
        result["current_budget"] * 100
        if result["current_budget"] != 0
        else 0
    )


    comparison_df = pd.DataFrame({

        "Metric": [
            "Budget",
            "Actual Spending",
            "Variance",
            "Variance %"
        ],

        "Current": [
            result["current_budget"],
            result["current_actual"],
            result["current_variance"],
            current_variance_pct
        ],

        "After Scenario": [
            result["current_budget"],
            result["new_actual"],
            result["new_variance"],
            new_variance_pct
        ],

        "Change": [
            0,
            result["new_actual"] -
            result["current_actual"],
            result["new_variance"] -
            result["current_variance"],
            new_variance_pct -
            current_variance_pct
        ]
    })


    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # SIMPLE MANAGEMENT INTERPRETATION
    # -----------------------------------------------------

    if result["action"] == "Reduce current spending by":

        st.write(
            f"**Management interpretation:** A "
            f"{result['percentage']}% reduction in "
            f"{result['department']} spending would reduce "
            f"estimated spending by approximately "
            f"₹{result['adjustment_amount']:,.0f}."
        )

    else:

        st.write(
            f"**Management interpretation:** A "
            f"{result['percentage']}% increase in "
            f"{result['department']} spending would add "
            f"approximately "
            f"₹{result['adjustment_amount']:,.0f} "
            f"to current spending."
        )

# ---------------------------------------------------------
# AI SCENARIO EXPLANATION
# ---------------------------------------------------------

st.markdown("---")

st.markdown("### 🤖 AI Scenario Explanation")

st.write(
    "Get an AI-powered interpretation of the simulated "
    "financial impact and practical management actions."
)


if "simulation_result" in st.session_state:

    if st.button(
        "✨ Explain This Scenario with AI",
        use_container_width=True
    ):

        try:

            groq_client = Groq(
                api_key=st.secrets["GROQ_API_KEY"]
            )

            result = st.session_state["simulation_result"]

            scenario_prompt = f"""
You are BudgetIQ, an AI business budgeting assistant.

Interpret this hypothetical What-If budget scenario.

Department:
{result["department"]}

Scenario:
{result["action"]} {result["percentage"]}%

Current Department Budget:
₹{result["current_budget"]:,.0f}

Current Department Spending:
₹{result["current_actual"]:,.0f}

Current Department Variance:
₹{result["current_variance"]:,.0f}

Simulated Adjustment:
₹{result["adjustment_amount"]:,.0f}

New Estimated Spending:
₹{result["new_actual"]:,.0f}

New Department Variance:
₹{result["new_variance"]:,.0f}

Change in Variance:
₹{result["variance_improvement"]:,.0f}

Current Overall Spending:
₹{result["total_actual"]:,.0f}

New Overall Spending:
₹{result["overall_new_actual"]:,.0f}

New Overall Variance:
₹{result["overall_new_variance"]:,.0f}


IMPORTANT RULES:

1. Use only the figures provided above.
2. Do not invent numbers.
3. Do not modify the calculations.
4. Explain whether the scenario improves or worsens the budget position.
5. Explain the business implication in simple language.
6. Give 2-3 practical management recommendations.
7. Clearly state that this is a hypothetical scenario.
8. Do not assume that a spending change is automatically feasible.
9. Do not claim a specific cause unless supported by the data.
10. Keep the answer concise and suitable for an MBA presentation.

Use these headings:

### Scenario Interpretation

### Business Impact

### Recommended Actions

### Management Takeaway
"""

            with st.spinner(
                "BudgetIQ is explaining the scenario..."
            ):

                ai_response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a careful business "
                                "budgeting assistant. "
                                "Never invent financial figures."
                            )
                        },
                        {
                            "role": "user",
                            "content": scenario_prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=700
                )

            scenario_answer = (
                ai_response
                .choices[0]
                .message
                .content
            )

            st.markdown(
                '<div class="ai-box">',
                unsafe_allow_html=True
            )

            st.markdown(scenario_answer)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )

        except Exception as e:

            st.error(
                "Unable to generate the AI explanation."
            )

            st.caption(
                f"Technical details: {e}"
            )

else:

    st.info(
        "Run a What-If Simulation first to enable AI explanation."
    )

# =========================================================
# ASK BUDGETIQ - INTERACTIVE AI Q&A
# =========================================================

st.markdown(
    '<div class="section-title">💬 Ask BudgetIQ</div>',
    unsafe_allow_html=True
)

st.write(
    "Ask questions about the current budget, spending, "
    "anomalies, departments, categories and forecast."
)


# ---------------------------------------------------------
# CREATE A COMPACT DATA SUMMARY FOR THE AI
# ---------------------------------------------------------

# Department summary
department_summary = department_df[
    [
        "Department",
        "Budget",
        "Actual",
        "Variance",
        "Variance %"
    ]
].sort_values(
    "Variance",
    ascending=False
).head(10)


# Category summary
category_summary = category_df[
    [
        "Category",
        "Budget",
        "Actual",
        "Variance",
        "Variance %"
    ]
].sort_values(
    "Variance",
    ascending=False
).head(10)


# Anomaly summary
if not anomaly_df.empty:

    anomaly_summary = anomaly_df[
        [
            "Date",
            "Department",
            "Category",
            "Budget",
            "Actual",
            "Variance",
            "Variance %"
        ]
    ].sort_values(
        "Variance %",
        ascending=False
    ).head(10)

else:

    anomaly_summary = pd.DataFrame(
        columns=[
            "Date",
            "Department",
            "Category",
            "Budget",
            "Actual",
            "Variance",
            "Variance %"
        ]
    )


# Forecast summary
if len(forecast_values) > 0:

    forecast_summary = "\n".join(
        [
            f"{month}: ₹{value:,.0f}"
            for month, value
            in zip(
                forecast_months,
                forecast_values
            )
        ]
    )

else:

    forecast_summary = "Forecast unavailable."


# ---------------------------------------------------------
# SAMPLE QUESTIONS
# ---------------------------------------------------------

st.markdown("**Try asking:**")

sample_col1, sample_col2, sample_col3 = st.columns(3)

with sample_col1:

    if st.button(
        "Which department needs attention?",
        use_container_width=True
    ):

        st.session_state["budget_question"] = (
            "Which department needs the most attention "
            "and why?"
        )


with sample_col2:

    if st.button(
        "Explain the anomalies",
        use_container_width=True
    ):

        st.session_state["budget_question"] = (
            "Which anomalies should management investigate "
            "first and why?"
        )


with sample_col3:

    if st.button(
        "What should management do?",
        use_container_width=True
    ):

        st.session_state["budget_question"] = (
            "What are the three most important actions "
            "management should take based on the current "
            "budget analysis?"
        )


# ---------------------------------------------------------
# QUESTION INPUT
# ---------------------------------------------------------

if "budget_question" not in st.session_state:

    st.session_state["budget_question"] = ""


question = st.text_input(
    "Ask BudgetIQ a question",
    value=st.session_state["budget_question"],
    placeholder="Example: Why is Marketing overspending?",
    key="budget_question_input"
)


# ---------------------------------------------------------
# ASK BUTTON
# ---------------------------------------------------------

if st.button(
    "🤖 Ask BudgetIQ",
    type="primary",
    use_container_width=True
):

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        try:

            groq_client = Groq(
                api_key=st.secrets["GROQ_API_KEY"]
            )


            # -------------------------------------------------
            # SYSTEM INSTRUCTIONS
            # -------------------------------------------------

            ask_system_prompt = """
You are BudgetIQ, an AI budget decision-support assistant.

You answer questions about a company's budget and spending
using only the financial information provided to you.

IMPORTANT RULES:

1. Use ONLY the data provided in the context.
2. Never invent financial figures.
3. Do not change or recalculate the supplied figures.
4. If the answer cannot be determined from the data, clearly say:
   "The available data is insufficient to determine this."
5. Distinguish facts from possible interpretations.
6. Do not claim a specific cause of overspending unless the data
   supports that conclusion.
7. Give practical business recommendations when appropriate.
8. Keep answers concise and easy to understand.
9. Use ₹ for Indian currency.
10. Answer like a business analyst helping a management team.
11. Do not provide investment advice.

When answering numerical questions, mention the relevant
department/category and figures from the supplied data.
"""


            # -------------------------------------------------
            # BUILD DATA CONTEXT
            # -------------------------------------------------

            data_context = f"""

CURRENT BUDGET OVERVIEW

Total Budget:
₹{total_budget:,.0f}

Total Actual Spending:
₹{total_actual:,.0f}

Total Variance:
₹{total_variance:,.0f}

Overall Variance:
{overall_variance_pct:.2f}%

Over-Budget Records:
{over_budget_records}


DEPARTMENT SUMMARY

{department_summary.to_string(index=False)}


CATEGORY SUMMARY

{category_summary.to_string(index=False)}


STATISTICAL ANOMALIES

{anomaly_summary.to_string(index=False)}


FORECAST

{forecast_summary}
"""


            # -------------------------------------------------
            # FINAL USER PROMPT
            # -------------------------------------------------

            user_prompt = f"""
Here is the current BudgetIQ analysis:

{data_context}

USER QUESTION:

{question}

Answer the user's question directly.

If useful, include:
- the relevant figure
- the department/category
- a short explanation
- a practical management action

Do not provide information that is not supported by the
provided BudgetIQ data.
"""


            # -------------------------------------------------
            # CALL GROQ
            # -------------------------------------------------

            with st.spinner(
                "BudgetIQ is analyzing your question..."
            ):

                response = groq_client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": ask_system_prompt
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    temperature=0.2,
                    max_tokens=700
                )


            answer = (
                response
                .choices[0]
                .message
                .content
            )


            # -------------------------------------------------
            # DISPLAY ANSWER
            # -------------------------------------------------

            st.markdown("### 🤖 BudgetIQ Answer")

            st.markdown(
                '<div class="ai-box">',
                unsafe_allow_html=True
            )

            st.markdown(answer)

            st.markdown(
                '</div>',
                unsafe_allow_html=True
            )


        except Exception as e:

            st.error(
                "Unable to process your question."
            )

            st.caption(
                f"Technical details: {e}"
            )


# =========================================================
# DETAILED DATA
# =========================================================

st.markdown(
    '<div class="section-title">📋 Detailed Analysis</div>',
    unsafe_allow_html=True
)

display_columns = [
    "Date",
    "Department",
    "Category",
    "Budget",
    "Actual",
    "Variance",
    "Variance %",
    "Anomaly"
]

st.dataframe(
    filtered_df[display_columns],
    use_container_width=True
)


# =========================================================
# DOWNLOAD
# =========================================================

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="⬇️ Download Analysis CSV",
    data=csv_data,
    file_name="BudgetIQ_Analysis.csv",
    mime="text/csv",
    use_container_width=True
)


# =========================================================
# ABOUT BUDGETIQ
# =========================================================

st.markdown("---")

with st.expander("ℹ️ About BudgetIQ"):

    st.markdown(
        """
        **BudgetIQ** is an AI-powered budget decision-support
        application developed as an academic project.

        **Core capabilities:**

        - Budget vs Actual Analysis
        - Variance Analysis
        - Statistical Anomaly Detection
        - Spending Forecasting
        - AI-Generated Budget Insights
        - Natural Language Q&A
        - What-If Budget Simulation
        - AI Scenario Interpretation

        **Technology Stack**

        - Python
        - Streamlit
        - Pandas
        - NumPy
        - Plotly
        - Groq LLM API

        **AI Design Principle**

        Financial calculations are performed using deterministic
        Python logic. The AI model is used primarily for
        interpretation, explanation and management recommendations.

        This separation helps reduce the risk of incorrect
        AI-generated financial calculations.
        """
    )


    st.caption(
    "Academic prototype — simulated data used for demonstration. "
    "AI outputs should be reviewed by management before making decisions."
)