import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.title("📊 Amazon Inventory Dashboard")
st.markdown("This dashboard tracks FBA stock levels, values, and restocking needs.")

# Upload CSV
uploaded_file = st.sidebar.file_uploader("📁 Upload Inventory CSV", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Clean columns
    df.columns = df.columns.str.strip().str.lower()
    df['inventory_value'] = df['price'] * df['quantity']

    # KPIs
    total_skus = df.shape[0]
    total_value = df['inventory_value'].sum()
    low_stock = df[df['quantity'] < 10].shape[0]
    overstock = df[df['quantity'] > 100].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧾 Total SKUs", total_skus)
    col2.metric("💰 Inventory Value", f"${total_value:,.2f}")
    col3.metric("📉 Low Stock (<10)", low_stock)
    col4.metric("📦 Overstocked (>100)", overstock)

    st.divider()

    # Quantity Bins
    bins = [0, 10, 50, 100, 500, df['quantity'].max() + 1]
    labels = ['0–10', '11–50', '51–100', '101–500', '500+']
    df['quantity_range'] = pd.cut(df['quantity'], bins=bins, labels=labels)

    st.subheader("📦 Quantity Distribution")
    dist = df['quantity_range'].value_counts().sort_index()

    fig, ax = plt.subplots()
    dist.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_ylabel("Number of SKUs")
    ax.set_xlabel("Quantity Range")
    ax.set_title("Distribution of Inventory Levels")
    st.pyplot(fig)

    st.divider()

    # Top Products by Inventory Value
    st.subheader("💎 Top 10 SKUs by Inventory Value")
    top10 = df.sort_values(by="inventory_value", ascending=False).head(10)
    st.dataframe(top10, use_container_width=True)

    # View all
    with st.expander("📄 View Full Inventory Table"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("Please upload your inventory CSV to begin.")
