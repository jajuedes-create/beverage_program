{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww13260\viewh10000\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 %%writefile bev_app.py\
import streamlit as st\
import pandas as pd\
import numpy as np\
from datetime import datetime, timedelta\
import plotly.express as px\
import plotly.graph_objects as go\
import json\
from typing import Dict, List, Optional\
import time\
import re\
\
# ============================================\
# CSV UPLOAD FUNCTIONS WITH EXCEL FORMULAS\
# ============================================\
\
def clean_currency_column(series):\
    """Clean currency columns by removing $ and , symbols"""\
    if series.dtype == 'object':\
        # Remove dollar signs, commas, and any whitespace\
        series = series.astype(str).str.replace('$', '', regex=False)\
        series = series.str.replace(',', '', regex=False)\
        series = series.str.strip()\
        # Replace empty strings with 0\
        series = series.replace('', '0')\
    return pd.to_numeric(series, errors='coerce').fillna(0)\
\
def process_uploaded_csv(uploaded_file, category):\
    """Process uploaded CSV file for a specific inventory category"""\
    try:\
        # Read CSV\
        df = pd.read_csv(uploaded_file)\
        \
        # Clean column names\
        df.columns = df.columns.str.strip()\
        \
        # Process based on category\
        if category == 'spirits':\
            # Map columns for spirits (matching Excel structure)\
            column_mapping = \{\
                'Product': 'Product',\
                'Type': 'Type', \
                'Cost': 'Cost',\
                'Size (oz.)': 'Size (oz)',\
                'Cost/Oz': 'Cost/Oz',\
                'Margin': 'Margin',\
                'Neat Price': 'Neat Price',\
                'Inventory': 'Inventory',\
                'Value': 'Value',\
                'Use': 'Use',\
                'Distributor': 'Distributor',\
                'Order Notes': 'Order Notes'\
            \}\
            \
            # Rename columns that exist\
            df = df.rename(columns=\{k: v for k, v in column_mapping.items() if k in df.columns\})\
            \
            # Clean and convert numeric columns\
            if 'Cost' in df.columns:\
                df['Cost'] = clean_currency_column(df['Cost'])\
            if 'Size (oz)' in df.columns:\
                df['Size (oz)'] = pd.to_numeric(df['Size (oz)'], errors='coerce').fillna(33.8)\
            if 'Margin' in df.columns:\
                # remove percent sign\
                df['Margin'] = df['Margin'].str.replace('%', '')\
                df['Margin'] = (pd.to(df['Margin'], errors='coerce')/100).fillna(0.20)\
            if 'Neat Price' in df.columns:\
                df['Neat Price'] = clean_currency_column(df['Neat Price'])\
            if 'Inventory' in df.columns:\
                df['Inventory'] = pd.to_numeric(df['Inventory'], errors='coerce').fillna(0)\
            \
            # Calculate Cost/Oz (Excel formula: Cost / Size)\
            if 'Cost' in df.columns and 'Size (oz)' in df.columns:\
                df['Cost/Oz'] = df.apply(lambda row: row['Cost'] / row['Size (oz)'] if row['Size (oz)'] > 0 else 0, axis=1)\
            \
            # Calculate Value (Excel formula: Inventory * Cost)\
            if 'Inventory' in df.columns and 'Cost' in df.columns:\
                df['Value'] = df['Inventory'] * df['Cost']\
            \
            # Calculate suggested Neat Price if not present (based on margin)\
            if 'Neat Price' not in df.columns and 'Cost/Oz' in df.columns and 'Margin' in df.columns:\
                # Formula: Cost/Oz * 2 / (1 - Margin)  [for 2 oz pour]\
                df['Neat Price'] = df.apply(lambda row: (row['Cost/Oz'] * 2) / (1 - row['Margin']) if row['Margin'] < 1 else 0, axis=1)\
                df['Neat Price'] = df['Neat Price'].round(0)  # Round to nearest dollar\
            \
            # Remove Par column if it exists\
            if 'Par' in df.columns:\
                df = df.drop('Par', axis=1)\
        \
        elif category == 'wine':\
            column_mapping = \{\
                'Product': 'Product',\
                'Type': 'Type',\
                'Cost': 'Cost',\
                'Size (oz.)': 'Size (oz)',\
                'Margin': 'Margin',\
                'Bottle Price': 'Bottle Price',\
                'Inventory': 'Inventory',\
                'Value': 'Value',\
                'Distributor': 'Distributor',\
                'BTG': 'BTG'\
            \}\
            \
            df = df.rename(columns=\{k: v for k, v in column_mapping.items() if k in df.columns\})\
            \
            # Clean numeric columns\
            if 'Cost' in df.columns:\
                df['Cost'] = clean_currency_column(df['Cost'])\
            if 'Size (oz)' in df.columns:\
                df['Size (oz)'] = pd.to_numeric(df['Size (oz)'], errors='coerce').fillna(25.3)  # Standard wine bottle\
            if 'Margin' in df.columns:\
                df['Margin'] = pd.to_numeric(df['Margin'], errors='coerce').fillna(0.33)\
            if 'Bottle Price' in df.columns:\
                df['Bottle Price'] = clean_currency_column(df['Bottle Price'])\
            if 'Inventory' in df.columns:\
                df['Inventory'] = pd.to_numeric(df['Inventory'], errors='coerce').fillna(0)\
            \
            # Calculate Bottle Price if not present (based on margin)\
            if 'Bottle Price' not in df.columns and 'Cost' in df.columns and 'Margin' in df.columns:\
                df['Bottle Price'] = df.apply(lambda row: row['Cost'] / (1 - row['Margin']) if row['Margin'] < 1 else 0, axis=1)\
                df['Bottle Price'] = df['Bottle Price'].round(0)\
            \
            # Calculate BTG Price if BTG column indicates wine is sold by glass\
            if 'BTG' in df.columns:\
                # BTG Price = Bottle Price / 4 (assuming 4 glasses per bottle)\
                df['BTG Price'] = df.apply(lambda row: row['Bottle Price'] / 4 if row.get('BTG') == 'Yes' else 0, axis=1)\
                df['BTG Price'] = df['BTG Price'].round(0)\
            \
            # Calculate Value\
            if 'Inventory' in df.columns and 'Cost' in df.columns:\
                df['Value'] = df['Inventory'] * df['Cost']\
            \
            # Remove Par column\
            if 'Par' in df.columns:\
                df = df.drop('Par', axis=1)\
        \
        elif category == 'beer':\
            column_mapping = \{\
                'Product': 'Product',\
                'Type': 'Type',\
                'Cost per Keg/Case': 'Cost per Keg/Case',\
                'Size': 'Size',\
                'UoM': 'UoM',\
                'Cost/Unit': 'Cost/Unit',\
                'Margin': 'Margin',\
                'Menu Price': 'Menu Price',\
                'Inventory': 'Inventory',\
                'Value': 'Value',\
                'Distributor': 'Distributor',\
                'Order Notes': 'Order Notes'\
            \}\
            \
            df = df.rename(columns=\{k: v for k, v in column_mapping.items() if k in df.columns\})\
            \
            # Clean numeric columns\
            if 'Cost per Keg/Case' in df.columns:\
                df['Cost per Keg/Case'] = clean_currency_column(df['Cost per Keg/Case'])\
            if 'Size' in df.columns:\
                df['Size'] = pd.to_numeric(df['Size'], errors='coerce').fillna(1)\
            if 'Margin' in df.columns:\
                df['Margin'] = pd.to_numeric(df['Margin'], errors='coerce').fillna(0.25)\
            if 'Menu Price' in df.columns:\
                df['Menu Price'] = clean_currency_column(df['Menu Price'])\
            if 'Inventory' in df.columns:\
                df['Inventory'] = pd.to_numeric(df['Inventory'], errors='coerce').fillna(0)\
            \
            # Calculate Cost/Unit (Excel formula: Cost per Keg/Case / Size)\
            if 'Cost per Keg/Case' in df.columns and 'Size' in df.columns:\
                df['Cost/Unit'] = df.apply(lambda row: row['Cost per Keg/Case'] / row['Size'] if row['Size'] > 0 else 0, axis=1)\
            \
            # Calculate Menu Price if not present\
            if 'Menu Price' not in df.columns and 'Cost/Unit' in df.columns and 'Margin' in df.columns:\
                df['Menu Price'] = df.apply(lambda row: row['Cost/Unit'] / (1 - row['Margin']) if row['Margin'] < 1 else 0, axis=1)\
                df['Menu Price'] = df['Menu Price'].round(2)\
            \
            # Calculate Value (Inventory * Cost per Keg/Case)\
            if 'Inventory' in df.columns and 'Cost per Keg/Case' in df.columns:\
                df['Value'] = df['Inventory'] * df['Cost per Keg/Case']\
            \
            # Remove Par column\
            if 'Par' in df.columns:\
                df = df.drop('Par', axis=1)\
        \
        elif category == 'ingredients':\
            column_mapping = \{\
                'Product': 'Product',\
                'Cost': 'Cost',\
                'Size/Yield': 'Size/Yield',\
                'UoM': 'UoM',\
                'Cost/Unit': 'Cost/Unit',\
                'Inventory': 'Inventory',\
                'Distributor': 'Distributor',\
                'Order Notes': 'Order Notes'\
            \}\
            \
            df = df.rename(columns=\{k: v for k, v in column_mapping.items() if k in df.columns\})\
            \
            # Clean numeric columns\
            if 'Cost' in df.columns:\
                df['Cost'] = clean_currency_column(df['Cost'])\
            if 'Size/Yield' in df.columns:\
                df['Size/Yield'] = pd.to_numeric(df['Size/Yield'], errors='coerce').fillna(1)\
            if 'Cost/Unit' in df.columns:\
                df['Cost/Unit'] = clean_currency_column(df['Cost/Unit'])\
            \
            # Add Inventory if not present\
            if 'Inventory' not in df.columns:\
                df['Inventory'] = 0\
            else:\
                df['Inventory'] = pd.to_numeric(df['Inventory'], errors='coerce').fillna(0)\
            \
            # Calculate Cost/Unit (Excel formula: Cost / Size/Yield)\
            if 'Cost' in df.columns and 'Size/Yield' in df.columns:\
                df['Cost/Unit'] = df.apply(lambda row: row['Cost'] / row['Size/Yield'] if row['Size/Yield'] > 0 else 0, axis=1)\
            \
            # Calculate Value (Inventory * Cost)\
            df['Value'] = df['Inventory'] * df['Cost']\
            \
            # Remove Par column\
            if 'Par' in df.columns:\
                df = df.drop('Par', axis=1)\
        \
        return df\
        \
    except Exception as e:\
        st.error(f"Error processing \{category\} CSV: \{str(e)\}")\
        st.error(f"Please check that your CSV file has the correct format and column names")\
        return None\
\
def show_csv_upload_section():\
    """Display CSV upload interface"""\
    with st.expander("\uc0\u55357 \u56548  Upload Inventory CSV Files", expanded=True):\
        st.info("""\
        ### Upload your inventory data as CSV files\
        Export each tab from your Google Sheet as CSV and upload here.\
        \
        **Note:** Make sure your CSV files include these columns:\
        - **Spirits**: Product, Type, Cost, Size (oz.), Inventory, Distributor\
        - **Wine**: Product, Type, Cost, Inventory, Distributor\
        - **Beer**: Product, Type, Cost per Keg/Case, Size, UoM, Inventory\
        - **Ingredients**: Product, Cost, Size/Yield, UoM, Distributor\
        """)\
        \
        col1, col2 = st.columns(2)\
        \
        with col1:\
            spirits_file = st.file_uploader(\
                "\uc0\u55358 \u56643  Spirits Inventory CSV",\
                type=['csv'],\
                key="spirits_csv"\
            )\
            \
            wine_file = st.file_uploader(\
                "\uc0\u55356 \u57207  Wine Inventory CSV",\
                type=['csv'],\
                key="wine_csv"\
            )\
        \
        with col2:\
            beer_file = st.file_uploader(\
                "\uc0\u55356 \u57210  Beer Inventory CSV",\
                type=['csv'],\
                key="beer_csv"\
            )\
            \
            ingredients_file = st.file_uploader(\
                "\uc0\u55356 \u57163  Ingredients Inventory CSV",\
                type=['csv'],\
                key="ingredients_csv"\
            )\
        \
        # Process uploaded files\
        if st.button("\uc0\u55357 \u56549  Load All Uploaded Files", type="primary", use_container_width=True):\
            success_count = 0\
            \
            if spirits_file:\
                df = process_uploaded_csv(spirits_file, 'spirits')\
                if df is not None:\
                    st.session_state.inventory_data['spirits'] = df\
                    success_count += 1\
                    st.success(f"\uc0\u9989  Loaded \{len(df)\} spirits")\
            \
            if wine_file:\
                df = process_uploaded_csv(wine_file, 'wine')\
                if df is not None:\
                    st.session_state.inventory_data['wine'] = df\
                    success_count += 1\
                    st.success(f"\uc0\u9989  Loaded \{len(df)\} wines")\
            \
            if beer_file:\
                df = process_uploaded_csv(beer_file, 'beer')\
                if df is not None:\
                    st.session_state.inventory_data['beer'] = df\
                    success_count += 1\
                    st.success(f"\uc0\u9989  Loaded \{len(df)\} beers")\
            \
            if ingredients_file:\
                df = process_uploaded_csv(ingredients_file, 'ingredients')\
                if df is not None:\
                    st.session_state.inventory_data['ingredients'] = df\
                    success_count += 1\
                    st.success(f"\uc0\u9989  Loaded \{len(df)\} ingredients")\
            \
            if success_count > 0:\
                st.balloons()\
                time.sleep(2)\
                st.rerun()\
            else:\
                st.warning("No files were uploaded. Please select CSV files to import.")\
\
def export_to_csv(category):\
    """Export inventory category to CSV"""\
    df = st.session_state.inventory_data[category]\
    if not df.empty:\
        csv = df.to_csv(index=False)\
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")\
        filename = f"\{category\}_inventory_\{timestamp\}.csv"\
        \
        st.download_button(\
            label=f"\uc0\u55357 \u56549  Download \{category.title()\} CSV",\
            data=csv,\
            file_name=filename,\
            mime="text/csv",\
            use_container_width=True\
        )\
\
# ============================================\
# CALCULATION FUNCTIONS (Excel Formulas)\
# ============================================\
\
def recalculate_spirits_values(df):\
    """Recalculate all values for spirits using Excel formulas"""\
    if df.empty:\
        return df\
    \
    # Cost/Oz = Cost / Size (oz)\
    if 'Cost' in df.columns and 'Size (oz)' in df.columns:\
        df['Cost/Oz'] = df.apply(lambda row: row['Cost'] / row['Size (oz)'] if row['Size (oz)'] > 0 else 0, axis=1)\
        df['Cost/Oz'] = df['Cost/Oz'].round(4)\
    \
    # Value = Inventory * Cost\
    if 'Inventory' in df.columns and 'Cost' in df.columns:\
        df['Value'] = df['Inventory'] * df['Cost']\
        df['Value'] = df['Value'].round(2)\
    \
    # Suggested Neat Price based on margin (2 oz pour)\
    if 'Cost/Oz' in df.columns and 'Margin' in df.columns:\
        df['Suggested Price'] = df.apply(\
            lambda row: (row['Cost/Oz'] * 2) / (1 - row['Margin']) if row['Margin'] < 1 else 0, \
            axis=1\
        ).round(0)\
    \
    return df\
\
def recalculate_wine_values(df):\
    """Recalculate all values for wine using Excel formulas"""\
    if df.empty:\
        return df\
    \
    # Value = Inventory * Cost\
    if 'Inventory' in df.columns and 'Cost' in df.columns:\
        df['Value'] = df['Inventory'] * df['Cost']\
        df['Value'] = df['Value'].round(2)\
    \
    # Suggested Bottle Price based on margin\
    if 'Cost' in df.columns and 'Margin' in df.columns:\
        df['Suggested Price'] = df.apply(\
            lambda row: row['Cost'] / (1 - row['Margin']) if row['Margin'] < 1 else 0,\
            axis=1\
        ).round(0)\
    \
    # BTG Price (if applicable)\
    if 'BTG' in df.columns and 'Bottle Price' in df.columns:\
        df['BTG Price'] = df.apply(\
            lambda row: (row['Bottle Price'] / 4).round(0) if row.get('BTG') == 'Yes' else None,\
            axis=1\
        )\
    \
    return df\
\
def recalculate_beer_values(df):\
    """Recalculate all values for beer using Excel formulas"""\
    if df.empty:\
        return df\
    \
    # Cost/Unit = Cost per Keg/Case / Size\
    if 'Cost per Keg/Case' in df.columns and 'Size' in df.columns:\
        df['Cost/Unit'] = df.apply(\
            lambda row: row['Cost per Keg/Case'] / row['Size'] if row['Size'] > 0 else 0,\
            axis=1\
        ).round(4)\
    \
    # Value = Inventory * Cost per Keg/Case\
    if 'Inventory' in df.columns and 'Cost per Keg/Case' in df.columns:\
        df['Value'] = df['Inventory'] * df['Cost per Keg/Case']\
        df['Value'] = df['Value'].round(2)\
    \
    # Suggested Menu Price based on margin\
    if 'Cost/Unit' in df.columns and 'Margin' in df.columns:\
        df['Suggested Price'] = df.apply(\
            lambda row: row['Cost/Unit'] / (1 - row['Margin']) if row['Margin'] < 1 else 0,\
            axis=1\
        ).round(2)\
    \
    return df\
\
def recalculate_ingredients_values(df):\
    """Recalculate all values for ingredients using Excel formulas"""\
    if df.empty:\
        return df\
    \
    # Cost/Unit = Cost / Size/Yield\
    if 'Cost' in df.columns and 'Size/Yield' in df.columns:\
        df['Cost/Unit'] = df.apply(\
            lambda row: row['Cost'] / row['Size/Yield'] if row['Size/Yield'] > 0 else 0,\
            axis=1\
        ).round(4)\
    \
    # Value = Inventory * Cost\
    if 'Inventory' in df.columns and 'Cost' in df.columns:\
        df['Value'] = df['Inventory'] * df['Cost']\
        df['Value'] = df['Value'].round(2)\
    \
    return df\
\
# ============================================\
# PAGE CONFIGURATION\
# ============================================\
st.set_page_config(\
    page_title="Canter Inn Beverage Manager",\
    page_icon="\uc0\u55356 \u57208 ",\
    layout="wide",\
    initial_sidebar_state="expanded"\
)\
\
# ============================================\
# CUSTOM CSS\
# ============================================\
st.markdown("""\
<style>\
    .main-header \{\
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);\
        color: white;\
        padding: 30px;\
        border-radius: 10px;\
        margin-bottom: 30px;\
        text-align: center;\
    \}\
    .stMetric \{\
        background-color: #f8f9fa;\
        padding: 15px;\
        border-radius: 10px;\
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);\
    \}\
    .inventory-header \{\
        background: #f8f9fa;\
        padding: 15px;\
        border-radius: 10px;\
        margin-bottom: 20px;\
    \}\
