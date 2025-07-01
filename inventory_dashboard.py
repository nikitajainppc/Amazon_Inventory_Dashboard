import streamlit as st
import pandas as pd
import os

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Amazon Inventory Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ------------------ CUSTOM STYLING ------------------
dark_theme_style = """
    <style>
    html, body, [class*="css"]  {
        background-color: #1e1e1e !important;
        color: #f5f5f5 !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5em 1em;
        font-weight: bold;
    }
    .stMetricLabel {
        color: #999 !important;
    }
    </style>
"""
st.markdown(dark_theme_style, unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.title("📦 Amazon Inventory Dashboard")
st.markdown("Upload your **Active Listings Report** from Seller Central in `.csv`, `.txt`, `.tsv`, `.xls`, or `.xlsx` format.")

# ------------------ FILE UPLOADER ------------------
uploaded_file = st.file_uploader("Upload Inventory Report", type=None)

# ------------------ FILE READER ------------------
def load_file(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == '.csv':
        return pd.read_csv(file)
    elif ext == '.tsv':
        return pd.read_csv(file, delimiter='\t')
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(file)
    elif ext == '.txt':
        content = file.getvalue().decode('utf-8', errors='ignore')
        delimiter = '\t' if '\t' in content else ','
        file.seek(0)
        return pd.read_csv(file, delimiter=delimiter)
    else:
        raise ValueError("Unsupported file format.")

# ------------------ MAIN ------------------
if uploaded_file:
    try:
        df = load_file(uploaded_file)
        df.columns = df.columns.str.lower().str.strip()

        has_asin = 'asin' in df.columns
        has_asin1 = 'asin1' in df.columns
        has_quantity = 'quantity' in df.columns

        if not (has_asin or has_asin1):
            st.error("Missing ASIN column: must include `asin` or `asin1`.")
        elif not has_quantity:
            st.error("Missing required column: `quantity`.")
        else:
            df['asin_final'] = df['asin'] if has_asin else df['asin1']
            df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)

            # Inventory status
            df['inventory_status'] = df['quantity'].apply(
                lambda x: 'Out of Stock' if x == 0 else ('Low Inventory' if x < 10 else 'In Stock')
            )

            # ------------------ TABS ------------------
            tab1, tab2, tab3 = st.tabs(["📈 Overview", "🔍 Filter & Export", "🧾 Raw Data"])

            # -------- TAB 1: OVERVIEW --------
            with tab1:
                st.subheader("🧠 Inventory Summary")

                out_of_stock = df[df['quantity'] == 0]
                low_stock = df[df['quantity'] < 10]

                col1, col2, col3 = st.columns(3)
                col1.metric("Total ASINs", df['asin_final'].nunique())
                col2.metric("Out of Stock", out_of_stock.shape[0])
                col3.metric("Low Inventory", low_stock.shape[0])

                st.markdown("#### 🔝 Top 10 ASINs by Quantity")
                top_asins = df.groupby('asin_final')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
                st.bar_chart(top_asins.set_index('asin_final'))

                if 'fulfillment-channel' in df.columns:
                    st.markdown("#### 🚚 Inventory by Fulfillment Channel")
                    channel_summary = df.groupby(['fulfillment-channel', 'inventory_status']).size().unstack(fill_value=0)
                    st.table(channel_summary)

            # -------- TAB 2: FILTER & EXPORT --------
            with tab2:
                st.subheader("🔍 Inventory Filters")

                col1, col2 = st.columns(2)
                status_filter = col1.multiselect("Filter by Inventory Status", df['inventory_status'].unique(), default=df['inventory_status'].unique())

                if 'fulfillment-channel' in df.columns:
                    channel_filter = col2.multiselect("Filter by Fulfillment Channel", df['fulfillment-channel'].unique(), default=df['fulfillment-channel'].unique())
                else:
                    channel_filter = None

                filtered = df[df['inventory_status'].isin(status_filter)]
                if channel_filter:
                    filtered = filtered[filtered['fulfillment-channel'].isin(channel_filter)]

                st.dataframe(filtered, use_container_width=True)

                csv = filtered.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download Filtered Report", csv, "Filtered_Inventory_Report.csv", "text/csv")

            # -------- TAB 3: RAW DATA --------
            with tab3:
                st.subheader("🧾 Full Uploaded Report")
                st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Error: {e}")
else:
    st.info("📂 Please upload your report to begin.")

# ------------------ FOOTER ------------------
with st.expander("ℹ️ Help"):
    st.markdown("""
    - Upload `.csv`, `.txt`, `.tsv`, `.xls`, or `.xlsx` files.
    - Required columns: `asin` or `asin1`, and `quantity`.
    - Inventory status:
        - ✅ **In Stock**: 10+
        - ⚠️ **Low Inventory**: 1–9
        - ❌ **Out of Stock**: 0
    """)

st.markdown("---")
st.markdown("Please provide feedback here nikitajain0220@gmail.com")
