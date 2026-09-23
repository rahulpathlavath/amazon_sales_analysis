import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Amazon Sales Analysis",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #f7f8fa; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    div[data-testid="metric-container"] label {
        font-size: 13px !important;
        color: #57606a !important;
        font-weight: 600;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 26px !important;
        font-weight: 700;
        color: #1f2328;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-size: 13px !important;
    }

    /* Section headers */
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #1f2328;
        margin-top: 10px;
        margin-bottom: 4px;
        border-left: 4px solid #3b82d4;
        padding-left: 10px;
    }
    .section-sub {
        font-size: 13px;
        color: #57606a;
        margin-bottom: 16px;
        padding-left: 14px;
    }

    /* Dataframe container */
    .dataframe-container {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #e5e7eb;
    }

    /* Insight boxes */
    .insight-box {
        background-color: #eef4ff;
        border-left: 4px solid #3b82d4;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #1f2328;
    }
    .insight-box strong { color: #3b82d4; }

    .warning-box {
        background-color: #fff8e1;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #1f2328;
    }
    .success-box {
        background-color: #e6f9f0;
        border-left: 4px solid #22c55e;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 8px 0;
        font-size: 14px;
        color: #1f2328;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    /* Divider */
    hr { border-top: 1px solid #e5e7eb; margin: 20px 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt_inr(val):
    """Format number as Indian Rupees with ₹ symbol."""
    if pd.isna(val):
        return "N/A"
    return f"₹{val:,.2f}"

def fmt_num(val):
    return f"{val:,.0f}"

CHART_COLORS = px.colors.qualitative.Bold

# ─────────────────────────────────────────────
# STEP 1 — LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    return df

# ─────────────────────────────────────────────
# SIDEBAR — file picker & filters
# ─────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=130)
    st.markdown("## 📂 Dataset")
    uploaded = st.file_uploader("Upload your CSV", type=["csv"])

    if uploaded:
        df_raw = pd.read_csv(uploaded, encoding="utf-8-sig")
        df_raw.columns = df_raw.columns.str.strip()
    else:
        try:
            df_raw = load_data("data analytics 1000 rows.csv")
        except FileNotFoundError:
            st.error("Default CSV not found. Please upload a file.")
            st.stop()

    st.success(f"✅ {len(df_raw):,} rows loaded")
    st.markdown("---")

    st.markdown("## 🔍 Filters")
    all_cats = sorted(df_raw["category"].dropna().unique().tolist())
    sel_cats = st.multiselect("Category", all_cats, default=all_cats)

    all_locs = sorted(df_raw["location"].dropna().unique().tolist())
    sel_locs = st.multiselect("Location", all_locs, default=all_locs)

    all_brands = sorted(df_raw["brand"].dropna().unique().tolist())
    sel_brands = st.multiselect("Brand", all_brands, default=all_brands)

    st.markdown("---")
    st.caption("Amazon Sales Analytics · Built with Streamlit")

# ─────────────────────────────────────────────
# STEP 2 — DATA CLEANING
# ─────────────────────────────────────────────
df = df_raw.copy()

# Parse purchase_date
df["purchase_date"] = pd.to_datetime(df["purchase_date"], dayfirst=True, errors="coerce")

# Normalize boolean is_returned
df["is_returned"] = df["is_returned"].astype(str).str.upper().str.strip()
df["is_returned"] = df["is_returned"].map({"TRUE": True, "FALSE": False, "1": True, "0": False})

# Numeric coercion
for col in ["price", "discount", "final_price", "rating", "review_count",
            "stock", "seller_rating", "shipping_time_days"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ─────────────────────────────────────────────
# STEP 3 — SALES CALCULATION
# ─────────────────────────────────────────────
# Each row = 1 order / 1 unit. quantity = 1 per record.
df["quantity"] = 1
df["sales"] = df["quantity"] * df["final_price"]
df["discount_amount"] = df["price"] - df["final_price"]
df["discount_pct"] = df["discount"].fillna(0)

# ─────────────────────────────────────────────
# APPLY SIDEBAR FILTERS
# ─────────────────────────────────────────────
df_f = df[
    df["category"].isin(sel_cats) &
    df["location"].isin(sel_locs) &
    df["brand"].isin(sel_brands)
].copy()

if df_f.empty:
    st.warning("No data matches the current filters. Please adjust the sidebar filters.")
    st.stop()

# Derived time columns (after filter)
df_f["year"]       = df_f["purchase_date"].dt.year
df_f["month"]      = df_f["purchase_date"].dt.month
df_f["month_name"] = df_f["purchase_date"].dt.strftime("%b %Y")
df_f["weekday"]    = df_f["purchase_date"].dt.day_name()

# ─────────────────────────────────────────────
# PAGE TITLE
# ─────────────────────────────────────────────
st.markdown("# 🛒 Amazon Sales Data Analysis")
st.markdown(
    "An end-to-end analysis of **1,000 Amazon order records** — "
    "covering data quality, sales metrics, trends, and actionable business insights."
)
st.markdown("---")

# ─────────────────────────────────────────────
# TAB NAVIGATION
# ─────────────────────────────────────────────
tabs = st.tabs([
    "📋 Data Overview",
    "🧹 Data Quality",
    "💰 Sales Summary",
    "📊 Group Analysis",
    "📈 Charts",
    "💡 Business Insights",
])

# ══════════════════════════════════════════════
# TAB 1 — DATA OVERVIEW
# ══════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-header">1. Dataset Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Raw data loaded from CSV — first look at structure and content.</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Rows", fmt_num(len(df_f)))
    c2.metric("Total Columns", fmt_num(df_f.shape[1]))
    c3.metric("Categories", fmt_num(df_f["category"].nunique()))
    c4.metric("Unique Brands", fmt_num(df_f["brand"].nunique()))

    st.markdown("#### 🗂️ Raw Data Sample (first 20 rows)")
    st.dataframe(
        df_f.head(20).reset_index(drop=True),
        use_container_width=True,
        height=320,
    )

    st.markdown("#### 🏷️ Column Descriptions")
    col_desc = pd.DataFrame({
        "Column": df_f.columns.tolist(),
        "Data Type": df_f.dtypes.astype(str).tolist(),
        "Non-Null Count": df_f.notnull().sum().tolist(),
        "Unique Values": [df_f[c].nunique() for c in df_f.columns],
        "Sample Value": [str(df_f[c].dropna().iloc[0]) if df_f[c].dropna().shape[0] > 0 else "N/A" for c in df_f.columns],
    })
    st.dataframe(col_desc, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════
# TAB 2 — DATA QUALITY
# ══════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">2. Data Quality Check</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Identify missing values, duplicates, and out-of-range entries before analysis.</div>', unsafe_allow_html=True)

    # Missing values
    missing = df_f.isnull().sum()
    missing_pct = (missing / len(df_f) * 100).round(2)
    missing_df = pd.DataFrame({
        "Column": missing.index,
        "Missing Count": missing.values,
        "Missing %": missing_pct.values,
        "Status": ["✅ Clean" if v == 0 else "⚠️ Has Nulls" for v in missing.values],
    }).sort_values("Missing Count", ascending=False)

    st.markdown("#### 🔍 Missing Values per Column")
    st.dataframe(missing_df, use_container_width=True, hide_index=True)

    total_missing = missing.sum()
    if total_missing == 0:
        st.markdown('<div class="success-box">✅ <strong>No missing values found.</strong> The dataset is complete.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-box">⚠️ <strong>{total_missing} missing values</strong> detected across the dataset. Rows with missing critical fields have been excluded from calculations.</div>', unsafe_allow_html=True)

    # Duplicates
    dup_count = df_f.duplicated().sum()
    st.markdown("#### 🔁 Duplicate Rows")
    if dup_count == 0:
        st.markdown('<div class="success-box">✅ <strong>No duplicate rows found.</strong></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-box">⚠️ <strong>{dup_count} duplicate rows</strong> were found. Consider removing them before further analysis.</div>', unsafe_allow_html=True)

    # Negative / zero price check
    neg_price = (df_f["final_price"] <= 0).sum()
    st.markdown("#### 💲 Price Validity")
    if neg_price == 0:
        st.markdown('<div class="success-box">✅ All <strong>final_price</strong> values are positive.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-box">⚠️ <strong>{neg_price} rows</strong> have a zero or negative final_price — possible data errors.</div>', unsafe_allow_html=True)

    # Rating range check
    bad_rating = ((df_f["rating"] < 1) | (df_f["rating"] > 5)).sum()
    st.markdown("#### ⭐ Rating Range (1–5)")
    if bad_rating == 0:
        st.markdown('<div class="success-box">✅ All <strong>rating</strong> values are within the valid range (1–5).</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="warning-box">⚠️ <strong>{bad_rating} rows</strong> have ratings outside 1–5.</div>', unsafe_allow_html=True)

    # Statistical summary
    st.markdown("#### 📐 Statistical Summary (Numeric Columns)")
    numeric_cols = ["price", "discount", "final_price", "rating", "review_count",
                    "stock", "seller_rating", "shipping_time_days", "sales"]
    st.dataframe(
        df_f[numeric_cols].describe().T.round(2).rename(columns={"50%": "median"}),
        use_container_width=True,
    )

# ══════════════════════════════════════════════
# TAB 3 — SALES SUMMARY
# ══════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-header">3. Sales Calculation & Summary</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'Sales = Quantity × Unit Price &nbsp;|&nbsp; Each order row = 1 unit. '
        'Unit price = <code>final_price</code> (price after discount).'
        '</div>',
        unsafe_allow_html=True,
    )

    total_sales      = df_f["sales"].sum()
    total_orders     = len(df_f)
    avg_order_value  = df_f["sales"].mean()
    total_discount   = df_f["discount_amount"].sum()
    return_rate      = df_f["is_returned"].mean() * 100 if df_f["is_returned"].notna().any() else 0
    avg_rating       = df_f["rating"].mean()
    avg_ship_days    = df_f["shipping_time_days"].mean()

    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Total Revenue", fmt_inr(total_sales))
    c2.metric("🛍️ Total Orders", fmt_num(total_orders))
    c3.metric("📦 Avg. Order Value", fmt_inr(avg_order_value))

    c4, c5, c6 = st.columns(3)
    c4.metric("🏷️ Total Discounts Given", fmt_inr(total_discount))
    c5.metric("↩️ Return Rate", f"{return_rate:.1f}%")
    c6.metric("⭐ Avg. Product Rating", f"{avg_rating:.2f} / 5.0")

    st.markdown("#### 🧮 Sales Column Preview")
    st.dataframe(
        df_f[["user_id", "product_id", "category", "brand",
              "price", "discount", "final_price", "quantity", "sales"]]
        .head(15)
        .reset_index(drop=True)
        .rename(columns={
            "price": "Unit Price (₹)",
            "discount": "Discount (%)",
            "final_price": "Final Price (₹)",
            "sales": "Sales (₹)",
        }),
        use_container_width=True,
        height=360,
    )

# ══════════════════════════════════════════════
# TAB 4 — GROUP ANALYSIS
# ══════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">4. Group & Summarize</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Totals, counts, and averages grouped by Category, Brand, Location, Payment Method, and Delivery Status.</div>', unsafe_allow_html=True)

    def make_summary(group_col, label):
        g = (
            df_f.groupby(group_col)
            .agg(
                Total_Sales=("sales", "sum"),
                Total_Orders=("sales", "count"),
                Avg_Order_Value=("sales", "mean"),
                Avg_Rating=("rating", "mean"),
                Avg_Discount=("discount_pct", "mean"),
                Avg_Shipping_Days=("shipping_time_days", "mean"),
            )
            .reset_index()
            .sort_values("Total_Sales", ascending=False)
        )
        g["Total_Sales"]       = g["Total_Sales"].round(2)
        g["Avg_Order_Value"]   = g["Avg_Order_Value"].round(2)
        g["Avg_Rating"]        = g["Avg_Rating"].round(2)
        g["Avg_Discount"]      = g["Avg_Discount"].round(2)
        g["Avg_Shipping_Days"] = g["Avg_Shipping_Days"].round(2)
        g.columns = [label, "Total Sales (₹)", "Orders", "Avg Order (₹)", "Avg Rating", "Avg Disc. %", "Avg Ship Days"]
        return g

    groupings = {
        "Category":       "category",
        "Brand":          "brand",
        "Location":       "location",
        "Payment Method": "payment_method",
        "Delivery Status":"delivery_status",
        "Device":         "device",
    }

    for title, col in groupings.items():
        st.markdown(f"##### 📌 By {title}")
        summary_df = make_summary(col, title)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
        st.markdown("")

# ══════════════════════════════════════════════
# TAB 5 — CHARTS
# ══════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-header">5. Visual Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Interactive charts to compare sales, returns, ratings, discounts, and trends.</div>', unsafe_allow_html=True)

    # ── 5.1 Total Sales by Category
    st.markdown("#### 🏷️ Total Sales by Category")
    cat_sales = df_f.groupby("category")["sales"].sum().reset_index().sort_values("sales", ascending=True)
    fig1 = px.bar(
        cat_sales, x="sales", y="category", orientation="h",
        color="category", color_discrete_sequence=CHART_COLORS,
        labels={"sales": "Total Sales (₹)", "category": ""},
        text=cat_sales["sales"].apply(lambda x: f"₹{x:,.0f}"),
    )
    fig1.update_traces(textposition="outside", textfont_size=11)
    fig1.update_layout(showlegend=False, height=350, margin=dict(l=10, r=10, t=10, b=10),
                       plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff")
    st.plotly_chart(fig1, use_container_width=True)

    # ── 5.2 Monthly Revenue Trend
    st.markdown("#### 📅 Monthly Revenue Trend")
    monthly = df_f.groupby(df_f["purchase_date"].dt.to_period("M"))["sales"].sum().reset_index()
    monthly["purchase_date"] = monthly["purchase_date"].astype(str)
    monthly = monthly.sort_values("purchase_date")
    fig2 = px.line(
        monthly, x="purchase_date", y="sales",
        markers=True, labels={"sales": "Revenue (₹)", "purchase_date": "Month"},
        color_discrete_sequence=["#3b82d4"],
    )
    fig2.update_layout(height=320, plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    col_a, col_b = st.columns(2)

    # ── 5.3 Sales by Location
    with col_a:
        st.markdown("#### 📍 Sales by Location")
        loc_sales = df_f.groupby("location")["sales"].sum().reset_index().sort_values("sales", ascending=False)
        fig3 = px.pie(
            loc_sales, names="location", values="sales",
            color_discrete_sequence=CHART_COLORS, hole=0.4,
        )
        fig3.update_layout(height=340, paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig3, use_container_width=True)

    # ── 5.4 Payment Method Distribution
    with col_b:
        st.markdown("#### 💳 Orders by Payment Method")
        pay_cnt = df_f["payment_method"].value_counts().reset_index()
        pay_cnt.columns = ["Payment Method", "Orders"]
        fig4 = px.pie(
            pay_cnt, names="Payment Method", values="Orders",
            color_discrete_sequence=CHART_COLORS, hole=0.4,
        )
        fig4.update_layout(height=340, paper_bgcolor="#ffffff", margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig4, use_container_width=True)

    # ── 5.5 Top 10 Brands by Revenue
    st.markdown("#### 🏆 Top 10 Brands by Revenue")
    brand_sales = df_f.groupby("brand")["sales"].sum().nlargest(10).reset_index().sort_values("sales", ascending=True)
    fig5 = px.bar(
        brand_sales, x="sales", y="brand", orientation="h",
        color="sales", color_continuous_scale="Blues",
        labels={"sales": "Total Sales (₹)", "brand": ""},
        text=brand_sales["sales"].apply(lambda x: f"₹{x:,.0f}"),
    )
    fig5.update_traces(textposition="outside", textfont_size=11)
    fig5.update_layout(showlegend=False, height=360, coloraxis_showscale=False,
                       plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig5, use_container_width=True)

    col_c, col_d = st.columns(2)

    # ── 5.6 Return Rate by Category
    with col_c:
        st.markdown("#### ↩️ Return Rate by Category (%)")
        ret_df = (
            df_f.groupby("category")["is_returned"]
            .apply(lambda x: x.mean() * 100)
            .reset_index()
            .rename(columns={"is_returned": "Return Rate (%)"})
            .sort_values("Return Rate (%)", ascending=False)
        )
        fig6 = px.bar(
            ret_df, x="category", y="Return Rate (%)",
            color="Return Rate (%)", color_continuous_scale="Reds",
            text=ret_df["Return Rate (%)"].apply(lambda x: f"{x:.1f}%"),
        )
        fig6.update_traces(textposition="outside")
        fig6.update_layout(coloraxis_showscale=False, height=320,
                           plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                           margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig6, use_container_width=True)

    # ── 5.7 Average Rating by Category
    with col_d:
        st.markdown("#### ⭐ Avg. Rating by Category")
        rat_df = (
            df_f.groupby("category")["rating"].mean()
            .reset_index()
            .rename(columns={"rating": "Avg Rating"})
            .sort_values("Avg Rating", ascending=False)
        )
        fig7 = px.bar(
            rat_df, x="category", y="Avg Rating",
            color="Avg Rating", color_continuous_scale="Greens",
            text=rat_df["Avg Rating"].apply(lambda x: f"{x:.2f}"),
        )
        fig7.update_traces(textposition="outside")
        fig7.update_layout(coloraxis_showscale=False, height=320,
                           yaxis_range=[0, 5.5],
                           plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                           margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig7, use_container_width=True)

    # ── 5.8 Discount % vs Sales Scatter
    st.markdown("#### 🏷️ Discount % vs Sales Amount")
    fig8 = px.scatter(
        df_f.sample(min(500, len(df_f)), random_state=42),
        x="discount_pct", y="sales", color="category",
        size="review_count", hover_data=["brand", "location"],
        color_discrete_sequence=CHART_COLORS,
        labels={"discount_pct": "Discount (%)", "sales": "Sale Value (₹)"},
        opacity=0.7,
    )
    fig8.update_layout(height=380, plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig8, use_container_width=True)

    # ── 5.9 Delivery Status Breakdown
    st.markdown("#### 🚚 Delivery Status Distribution")
    deliv = df_f["delivery_status"].value_counts().reset_index()
    deliv.columns = ["Status", "Count"]
    fig9 = px.bar(
        deliv, x="Status", y="Count",
        color="Status", color_discrete_sequence=CHART_COLORS,
        text="Count",
    )
    fig9.update_traces(textposition="outside")
    fig9.update_layout(showlegend=False, height=320,
                       plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                       margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig9, use_container_width=True)

    # ── 5.10 Avg Shipping Days by Location
    st.markdown("#### 📦 Avg. Shipping Days by Location")
    ship_df = (
        df_f.groupby("location")["shipping_time_days"].mean()
        .reset_index()
        .sort_values("shipping_time_days", ascending=False)
    )
    fig10 = px.bar(
        ship_df, x="location", y="shipping_time_days",
        color="shipping_time_days", color_continuous_scale="Oranges",
        text=ship_df["shipping_time_days"].apply(lambda x: f"{x:.1f}d"),
        labels={"shipping_time_days": "Avg Days", "location": "City"},
    )
    fig10.update_traces(textposition="outside")
    fig10.update_layout(coloraxis_showscale=False, height=320,
                        plot_bgcolor="#f7f8fa", paper_bgcolor="#ffffff",
                        margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig10, use_container_width=True)

# ══════════════════════════════════════════════
# TAB 6 — BUSINESS INSIGHTS
# ══════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-header">6. Business Decisions & Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Data-driven recommendations derived from the analysis above.</div>', unsafe_allow_html=True)

    # Compute key facts for dynamic insights
    top_cat       = df_f.groupby("category")["sales"].sum().idxmax()
    top_cat_val   = df_f.groupby("category")["sales"].sum().max()
    bot_cat       = df_f.groupby("category")["sales"].sum().idxmin()
    top_brand     = df_f.groupby("brand")["sales"].sum().idxmax()
    top_loc       = df_f.groupby("location")["sales"].sum().idxmax()
    high_ret_cat  = df_f.groupby("category")["is_returned"].mean().idxmax()
    high_ret_pct  = df_f.groupby("category")["is_returned"].mean().max() * 100
    low_rat_cat   = df_f.groupby("category")["rating"].mean().idxmin()
    low_rat_val   = df_f.groupby("category")["rating"].mean().min()
    top_pay       = df_f["payment_method"].value_counts().idxmax()
    top_device    = df_f["device"].value_counts().idxmax()
    slow_loc      = df_f.groupby("location")["shipping_time_days"].mean().idxmax()
    slow_days     = df_f.groupby("location")["shipping_time_days"].mean().max()
    avg_disc      = df_f["discount_pct"].mean()
    high_disc_cat = df_f.groupby("category")["discount_pct"].mean().idxmax()
    high_disc_val = df_f.groupby("category")["discount_pct"].mean().max()

    st.markdown("### 📌 Key Findings & Recommendations")

    insights = [
        ("🏆 Top Revenue Category",
         f"<strong>{top_cat}</strong> generates the highest revenue at <strong>{fmt_inr(top_cat_val)}</strong>. "
         f"Prioritize inventory, ad spend, and promotions for this category to maximize revenue."),
        ("📉 Underperforming Category",
         f"<strong>{bot_cat}</strong> has the lowest total sales. "
         f"Review product listings, pricing strategy, and marketing efforts — or consider discontinuing low-margin SKUs."),
        ("🏷️ Best-Selling Brand",
         f"<strong>{top_brand}</strong> is the top-performing brand by revenue. "
         f"Negotiate preferential placement or exclusive deals to strengthen this partnership."),
        ("📍 Top Sales City",
         f"<strong>{top_loc}</strong> drives the most orders. "
         f"Allocate more warehouse stock near this location to reduce shipping time and improve customer satisfaction."),
        ("↩️ High Return Category",
         f"<strong>{high_ret_cat}</strong> has a return rate of <strong>{high_ret_pct:.1f}%</strong>. "
         f"Investigate quality issues, misleading product descriptions, or sizing discrepancies. "
         f"Improving product pages can reduce returns and associated costs."),
        ("⭐ Low-Rated Category",
         f"<strong>{low_rat_cat}</strong> has the lowest average rating of <strong>{low_rat_val:.2f}/5.0</strong>. "
         f"Gather customer feedback, improve product quality, and respond to reviews to build trust."),
        ("💳 Preferred Payment Method",
         f"<strong>{top_pay}</strong> is the most used payment method. "
         f"Ensure a seamless checkout experience for this method and offer exclusive cashback/discounts to increase conversion."),
        ("📱 Top Device",
         f"Most orders come from <strong>{top_device}</strong> users. "
         f"Optimize the shopping experience for this platform — ensure fast load times, responsive UI, and easy checkout."),
        ("🚚 Slowest Shipping City",
         f"<strong>{slow_loc}</strong> has the longest average shipping time of <strong>{slow_days:.1f} days</strong>. "
         f"Partner with local logistics providers or open a fulfillment center nearby to meet delivery expectations."),
        ("🏷️ Discount Strategy",
         f"The average discount across all orders is <strong>{avg_disc:.1f}%</strong>. "
         f"<strong>{high_disc_cat}</strong> receives the highest average discount of <strong>{high_disc_val:.1f}%</strong>. "
         f"Review whether these deep discounts are driving incremental revenue or eroding margins."),
    ]

    for title, body in insights:
        st.markdown(
            f'<div class="insight-box"><strong>{title}</strong><br>{body}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 📊 Summary Scorecard")
    score_data = {
        "Metric": [
            "Total Revenue", "Total Orders", "Avg Order Value",
            "Return Rate", "Avg Product Rating", "Avg Shipping Days",
            "Total Discounts Given", "Top Category", "Top Brand", "Top City",
        ],
        "Value": [
            fmt_inr(total_sales), fmt_num(total_orders), fmt_inr(avg_order_value),
            f"{return_rate:.1f}%", f"{avg_rating:.2f} / 5.0", f"{avg_ship_days:.1f} days",
            fmt_inr(total_discount), top_cat, top_brand, top_loc,
        ],
    }
    st.dataframe(pd.DataFrame(score_data), use_container_width=True, hide_index=True, height=390)

    st.markdown("---")
    st.caption("📌 All insights are derived from the filtered dataset shown in the sidebar. Adjust filters to drill down further.")
