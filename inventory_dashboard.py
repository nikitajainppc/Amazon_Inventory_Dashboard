import streamlit as st
import pandas as pd

# ------------------ PAGE CONFIGURATION ------------------
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.markdown("## 📦 Amazon Inventory Dashboard")
st.markdown("Upload your **Active Inventory Report** in `.txt` or `.csv` format.")

# ------------------ FILE UPLOADER ------------------
uploaded_file = st.file_uploader("Upload Inventory Report", type=['csv', 'txt'])

# Required fields in Amazon inventory file
required_columns = ['sku', 'quantity', 'fulfillment-channel']

# ------------------ PROCESS FILE ------------------
if uploaded_file:
    try:
        # Determine delimiter based on file type
        if uploaded_file.name.endswith('.txt'):
            df = pd.read_csv(uploaded_file, delimiter='\t')
        else:
            df = pd.read_csv(uploaded_file)

        st.success("✅ File uploaded successfully!")
        st.markdown("### 🔍 File Preview")
        st.dataframe(df.head())

        # ------------------ VALIDATE COLUMNS ------------------
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            st.error(f"🚫 Missing required columns: {', '.join(missing)}")
        else:
            st.success("✅ All required columns are present.")

            # ------------------ DASHBOARD METRICS ------------------
            st.markdown("### 📊 Inventory Summary")

            col1, col2, col3 = st.columns(3)
            col1.metric("Total SKUs", df['sku'].nunique())
            col2.metric("Total Quantity", int(df['quantity'].sum()))
            col3.metric("Fulfillment Channels", ', '.join(df['fulfillment-channel'].dropna().unique()))

            # ------------------ OPTIONAL: ADVANCED STATS ------------------
            st.markdown("### 📈 Inventory Breakdown")
            breakdown = df.groupby('fulfillment-channel')['quantity'].sum().reset_index()
            st.bar_chart(breakdown.set_index('fulfillment-channel'))

    except Exception as e:
        st.error(f"❌ Error processing file: {str(e)}")

else:
    st.info("📂 Please upload a valid `.csv` or `.txt` file to get started.")

# ------------------ FAQ / HELP SECTION ------------------
with st.expander("❓ Why is my file not uploading or showing data?"):
    st.markdown("""
    - ✅ Ensure the file is in `.csv` or `.txt` format.
    - 🔑 It must include required columns like `sku`, `quantity`, and `fulfillment-channel`.
    - 🧾 File may be tab-delimited (`.txt`) or comma-delimited (`.csv`).
    - ⚠️ Avoid uploading files that are empty or corrupted.
    - 📤 Use the 'Active Inventory Report' downloaded from Amazon Seller Central.
    """)

# ------------------ FOOTER ------------------
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
