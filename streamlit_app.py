import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="Automotive Data Dashboard", layout="wide")

def get_connection():
    return psycopg2.connect(
        host=st.secrets["db"]["host"],
        database=st.secrets["db"]["database"],
        user=st.secrets["db"]["user"],
        password=st.secrets["db"]["password"],
        port=st.secrets["db"]["port"]
    )

with st.sidebar:
    st.header("Filters")
    start_date, end_date = st.date_input(
        "Select Sales Date Range", 
        value=(pd.to_datetime("2020-01-01"), pd.to_datetime("today"))
    )

st.title("Automotive Data Analytics Dashboard")

with st.spinner("Connecting to the database..."):
    conn = get_connection()
    cursor = conn.cursor()

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

with st.expander("See Query Details"):
    st.code(query2, language='sql')

st.subheader("Car Category Distribution")

query3 = """
SELECT category, COUNT(*) AS total_models
FROM car_model
GROUP BY category
ORDER BY total_models DESC;
"""

df3 = pd.read_sql_query(query3, conn)

fig3, ax3 = plt.subplots(figsize=(6, 6))
ax3.pie(df3['total_models'], labels=df3['category'], autopct='%1.1f%%', startangle=140)
ax3.axis('equal')

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

cursor.close()
conn.close()

st.success("Dashboard loaded successfully!")

st.markdown("---")
st.markdown("Dashboard created by the Automotive Analytics Team")
