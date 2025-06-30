import streamlit as st
import pandas as pd
import altair as alt

# Set up Streamlit
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.title("📦 Amazon Inventory Dashboard")
st.markdown("Track stock health, value, and insights for smarter ad decisions.")

# Sidebar: Upload CSV
uploaded_file = st.sidebar.file_uploader("📁 Upload Inventory CSV", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Calculate values
    df["inventory_value"] = df["price"] * df["quantity"]
    df["status"] = df["quantity"].apply(
        lambda x: "✅ In Stock" if x > 10 else ("⚠️ Low Stock" if 1 <= x <= 10 else "❌ Out of Stock")
    )

    # KPIs
    total_skus = df['sku'].nunique()
    total_value = df['inventory_value'].sum()
    out_of_stock = df[df['quantity'] == 0].shape[0]
    low_stock = df[df['quantity'] <= 10].shape[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total SKUs", total_skus)
    col2.metric("Inventory Value ($)", f"{total_value:,.2f}")
    col3.metric("Out of Stock", out_of_stock)
    col4.metric("Low Stock (≤10)", low_stock)

    st.divider()

    # Filters
    st.sidebar.header("🔍 Filters")
    search = st.sidebar.text_input("Search SKU/ASIN")
    min_qty = st.sidebar.slider("Minimum Quantity", 0, int(df["quantity"].max()), 0)

    filtered_df = df[df["quantity"] >= min_qty]
    if search:
        filtered_df = filtered_df[
            filtered_df["sku"].astype(str).str.contains(search, case=False) |
            filtered_df["asin"].astype(str).str.contains(search, case=False)
        ]

    # Bar chart – Top SKUs by Inventory Value
    st.subheader("💰 Top 10 Products by Inventory Value")
    top_10 = df.sort_values("inventory_value", ascending=False).head(10)
    chart = alt.Chart(top_10).mark_bar().encode(
        x=alt.X("inventory_value:Q", title="Inventory Value ($)"),
        y=alt.Y("sku:N", sort='-x', title="SKU"),
        color=alt.Color("status:N", title="Stock Status")
    ).properties(height=400)
    st.altair_chart(chart, use_container_width=True)

    # Pie Chart – Stock Status Distribution
    st.subheader("📊 Inventory Status Distribution")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    pie_chart = alt.Chart(status_counts).mark_arc(innerRadius=50).encode(
        theta="Count:Q",
        color="Status:N",
        tooltip=["Status", "Count"]
    )
    st.altair_chart(pie_chart, use_container_width=True)

    # Smart Alerts
    st.subheader("🚨 Smart Alerts")
    with st.expander("⚠️ Out-of-Stock Items Still Running Ads?"):
        oos = df[df["quantity"] == 0]
        st.dataframe(oos, use_container_width=True)
        st.download_button("⬇️ Download OOS Items", oos.to_csv(index=False), "out_of_stock.csv", "text/csv")

    with st.expander("⚠️ Low Inventory Items"):
        low = df[df["quantity"] <= 10]
        st.dataframe(low, use_container_width=True)
        st.download_button("⬇️ Download Low Stock", low.to_csv(index=False), "low_stock.csv", "text/csv")

    # Final table
    st.subheader("📋 Full Inventory")
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button("⬇️ Download Filtered Inventory", filtered_df.to_csv(index=False), "filtered_inventory.csv", "text/csv")

else:
    st.info("Upload a CSV file to view your inventory dashboard.")
