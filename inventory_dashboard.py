import streamlit as st
import pandas as pd
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.title(":package: Amazon Inventory Dashboard")
uploaded_file = st.file_uploader("Upload your Active Inventory Report (CSV)", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader(":clipboard: Raw Data")
    st.dataframe(df)
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
    df['inventory_status'] = df['quantity'].apply(
        lambda x: 'Out of Stock' if x == 0 else ('Low Inventory' if x < 10 else 'In Stock')
    )
    st.subheader(":bar_chart: Inventory Summary")
    summary = df['inventory_status'].value_counts().rename_axis('Status').reset_index(name='Count')
    st.table(summary)
    status_filter = st.multiselect(":mag: Filter by Inventory Status", options=df['inventory_status'].unique(), default=df['inventory_status'].unique())
    filtered_df = df[df['inventory_status'].isin(status_filter)]
    st.subheader(":package: Filtered Inventory Report")
    st.dataframe(filtered_df)
    csv_export = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(":inbox_tray: Download Filtered Report", csv_export, file_name="Filtered_Inventory_Report.csv", mime='text/csv')
else:
    st.info("Upload a CSV file to get started.")
