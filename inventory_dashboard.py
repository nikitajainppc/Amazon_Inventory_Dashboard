import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Setup
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.title("📊 Amazon Inventory Dashboard")
st.markdown("This dashboard helps track Amazon FBA stock levels, values, and fulfillment risks in real-time.")

# --- Load Data ---
@st.cache_data
def load_data():
    return pd.read_csv("SmoothOn Inventory - Sheet1.csv")

df = load_data()

# --- Top-Level KPIs ---
st.markdown("### 🔍 Summary")

total_skus = df.shape[0]
total_value = df['Inventory Value'].sum()
low_stock = df[df['Quantity'] < 10].shape[0]
overstock = df[df['Quantity'] > 100].shape[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total SKUs", total_skus)
col2.metric("💰 Total Inventory Value", f"${total_value:,.2f}")
col3.metric("📉 Low Stock (<10)", low_stock)
col4.metric("📦 Overstocked (>100)", overstock)

st.divider()

# --- Quantity Distribution Chart ---
st.markdown("### 📦 Quantity Distribution")

bins = [0, 10, 50, 100, 500, df['Quantity'].max() + 1]
labels = ['0–10', '11–50', '51–100', '101–500', '500+']
df['Quantity Category'] = pd.cut(df['Quantity'], bins=bins, labels=labels)

qty_dist = df['Quantity Category'].value_counts().sort_index()

fig, ax = plt.subplots()
qty_dist.plot(kind='bar', color='skyblue', ax=ax)
ax.set_xlabel("Quantity Ranges")
ax.set_ylabel("Number of SKUs")
ax.set_title("Distribution of Stock Quantity")
st.pyplot(fig)

st.divider()

# --- Top Products ---
st.markdown("### 💎 Top 10 SKUs by Inventory Value")

top_products = df.sort_values(by="Inventory Value", ascending=False).head(10)
st.dataframe(top_products, use_container_width=True)

st.divider()

# --- Raw Data Option ---
with st.expander("📄 View Full Inventory Table"):
    st.dataframe(df, use_container_width=True)
