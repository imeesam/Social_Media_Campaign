import streamlit as st
import plotly.express as px
import pandas as pd
import sqlite3
import os
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(page_title="Social Media Campaign Analysis", page_icon=":bar_chart:", layout="wide")

# Title and introduction
st.title(":bar_chart: Social Media Campaign Analysis Dashboard")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
st.markdown("Welcome to the Social Media Campaign Analysis Dashboard. This tool allows you to upload campaign data, filter it based on various criteria, and visualize key metrics and trends.")

# File uploader
file_uploaded = st.file_uploader(":file_folder: Upload a CSV file", type=["csv"])

if file_uploaded:
    try:
        df = pd.read_csv(file_uploaded, encoding="ISO-8859-1")
        st.write(f"Uploaded file: {file_uploaded.name}")
        
        # Database setup
        conn = sqlite3.connect('campaign_data.db')
        df.to_sql('campaign_data', conn, if_exists='replace', index=False)
        st.success("Data loaded successfully into the database.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()
else:
    st.warning("Please upload a CSV file to proceed.")
    st.stop()

# Data preprocessing
df["Order Date"] = pd.to_datetime(df["Order Date"])
df["month_year"] = df["Order Date"].dt.to_period("M")

# Sidebar filters
st.sidebar.header("Filters:")
region = st.sidebar.multiselect("Select Region(s)", df["Region"].unique())
state = st.sidebar.multiselect("Select State(s)", df["State"].unique())
city = st.sidebar.multiselect("Select City/Cities", df["City"].unique())

# Date filter
start_date = st.sidebar.date_input("Start Date", df["Order Date"].min().date())
end_date = st.sidebar.date_input("End Date", df["Order Date"].max().date())

if start_date > end_date:
    st.sidebar.error("Error: End date must be after start date.")
    st.stop()

# Apply filters
start_date = datetime.combine(start_date, datetime.min.time())
end_date = datetime.combine(end_date, datetime.max.time())
filtered_df = df[(df["Order Date"] >= start_date) & (df["Order Date"] <= end_date)]
if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

# Display data statistics
st.subheader("Data Overview")
st.write(filtered_df.describe())

# Category-wise Sales
category_df = filtered_df.groupby("Category")["Sales"].sum().reset_index()
st.subheader("Category-wise Sales")
fig = px.bar(category_df, x="Category", y="Sales", text=category_df["Sales"].apply(lambda x: f"${x:,.2f}"), template="seaborn")
st.plotly_chart(fig, use_container_width=True)

# Region-wise Sales
region_df = filtered_df.groupby("Region")["Sales"].sum().reset_index()
st.subheader("Region-wise Sales")
fig = px.pie(region_df, values="Sales", names="Region", hole=0.5)
st.plotly_chart(fig, use_container_width=True)

# Time Series Analysis
st.subheader('Time Series Analysis')
linechart = filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y-%m"))["Sales"].sum().reset_index()
fig = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig, use_container_width=True)

# Treemap
st.subheader("Hierarchical View of Sales using TreeMap")
fig = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
st.plotly_chart(fig, use_container_width=True)

# Segment-wise Sales
segment_df = filtered_df.groupby("Segment")["Sales"].sum().reset_index()
st.subheader("Segment-wise Sales")
fig = px.pie(segment_df, values="Sales", names="Segment", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Scatter Plot
st.subheader("Relationship between Sales and Profit")
fig = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity", title="Relationship between Sales and Profits using Scatter Plot.")
st.plotly_chart(fig, use_container_width=True)

# Data download buttons
csv_filtered = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button('Download Filtered Data', data=csv_filtered, file_name="filtered_data.csv", mime="text/csv")

csv_original = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Original Data', data=csv_original, file_name="original_data.csv", mime="text/csv")

st.sidebar.markdown("---")
st.sidebar.markdown("**User Instructions:**")
st.sidebar.markdown("1. Upload a CSV file containing your campaign data.")
st.sidebar.markdown("2. Use the filters to narrow down the data based on Region, State, and City.")
st.sidebar.markdown("3. View and interact with the visualizations to gain insights.")
st.sidebar.markdown("4. Download the filtered data for further analysis.")

# Close database connection
conn.close()

st.markdown("**Thank you for using the Social Media Campaign Analysis Dashboard!**")
st.markdown("For any queries or support, please contact us at meesam297@gmail.com.")
