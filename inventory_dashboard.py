import streamlit as st
import pandas as pd
import os

# ------------------ PAGE CONFIGURATION ------------------
st.set_page_config(page_title="Amazon Inventory Dashboard", layout="wide")
st.markdown("## 📦 Amazon Inventory Dashboard")
st.markdown("Upload your **Active Inventory Report** in any format: `.csv`, `.txt`, `.xls`, `.xlsx`, or `.tsv`.")

# ------------------ FILE UPLOADER ------------------
uploaded_file = st.file_uploader("Upload Inventory Report", type=None)  # Allow all file types

# ------------------ FILE LOADER FUNCTION ------------------
def load_file(uploaded_file):
    filename = uploaded_file.name.lower()
    ext = os.path.splitext(filename)[1]

    if ext == '.csv':
        return pd.read_csv(uploaded_file)
    elif ext == '.tsv':
        return pd.read_csv(uploaded_file, delimiter='\t')
    elif ext in ['.xls', '.xlsx']:
        return pd.read_excel(uploaded_file)
    elif ext == '.txt':
        content = uploaded_file.getvalue().decode('utf-8', errors='ignore')
        delimiter = '\t' if '\t' in content else ','
        uploaded_file.seek(0)  # Reset pointer after reading
        return pd.read_csv(uploaded_file, delimiter=delimiter)
    else:
        raise ValueError("Unsupported file format. Please upload .csv, .txt, .tsv, .xls, or .xlsx")

# ------------------ REQUIRED FIELDS ------------------
required_columns = ['asin', 'quantity']

# ------------------ FILE PROCESSING ------------------
if uploaded_file:
    try:
        df = load_file(uploaded_file)
        df.columns = df.columns.str.lower().str.strip()  # Normalize column names

        st.success("✅ File uploaded successfully!")
        st.markdown("### 🔍 File Preview")
        st.dataframe(df.head())

        # ------------------ VALIDATE COLUMNS ------------------
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            st.error(f"🚫 Missing required columns: {', '.join(missing)}")
        else:
            st.success("✅ All required columns are present.")

            # ------------------ METRICS ------------------
            st.markdown("### 📊 Inventory Summary")
            col1, col2 = st.columns(2)
            col1.metric("Total Unique ASINs", df['asin'].nunique())
            col2.metric("Total Quantity", int(df['quantity'].sum()))

            # ------------------ CHART ------------------
            st.markdown("### 📈 Top 10 ASINs by Quantity")
            top_asins = df.groupby('asin')['quantity'].sum().sort_values(ascending=False).head(10).reset_index()
            st.bar_chart(top_asins.set_index('asin'))

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("📂 Please upload a valid inventory file to get started.")

# ------------------ FAQ / HELP SECTION ------------------
with st.expander("❓ Why is my file not uploading or showing data?"):
    st.markdown("""
    - ✅ You can upload `.csv`, `.txt`, `.tsv`, `.xls`, or `.xlsx` files.
    - 🔑 Required columns: `asin` and `quantity` (case-insensitive).
    - 🧾 Tab-delimited `.txt` files from Amazon are supported.
    - ⚠️ Avoid uploading empty or corrupted files.
    - 📤 Use the 'Active Listings Report' from Amazon Seller Central for best results.
    """)

# ------------------ FOOTER ------------------
st.markdown("---") 