</style>\
""", unsafe_allow_html=True)\
\
# ============================================\
# SESSION STATE INITIALIZATION\
# ============================================\
if 'inventory_data' not in st.session_state:\
    st.session_state.inventory_data = \{\
        'spirits': pd.DataFrame(),\
        'wine': pd.DataFrame(),\
        'beer': pd.DataFrame(),\
        'ingredients': pd.DataFrame()\
    \}\
\
if 'orders_history' not in st.session_state:\
    st.session_state.orders_history = []\
\
if 'show_csv_upload' not in st.session_state:\
    st.session_state.show_csv_upload = False\
\
if 'show_csv_export' not in st.session_state:\
    st.session_state.show_csv_export = False\
\
# ============================================\
# DATA STRUCTURE FUNCTIONS (NO PAR COLUMNS)\
# ============================================\
def create_empty_spirits_inventory():\
    return pd.DataFrame(\{\
        'Product': pd.Series(dtype='str'),\
        'Type': pd.Series(dtype='str'),\
        'Cost': pd.Series(dtype='float64'),\
        'Size (oz)': pd.Series(dtype='float64'),\
        'Cost/Oz': pd.Series(dtype='float64'),\
        'Margin': pd.Series(dtype='float64'),\
        'Neat Price': pd.Series(dtype='float64'),\
        'Inventory': pd.Series(dtype='float64'),\
        'Value': pd.Series(dtype='float64'),\
        'Use': pd.Series(dtype='str'),\
        'Distributor': pd.Series(dtype='str'),\
        'Order Notes': pd.Series(dtype='str')\
    \})\
\
def create_empty_wine_inventory():\
    return pd.DataFrame(\{\
        'Product': pd.Series(dtype='str'),\
        'Type': pd.Series(dtype='str'),\
        'Cost': pd.Series(dtype='float64'),\
        'Size (oz)': pd.Series(dtype='float64'),\
        'Margin': pd.Series(dtype='float64'),\
        'Bottle Price': pd.Series(dtype='float64'),\
        'Inventory': pd.Series(dtype='float64'),\
        'Value': pd.Series(dtype='float64'),\
        'Distributor': pd.Series(dtype='str'),\
        'BTG': pd.Series(dtype='str'),\
        'BTG Price': pd.Series(dtype='float64')\
    \})\
\
def create_empty_beer_inventory():\
    return pd.DataFrame(\{\
        'Product': pd.Series(dtype='str'),\
        'Type': pd.Series(dtype='str'),\
        'Cost per Keg/Case': pd.Series(dtype='float64'),\
        'Size': pd.Series(dtype='float64'),\
        'UoM': pd.Series(dtype='str'),\
        'Cost/Unit': pd.Series(dtype='float64'),\
        'Margin': pd.Series(dtype='float64'),\
        'Menu Price': pd.Series(dtype='float64'),\
        'Inventory': pd.Series(dtype='float64'),\
        'Value': pd.Series(dtype='float64'),\
        'Distributor': pd.Series(dtype='str'),\
        'Order Notes': pd.Series(dtype='str')\
    \})\
\
def create_empty_ingredients_inventory():\
    return pd.DataFrame(\{\
        'Product': pd.Series(dtype='str'),\
        'Cost': pd.Series(dtype='float64'),\
        'Size/Yield': pd.Series(dtype='float64'),\
        'UoM': pd.Series(dtype='str'),\
        'Cost/Unit': pd.Series(dtype='float64'),\
        'Inventory': pd.Series(dtype='float64'),\
        'Value': pd.Series(dtype='float64'),\
        'Distributor': pd.Series(dtype='str'),\
        'Order Notes': pd.Series(dtype='str')\
    \})\
\
def calculate_total_inventory_value():\
    """Calculate total inventory value across all categories"""\
    total = 0\
    for category, df in st.session_state.inventory_data.items():\
        if not df.empty and 'Value' in df.columns:\
            total += df['Value'].sum()\
    return total\
\
# ============================================\
# SIDEBAR\
# ============================================\
with st.sidebar:\
    st.title("\uc0\u55356 \u57208  Canter Inn")\
    st.divider()\
    \
    module = st.selectbox(\
        "Navigate to:",\
        ["\uc0\u55356 \u57312  Dashboard", "\u55357 \u56522  Inventory", "\u55357 \u56550  Weekly Ordering", "\u55356 \u57209  Recipe Book", "\u9881 \u65039  Settings"]\
    )\
    \
    st.divider()\
    \
    # Quick Stats\
    total_skus = sum(len(df) for df in st.session_state.inventory_data.values())\
    total_value = calculate_total_inventory_value()\
    \
    col1, col2 = st.columns(2)\
    with col1:\
        st.metric("Total SKUs", total_skus)\
    with col2:\
        st.metric("Total Value", f"$\{total_value:,.0f\}")\
    \
    st.divider()\
    st.caption(f"Last update: \{datetime.now().strftime('%H:%M:%S')\}")\
\
# ============================================\
# MAIN CONTENT\
# ============================================\
if module == "\uc0\u55356 \u57312  Dashboard":\
    # Dashboard Header\
    st.markdown("""\
        <div class="main-header">\
            <h1>\uc0\u55356 \u57208  Canter Inn Beverage Management System</h1>\
            <p>Complete inventory, ordering, and recipe management solution</p>\
        </div>\
    """, unsafe_allow_html=True)\
    \
    # Metrics\
    col1, col2, col3, col4 = st.columns(4)\
    with col1:\
        total_value = calculate_total_inventory_value()\
        st.metric("Total Inventory Value", f"$\{total_value:,.2f\}")\
    with col2:\
        total_items = sum(len(df) for df in st.session_state.inventory_data.values())\
        st.metric("Total Products", total_items)\
    with col3:\
        out_of_stock = sum(\
            len(df[df['Inventory'] == 0]) \
            for df in st.session_state.inventory_data.values() \
            if not df.empty and 'Inventory' in df.columns\
        )\
        st.metric("Out of Stock", out_of_stock)\
    with col4:\
        st.metric("Active Recipes", "0")\
    \
    st.divider()\
    \
    # Quick Actions and Status\
    col1, col2 = st.columns([2, 1])\
    with col1:\
        st.subheader("\uc0\u55357 \u56520  Inventory Status")\
        if sum(len(df) for df in st.session_state.inventory_data.values()) > 0:\
            # Create inventory breakdown\
            categories = []\
            values = []\
            for category, df in st.session_state.inventory_data.items():\
                if not df.empty and 'Value' in df.columns:\
                    categories.append(category.title())\
                    values.append(df['Value'].sum())\
            \
            if categories:\
                fig = px.pie(\
                    values=values,\
                    names=categories,\
                    title='Inventory Value Distribution',\
                    color_discrete_sequence=['#3498db', '#9b59b6', '#f39c12', '#27ae60']\
                )\
                st.plotly_chart(fig, use_container_width=True)\
            else:\
                st.info("No inventory data with values available.")\
        else:\
            st.info("No inventory data available. Import CSV files to get started.")\
            if st.button("Import Data Now", type="primary"):\
                module = "\uc0\u55357 \u56522  Inventory"\
                st.session_state.show_csv_upload = True\
    \
    with col2:\
        st.subheader("\uc0\u9889  Quick Actions")\
        if st.button("\uc0\u55357 \u56541  Update Inventory", use_container_width=True):\
            st.info("Navigate to Inventory module")\
        if st.button("\uc0\u55357 \u56550  Create Order", use_container_width=True):\
            st.info("Navigate to Weekly Ordering")\
        if st.button("\uc0\u55356 \u57209  Add Recipe", use_container_width=True):\
            st.info("Navigate to Recipe Book")\
        if st.button("\uc0\u55357 \u56522  Reports", use_container_width=True):\
            st.info("Reports feature coming soon")\
        if st.button("\uc0\u55357 \u56548  Import CSVs", use_container_width=True):\
            st.session_state.show_csv_upload = True\
\
elif module == "\uc0\u55357 \u56522  Inventory":\
    st.title("\uc0\u55357 \u56522  Inventory Management")\
    \
    # Initialize empty dataframes if needed\
    if not st.session_state.inventory_data['spirits'].shape[0]:\
        st.session_state.inventory_data = \{\
            'spirits': create_empty_spirits_inventory(),\
            'wine': create_empty_wine_inventory(),\
            'beer': create_empty_beer_inventory(),\
            'ingredients': create_empty_ingredients_inventory()\
        \}\
    \
    # Category metrics\
    col1, col2, col3, col4 = st.columns(4)\
    with col1:\
        spirits_value = st.session_state.inventory_data['spirits']['Value'].sum() if not st.session_state.inventory_data['spirits'].empty else 0\
        st.metric("Spirits", f"$\{spirits_value:,.2f\}")\
    with col2:\
        wine_value = st.session_state.inventory_data['wine']['Value'].sum() if not st.session_state.inventory_data['wine'].empty else 0\
        st.metric("Wine", f"$\{wine_value:,.2f\}")\
    with col3:\
        beer_value = st.session_state.inventory_data['beer']['Value'].sum() if not st.session_state.inventory_data['beer'].empty else 0\
        st.metric("Beer", f"$\{beer_value:,.2f\}")\
    with col4:\
        ingredients_value = st.session_state.inventory_data['ingredients']['Value'].sum() if not st.session_state.inventory_data['ingredients'].empty else 0\
        st.metric("Ingredients", f"$\{ingredients_value:,.2f\}")\
    \
    st.divider()\
    \
    # Import/Export buttons\
    col1, col2 = st.columns(2)\
    with col1:\
        if st.button("\uc0\u55357 \u56548  Import from CSV Files", type="primary", use_container_width=True):\
            st.session_state.show_csv_upload = True\
    \
    with col2:\
        if st.button("\uc0\u55357 \u56510  Export All to CSV", use_container_width=True):\
            st.session_state.show_csv_export = True\
    \
    # Show CSV upload section if requested\
    if st.session_state.show_csv_upload:\
        show_csv_upload_section()\
    \
    # Show export section if requested\
    if st.session_state.show_csv_export:\
        with st.expander("\uc0\u55357 \u56549  Export Inventory to CSV", expanded=True):\
            col1, col2 = st.columns(2)\
            with col1:\
                export_to_csv('spirits')\
                export_to_csv('wine')\
            with col2:\
                export_to_csv('beer')\
                export_to_csv('ingredients')\
    \
    st.divider()\
    \
    # Inventory tabs\
    tab1, tab2, tab3, tab4 = st.tabs(["\uc0\u55358 \u56643  Spirits", "\u55356 \u57207  Wine", "\u55356 \u57210  Beer", "\u55356 \u57163  Ingredients"])\
    \
    with tab1:\
        st.subheader("Spirits Inventory")\
        \
        if st.session_state.inventory_data['spirits'].empty:\
            st.info("No spirits data. Import from CSV or add manually.")\
        else:\
            # Display summary metrics\
            col1, col2, col3, col4 = st.columns(4)\
            with col1:\
                st.metric("Total Products", len(st.session_state.inventory_data['spirits']))\
            with col2:\
                total_bottles = st.session_state.inventory_data['spirits']['Inventory'].sum()\
                st.metric("Total Bottles", f"\{total_bottles:.1f\}")\
            with col3:\
                out_of_stock = len(st.session_state.inventory_data['spirits'][\
                    st.session_state.inventory_data['spirits']['Inventory'] == 0\
                ])\
                st.metric("Out of Stock", out_of_stock)\
            with col4:\
                avg_cost_oz = st.session_state.inventory_data['spirits']['Cost/Oz'].mean()\
                st.metric("Avg $/Oz", f"$\{avg_cost_oz:.2f\}")\
            \
            # Editable dataframe with Excel-like formulas\
            edited_df = st.data_editor(\
                st.session_state.inventory_data['spirits'],\
                use_container_width=True,\
                num_rows="dynamic",\
                column_config=\{\
                    "Product": st.column_config.TextColumn("Product", width="medium"),\
                    "Type": st.column_config.SelectboxColumn(\
                        "Type",\
                        options=["Vodka", "Gin", "Whiskey", "Bourbon", "Rum", "Tequila", "Scotch", "Brandy", "Cordial & Digestif", "Bitters", "Vermouth", "N/A"],\
                        width="small"\
                    ),\
                    "Cost": st.column_config.NumberColumn("Cost ($)", format="$%.2f", width="small"),\
                    "Size (oz)": st.column_config.NumberColumn("Size (oz)", format="%.1f", width="small"),\
                    "Cost/Oz": st.column_config.NumberColumn("$/Oz", format="$%.4f", disabled=True, width="small"),\
                    "Margin": st.column_config.NumberColumn("Margin", format="%.1%%", width="small"),\
                    "Neat Price": st.column_config.NumberColumn("Neat Price", format="$%.0f", width="small"),\
                    "Inventory": st.column_config.NumberColumn("Inventory", min_value=0, step=0.5, width="small"),\
                    "Value": st.column_config.NumberColumn("Value", format="$%.2f", disabled=True, width="small"),\
                    "Use": st.column_config.SelectboxColumn("Use", options=["Well", "Call", "Premium", "Top Shelf"], width="small"),\
                    "Distributor": st.column_config.TextColumn("Distributor", width="small"),\
                    "Order Notes": st.column_config.TextColumn("Notes", width="medium")\
                \}\
            )\
            \
            if st.button("\uc0\u55357 \u56510  Save & Recalculate", key="save_spirits", type="primary"):\
                # Recalculate all values using Excel formulas\
                edited_df = recalculate_spirits_values(edited_df)\
                st.session_state.inventory_data['spirits'] = edited_df\
                st.success("\uc0\u9989  Spirits inventory saved and values recalculated!")\
                st.rerun()\
    \
    with tab2:\
        st.subheader("Wine Inventory")\
        \
        if st.session_state.inventory_data['wine'].empty:\
            st.info("No wine data. Import from CSV or add manually.")\
        else:\
            # Display metrics\
            col1, col2, col3, col4 = st.columns(4)\
            with col1:\
                st.metric("Total Wines", len(st.session_state.inventory_data['wine']))\
            with col2:\
                total_bottles = st.session_state.inventory_data['wine']['Inventory'].sum()\
                st.metric("Total Bottles", f"\{total_bottles:.0f\}")\
            with col3:\
                btg_count = len(st.session_state.inventory_data['wine'][\
                    st.session_state.inventory_data['wine'].get('BTG', '') == 'Yes'\
                ]) if 'BTG' in st.session_state.inventory_data['wine'].columns else 0\
                st.metric("BTG Wines", btg_count)\
            with col4:\
                avg_bottle_price = st.session_state.inventory_data['wine']['Bottle Price'].mean() if 'Bottle Price' in st.session_state.inventory_data['wine'].columns else 0\
                st.metric("Avg Bottle Price", f"$\{avg_bottle_price:.0f\}")\
            \
            edited_df = st.data_editor(\
                st.session_state.inventory_data['wine'],\
                use_container_width=True,\
                num_rows="dynamic",\
                column_config=\{\
                    "Product": st.column_config.TextColumn("Wine", width="large"),\
                    "Type": st.column_config.SelectboxColumn(\
                        "Type",\
                        options=["Red", "White", "Rose", "Bubbles", "Dessert", "Fortified", "BTG"],\
                        width="small"\
                    ),\
                    "Cost": st.column_config.NumberColumn("Cost", format="$%.2f", width="small"),\
                    "Bottle Price": st.column_config.NumberColumn("Bottle Price", format="$%.0f", width="small"),\
                    "BTG": st.column_config.SelectboxColumn("BTG", options=["Yes", "No", ""], width="small"),\
                    "BTG Price": st.column_config.NumberColumn("BTG Price", format="$%.0f", width="small"),\
                    "Inventory": st.column_config.NumberColumn("Inventory", min_value=0, step=1, width="small"),\
                    "Value": st.column_config.NumberColumn("Value", format="$%.2f", disabled=True, width="small")\
                \}\
            )\
            \
            if st.button("\uc0\u55357 \u56510  Save & Recalculate", key="save_wine", type="primary"):\
                edited_df = recalculate_wine_values(edited_df)\
                st.session_state.inventory_data['wine'] = edited_df\
                st.success("\uc0\u9989  Wine inventory saved and values recalculated!")\
                st.rerun()\
    \
    with tab3:\
        st.subheader("Beer Inventory")\
        \
        if st.session_state.inventory_data['beer'].empty:\
            st.info("No beer data. Import from CSV or add manually.")\
        else:\
            # Display metrics\
            col1, col2, col3, col4 = st.columns(4)\
            with col1:\
                st.metric("Total Products", len(st.session_state.inventory_data['beer']))\
            with col2:\
                total_units = st.session_state.inventory_data['beer']['Inventory'].sum()\
                st.metric("Total Units", f"\{total_units:.0f\}")\
            with col3:\
                keg_count = len(st.session_state.inventory_data['beer'][\
                    st.session_state.inventory_data['beer']['UoM'].str.contains('Oz', na=False)\
                ]) if 'UoM' in st.session_state.inventory_data['beer'].columns else 0\
                st.metric("Kegs", keg_count)\
            with col4:\
                avg_cost_unit = st.session_state.inventory_data['beer']['Cost/Unit'].mean() if 'Cost/Unit' in st.session_state.inventory_data['beer'].columns else 0\
                st.metric("Avg $/Unit", f"$\{avg_cost_unit:.2f\}")\
            \
            edited_df = st.data_editor(\
                st.session_state.inventory_data['beer'],\
                use_container_width=True,\
                num_rows="dynamic",\
                column_config=\{\
                    "Product": st.column_config.TextColumn("Beer", width="medium"),\
                    "Type": st.column_config.SelectboxColumn(\
                        "Type",\
                        options=["Can", "Bottle", "Sixtel", "Quarter Barrel", "Half Barrel"],\
                        width="small"\
                    ),\
                    "Cost per Keg/Case": st.column_config.NumberColumn("Cost", format="$%.2f", width="small"),\
                    "Size": st.column_config.NumberColumn("Size", width="small"),\
                    "UoM": st.column_config.SelectboxColumn("UoM", options=["Can", "Bottle", "Oz"], width="small"),\
                    "Cost/Unit": st.column_config.NumberColumn("$/Unit", format="$%.4f", disabled=True, width="small"),\
                    "Menu Price": st.column_config.NumberColumn("Menu Price", format="$%.2f", width="small"),\
                    "Inventory": st.column_config.NumberColumn("Inventory", min_value=0, step=1, width="small"),\
                    "Value": st.column_config.NumberColumn("Value", format="$%.2f", disabled=True, width="small")\
                \}\
            )\
            \
            if st.button("\uc0\u55357 \u56510  Save & Recalculate", key="save_beer", type="primary"):\
                edited_df = recalculate_beer_values(edited_df)\
                st.session_state.inventory_data['beer'] = edited_df\
                st.success("\uc0\u9989  Beer inventory saved and values recalculated!")\
                st.rerun()\
    \
    with tab4:\
        st.subheader("Ingredients Inventory")\
        \
        if st.session_state.inventory_data['ingredients'].empty:\
            st.info("No ingredients data. Import from CSV or add manually.")\
        else:\
            # Display metrics\
            col1, col2, col3, col4 = st.columns(4)\
            with col1:\
                st.metric("Total Items", len(st.session_state.inventory_data['ingredients']))\
            with col2:\
                total_value = st.session_state.inventory_data['ingredients']['Value'].sum()\
                st.metric("Total Value", f"$\{total_value:.2f\}")\
            with col3:\
                out_of_stock = len(st.session_state.inventory_data['ingredients'][\
                    st.session_state.inventory_data['ingredients']['Inventory'] == 0\
                ])\
                st.metric("Out of Stock", out_of_stock)\
            with col4:\
                avg_cost = st.session_state.inventory_data['ingredients']['Cost'].mean()\
                st.metric("Avg Cost", f"$\{avg_cost:.2f\}")\
            \
            edited_df = st.data_editor(\
                st.session_state.inventory_data['ingredients'],\
                use_container_width=True,\
                num_rows="dynamic",\
                column_config=\{\
                    "Product": st.column_config.TextColumn("Ingredient", width="medium"),\
                    "Cost": st.column_config.NumberColumn("Cost", format="$%.2f", width="small"),\
                    "Size/Yield": st.column_config.NumberColumn("Size/Yield", width="small"),\
                    "UoM": st.column_config.TextColumn("Unit", width="small"),\
                    "Cost/Unit": st.column_config.NumberColumn("$/Unit", format="$%.4f", disabled=True, width="small"),\
                    "Inventory": st.column_config.NumberColumn("Inventory", min_value=0, step=0.5, width="small"),\
                    "Value": st.column_config.NumberColumn("Value", format="$%.2f", disabled=True, width="small"),\
                    "Distributor": st.column_config.TextColumn("Distributor", width="small"),\
                    "Order Notes": st.column_config.TextColumn("Notes", width="medium")\
                \}\
            )\
            \
            if st.button("\uc0\u55357 \u56510  Save & Recalculate", key="save_ingredients", type="primary"):\
                edited_df = recalculate_ingredients_values(edited_df)\
                st.session_state.inventory_data['ingredients'] = edited_df\
                st.success("\uc0\u9989  Ingredients inventory saved and values recalculated!")\
                st.rerun()\
\
elif module == "\uc0\u55357 \u56550  Weekly Ordering":\
    st.title("\uc0\u55357 \u56550  Weekly Ordering Module")\
    st.info("This module will generate orders based on reorder points. Par levels feature coming soon!")\
\
elif module == "\uc0\u55356 \u57209  Recipe Book":\
    st.title("\uc0\u55356 \u57209  Cocktail Recipe Book")\
    \
    tab1, tab2 = st.tabs(["\uc0\u55357 \u56534  Recipes", "\u10133  Add Recipe"])\
    \
    with tab1:\
        st.info("Recipe management coming soon!")\
    \
    with tab2:\
        st.subheader("Add New Recipe")\
        st.info("Recipe creation feature coming soon!")\
\
elif module == "\uc0\u9881 \u65039  Settings":\
    st.title("\uc0\u9881 \u65039  Settings")\
    \
    tab1, tab2 = st.tabs(["General", "Data Management"])\
    \
    with tab1:\
        st.subheader("General Settings")\
        col1, col2 = st.columns(2)\
        with col1:\
            st.text_input("Business Name", value="Canter Inn")\
            st.selectbox("Currency", ["USD ($)"])\
        with col2:\
            st.text_input("Location", value="Madison, WI")\
            st.selectbox("Date Format", ["MM/DD/YYYY"])\
        \
        if st.button("Save Settings", type="primary"):\
            st.success("\uc0\u9989  Settings saved!")\
    \
    with tab2:\
        st.subheader("Data Management")\
        \
        col1, col2 = st.columns(2)\
        with col1:\
            if st.button("\uc0\u55357 \u56548  Import CSV Files", use_container_width=True):\
                st.session_state.show_csv_upload = True\
        with col2:\
            if st.button("\uc0\u55357 \u56510  Export to CSV", use_container_width=True):\
                st.session_state.show_csv_export = True\
        \
        if st.session_state.get('show_csv_upload'):\
            show_csv_upload_section()\
        \
        if st.session_state.get('show_csv_export'):\
            with st.expander("Export Options", expanded=True):\
                col1, col2 = st.columns(2)\
                with col1:\
                    export_to_csv('spirits')\
                    export_to_csv('wine')\
                with col2:\
                    export_to_csv('beer')\
                    export_to_csv('ingredients')\
\
# Footer\
st.divider()\
st.caption("Canter Inn Beverage Management System v1.0 | \'a9 2024")}