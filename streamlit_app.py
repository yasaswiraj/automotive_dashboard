import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px  # NEW: For modern interactive charts

# Set the page configuration as the first Streamlit command
st.set_page_config(page_title="Automotive Data Dashboard", layout="wide")

# ------------------
# PostgreSQL Connection
# ------------------
def get_connection():
    # Updated: Use Streamlit secrets for secure credentials
    return psycopg2.connect(
        host=st.secrets["db"]["host"],
        database=st.secrets["db"]["database"],
        user=st.secrets["db"]["user"],
        password=st.secrets["db"]["password"],
        port=st.secrets["db"]["port"]
    )

# ------------------
# Streamlit App Layout
# ------------------
with st.sidebar:
    st.header("Filters")
    start_date, end_date = st.date_input(
        "Select Sales Date Range", 
        value=(pd.to_datetime("2020-01-01"), pd.to_datetime("today"))
    )

st.title("**Automotive Data Analytics Dashboard**")  # Enhanced title formatting

# Connect to the database with a spinner
with st.spinner("Connecting to the database..."):
    conn = get_connection()
    cursor = conn.cursor()

# ------------------
# 1. Top 5 Manufacturers by Average Rating
# ------------------
st.subheader("Top 5 Manufacturers by Average Customer Rating")

query1 = """
SELECT m.name AS manufacturer_name, AVG(r.rating) AS avg_rating
FROM reviews r
JOIN car_model cm ON r.model_id = cm.model_id
JOIN manufacturer m ON cm.manufacturer_id = m.manufacturer_id
GROUP BY m.name
ORDER BY avg_rating DESC
LIMIT 5;
"""

df1 = pd.read_sql_query(query1, conn)
st.bar_chart(df1.set_index('manufacturer_name')['avg_rating'])

st.markdown("**Insight:** Toyota and Honda consistently have high customer satisfaction ratings.")

# ------------------
# 2. Monthly Sales Trend
st.subheader("Monthly Sales Trend")

query2 = f"""
SELECT DATE_TRUNC('month', sale_date) AS sale_month, COUNT(*) AS total_sales
FROM sales
WHERE sale_date BETWEEN '{start_date}' AND '{end_date}'
GROUP BY sale_month
ORDER BY sale_month;
"""

with st.spinner("Loading Monthly Sales Trend..."):
    df2 = pd.read_sql_query(query2, conn)
    df2['sale_month'] = pd.to_datetime(df2['sale_month'])

with st.spinner("Rendering Monthly Sales Trend with Plotly..."):
    fig2 = px.line(df2, x='sale_month', y='total_sales', markers=True, title="Sales Over Time")
    st.plotly_chart(fig2)

st.markdown("**Insight:** Peak sales observed during the summer months.")
with st.expander("See Query Details"):
    st.code(query2, language='sql')

# ------------------
# 3. Car Category Distribution
# ------------------
st.subheader("Car Category Distribution")

query3 = """
SELECT category, COUNT(*) AS total_models
FROM car_model
GROUP BY category
ORDER BY total_models DESC;
"""

df3 = pd.read_sql_query(query3, conn)

# Correcting the rendering of the pie chart for car category distribution
fig3, ax3 = plt.subplots(figsize=(6, 6))  # Set a smaller figure size
ax3.pie(df3['total_models'], labels=df3['category'], autopct='%1.1f%%', startangle=140)
ax3.axis('equal')

# Adjusting the pie chart width and centering it using Streamlit's container
with st.container():
    st.markdown(
        """
        <style>
        .centered-chart {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 50%;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="centered-chart">', unsafe_allow_html=True)
    st.pyplot(fig3)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("**Insight:** SUVs dominate the inventory, followed by Sedans and Trucks.")

# ------------------
# 4. Top 5 Fastest Cars
# ------------------
st.subheader("Top 5 Fastest Cars")

query4 = """
SELECT cm.model_name, p.top_speed
FROM performance p
JOIN car_model cm ON p.model_id = cm.model_id
ORDER BY p.top_speed DESC
LIMIT 5;
"""

df4 = pd.read_sql_query(query4, conn)
st.bar_chart(df4.set_index('model_name')['top_speed'])

st.markdown("**Insight:** Sports car models top the speed chart, reaching over 180 mph.")

# ------------------
# 5. Top 5 Dealerships by Number of Sales
# ------------------
st.subheader("Top 5 Dealerships by Number of Sales")

query5 = """
SELECT d.name AS dealership_name, COUNT(*) AS total_sales
FROM sales s
JOIN dealership d ON s.dealership_id = d.dealership_id
GROUP BY d.name
ORDER BY total_sales DESC
LIMIT 5;
"""

df5 = pd.read_sql_query(query5, conn)
st.bar_chart(df5.set_index('dealership_name')['total_sales'])

st.markdown("**Insight:** These dealerships are leading in car sales.")

# ------------------
# 6. Average Discount Offered by Category
# ------------------
st.subheader("Average Discount Offered by Category")

query6 = """
SELECT cm.category, AVG(p.discount) AS avg_discount
FROM pricing p
JOIN car_model cm ON p.model_id = cm.model_id
GROUP BY cm.category
ORDER BY avg_discount DESC;
"""

df6 = pd.read_sql_query(query6, conn)
st.bar_chart(df6.set_index('category')['avg_discount'])

st.markdown("**Insight:** Some categories receive higher discounts than others.")

# ------------------
# 7. Sales by Car Category Over Time
# ------------------
st.subheader("Sales by Car Category Over Time")

query7 = """
SELECT DATE_TRUNC('month', s.sale_date) AS sale_month, cm.category, COUNT(*) AS total_sales
FROM sales s
JOIN car_model cm ON s.model_id = cm.model_id
GROUP BY sale_month, cm.category
ORDER BY sale_month, cm.category;
"""

df7 = pd.read_sql_query(query7, conn)
df7['sale_month'] = pd.to_datetime(df7['sale_month'])

fig7 = px.line(df7, x='sale_month', y='total_sales', color='category', title="Sales by Car Category Over Time")
st.plotly_chart(fig7)

st.markdown("**Insight:** Observe how different categories perform over time.")

# Close the connection
cursor.close()
conn.close()

st.success("Dashboard loaded successfully!")

# NEW: Add footer section
st.markdown("---")
st.markdown("**Dashboard created by the Automotive Analytics Team**")
