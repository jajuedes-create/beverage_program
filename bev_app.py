# =============================================================================
# BEVERAGE MANAGEMENT APP V2.22
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients)
#   - Weekly Order Builder
#   - Cocktail Builds Book
#
# Version History:
#   V1.0 - Initial release with all core modules
#   V2.0 - Added historical comparison and COGS calculation
#   V2.1 - Fixed currency formatting in CSV uploads
#   V2.2 - UI improvements and locked calculated fields
#   V2.3 - Weekly Ordering: Added helper function to pull products from Master Inventory
#   V2.5 - Weekly Ordering: Added category filter, renamed section title
#   V2.6 - Weekly Ordering: Added distributor filter, dedicated save button for persistence
#   V2.7 - Weekly Ordering: Moved Top Products to Order Analytics tab, renamed tab
#   V2.8 - Weekly Ordering: Added Product Analysis title and description
#   V2.9 - Weekly Ordering: Renamed tab, added category filter to Add Product dropdown
#   V2.10 - Weekly Ordering: Added Step 3 Order Verification workflow with status tracking
#   V2.11 - Weekly Ordering: Added Bar/Storage Inventory columns with auto-calculated total
#   V2.12 - Weekly Ordering: Added CSV upload option to populate weekly inventory
#   V2.13 - Weekly Ordering: UI improvements - inline row deletion, Copy Order button,
#           renamed buttons, red flag status indicator, removed redundant Order Summary
#   V2.14 - Weekly Ordering: Simplified Add Products dropdown, removed redundant remove section
#   V2.15 - Weekly Ordering: Hidden table indexes, smaller Status column, renamed Notes to
#           Order Notes, added Invoice # column in Step 3
#   V2.16 - Weekly Ordering: Renamed Order Notes to Order Deals in Step 1
#   V2.17 - Order History: Added Month filter and TOTAL row in Weekly Order Totals
#   V2.18 - Added Unit column to Step 3 verification and Order History tables
#   V2.19 - Order Analytics: Category-specific top 10 dropdowns, dollar y-axis formatting,
#           removed redundant Top Products expander
#   V2.20 - Order Analytics: Major enhancement - Key Metrics Dashboard with trend indicators,
#           Date Range Filter, Budget vs Actual tracker, Price Change Tracker, Distributor
#           Analytics, consistent category colors, horizontal bar charts, export reports
#   V2.21 - Weekly Order Builder: Added Invoice Date column with calendar date picker in Step 3
#   V2.22 - Order Analytics: Streamlined Key Metrics (4 cards), removed Budget section,
#           combined Spending by Category pie chart with Top Products dropdowns,
#           enhanced Price Change Tracker with date, acknowledgment checkbox, and
#           Google Sheets persistence for reviewed status
#
# Author: Canter Inn
# Deployment: Streamlit Community Cloud via GitHub
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# =============================================================================
# GOOGLE SHEETS DATA PERSISTENCE
# =============================================================================
# Data is saved to Google Sheets for permanent storage
# This persists across all sessions, refreshes, and redeployments
#
# SETUP INSTRUCTIONS:
# 1. Create a Google Cloud project at https://console.cloud.google.com/
# 2. Enable the Google Sheets API and Google Drive API
# 3. Create a Service Account and download the JSON credentials
# 4. Create a Google Sheet and share it with the service account email
# 5. Add credentials to Streamlit secrets (see secrets.toml template below)
#
# Required in .streamlit/secrets.toml:
# [gcp_service_account]
# type = "service_account"
# project_id = "your-project-id"
# private_key_id = "..."
# private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
# client_email = "your-service-account@your-project.iam.gserviceaccount.com"
# client_id = "..."
# auth_uri = "https://accounts.google.com/o/oauth2/auth"
# token_uri = "https://oauth2.googleapis.com/token"
# auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
# client_x509_cert_url = "..."
#
# [google_sheets]
# spreadsheet_id = "your-spreadsheet-id-from-url"

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False

# Cache the Google Sheets connection
@st.cache_resource
def get_google_sheets_connection():
    """
    Creates and caches a connection to Google Sheets.
    Returns None if credentials are not configured.
    """
    if not GSHEETS_AVAILABLE:
        return None
    
    try:
        # Check if secrets are configured
        if "gcp_service_account" not in st.secrets:
            return None
        
        # Define the scope
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # Create credentials from secrets
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )
        
        # Connect to Google Sheets
        client = gspread.authorize(credentials)
        return client
    
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None

def get_spreadsheet():
    """Gets the configured spreadsheet."""
    client = get_google_sheets_connection()
    if client is None:
        return None
    
    try:
        spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        return client.open_by_key(spreadsheet_id)
    except Exception as e:
        st.error(f"Error opening spreadsheet: {e}")
        return None

def get_or_create_worksheet(spreadsheet, sheet_name: str):
    """Gets a worksheet by name, creating it if it doesn't exist."""
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)

def save_dataframe_to_sheets(df: pd.DataFrame, sheet_name: str):
    """
    Saves a DataFrame to a Google Sheets worksheet.
    
    Args:
        df: DataFrame to save
        sheet_name: Name of the worksheet
    """
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        
        # Clear existing data
        worksheet.clear()
        
        # Convert DataFrame to list of lists (handle NaN values)
        df_clean = df.fillna("")
        data = [df_clean.columns.tolist()] + df_clean.values.tolist()
        
        # Update the worksheet
        worksheet.update(data, value_input_option='RAW')
        return True
    
    except Exception as e:
        st.error(f"Error saving to Google Sheets ({sheet_name}): {e}")
        return False

def load_dataframe_from_sheets(sheet_name: str) -> pd.DataFrame:
    """
    Loads a DataFrame from a Google Sheets worksheet.
    
    Args:
        sheet_name: Name of the worksheet
        
    Returns:
        pd.DataFrame or None if sheet doesn't exist or error occurs
    """
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        
        if len(data) < 2:  # No data (only header or empty)
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Convert numeric columns back to numbers
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass  # Keep as string if conversion fails
        
        return df
    
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        st.error(f"Error loading from Google Sheets ({sheet_name}): {e}")
        return None

def save_json_to_sheets(data: list, sheet_name: str):
    """
    Saves JSON data (like cocktail recipes) to a Google Sheets worksheet.
    Stores as a single cell with JSON string.
    
    Args:
        data: List or dict to save as JSON
        sheet_name: Name of the worksheet
    """
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        worksheet.clear()
        
        # Store JSON as a single cell
        json_str = json.dumps(data, indent=2)
        worksheet.update('A1', [[json_str]], value_input_option='RAW')
        return True
    
    except Exception as e:
        st.error(f"Error saving JSON to Google Sheets ({sheet_name}): {e}")
        return False

def load_json_from_sheets(sheet_name: str) -> list:
    """
    Loads JSON data from a Google Sheets worksheet.
    
    Args:
        sheet_name: Name of the worksheet
        
    Returns:
        list or None if sheet doesn't exist or error occurs
    """
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        json_str = worksheet.acell('A1').value
        
        if json_str:
            return json.loads(json_str)
        return None
    
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        st.error(f"Error loading JSON from Google Sheets ({sheet_name}): {e}")
        return None

def save_text_to_sheets(text: str, sheet_name: str):
    """Saves a text value to a Google Sheets worksheet."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        worksheet.clear()
        worksheet.update('A1', [[text]], value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"Error saving text to Google Sheets ({sheet_name}): {e}")
        return False

def load_text_from_sheets(sheet_name: str) -> str:
    """Loads a text value from a Google Sheets worksheet."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        return worksheet.acell('A1').value
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        return None

def is_google_sheets_configured() -> bool:
    """Checks if Google Sheets is properly configured."""
    if not GSHEETS_AVAILABLE:
        return False
    return get_google_sheets_connection() is not None

def save_all_inventory_data():
    """Saves all inventory DataFrames to Google Sheets and creates a historical snapshot."""
    if not is_google_sheets_configured():
        return
    
    if 'spirits_inventory' in st.session_state:
        save_dataframe_to_sheets(st.session_state.spirits_inventory, 'spirits_inventory')
    if 'wine_inventory' in st.session_state:
        save_dataframe_to_sheets(st.session_state.wine_inventory, 'wine_inventory')
    if 'beer_inventory' in st.session_state:
        save_dataframe_to_sheets(st.session_state.beer_inventory, 'beer_inventory')
    if 'ingredients_inventory' in st.session_state:
        save_dataframe_to_sheets(st.session_state.ingredients_inventory, 'ingredients_inventory')
    if 'weekly_inventory' in st.session_state:
        save_dataframe_to_sheets(st.session_state.weekly_inventory, 'weekly_inventory')
    if 'order_history' in st.session_state:
        save_dataframe_to_sheets(st.session_state.order_history, 'order_history')
    if 'last_inventory_date' in st.session_state:
        save_text_to_sheets(st.session_state.last_inventory_date, 'last_inventory_date')
    
    # V2.10: Save pending order for verification workflow
    if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
        save_dataframe_to_sheets(st.session_state.pending_order, 'pending_order')
    
    # Save historical snapshot for comparison tracking
    save_inventory_snapshot()


def save_pending_order():
    """Saves pending order to Google Sheets for verification workflow."""
    if not is_google_sheets_configured():
        return
    
    if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
        save_dataframe_to_sheets(st.session_state.pending_order, 'pending_order')


def clear_pending_order():
    """Clears pending order from session state and Google Sheets."""
    st.session_state.pending_order = pd.DataFrame()
    
    if is_google_sheets_configured():
        spreadsheet = get_spreadsheet()
        if spreadsheet:
            try:
                worksheet = spreadsheet.worksheet('pending_order')
                worksheet.clear()
            except:
                pass  # Worksheet doesn't exist, that's fine


def save_price_change_acks():
    """Saves price change acknowledgments to Google Sheets."""
    if not is_google_sheets_configured():
        return
    
    if 'price_change_acks' in st.session_state and len(st.session_state.price_change_acks) > 0:
        # Convert dictionary to dataframe
        acks_data = [{'ack_key': k, 'reviewed': v} for k, v in st.session_state.price_change_acks.items()]
        acks_df = pd.DataFrame(acks_data)
        save_dataframe_to_sheets(acks_df, 'price_change_acks')


def load_price_change_acks() -> dict:
    """Loads price change acknowledgments from Google Sheets."""
    if not is_google_sheets_configured():
        return {}
    
    try:
        acks_df = load_dataframe_from_sheets('price_change_acks')
        if acks_df is not None and len(acks_df) > 0:
            # Convert dataframe back to dictionary
            acks_dict = {}
            for _, row in acks_df.iterrows():
                # Handle boolean conversion (may come back as string from sheets)
                reviewed = row['reviewed']
                if isinstance(reviewed, str):
                    reviewed = reviewed.lower() == 'true'
                acks_dict[row['ack_key']] = reviewed
            return acks_dict
    except Exception as e:
        pass  # Worksheet doesn't exist yet, that's fine
    
    return {}


def save_cocktail_recipes():
    """Saves cocktail recipes to Google Sheets."""
    if not is_google_sheets_configured():
        return
    
    if 'cocktail_recipes' in st.session_state:
        save_json_to_sheets(st.session_state.cocktail_recipes, 'cocktail_recipes')


def save_inventory_snapshot():
    """
    Saves a snapshot of current inventory values with timestamp.
    Used for historical comparison tracking.
    """
    if not is_google_sheets_configured():
        return
    
    # Calculate current values
    spirits_value = calculate_total_value(st.session_state.spirits_inventory) if 'spirits_inventory' in st.session_state else 0
    wine_value = calculate_total_value(st.session_state.wine_inventory) if 'wine_inventory' in st.session_state else 0
    beer_value = calculate_total_value(st.session_state.beer_inventory) if 'beer_inventory' in st.session_state else 0
    ingredients_value = calculate_total_value(st.session_state.ingredients_inventory) if 'ingredients_inventory' in st.session_state else 0
    total_value = spirits_value + wine_value + beer_value + ingredients_value
    
    # Create snapshot record
    snapshot = {
        'Date': datetime.now().strftime("%Y-%m-%d"),
        'Spirits Value': spirits_value,
        'Wine Value': wine_value,
        'Beer Value': beer_value,
        'Ingredients Value': ingredients_value,
        'Total Value': total_value
    }
    
    # Load existing history
    existing_history = load_dataframe_from_sheets('inventory_history')
    
    if existing_history is not None and len(existing_history) > 0:
        # Check if we already have a snapshot for today
        today = datetime.now().strftime("%Y-%m-%d")
        if today in existing_history['Date'].values:
            # Update today's snapshot
            existing_history.loc[existing_history['Date'] == today, 'Spirits Value'] = spirits_value
            existing_history.loc[existing_history['Date'] == today, 'Wine Value'] = wine_value
            existing_history.loc[existing_history['Date'] == today, 'Beer Value'] = beer_value
            existing_history.loc[existing_history['Date'] == today, 'Ingredients Value'] = ingredients_value
            existing_history.loc[existing_history['Date'] == today, 'Total Value'] = total_value
            history_df = existing_history
        else:
            # Add new snapshot
            history_df = pd.concat([existing_history, pd.DataFrame([snapshot])], ignore_index=True)
    else:
        # Create new history
        history_df = pd.DataFrame([snapshot])
    
    # Save to Google Sheets
    save_dataframe_to_sheets(history_df, 'inventory_history')


def load_inventory_history() -> pd.DataFrame:
    """
    Loads historical inventory snapshots.
    
    Returns:
        pd.DataFrame with columns: Date, Spirits Value, Wine Value, Beer Value, Ingredients Value, Total Value
    """
    if not is_google_sheets_configured():
        return None
    
    history = load_dataframe_from_sheets('inventory_history')
    
    if history is not None and len(history) > 0:
        # Ensure numeric columns are numeric
        value_cols = ['Spirits Value', 'Wine Value', 'Beer Value', 'Ingredients Value', 'Total Value']
        for col in value_cols:
            if col in history.columns:
                history[col] = pd.to_numeric(history[col], errors='coerce').fillna(0)
        
        # Sort by date descending
        history = history.sort_values('Date', ascending=False)
    
    return history

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Beverage Management App V2.22",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

st.markdown("""
<style>
    /* ----- Card Container Styling ----- */
    .module-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 30px;
        margin: 10px 0;
        color: white;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        cursor: pointer;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .module-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* ----- Individual Card Color Themes ----- */
    .card-inventory {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .card-ordering {
        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
    }
    
    .card-cocktails {
        background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%);
    }
    
    /* ----- Card Text Styling ----- */
    .card-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .card-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .card-description {
        font-size: 14px;
        opacity: 0.9;
    }
    
    /* ----- Header Styling ----- */
    .main-header {
        text-align: center;
        padding: 20px 0 40px 0;
    }
    
    .main-header h1 {
        color: #1f1f1f;
        font-size: 42px;
        margin-bottom: 10px;
    }
    
    .main-header p {
        color: #666;
        font-size: 18px;
    }
    
    /* ----- Cocktail Card Styling ----- */
    .cocktail-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #8E2DE2;
    }
    
    .cocktail-name {
        font-size: 20px;
        font-weight: bold;
        color: #1f1f1f;
        margin-bottom: 10px;
    }
    
    .cocktail-meta {
        font-size: 14px;
        color: #666;
    }
    
    /* ----- Recipe Display ----- */
    .recipe-section {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .ingredient-row {
        display: flex;
        justify-content: space-between;
        padding: 5px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* ----- Inventory Tab Styling ----- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 70px;
        padding: 12px 28px;
        font-size: 22px;
        font-weight: 700;
        border-radius: 8px 8px 0 0;
        background-color: #f0f2f6;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        border-top: 3px solid #ff4b4b;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e6e9ef;
    }
    
    /* ----- Expander Styling ----- */
    .streamlit-expanderHeader {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 16px 12px !important;
    }
    
    .streamlit-expanderHeader p {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
    
    details[data-testid="stExpander"] > summary {
        font-size: 20px !important;
        font-weight: 600 !important;
        padding: 16px 12px !important;
    }
    
    details[data-testid="stExpander"] > summary > span {
        font-size: 20px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SAMPLE DATA - SPIRITS INVENTORY
# =============================================================================

def get_sample_spirits():
    """
    Returns a DataFrame with sample spirit inventory data.
    Margins are stored as whole numbers (e.g., 20 for 20%).
    """
    data = [
        {"Product": "Hendrick's", "Type": "Gin", "Cost": 30.80, "Size (oz.)": 33.8, 
         "Margin": 20, "Neat Price": 9.0, "Inventory": 1.0, "Use": "Backbar", 
         "Distributor": "Breakthru", "Order Notes": "6 pk deal", "Suggested Retail": 44},
        {"Product": "Tito's", "Type": "Vodka", "Cost": 24.50, "Size (oz.)": 33.8, 
         "Margin": 18, "Neat Price": 8.0, "Inventory": 3.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal", "Suggested Retail": 35},
        {"Product": "Ketel One", "Type": "Vodka", "Cost": 32.25, "Size (oz.)": 33.8, 
         "Margin": 19, "Neat Price": 10.0, "Inventory": 3.0, "Use": "Backbar", 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal", "Suggested Retail": 46},
        {"Product": "Tempus Fugit Crème de Cacao", "Type": "Cordial & Digestif", "Cost": 32.50, "Size (oz.)": 23.7, 
         "Margin": 22, "Neat Price": 12.0, "Inventory": 6.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "6 pk deal", "Suggested Retail": 47},
        {"Product": "St. George Absinthe", "Type": "Cordial & Digestif", "Cost": 54.00, "Size (oz.)": 25.3, 
         "Margin": 23, "Neat Price": 19.0, "Inventory": 1.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 78},
        {"Product": "Espolòn Blanco", "Type": "Tequila", "Cost": 25.00, "Size (oz.)": 33.8, 
         "Margin": 20, "Neat Price": 8.0, "Inventory": 4.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 36},
        {"Product": "Lustau Vermut Rojo", "Type": "Vermouth & Aperitif", "Cost": 16.00, "Size (oz.)": 25.3, 
         "Margin": 18, "Neat Price": 7.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 23},
        {"Product": "Buffalo Trace", "Type": "Whiskey", "Cost": 31.00, "Size (oz.)": 33.8, 
         "Margin": 20, "Neat Price": 9.0, "Inventory": 2.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 44},
        {"Product": "Rittenhouse Rye", "Type": "Whiskey", "Cost": 28.00, "Size (oz.)": 25.3, 
         "Margin": 19, "Neat Price": 9.0, "Inventory": 3.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 40},
        {"Product": "Botanist", "Type": "Gin", "Cost": 33.74, "Size (oz.)": 33.8, 
         "Margin": 21, "Neat Price": 10.0, "Inventory": 4.0, "Use": "Menu", 
         "Distributor": "General Beverage", "Order Notes": "", "Suggested Retail": 48},
        {"Product": "Bordiga Extra Dry Vermouth", "Type": "Vermouth & Aperitif", "Cost": 23.00, "Size (oz.)": 25.3, 
         "Margin": 18, "Neat Price": 8.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 33},
        {"Product": "Campari", "Type": "Vermouth & Aperitif", "Cost": 28.00, "Size (oz.)": 33.8, 
         "Margin": 20, "Neat Price": 8.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 40},
        {"Product": "Angostura Bitters", "Type": "Bitters", "Cost": 32.00, "Size (oz.)": 16.0, 
         "Margin": 15, "Neat Price": 0.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 0},
        {"Product": "Angostura Orange Bitters", "Type": "Bitters", "Cost": 16.00, "Size (oz.)": 4.0, 
         "Margin": 15, "Neat Price": 0.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 0},
    ]
    
    df = pd.DataFrame(data)
    df["Cost/Oz"] = df["Cost"] / df["Size (oz.)"]
    df["Value"] = df["Cost"] * df["Inventory"]
    
    column_order = ["Product", "Type", "Cost", "Size (oz.)", "Cost/Oz", "Margin", 
                    "Neat Price", "Inventory", "Value", "Use", "Distributor", 
                    "Order Notes", "Suggested Retail"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - WINE INVENTORY
# =============================================================================

def get_sample_wines():
    """
    Returns a DataFrame with sample wine inventory data.
    Margins are stored as whole numbers (e.g., 35 for 35%).
    """
    data = [
        {"Product": "Mauzac Nature, 2022, Domaine Plageoles, Gaillac, France", 
         "Type": "Bubbles", "Cost": 22.0, "Size (oz.)": 25.3, "Margin": 35, 
         "Bottle Price": 63.0, "Inventory": 18.0, "Distributor": "Chromatic", 
         "BTG": 14.0, "Suggested Retail": 32},
        {"Product": "Savagnin, 2022, Domaine de la Pinte, 'Sav'Or' Vin de France (Jura)", 
         "Type": "Rosé/Orange", "Cost": 29.0, "Size (oz.)": 25.3, "Margin": 37, 
         "Bottle Price": 79.0, "Inventory": 5.0, "Distributor": "Chromatic", 
         "BTG": 18.0, "Suggested Retail": 42},
        {"Product": "Sémillon, 2015, Forlorn Hope, 'Nacré', Napa Valley, CA", 
         "Type": "White", "Cost": 17.0, "Size (oz.)": 25.3, "Margin": 33, 
         "Bottle Price": 51.0, "Inventory": 2.0, "Distributor": "Chromatic", 
         "BTG": 11.0, "Suggested Retail": 24},
        {"Product": "Blanc de Blancs Extra Brut, 2012, Le Brun Servenay, Champagne, France", 
         "Type": "Bubbles", "Cost": 65.0, "Size (oz.)": 25.3, "Margin": 35, 
         "Bottle Price": 186.0, "Inventory": 2.0, "Distributor": "Left Bank", 
         "BTG": 41.0, "Suggested Retail": 94},
        {"Product": "Rosé of Gewürtztraminer/Pinot Noir, 2023, Teutonic, Willamette Valley, OR", 
         "Type": "Rosé/Orange", "Cost": 23.0, "Size (oz.)": 25.3, "Margin": 33, 
         "Bottle Price": 69.0, "Inventory": 2.0, "Distributor": "Left Bank", 
         "BTG": 15.0, "Suggested Retail": 33},
        {"Product": "Chardonnay, 2023, Jean Dauvissat, Chablis, France", 
         "Type": "White", "Cost": 31.5, "Size (oz.)": 25.3, "Margin": 35, 
         "Bottle Price": 90.0, "Inventory": 6.0, "Distributor": "Vino Veritas", 
         "BTG": 20.0, "Suggested Retail": 45},
        {"Product": "Pinot Noir, 2021, Domaine de la Côte, Sta. Rita Hills, CA", 
         "Type": "Red", "Cost": 55.0, "Size (oz.)": 25.3, "Margin": 34, 
         "Bottle Price": 162.0, "Inventory": 3.0, "Distributor": "Vino Veritas", 
         "BTG": 36.0, "Suggested Retail": 79},
        {"Product": "Nebbiolo, 2019, Cantina Massara, Barolo, Piedmont, Italy", 
         "Type": "Red", "Cost": 31.0, "Size (oz.)": 25.3, "Margin": 32, 
         "Bottle Price": 97.0, "Inventory": 4.0, "Distributor": "Vino Veritas", 
         "BTG": 22.0, "Suggested Retail": 45},
    ]
    
    df = pd.DataFrame(data)
    df["Value"] = df["Cost"] * df["Inventory"]
    
    column_order = ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Bottle Price", 
                    "Inventory", "Value", "Distributor", "BTG", "Suggested Retail"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - BEER INVENTORY
# =============================================================================

def get_sample_beers():
    """
    Returns a DataFrame with sample beer inventory data.
    Margins are stored as whole numbers (e.g., 21 for 21%).
    """
    data = [
        {"Product": "New Glarus Staghorn Oktoberfest", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 21, "Menu Price": 5.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Moon Man", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 21, "Menu Price": 5.0, "Inventory": 2.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Coors Light", "Type": "Can", 
         "Cost per Keg/Case": 24.51, "Size": 30.0, "UoM": "cans", 
         "Margin": 19, "Menu Price": 4.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Fat Squirrel", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 22, "Menu Price": 5.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Hop Haus Yard Work IPA", "Type": "Sixtel", 
         "Cost per Keg/Case": 75.00, "Size": 1.0, "UoM": "keg", 
         "Margin": 22, "Menu Price": 7.0, "Inventory": 1.0, 
         "Distributor": "GB Beer", "Order Notes": ""},
        {"Product": "High Life", "Type": "Bottles", 
         "Cost per Keg/Case": 21.15, "Size": 24.0, "UoM": "bottles", 
         "Margin": 18, "Menu Price": 4.0, "Inventory": 2.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
    ]
    
    df = pd.DataFrame(data)
    df["Cost/Unit"] = df["Cost per Keg/Case"] / df["Size"]
    df["Value"] = df["Cost per Keg/Case"] * df["Inventory"]
    
    column_order = ["Product", "Type", "Cost per Keg/Case", "Size", "UoM", 
                    "Cost/Unit", "Margin", "Menu Price", "Inventory", "Value", 
                    "Distributor", "Order Notes"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - INGREDIENT INVENTORY
# =============================================================================

def get_sample_ingredients():
    """
    Returns a DataFrame with sample ingredient inventory data.
    """
    data = [
        {"Product": "Amaretto Cherries", "Cost": 15.00, "Size/Yield": 80.0, 
         "UoM": "cherries", "Distributor": "Left Bank", "Order Notes": ""},
        {"Product": "Olives", "Cost": 29.63, "Size/Yield": 300.0, 
         "UoM": "pieces", "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Natalie's Lime Juice", "Cost": 8.34, "Size/Yield": 32.0, 
         "UoM": "oz", "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Natalie's Lemon Juice", "Cost": 8.34, "Size/Yield": 32.0, 
         "UoM": "oz", "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Agave Nectar", "Cost": 17.56, "Size/Yield": 64.0, 
         "UoM": "oz", "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Q Ginger Beer", "Cost": 0.00, "Size/Yield": 7.5, 
         "UoM": "oz", "Distributor": "Breakthru", "Order Notes": "Free"},
        {"Product": "Q Club Soda", "Cost": 1.04, "Size/Yield": 7.5, 
         "UoM": "oz", "Distributor": "Breakthru", "Order Notes": "3cs mix n' match + 1cs Ginger Beer NC"},
        {"Product": "Heavy Cream", "Cost": 9.59, "Size/Yield": 64.0, 
         "UoM": "oz", "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Simple Syrup (House)", "Cost": 5.00, "Size/Yield": 32.0, 
         "UoM": "oz", "Distributor": "House Made", "Order Notes": ""},
        {"Product": "Demerara Syrup (House)", "Cost": 8.00, "Size/Yield": 32.0, 
         "UoM": "oz", "Distributor": "House Made", "Order Notes": ""},
        {"Product": "Orange Peel", "Cost": 0.50, "Size/Yield": 10.0, 
         "UoM": "pieces", "Distributor": "House Made", "Order Notes": ""},
        {"Product": "Lemon Peel", "Cost": 0.50, "Size/Yield": 10.0, 
         "UoM": "pieces", "Distributor": "House Made", "Order Notes": ""},
        {"Product": "Luxardo Cherry", "Cost": 25.00, "Size/Yield": 50.0, 
         "UoM": "cherries", "Distributor": "Breakthru", "Order Notes": ""},
    ]
    
    df = pd.DataFrame(data)
    df["Cost/Unit"] = df["Cost"] / df["Size/Yield"]
    
    column_order = ["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit", 
                    "Distributor", "Order Notes"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - WEEKLY INVENTORY (Par Levels)
# =============================================================================

def get_sample_weekly_inventory():
    """
    Returns a DataFrame with weekly inventory items and par levels.
    V2.11: Added Bar Inventory and Storage Inventory columns.
    """
    data = [
        {"Product": "New Glarus Moon Man", "Category": "Beer", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Case", "Unit Cost": 26.40, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Coors Light", "Category": "Beer", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Case", "Unit Cost": 24.51, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Fat Squirrel", "Category": "Beer", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Case", "Unit Cost": 26.40, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Hop Haus Yard Work IPA", "Category": "Beer", "Par": 1, 
         "Bar Inventory": 0.5, "Storage Inventory": 0, "Unit": "Sixtel", "Unit Cost": 75.00, 
         "Distributor": "GB Beer", "Order Notes": ""},
        {"Product": "High Life", "Category": "Beer", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Case", "Unit Cost": 21.15, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Tito's", "Category": "Spirits", "Par": 4, 
         "Bar Inventory": 1, "Storage Inventory": 2, "Unit": "Bottle", "Unit Cost": 24.50, 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal"},
        {"Product": "Espolòn Blanco", "Category": "Spirits", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Bottle", "Unit Cost": 25.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Buffalo Trace", "Category": "Spirits", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Bottle", "Unit Cost": 31.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Rittenhouse Rye", "Category": "Spirits", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Bottle", "Unit Cost": 28.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Botanist", "Category": "Spirits", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Bottle", "Unit Cost": 33.74, 
         "Distributor": "General Beverage", "Order Notes": ""},
        {"Product": "Natalie's Lime Juice", "Category": "Ingredients", "Par": 4, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Bottle", "Unit Cost": 8.34, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Natalie's Lemon Juice", "Category": "Ingredients", "Par": 4, 
         "Bar Inventory": 1, "Storage Inventory": 2, "Unit": "Bottle", "Unit Cost": 8.34, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Agave Nectar", "Category": "Ingredients", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Bottle", "Unit Cost": 17.56, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Q Club Soda", "Category": "Ingredients", "Par": 3, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Case", "Unit Cost": 12.48, 
         "Distributor": "Breakthru", "Order Notes": "3cs mix n' match + 1cs Ginger Beer NC"},
        {"Product": "Heavy Cream", "Category": "Ingredients", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Quart", "Unit Cost": 9.59, 
         "Distributor": "US Foods", "Order Notes": ""},
    ]
    
    df = pd.DataFrame(data)
    # V2.11: Calculate Total Current Inventory
    df['Total Current Inventory'] = df['Bar Inventory'] + df['Storage Inventory']
    return df


# =============================================================================
# SAMPLE DATA - ORDER HISTORY
# =============================================================================

def get_sample_order_history():
    """
    Returns a DataFrame with sample historical order data.
    V2.18: Added Unit column
    """
    today = datetime.now()
    weeks = []
    for i in range(6, 0, -1):
        week_start = today - timedelta(weeks=i)
        weeks.append(week_start.strftime("%Y-%m-%d"))
    
    data = [
        {"Week": weeks[0], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[0], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit": "Case", "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[0], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 3, "Unit": "Bottle", "Unit Cost": 8.34, "Total Cost": 25.02, "Distributor": "US Foods"},
        {"Week": weeks[1], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 24.50, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 31.00, "Total Cost": 62.00, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Coors Light", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit": "Case", "Unit Cost": 24.51, "Total Cost": 24.51, "Distributor": "Frank Beer"},
        {"Week": weeks[2], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 25.00, "Total Cost": 50.00, "Distributor": "Breakthru"},
        {"Week": weeks[2], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit": "Case", "Unit Cost": 26.40, "Total Cost": 26.40, "Distributor": "Frank Beer"},
        {"Week": weeks[2], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[2], "Product": "Natalie's Lemon Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[3], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 3, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 73.50, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "Rittenhouse Rye", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit": "Bottle", "Unit Cost": 28.00, "Total Cost": 28.00, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "High Life", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit": "Case", "Unit Cost": 21.15, "Total Cost": 42.30, "Distributor": "Frank Beer"},
        {"Week": weeks[4], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit": "Bottle", "Unit Cost": 31.00, "Total Cost": 31.00, "Distributor": "Breakthru"},
        {"Week": weeks[4], "Product": "Botanist", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 33.74, "Total Cost": 67.48, "Distributor": "General Beverage"},
        {"Week": weeks[4], "Product": "Hop Haus Yard Work IPA", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit": "Sixtel", "Unit Cost": 75.00, "Total Cost": 75.00, "Distributor": "GB Beer"},
        {"Week": weeks[4], "Product": "Q Club Soda", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit": "Case", "Unit Cost": 12.48, "Total Cost": 24.96, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit": "Bottle", "Unit Cost": 25.00, "Total Cost": 25.00, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit": "Case", "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[5], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[5], "Product": "Heavy Cream", "Category": "Ingredients", 
         "Quantity Ordered": 1, "Unit": "Quart", "Unit Cost": 9.59, "Total Cost": 9.59, "Distributor": "US Foods"},
    ]
    
    return pd.DataFrame(data)


# =============================================================================
# SAMPLE DATA - COCKTAIL RECIPES
# =============================================================================

def get_sample_cocktails():
    """
    Returns a list of sample cocktail recipes.
    Each recipe is a dictionary containing all recipe information.
    
    Structure:
        - name: Cocktail name
        - glass: Glassware used
        - instructions: Build instructions
        - sale_price: Menu price
        - ingredients: List of {product, amount, unit, unit_cost, cost}
    """
    cocktails = [
        {
            "name": "Martini at The Inn",
            "glass": "Martini",
            "instructions": "Combine gin, vermouth, and bitters in mixing glass. Add ice and stir until ice cold. Strain into chilled martini glass and garnish with olives.",
            "sale_price": 14.00,
            "ingredients": [
                {"product": "Botanist", "amount": 2.5, "unit": "oz"},
                {"product": "Bordiga Extra Dry Vermouth", "amount": 0.5, "unit": "oz"},
                {"product": "Angostura Orange Bitters", "amount": 0.03, "unit": "oz"},
                {"product": "Olives", "amount": 2, "unit": "pieces"},
            ]
        },
        {
            "name": "Old Fashioned",
            "glass": "Rocks",
            "instructions": "Add sugar, bitters, and a splash of water to rocks glass. Muddle until dissolved. Add bourbon and ice, stir. Garnish with orange peel and cherry.",
            "sale_price": 13.00,
            "ingredients": [
                {"product": "Buffalo Trace", "amount": 2.0, "unit": "oz"},
                {"product": "Demerara Syrup (House)", "amount": 0.25, "unit": "oz"},
                {"product": "Angostura Bitters", "amount": 0.1, "unit": "oz"},
                {"product": "Orange Peel", "amount": 1, "unit": "pieces"},
                {"product": "Luxardo Cherry", "amount": 1, "unit": "cherries"},
            ]
        },
        {
            "name": "Margarita",
            "glass": "Coupe",
            "instructions": "Combine tequila, lime juice, and agave in shaker with ice. Shake vigorously and strain into salt-rimmed coupe glass. Garnish with lime wheel.",
            "sale_price": 12.00,
            "ingredients": [
                {"product": "Espolòn Blanco", "amount": 2.0, "unit": "oz"},
                {"product": "Natalie's Lime Juice", "amount": 1.0, "unit": "oz"},
                {"product": "Agave Nectar", "amount": 0.75, "unit": "oz"},
            ]
        },
        {
            "name": "Negroni",
            "glass": "Rocks",
            "instructions": "Add all ingredients to rocks glass with ice. Stir until well chilled. Garnish with orange peel.",
            "sale_price": 13.00,
            "ingredients": [
                {"product": "Botanist", "amount": 1.0, "unit": "oz"},
                {"product": "Campari", "amount": 1.0, "unit": "oz"},
                {"product": "Lustau Vermut Rojo", "amount": 1.0, "unit": "oz"},
                {"product": "Orange Peel", "amount": 1, "unit": "pieces"},
            ]
        },
        {
            "name": "Moscow Mule",
            "glass": "Copper Mug",
            "instructions": "Add vodka and lime juice to copper mug. Fill with ice and top with ginger beer. Stir gently and garnish with lime wheel.",
            "sale_price": 11.00,
            "ingredients": [
                {"product": "Tito's", "amount": 2.0, "unit": "oz"},
                {"product": "Natalie's Lime Juice", "amount": 0.75, "unit": "oz"},
                {"product": "Q Ginger Beer", "amount": 4.0, "unit": "oz"},
            ]
        },
        {
            "name": "Whiskey Sour",
            "glass": "Coupe",
            "instructions": "Combine bourbon, lemon juice, and simple syrup in shaker. Dry shake, then add ice and shake again. Strain into coupe and garnish with cherry.",
            "sale_price": 12.00,
            "ingredients": [
                {"product": "Buffalo Trace", "amount": 2.0, "unit": "oz"},
                {"product": "Natalie's Lemon Juice", "amount": 0.75, "unit": "oz"},
                {"product": "Simple Syrup (House)", "amount": 0.75, "unit": "oz"},
                {"product": "Luxardo Cherry", "amount": 1, "unit": "cherries"},
            ]
        },
    ]
    
    return cocktails


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """
    Initializes all session state variables.
    First tries to load from Google Sheets, then falls back to sample data.
    """
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Check if Google Sheets is configured
    sheets_configured = is_google_sheets_configured()
    
    # ----- Load Inventory Data (from Google Sheets or sample data) -----
    
    if 'spirits_inventory' not in st.session_state:
        saved_spirits = load_dataframe_from_sheets('spirits_inventory') if sheets_configured else None
        if saved_spirits is not None and len(saved_spirits) > 0:
            st.session_state.spirits_inventory = saved_spirits
        else:
            st.session_state.spirits_inventory = get_sample_spirits()
    
    if 'wine_inventory' not in st.session_state:
        saved_wine = load_dataframe_from_sheets('wine_inventory') if sheets_configured else None
        if saved_wine is not None and len(saved_wine) > 0:
            st.session_state.wine_inventory = saved_wine
        else:
            st.session_state.wine_inventory = get_sample_wines()
    
    if 'beer_inventory' not in st.session_state:
        saved_beer = load_dataframe_from_sheets('beer_inventory') if sheets_configured else None
        if saved_beer is not None and len(saved_beer) > 0:
            st.session_state.beer_inventory = saved_beer
        else:
            st.session_state.beer_inventory = get_sample_beers()
    
    if 'ingredients_inventory' not in st.session_state:
        saved_ingredients = load_dataframe_from_sheets('ingredients_inventory') if sheets_configured else None
        if saved_ingredients is not None and len(saved_ingredients) > 0:
            st.session_state.ingredients_inventory = saved_ingredients
        else:
            st.session_state.ingredients_inventory = get_sample_ingredients()
    
    if 'last_inventory_date' not in st.session_state:
        saved_date = load_text_from_sheets('last_inventory_date') if sheets_configured else None
        if saved_date is not None:
            st.session_state.last_inventory_date = saved_date
        else:
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
    
    # ----- Load Weekly Order Builder Data -----
    
    if 'weekly_inventory' not in st.session_state:
        saved_weekly = load_dataframe_from_sheets('weekly_inventory') if sheets_configured else None
        if saved_weekly is not None and len(saved_weekly) > 0:
            st.session_state.weekly_inventory = saved_weekly
        else:
            st.session_state.weekly_inventory = get_sample_weekly_inventory()
    
    if 'order_history' not in st.session_state:
        saved_history = load_dataframe_from_sheets('order_history') if sheets_configured else None
        if saved_history is not None and len(saved_history) > 0:
            st.session_state.order_history = saved_history
        else:
            st.session_state.order_history = get_sample_order_history()
    
    if 'current_order' not in st.session_state:
        st.session_state.current_order = pd.DataFrame()
    
    # V2.10: Load pending order for verification workflow
    if 'pending_order' not in st.session_state:
        saved_pending = load_dataframe_from_sheets('pending_order') if sheets_configured else None
        if saved_pending is not None and len(saved_pending) > 0:
            # V2.12 Fix: Ensure Verification Notes is string type
            if 'Verification Notes' in saved_pending.columns:
                saved_pending['Verification Notes'] = saved_pending['Verification Notes'].fillna('').astype(str)
            st.session_state.pending_order = saved_pending
        else:
            st.session_state.pending_order = pd.DataFrame()
    
    # V2.22: Load price change acknowledgments
    if 'price_change_acks' not in st.session_state:
        saved_acks = load_price_change_acks() if sheets_configured else {}
        st.session_state.price_change_acks = saved_acks
    
    # ----- Load Cocktail Recipes -----
    
    if 'cocktail_recipes' not in st.session_state:
        saved_cocktails = load_json_from_sheets('cocktail_recipes') if sheets_configured else None
        if saved_cocktails is not None and len(saved_cocktails) > 0:
            st.session_state.cocktail_recipes = saved_cocktails
        else:
            st.session_state.cocktail_recipes = get_sample_cocktails()


# =============================================================================
# NAVIGATION FUNCTION
# =============================================================================

def navigate_to(page: str):
    """
    Sets the current page in session state.
    """
    st.session_state.current_page = page


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clean_currency_value(value):
    """
    Cleans a currency value by removing $, commas, and converting to float.
    Handles strings like "$30.80", "30.80", "$1,234.56", or already numeric values.
    
    Args:
        value: The value to clean (string or numeric)
        
    Returns:
        float: Cleaned numeric value, or 0.0 if conversion fails
    """
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # Remove $, commas, and whitespace
        cleaned = value.replace('$', '').replace(',', '').strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


def clean_currency_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Cleans a currency column in a DataFrame, converting string values to floats.
    
    Args:
        df: DataFrame to modify
        column_name: Name of the column to clean
        
    Returns:
        pd.DataFrame: DataFrame with cleaned column
    """
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(clean_currency_value)
    return df


def clean_percentage_value(value):
    """
    Cleans a percentage value by handling various formats.
    Returns percentage as a whole number (e.g., 20 for 20%, not 0.20).
    
    Input handling:
    - "20%" -> 20
    - "0.20" -> 20
    - 20 -> 20
    - 0.20 -> 20
    
    Args:
        value: The value to clean (string or numeric)
        
    Returns:
        float: Cleaned percentage as whole number (e.g., 20 for 20%)
    """
    if pd.isna(value):
        return 0.0
    
    # If already a float/int
    if isinstance(value, (int, float)):
        # If less than or equal to 1, assume it's a decimal that needs conversion
        if value <= 1:
            return float(value) * 100.0
        return float(value)
    
    # If it's a string
    if isinstance(value, str):
        # Remove whitespace
        cleaned = value.strip()
        
        # Check for % symbol
        if '%' in cleaned:
            # Remove % and convert - already a whole number
            cleaned = cleaned.replace('%', '').strip()
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        else:
            # No % symbol, try to convert
            try:
                num = float(cleaned)
                # If less than or equal to 1, assume it's a decimal
                if num <= 1:
                    return num * 100.0
                return num
            except ValueError:
                return 0.0
    
    return 0.0


def clean_percentage_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Cleans a percentage column in a DataFrame.
    
    Args:
        df: DataFrame to modify
        column_name: Name of the column to clean
        
    Returns:
        pd.DataFrame: DataFrame with cleaned column
    """
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(clean_percentage_value)
    return df


def process_uploaded_spirits(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes an uploaded Spirits inventory CSV:
    - Cleans currency columns
    - Cleans percentage columns (Margin)
    - Recalculates derived fields (Cost/Oz, Value)
    
    Args:
        df: Raw uploaded DataFrame
        
    Returns:
        pd.DataFrame: Processed DataFrame ready for use
    """
    try:
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Clean currency columns
        currency_columns = ['Cost', 'Neat Price', 'Suggested Retail', 'Cost/Oz', 'Value']
        for col in currency_columns:
            df = clean_currency_column(df, col)
        
        # Clean percentage columns
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        
        # Clean numeric columns (excluding Margin which is handled above)
        numeric_columns = ['Size (oz.)', 'Inventory']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Recalculate derived fields
        if 'Cost' in df.columns and 'Size (oz.)' in df.columns:
            df['Cost/Oz'] = df.apply(
                lambda row: round(row['Cost'] / row['Size (oz.)'], 2) if row['Size (oz.)'] > 0 else 0, 
                axis=1
            )
        
        if 'Cost' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost'] * df['Inventory'], 2)
        
        return df
    except Exception as e:
        st.error(f"Error processing spirits data: {e}")
        return df


def process_uploaded_wine(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes an uploaded Wine inventory CSV.
    """
    try:
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Clean currency columns
        currency_columns = ['Cost', 'Bottle Price', 'BTG', 'Suggested Retail', 'Value']
        for col in currency_columns:
            df = clean_currency_column(df, col)
        
        # Clean percentage columns
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        
        # Clean numeric columns (excluding Margin which is handled above)
        numeric_columns = ['Size (oz.)', 'Inventory']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Recalculate Value
        if 'Cost' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost'] * df['Inventory'], 2)
        
        return df
    except Exception as e:
        st.error(f"Error processing wine data: {e}")
        return df


def process_uploaded_beer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes an uploaded Beer inventory CSV.
    """
    try:
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Clean currency columns
        currency_columns = ['Cost per Keg/Case', 'Menu Price', 'Cost/Unit', 'Value']
        for col in currency_columns:
            df = clean_currency_column(df, col)
        
        # Clean percentage columns
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        
        # Clean numeric columns (excluding Margin which is handled above)
        numeric_columns = ['Size', 'Inventory']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Recalculate derived fields
        if 'Cost per Keg/Case' in df.columns and 'Size' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost per Keg/Case'] / row['Size'], 2) if row['Size'] > 0 else 0, 
                axis=1
            )
        
        if 'Cost per Keg/Case' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost per Keg/Case'] * df['Inventory'], 2)
        
        return df
    except Exception as e:
        st.error(f"Error processing beer data: {e}")
        return df


def process_uploaded_ingredients(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processes an uploaded Ingredients inventory CSV.
    """
    try:
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Clean currency columns
        currency_columns = ['Cost', 'Cost/Unit']
        for col in currency_columns:
            df = clean_currency_column(df, col)
        
        # Clean numeric columns
        numeric_columns = ['Size/Yield']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Recalculate Cost/Unit
        if 'Cost' in df.columns and 'Size/Yield' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost'] / row['Size/Yield'], 2) if row['Size/Yield'] > 0 else 0, 
                axis=1
            )
        
        return df
    except Exception as e:
        st.error(f"Error processing ingredients data: {e}")
        return df


def calculate_total_value(df: pd.DataFrame) -> float:
    """
    Calculates total inventory value from a DataFrame.
    Handles edge cases like missing columns, NaN values, and string values.
    
    Args:
        df: DataFrame with potential 'Value' column
        
    Returns:
        float: Sum of the Value column, or 0.0 if not available
    """
    # Handle None or empty DataFrame
    if df is None:
        return 0.0
    
    try:
        if len(df) == 0:
            return 0.0
    except Exception:
        return 0.0
    
    if 'Value' not in df.columns:
        return 0.0
    
    try:
        # Get the Value column and clean it
        value_col = df['Value'].copy()
        
        # Apply currency cleaning to each value
        cleaned_values = value_col.apply(clean_currency_value)
        
        # Sum and return as float
        result = cleaned_values.sum()
        return float(result) if pd.notna(result) else 0.0
    except Exception:
        return 0.0


def format_currency(value: float) -> str:
    """
    Formats a number as USD currency.
    """
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def filter_dataframe(df: pd.DataFrame, search_term: str, column_filters: dict) -> pd.DataFrame:
    """
    Filters a DataFrame based on search term and column filters.
    """
    filtered_df = df.copy()
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Product'].str.contains(search_term, case=False, na=False)
        ]
    
    for column, values in column_filters.items():
        if values and column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column].isin(values)]
    
    return filtered_df


def generate_order_from_inventory(weekly_inv: pd.DataFrame) -> pd.DataFrame:
    """
    Generates an order list based on items below par level.
    V2.11: Updated to use Total Current Inventory (Bar + Storage)
    """
    # V2.11: Handle both old and new column names
    inventory_col = 'Total Current Inventory' if 'Total Current Inventory' in weekly_inv.columns else 'Current Inventory'
    
    # Ensure Total Current Inventory exists
    if 'Total Current Inventory' not in weekly_inv.columns:
        if 'Bar Inventory' in weekly_inv.columns and 'Storage Inventory' in weekly_inv.columns:
            weekly_inv['Total Current Inventory'] = weekly_inv['Bar Inventory'] + weekly_inv['Storage Inventory']
            inventory_col = 'Total Current Inventory'
    
    needs_order = weekly_inv[weekly_inv[inventory_col] < weekly_inv['Par']].copy()
    
    if len(needs_order) == 0:
        return pd.DataFrame()
    
    needs_order['Suggested Order'] = needs_order['Par'] - needs_order[inventory_col]
    needs_order['Order Quantity'] = needs_order['Suggested Order']
    needs_order['Order Value'] = needs_order['Order Quantity'] * needs_order['Unit Cost']
    
    # V2.11: Use Total Current Inventory in display
    needs_order['Current Inventory'] = needs_order[inventory_col]  # For display compatibility
    
    order_columns = ['Product', 'Category', 'Current Inventory', 'Par', 
                     'Suggested Order', 'Order Quantity', 'Unit', 'Unit Cost', 
                     'Order Value', 'Distributor', 'Order Notes']
    
    return needs_order[order_columns]


def get_ingredient_cost_per_unit(product_name: str) -> float:
    """
    Looks up the cost per unit for a product from inventory.
    Searches both Spirits (Cost/Oz) and Ingredients (Cost/Unit) inventories.
    
    Args:
        product_name: Name of the product to look up
        
    Returns:
        float: Cost per unit (oz for spirits, varies for ingredients)
    """
    try:
        # Check spirits inventory
        spirits = st.session_state.spirits_inventory
        spirit_match = spirits[spirits['Product'] == product_name]
        if len(spirit_match) > 0 and 'Cost/Oz' in spirit_match.columns:
            value = spirit_match['Cost/Oz'].values[0]
            return clean_currency_value(value)
        
        # Check ingredients inventory
        ingredients = st.session_state.ingredients_inventory
        ingredient_match = ingredients[ingredients['Product'] == product_name]
        if len(ingredient_match) > 0 and 'Cost/Unit' in ingredient_match.columns:
            value = ingredient_match['Cost/Unit'].values[0]
            return clean_currency_value(value)
    except Exception:
        pass
    
    return 0.0


def calculate_cocktail_cost(ingredients: list) -> float:
    """
    Calculates total cost for a cocktail based on ingredients.
    
    Args:
        ingredients: List of ingredient dicts with 'product', 'amount', 'unit'
        
    Returns:
        float: Total cost of ingredients
    """
    total = 0.0
    for ing in ingredients:
        unit_cost = get_ingredient_cost_per_unit(ing['product'])
        total += unit_cost * ing['amount']
    return total


def calculate_margin(cost: float, sale_price: float) -> float:
    """
    Calculates cost margin (cost / sale_price).
    
    Args:
        cost: Total cost of cocktail
        sale_price: Menu sale price
        
    Returns:
        float: Margin as decimal (e.g., 0.20 for 20%)
    """
    if sale_price > 0:
        return cost / sale_price
    return 0.0


def suggest_price_from_cost(cost: float, target_margin: float = 0.20) -> float:
    """
    Suggests a sale price based on target cost margin.
    
    Args:
        cost: Total cost of cocktail
        target_margin: Target cost percentage (default 20%)
        
    Returns:
        float: Suggested sale price
    """
    if target_margin > 0:
        return cost / target_margin
    return 0.0


def get_available_products():
    """
    Returns a combined list of all products from Spirits and Ingredients inventories.
    Used for ingredient selection in cocktail builder.
    
    Returns:
        list: Sorted list of product names
    """
    spirits = st.session_state.spirits_inventory['Product'].tolist()
    ingredients = st.session_state.ingredients_inventory['Product'].tolist()
    return sorted(list(set(spirits + ingredients)))


# =============================================================================
# WEEKLY ORDERING - MASTER INVENTORY PRODUCT LOOKUP (V2.3)
# =============================================================================

def get_master_inventory_products():
    """
    Returns a DataFrame of all products from Master Inventory (Spirits, Wine, Beer, Ingredients)
    with standardized columns for use in Weekly Inventory.
    
    This function pulls product details from the Master Inventory so that Weekly Inventory
    products are always sourced from the master list (not hardcoded).
    
    Returns:
        pd.DataFrame with columns: Product, Category, Unit Cost, Distributor, Source
    """
    all_products = []
    
    # Spirits
    if 'spirits_inventory' in st.session_state:
        spirits = st.session_state.spirits_inventory
        for _, row in spirits.iterrows():
            all_products.append({
                'Product': row['Product'],
                'Category': 'Spirits',
                'Unit Cost': clean_currency_value(row.get('Cost', 0)),
                'Distributor': row.get('Distributor', ''),
                'Order Notes': row.get('Order Notes', ''),
                'Source': 'Spirits'
            })
    
    # Wine
    if 'wine_inventory' in st.session_state:
        wine = st.session_state.wine_inventory
        for _, row in wine.iterrows():
            all_products.append({
                'Product': row['Product'],
                'Category': 'Wine',
                'Unit Cost': clean_currency_value(row.get('Cost', 0)),
                'Distributor': row.get('Distributor', ''),
                'Order Notes': '',  # Wine doesn't have Order Notes column
                'Source': 'Wine'
            })
    
    # Beer
    if 'beer_inventory' in st.session_state:
        beer = st.session_state.beer_inventory
        for _, row in beer.iterrows():
            all_products.append({
                'Product': row['Product'],
                'Category': 'Beer',
                'Unit Cost': clean_currency_value(row.get('Cost per Keg/Case', 0)),
                'Distributor': row.get('Distributor', ''),
                'Order Notes': row.get('Order Notes', ''),
                'Source': 'Beer'
            })
    
    # Ingredients
    if 'ingredients_inventory' in st.session_state:
        ingredients = st.session_state.ingredients_inventory
        for _, row in ingredients.iterrows():
            all_products.append({
                'Product': row['Product'],
                'Category': 'Ingredients',
                'Unit Cost': clean_currency_value(row.get('Cost', 0)),
                'Distributor': row.get('Distributor', ''),
                'Order Notes': row.get('Order Notes', ''),
                'Source': 'Ingredients'
            })
    
    return pd.DataFrame(all_products)


def get_products_not_in_weekly_inventory():
    """
    Returns a list of products from Master Inventory that are NOT already 
    in the Weekly Inventory. Used to populate the "Add Product" dropdown.
    
    Returns:
        pd.DataFrame: Products available to add (not already in weekly inventory)
    """
    # Get all master inventory products
    master_products = get_master_inventory_products()
    
    if master_products.empty:
        return pd.DataFrame()
    
    # Get current weekly inventory product names
    weekly_products = []
    if 'weekly_inventory' in st.session_state:
        weekly_products = st.session_state.weekly_inventory['Product'].tolist()
    
    # Filter to products not already in weekly inventory
    available = master_products[~master_products['Product'].isin(weekly_products)]
    
    return available


# =============================================================================
# PAGE: HOMESCREEN
# =============================================================================

def show_home():
    """
    Renders the homescreen with navigation cards.
    """
    
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Beverage Management App V2.22</h1>
        <p>Manage your inventory, orders, and cocktail recipes in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="module-card card-inventory">
            <div class="card-icon">📦</div>
            <div class="card-title">Master Inventory</div>
            <div class="card-description">
                Track spirits, wine, beer, and ingredients.<br>
                View values, costs, and stock levels.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Inventory", key="btn_inventory", use_container_width=True):
            navigate_to('inventory')
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="module-card card-ordering">
            <div class="card-icon">📋</div>
            <div class="card-title">Weekly Order Builder</div>
            <div class="card-description">
                Build weekly orders based on par levels.<br>
                Track order history and spending.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Ordering", key="btn_ordering", use_container_width=True):
            navigate_to('ordering')
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="module-card card-cocktails">
            <div class="card-icon">🍹</div>
            <div class="card-title">Cocktail Builds Book</div>
            <div class="card-description">
                Store and cost cocktail recipes.<br>
                Calculate margins and pricing.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Cocktails", key="btn_cocktails", use_container_width=True):
            navigate_to('cocktails')
            st.rerun()
    
    st.markdown("---")
    
    # Show Google Sheets connection status
    if is_google_sheets_configured():
        st.success("✅ Connected to Google Sheets - Data will persist permanently")
    else:
        st.warning("⚠️ Google Sheets not configured - Data will reset on app restart. See setup instructions in secrets_template.toml")
    
    st.markdown(
        "<p style='text-align: center; color: #888;'>Canter Inn • Madison, WI</p>",
        unsafe_allow_html=True
    )


# =============================================================================
# PAGE: MASTER INVENTORY
# =============================================================================

def show_inventory():
    """
    Renders the Master Inventory module.
    """
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📦 Master Inventory")
    
    # Dashboard metrics
    st.markdown("### 📊 Inventory Dashboard")
    
    # Calculate values with defensive error handling
    try:
        spirits_value = float(calculate_total_value(st.session_state.spirits_inventory) or 0)
    except Exception:
        spirits_value = 0.0
    
    try:
        wine_value = float(calculate_total_value(st.session_state.wine_inventory) or 0)
    except Exception:
        wine_value = 0.0
    
    try:
        beer_value = float(calculate_total_value(st.session_state.beer_inventory) or 0)
    except Exception:
        beer_value = 0.0
    
    try:
        ingredients_value = float(calculate_total_value(st.session_state.ingredients_inventory) or 0)
    except Exception:
        ingredients_value = 0.0
    
    total_value = spirits_value + wine_value + beer_value + ingredients_value
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="🥃 Spirits", value=format_currency(spirits_value))
    with col2:
        st.metric(label="🍷 Wine", value=format_currency(wine_value))
    with col3:
        st.metric(label="🍺 Beer", value=format_currency(beer_value))
    with col4:
        st.metric(label="🧴 Ingredients", value=format_currency(ingredients_value))
    with col5:
        st.metric(label="💰 Total Value", value=format_currency(total_value))
    
    st.caption(f"Last inventory recorded: {st.session_state.last_inventory_date}")
    
    st.markdown("---")
    
    # Tabbed inventory views
    tab_spirits, tab_wine, tab_beer, tab_ingredients = st.tabs([
        "🥃 Spirits", "🍷 Wine", "🍺 Beer", "🧴 Ingredients"
    ])
    
    with tab_spirits:
        show_inventory_tab(
            df=st.session_state.spirits_inventory,
            category="spirits",
            filter_columns=["Type", "Distributor", "Use"],
            display_name="Spirits"
        )
    
    with tab_wine:
        show_inventory_tab(
            df=st.session_state.wine_inventory,
            category="wine",
            filter_columns=["Type", "Distributor"],
            display_name="Wine"
        )
    
    with tab_beer:
        show_inventory_tab(
            df=st.session_state.beer_inventory,
            category="beer",
            filter_columns=["Type", "Distributor"],
            display_name="Beer"
        )
    
    with tab_ingredients:
        show_inventory_tab(
            df=st.session_state.ingredients_inventory,
            category="ingredients",
            filter_columns=["Distributor"],
            display_name="Ingredients"
        )
    
    st.markdown("---")
    
    # Historical Comparison Section with COGS Calculation (moved below inventory tabs)
    with st.expander("📈 Historical Value Comparison & COGS", expanded=False):
        history = load_inventory_history()
        
        if history is not None and len(history) > 0:
            # Get list of dates for dropdown
            available_dates = history['Date'].unique().tolist()
            
            if len(available_dates) >= 1:
                st.markdown("**Select inventory periods to compare:**")
                
                # Two columns for date selection
                date_col1, date_col2 = st.columns(2)
                
                with date_col1:
                    # Default to oldest date for starting inventory
                    start_date = st.selectbox(
                        "Starting Inventory Date:",
                        options=available_dates,
                        index=len(available_dates) - 1 if len(available_dates) > 1 else 0,
                        key="history_start_date",
                        help="Select the beginning period for comparison"
                    )
                
                with date_col2:
                    # Default to most recent date for ending inventory
                    end_date = st.selectbox(
                        "Ending Inventory Date:",
                        options=available_dates,
                        index=0,
                        key="history_end_date",
                        help="Select the ending period for comparison"
                    )
                
                # Get values for selected dates
                start_row = history[history['Date'] == start_date].iloc[0]
                end_row = history[history['Date'] == end_date].iloc[0]
                
                start_spirits = float(start_row.get('Spirits Value', 0))
                start_wine = float(start_row.get('Wine Value', 0))
                start_beer = float(start_row.get('Beer Value', 0))
                start_ingredients = float(start_row.get('Ingredients Value', 0))
                start_total = float(start_row.get('Total Value', 0))
                
                end_spirits = float(end_row.get('Spirits Value', 0))
                end_wine = float(end_row.get('Wine Value', 0))
                end_beer = float(end_row.get('Beer Value', 0))
                end_ingredients = float(end_row.get('Ingredients Value', 0))
                end_total = float(end_row.get('Total Value', 0))
                
                # Calculate differences
                delta_spirits = end_spirits - start_spirits
                delta_wine = end_wine - start_wine
                delta_beer = end_beer - start_beer
                delta_ingredients = end_ingredients - start_ingredients
                delta_total = end_total - start_total
                
                st.markdown("---")
                st.markdown("**Enter purchases for the period:**")
                
                # Purchase input fields
                purch_col1, purch_col2, purch_col3, purch_col4 = st.columns(4)
                
                with purch_col1:
                    purchase_spirits = st.number_input(
                        "🥃 Spirits Purchases",
                        min_value=0.0,
                        value=0.0,
                        step=100.0,
                        format="%.2f",
                        key="purchase_spirits"
                    )
                
                with purch_col2:
                    purchase_wine = st.number_input(
                        "🍷 Wine Purchases",
                        min_value=0.0,
                        value=0.0,
                        step=100.0,
                        format="%.2f",
                        key="purchase_wine"
                    )
                
                with purch_col3:
                    purchase_beer = st.number_input(
                        "🍺 Beer Purchases",
                        min_value=0.0,
                        value=0.0,
                        step=100.0,
                        format="%.2f",
                        key="purchase_beer"
                    )
                
                with purch_col4:
                    purchase_ingredients = st.number_input(
                        "🧴 Ingredients Purchases",
                        min_value=0.0,
                        value=0.0,
                        step=100.0,
                        format="%.2f",
                        key="purchase_ingredients"
                    )
                
                total_purchases = purchase_spirits + purchase_wine + purchase_beer + purchase_ingredients
                
                # Calculate COGS: (Starting Inventory + Purchases) - Ending Inventory
                cogs_spirits = (start_spirits + purchase_spirits) - end_spirits
                cogs_wine = (start_wine + purchase_wine) - end_wine
                cogs_beer = (start_beer + purchase_beer) - end_beer
                cogs_ingredients = (start_ingredients + purchase_ingredients) - end_ingredients
                cogs_total = (start_total + total_purchases) - end_total
                
                st.markdown("---")
                
                # Helper function to format difference with color
                def format_difference(delta):
                    if delta < 0:
                        return f'<span style="color: #ff4b4b; font-weight: 600;">{format_currency(delta)}</span>'
                    elif delta > 0:
                        return f'<span style="color: #21c354; font-weight: 600;">+{format_currency(delta)}</span>'
                    else:
                        return f'<span style="color: #808080;">{format_currency(delta)}</span>'
                
                # Create comparison table with Starting, Ending, Difference, Purchases, and COGS
                comparison_data = f"""
                <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                    <thead>
                        <tr style="border-bottom: 2px solid #ddd; text-align: left;">
                            <th style="padding: 12px 8px; font-size: 15px;">Category</th>
                            <th style="padding: 12px 8px; font-size: 15px; text-align: right;">Starting<br/>({start_date})</th>
                            <th style="padding: 12px 8px; font-size: 15px; text-align: right;">Ending<br/>({end_date})</th>
                            <th style="padding: 12px 8px; font-size: 15px; text-align: right;">Difference</th>
                            <th style="padding: 12px 8px; font-size: 15px; text-align: right;">Purchases</th>
                            <th style="padding: 12px 8px; font-size: 15px; text-align: right;">COGS</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px 8px; font-size: 14px;">🥃 Spirits</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(start_spirits)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(end_spirits)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_difference(delta_spirits)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(purchase_spirits)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right; font-weight: 600;">{format_currency(cogs_spirits)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px 8px; font-size: 14px;">🍷 Wine</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(start_wine)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(end_wine)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_difference(delta_wine)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(purchase_wine)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right; font-weight: 600;">{format_currency(cogs_wine)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px 8px; font-size: 14px;">🍺 Beer</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(start_beer)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(end_beer)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_difference(delta_beer)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(purchase_beer)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right; font-weight: 600;">{format_currency(cogs_beer)}</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #eee;">
                            <td style="padding: 12px 8px; font-size: 14px;">🧴 Ingredients</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(start_ingredients)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(end_ingredients)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_difference(delta_ingredients)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right;">{format_currency(purchase_ingredients)}</td>
                            <td style="padding: 12px 8px; font-size: 14px; text-align: right; font-weight: 600;">{format_currency(cogs_ingredients)}</td>
                        </tr>
                        <tr style="border-top: 2px solid #ddd; background-color: #f8f9fa;">
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700;">💰 Total</td>
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700; text-align: right;">{format_currency(start_total)}</td>
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700; text-align: right;">{format_currency(end_total)}</td>
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700; text-align: right;">{format_difference(delta_total)}</td>
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700; text-align: right;">{format_currency(total_purchases)}</td>
                            <td style="padding: 12px 8px; font-size: 15px; font-weight: 700; text-align: right;">{format_currency(cogs_total)}</td>
                        </tr>
                    </tbody>
                </table>
                """
                
                st.markdown(comparison_data, unsafe_allow_html=True)
                
                # COGS formula explanation
                st.caption("**COGS Formula:** (Starting Inventory + Purchases) − Ending Inventory")
                
                # Show historical values table
                st.markdown("---")
                st.markdown("**Historical Inventory Values:**")
                
                # Format history for display
                display_history = history.copy()
                for col in ['Spirits Value', 'Wine Value', 'Beer Value', 'Ingredients Value', 'Total Value']:
                    if col in display_history.columns:
                        display_history[col] = display_history[col].apply(lambda x: format_currency(x))
                
                st.dataframe(
                    display_history,
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No historical data available yet. Save inventory changes to start tracking history.")
        else:
            st.info("📊 No historical data available yet. Save inventory changes to start tracking value history.")
    
    st.markdown("---")
    
    # CSV Upload (moved to bottom of page)
    with st.expander("📤 Upload Inventory Data (CSV)", expanded=False):
        st.markdown("""
        Upload a CSV file to replace inventory data for any category.
        The CSV should have matching column headers. Currency formatting (e.g., "$30.80") 
        will be automatically cleaned, and calculated fields will be recalculated.
        """)
        
        upload_category = st.selectbox(
            "Select category to upload:",
            ["Spirits", "Wine", "Beer", "Ingredients"],
            key="upload_category"
        )
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data (raw):")
                st.dataframe(new_data.head())
                
                # Show expected columns for the selected category
                expected_cols = {
                    "Spirits": ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Neat Price", 
                               "Inventory", "Use", "Distributor", "Order Notes", "Suggested Retail"],
                    "Wine": ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Bottle Price",
                            "Inventory", "Distributor", "BTG", "Suggested Retail"],
                    "Beer": ["Product", "Type", "Cost per Keg/Case", "Size", "UoM", "Margin",
                            "Menu Price", "Inventory", "Distributor", "Order Notes"],
                    "Ingredients": ["Product", "Cost", "Size/Yield", "UoM", "Distributor", "Order Notes"]
                }
                
                st.caption(f"Expected columns for {upload_category}: {', '.join(expected_cols[upload_category])}")
                
                if st.button("✅ Confirm Upload", key="confirm_upload"):
                    # Process the data based on category
                    if upload_category == "Spirits":
                        processed_data = process_uploaded_spirits(new_data)
                        st.session_state.spirits_inventory = processed_data
                    elif upload_category == "Wine":
                        processed_data = process_uploaded_wine(new_data)
                        st.session_state.wine_inventory = processed_data
                    elif upload_category == "Beer":
                        processed_data = process_uploaded_beer(new_data)
                        st.session_state.beer_inventory = processed_data
                    elif upload_category == "Ingredients":
                        processed_data = process_uploaded_ingredients(new_data)
                        st.session_state.ingredients_inventory = processed_data
                    
                    st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
                    
                    # Save all inventory data to files for persistence
                    save_all_inventory_data()
                    
                    st.success(f"✅ {upload_category} inventory uploaded and saved successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def show_inventory_tab(df: pd.DataFrame, category: str, filter_columns: list, display_name: str):
    """
    Renders an inventory tab with search, filter, and editing.
    Calculated fields are locked from manual editing.
    """
    
    st.markdown(f"#### Search & Filter {display_name}")
    
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input(
            "🔍 Search by Product",
            key=f"search_{category}",
            placeholder="Type to search..."
        )
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(
                    f"Filter by {col_name}",
                    options=unique_values,
                    key=f"filter_{category}_{col_name}"
                )
                if selected:
                    column_filters[col_name] = selected
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    st.markdown(f"#### {display_name} Inventory")
    
    # Define which columns are calculated (locked) vs editable for each category
    if category == "spirits":
        disabled_columns = ["Cost/Oz", "Value"]  # Calculated fields
    elif category == "wine":
        disabled_columns = ["Value"]  # Calculated field
    elif category == "beer":
        disabled_columns = ["Cost/Unit", "Value"]  # Calculated fields
    elif category == "ingredients":
        disabled_columns = ["Cost/Unit"]  # Calculated field
    else:
        disabled_columns = []
    
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
        key=f"editor_{category}",
        disabled=disabled_columns,  # Lock calculated columns
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Cost/Oz": st.column_config.NumberColumn(
                format="$%.2f", 
                help="🔒 Calculated: Cost ÷ Size (oz.)",
                disabled=True
            ),
            "Cost/Unit": st.column_config.NumberColumn(
                format="$%.2f",
                help="🔒 Calculated automatically",
                disabled=True
            ),
            "Value": st.column_config.NumberColumn(
                format="$%.2f",
                help="🔒 Calculated: Cost × Inventory",
                disabled=True
            ),
            "Neat Price": st.column_config.NumberColumn(format="$%.2f"),
            "Bottle Price": st.column_config.NumberColumn(format="$%.2f"),
            "Menu Price": st.column_config.NumberColumn(format="$%.2f"),
            "BTG": st.column_config.NumberColumn(format="$%.2f"),
            "Margin": st.column_config.NumberColumn(format="%.0f%%", help="Cost margin as percentage"),
            "Cost per Keg/Case": st.column_config.NumberColumn(format="$%.2f"),
            "Suggested Retail": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    col_save, col_spacer = st.columns([1, 5])
    
    with col_save:
        if st.button(f"💾 Save Changes", key=f"save_{category}"):
            # Recalculate derived fields before saving
            if category == "spirits":
                if "Cost" in edited_df.columns and "Size (oz.)" in edited_df.columns:
                    edited_df["Cost/Oz"] = edited_df.apply(
                        lambda row: round(row['Cost'] / row['Size (oz.)'], 2) if row['Size (oz.)'] > 0 else 0, 
                        axis=1
                    )
                if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = round(edited_df["Cost"] * edited_df["Inventory"], 2)
                st.session_state.spirits_inventory = edited_df
            elif category == "wine":
                if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = round(edited_df["Cost"] * edited_df["Inventory"], 2)
                st.session_state.wine_inventory = edited_df
            elif category == "beer":
                if "Cost per Keg/Case" in edited_df.columns and "Size" in edited_df.columns:
                    edited_df["Cost/Unit"] = edited_df.apply(
                        lambda row: round(row['Cost per Keg/Case'] / row['Size'], 2) if row['Size'] > 0 else 0, 
                        axis=1
                    )
                if "Cost per Keg/Case" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = round(edited_df["Cost per Keg/Case"] * edited_df["Inventory"], 2)
                st.session_state.beer_inventory = edited_df
            elif category == "ingredients":
                if "Cost" in edited_df.columns and "Size/Yield" in edited_df.columns:
                    edited_df["Cost/Unit"] = edited_df.apply(
                        lambda row: round(row['Cost'] / row['Size/Yield'], 2) if row['Size/Yield'] > 0 else 0, 
                        axis=1
                    )
                st.session_state.ingredients_inventory = edited_df
            
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            
            # Save to files for persistence
            save_all_inventory_data()
            
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# PAGE: WEEKLY ORDER BUILDER
# =============================================================================

def show_ordering():
    """
    Renders the Weekly Order Builder module.
    """
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📋 Weekly Order Builder")
    
    # Dashboard
    st.markdown("### 📊 Order Dashboard")
    
    order_history = st.session_state.order_history
    
    if len(order_history) > 0:
        weeks = sorted(order_history['Week'].unique())
        if len(weeks) >= 1:
            prev_week = weeks[-1]
            prev_week_total = order_history[order_history['Week'] == prev_week]['Total Cost'].sum()
        else:
            prev_week_total = 0
    else:
        prev_week_total = 0
    
    if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
        current_order_total = st.session_state.current_order['Order Value'].sum()
    else:
        current_order_total = 0
    
    # V2.10: Check for pending verification
    pending_verification_total = 0
    if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
        pending_verification_total = st.session_state.pending_order['Order Value'].sum() if 'Order Value' in st.session_state.pending_order.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📅 Previous Week's Order", value=format_currency(prev_week_total))
    with col2:
        st.metric(label="🛒 Current Order (Building)", value=format_currency(current_order_total))
    with col3:
        if pending_verification_total > 0:
            st.metric(label="⏳ Pending Verification", value=format_currency(pending_verification_total))
        else:
            st.metric(label="⏳ Pending Verification", value="None")
    with col4:
        st.metric(label="📈 6-Week Avg Order", 
                  value=format_currency(order_history.groupby('Week')['Total Cost'].sum().mean() if len(order_history) > 0 else 0))
    
    st.markdown("---")
    
    # Tabs
    tab_build, tab_history, tab_analytics = st.tabs([
        "🛒 Weekly Order Builder", "📜 Order History", "📈 Order Analytics"
    ])
    
    with tab_build:
        st.markdown("### Step 1: Update Weekly Inventory")
        st.markdown("Enter your current inventory counts below. Products below par will be added to the order.")
        
        # =====================================================================
        # V2.3: ADD/REMOVE PRODUCTS FROM WEEKLY INVENTORY
        # =====================================================================
        
        with st.expander("➕ Add Products to your Weekly Order Inventory", expanded=False):
            st.markdown("**Add a product from Master Inventory:**")
            
            # Get products not already in weekly inventory
            available_products = get_products_not_in_weekly_inventory()
            
            if len(available_products) > 0:
                # V2.9: Category filter for Add Product dropdown
                add_categories = sorted(available_products['Category'].unique().tolist())
                
                col_cat_filter, col_spacer = st.columns([2, 4])
                with col_cat_filter:
                    add_category_filter = st.selectbox(
                        "🔍 Filter by Category:",
                        options=["All Categories"] + add_categories,
                        key="add_product_category_filter"
                    )
                
                # Filter available products by selected category
                if add_category_filter != "All Categories":
                    filtered_available = available_products[available_products['Category'] == add_category_filter].copy()
                else:
                    filtered_available = available_products.copy()
                
                if len(filtered_available) > 0:
                    col_select, col_par, col_unit, col_add = st.columns([3, 1, 1, 1])
                    
                    with col_select:
                        # Create display options with category
                        filtered_available['Display'] = filtered_available['Product'] + " (" + filtered_available['Category'] + ")"
                        product_options = filtered_available['Display'].tolist()
                        
                        selected_display = st.selectbox(
                            "Select Product:",
                            options=[""] + product_options,
                            key="add_weekly_product"
                        )
                    
                    with col_par:
                        new_par = st.number_input(
                            "Par Level:",
                            min_value=1,
                            value=2,
                            step=1,
                            key="add_weekly_par"
                        )
                    
                    with col_unit:
                        unit_options = ["Bottle", "Case", "Sixtel", "Keg", "Each", "Quart", "Gallon"]
                        new_unit = st.selectbox(
                            "Unit:",
                            options=unit_options,
                            key="add_weekly_unit"
                        )
                    
                    with col_add:
                        st.write("")  # Spacer
                        st.write("")  # Spacer
                        if st.button("➕ Add", key="btn_add_weekly_product"):
                            if selected_display:
                                # Get the product details from filtered_available
                                selected_row = filtered_available[filtered_available['Display'] == selected_display].iloc[0]
                                
                                # Create new row for weekly inventory
                                # V2.11: Include Bar/Storage Inventory columns
                                new_row = pd.DataFrame([{
                                    'Product': selected_row['Product'],
                                    'Category': selected_row['Category'],
                                    'Par': new_par,
                                    'Bar Inventory': 0,
                                    'Storage Inventory': 0,
                                    'Total Current Inventory': 0,
                                    'Unit': new_unit,
                                    'Unit Cost': selected_row['Unit Cost'],
                                    'Distributor': selected_row['Distributor'],
                                    'Order Notes': selected_row['Order Notes']
                                }])
                                
                                # Add to weekly inventory
                                st.session_state.weekly_inventory = pd.concat(
                                    [st.session_state.weekly_inventory, new_row],
                                    ignore_index=True
                                )
                                
                                # Save changes
                                save_all_inventory_data()
                                
                                st.success(f"✅ Added {selected_row['Product']} to Weekly Inventory!")
                                st.rerun()
                            else:
                                st.warning("Please select a product to add.")
                else:
                    st.info(f"No products available in {add_category_filter} category.")
            else:
                st.info("All Master Inventory products are already in Weekly Inventory.")
            
            # =================================================================
            # V2.12: CSV UPLOAD FOR WEEKLY INVENTORY
            # =================================================================
            st.markdown("---")
            st.markdown("**📤 Upload CSV to populate Weekly Inventory:**")
            
            with st.expander("ℹ️ CSV Format Requirements", expanded=False):
                st.markdown("""
                Your CSV file should include the following columns:
                
                | Column | Required | Description |
                |--------|----------|-------------|
                | Product | ✅ Yes | Product name |
                | Category | ✅ Yes | Spirits, Wine, Beer, or Ingredients |
                | Par | ✅ Yes | Par level (number) |
                | Bar Inventory | Optional | Inventory at bar (default: 0) |
                | Storage Inventory | Optional | Inventory in storage (default: 0) |
                | Unit | Optional | Bottle, Case, Sixtel, Keg, Each, Quart, Gallon (default: Bottle) |
                | Unit Cost | Optional | Cost per unit (default: 0) |
                | Distributor | Optional | Distributor name (default: blank) |
                | Order Notes | Optional | Notes for ordering (default: blank) |
                
                **Note:** Products already in Weekly Inventory will be skipped.
                """)
                
                # Download template button
                template_df = pd.DataFrame({
                    'Product': ['Example Product 1', 'Example Product 2'],
                    'Category': ['Spirits', 'Beer'],
                    'Par': [3, 2],
                    'Bar Inventory': [1, 0.5],
                    'Storage Inventory': [1, 0.5],
                    'Unit': ['Bottle', 'Case'],
                    'Unit Cost': [25.00, 24.00],
                    'Distributor': ['Breakthru', 'Frank Beer'],
                    'Order Notes': ['', '']
                })
                
                csv_template = template_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV Template",
                    data=csv_template,
                    file_name="weekly_inventory_template.csv",
                    mime="text/csv",
                    key="download_weekly_template"
                )
            
            uploaded_csv = st.file_uploader(
                "Choose a CSV file:",
                type=['csv'],
                key="weekly_inventory_csv_upload"
            )
            
            if uploaded_csv is not None:
                try:
                    # Read CSV
                    upload_df = pd.read_csv(uploaded_csv)
                    
                    # Validate required columns
                    required_cols = ['Product', 'Category', 'Par']
                    missing_cols = [col for col in required_cols if col not in upload_df.columns]
                    
                    if missing_cols:
                        st.error(f"❌ Missing required columns: {', '.join(missing_cols)}")
                    else:
                        # Preview the data
                        st.markdown(f"**Preview ({len(upload_df)} products):**")
                        st.dataframe(upload_df.head(10), use_container_width=True, hide_index=True)
                        
                        # Check for duplicates with existing inventory
                        existing_products = st.session_state.weekly_inventory['Product'].tolist()
                        new_products = upload_df[~upload_df['Product'].isin(existing_products)]
                        duplicate_products = upload_df[upload_df['Product'].isin(existing_products)]
                        
                        if len(duplicate_products) > 0:
                            st.warning(f"⚠️ {len(duplicate_products)} product(s) already exist and will be skipped: {', '.join(duplicate_products['Product'].tolist()[:5])}{'...' if len(duplicate_products) > 5 else ''}")
                        
                        if len(new_products) > 0:
                            col_upload_btn, col_upload_info = st.columns([1, 2])
                            
                            with col_upload_btn:
                                if st.button(f"✅ Import {len(new_products)} Product(s)", key="btn_import_csv", type="primary"):
                                    # Prepare the data with all required columns
                                    import_df = new_products.copy()
                                    
                                    # Add default values for optional columns
                                    if 'Bar Inventory' not in import_df.columns:
                                        import_df['Bar Inventory'] = 0
                                    if 'Storage Inventory' not in import_df.columns:
                                        import_df['Storage Inventory'] = 0
                                    if 'Unit' not in import_df.columns:
                                        import_df['Unit'] = 'Bottle'
                                    if 'Unit Cost' not in import_df.columns:
                                        import_df['Unit Cost'] = 0
                                    else:
                                        # Clean currency values
                                        import_df['Unit Cost'] = import_df['Unit Cost'].apply(clean_currency_value)
                                    if 'Distributor' not in import_df.columns:
                                        import_df['Distributor'] = ''
                                    if 'Order Notes' not in import_df.columns:
                                        import_df['Order Notes'] = ''
                                    
                                    # Calculate Total Current Inventory
                                    import_df['Total Current Inventory'] = import_df['Bar Inventory'] + import_df['Storage Inventory']
                                    
                                    # Ensure numeric columns are proper types
                                    import_df['Par'] = pd.to_numeric(import_df['Par'], errors='coerce').fillna(0)
                                    import_df['Bar Inventory'] = pd.to_numeric(import_df['Bar Inventory'], errors='coerce').fillna(0)
                                    import_df['Storage Inventory'] = pd.to_numeric(import_df['Storage Inventory'], errors='coerce').fillna(0)
                                    import_df['Unit Cost'] = pd.to_numeric(import_df['Unit Cost'], errors='coerce').fillna(0)
                                    
                                    # Select and order columns to match existing structure
                                    cols_to_keep = ['Product', 'Category', 'Par', 'Bar Inventory', 'Storage Inventory', 
                                                   'Total Current Inventory', 'Unit', 'Unit Cost', 'Distributor', 'Order Notes']
                                    import_df = import_df[cols_to_keep]
                                    
                                    # Append to weekly inventory
                                    st.session_state.weekly_inventory = pd.concat(
                                        [st.session_state.weekly_inventory, import_df],
                                        ignore_index=True
                                    )
                                    
                                    # Save changes
                                    save_all_inventory_data()
                                    
                                    st.success(f"✅ Successfully imported {len(new_products)} product(s)!")
                                    st.rerun()
                            
                            with col_upload_info:
                                st.caption(f"Ready to import {len(new_products)} new product(s)")
                        else:
                            st.info("All products in the CSV already exist in Weekly Inventory.")
                
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {str(e)}")
        
        # =====================================================================
        # END V2.3 ADD/REMOVE SECTION
        # =====================================================================
        
        # =====================================================================
        # V2.6: CATEGORY AND DISTRIBUTOR FILTERS FOR WEEKLY INVENTORY
        # V2.11: Added Bar/Storage Inventory columns with auto-calculated total
        # =====================================================================
        
        weekly_inv = st.session_state.weekly_inventory.copy()
        
        # V2.11: Ensure Bar/Storage Inventory columns exist (backwards compatibility)
        if 'Bar Inventory' not in weekly_inv.columns:
            # Migrate from old Current Inventory column
            if 'Current Inventory' in weekly_inv.columns:
                weekly_inv['Bar Inventory'] = weekly_inv['Current Inventory'] / 2
                weekly_inv['Storage Inventory'] = weekly_inv['Current Inventory'] / 2
            else:
                weekly_inv['Bar Inventory'] = 0
                weekly_inv['Storage Inventory'] = 0
        
        if 'Storage Inventory' not in weekly_inv.columns:
            weekly_inv['Storage Inventory'] = 0
        
        # V2.11: Calculate Total Current Inventory
        weekly_inv['Total Current Inventory'] = weekly_inv['Bar Inventory'] + weekly_inv['Storage Inventory']
        
        # Status based on Total Current Inventory vs Par
        weekly_inv['Status'] = weekly_inv.apply(
            lambda row: "🔴 Order" if row['Total Current Inventory'] < row['Par'] else "✅ OK", axis=1
        )
        
        # Get unique categories and distributors for filters
        all_categories = weekly_inv['Category'].unique().tolist()
        all_distributors = weekly_inv['Distributor'].unique().tolist()
        
        # Filter row
        col_cat_filter, col_dist_filter, col_count = st.columns([2, 2, 2])
        
        with col_cat_filter:
            selected_category = st.selectbox(
                "🔍 Filter by Category:",
                options=["All Categories"] + sorted(all_categories),
                key="weekly_category_filter"
            )
        
        with col_dist_filter:
            selected_distributor = st.selectbox(
                "🚚 Filter by Distributor:",
                options=["All Distributors"] + sorted(all_distributors),
                key="weekly_distributor_filter"
            )
        
        # Apply filters
        filtered_weekly_inv = weekly_inv.copy()
        
        if selected_category != "All Categories":
            filtered_weekly_inv = filtered_weekly_inv[filtered_weekly_inv['Category'] == selected_category]
        
        if selected_distributor != "All Distributors":
            filtered_weekly_inv = filtered_weekly_inv[filtered_weekly_inv['Distributor'] == selected_distributor]
        
        with col_count:
            st.write("")  # Spacer to align with dropdowns
            st.caption(f"Showing {len(filtered_weekly_inv)} of {len(weekly_inv)} products")
        
        # =====================================================================
        # END V2.6 FILTERS
        # =====================================================================
        
        # V2.11: Updated display columns with Bar/Storage/Total
        # V2.12: Added Select column for row deletion
        display_df = filtered_weekly_inv.copy()
        display_df.insert(0, 'Select', False)  # Add checkbox column at the beginning
        
        display_cols = ['Select', 'Product', 'Category', 'Par', 'Bar Inventory', 'Storage Inventory', 
                       'Total Current Inventory', 'Status', 'Unit', 'Unit Cost', 'Distributor', 'Order Notes']
        
        edited_weekly = st.data_editor(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            key="weekly_inv_editor",
            column_config={
                "Select": st.column_config.CheckboxColumn("🗑️", help="Select rows to delete", width="small"),
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Bar Inventory": st.column_config.NumberColumn("🍸 Bar", min_value=0, step=0.5),
                "Storage Inventory": st.column_config.NumberColumn("📦 Storage", min_value=0, step=0.5),
                "Total Current Inventory": st.column_config.NumberColumn("Total", disabled=True),
                "Par": st.column_config.NumberColumn(min_value=0, step=1),
                "Status": st.column_config.TextColumn(disabled=True),
                "Order Notes": st.column_config.TextColumn("Order Deals", disabled=True),
            },
            disabled=["Product", "Category", "Status", "Total Current Inventory", "Unit", "Unit Cost", "Distributor", "Order Notes"]
        )
        
        # V2.11: Recalculate Total Current Inventory in real-time from edited values
        edited_weekly['Total Current Inventory'] = edited_weekly['Bar Inventory'] + edited_weekly['Storage Inventory']
        edited_weekly['Status'] = edited_weekly.apply(
            lambda row: "🔴 Order" if row['Total Current Inventory'] < row['Par'] else "✅ OK", axis=1
        )
        
        # V2.12: Check for selected rows to delete
        selected_for_deletion = edited_weekly[edited_weekly['Select'] == True]['Product'].tolist()
        
        # V2.6: Action buttons - Save, Generate Order, and Delete
        col_save, col_update, col_delete, col_spacer = st.columns([1, 1, 1, 3])
        
        with col_save:
            if st.button("💾 Update Table", key="save_weekly_only", help="Save inventory changes without generating an order"):
                # Update values only for products that were displayed (filtered view)
                for idx, row in edited_weekly.iterrows():
                    mask = st.session_state.weekly_inventory['Product'] == row['Product']
                    st.session_state.weekly_inventory.loc[mask, 'Bar Inventory'] = row['Bar Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Storage Inventory'] = row['Storage Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Total Current Inventory'] = row['Bar Inventory'] + row['Storage Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Par'] = row['Par']
                
                # Save weekly inventory to Google Sheets for persistence
                save_all_inventory_data()
                
                st.success("✅ Table updated!")
                st.rerun()
        
        with col_update:
            if st.button("🔄 Generate Orders", key="update_weekly"):
                # Update values only for products that were displayed (filtered view)
                for idx, row in edited_weekly.iterrows():
                    mask = st.session_state.weekly_inventory['Product'] == row['Product']
                    st.session_state.weekly_inventory.loc[mask, 'Bar Inventory'] = row['Bar Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Storage Inventory'] = row['Storage Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Total Current Inventory'] = row['Bar Inventory'] + row['Storage Inventory']
                    st.session_state.weekly_inventory.loc[mask, 'Par'] = row['Par']
                
                order = generate_order_from_inventory(st.session_state.weekly_inventory)
                st.session_state.current_order = order
                
                # Save weekly inventory to files for persistence
                save_all_inventory_data()
                
                st.success("✅ Orders generated!")
                st.rerun()
        
        with col_delete:
            delete_disabled = len(selected_for_deletion) == 0
            if st.button("🗑️ Delete Selected", key="delete_selected_rows", disabled=delete_disabled, 
                        help="Select rows using checkboxes, then click to delete"):
                if selected_for_deletion:
                    st.session_state.weekly_inventory = st.session_state.weekly_inventory[
                        ~st.session_state.weekly_inventory['Product'].isin(selected_for_deletion)
                    ].reset_index(drop=True)
                    
                    save_all_inventory_data()
                    st.success(f"✅ Deleted {len(selected_for_deletion)} product(s)!")
                    st.rerun()
        
        # Show count of selected items
        if len(selected_for_deletion) > 0:
            st.caption(f"🗑️ {len(selected_for_deletion)} row(s) selected for deletion")
        
        st.markdown("---")
        st.markdown("### Step 2: Review & Adjust This Week's Order")
        
        if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
            order_df = st.session_state.current_order.copy()
            st.markdown(f"**{len(order_df)} items need ordering:**")
            
            edited_order = st.data_editor(
                order_df,
                use_container_width=True,
                hide_index=True,
                key="order_editor",
                column_config={
                    "Unit Cost": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                    "Order Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                    "Suggested Order": st.column_config.NumberColumn(disabled=True),
                    "Current Inventory": st.column_config.NumberColumn(disabled=True),
                    "Par": st.column_config.NumberColumn(disabled=True),
                    "Order Quantity": st.column_config.NumberColumn(min_value=0, step=0.5),
                },
                disabled=["Product", "Category", "Current Inventory", "Par", "Suggested Order",
                         "Unit", "Unit Cost", "Distributor", "Order Notes"]
            )
            
            # V2.12: Action buttons row with Recalculate and Copy options
            col_recalc, col_copy_order, col_spacer = st.columns([1, 1, 3])
            
            with col_recalc:
                if st.button("💰 Recalculate Total", key="recalc_order"):
                    edited_order['Order Value'] = edited_order['Order Quantity'] * edited_order['Unit Cost']
                    st.session_state.current_order = edited_order
                    st.rerun()
            
            with col_copy_order:
                # Create a simple text format for clipboard
                copy_cols = ['Product', 'Order Quantity', 'Unit', 'Distributor']
                copy_df = edited_order[copy_cols].copy()
                
                # Group by distributor for organized copying
                copy_text = "ORDER LIST\n" + "=" * 40 + "\n\n"
                for dist in copy_df['Distributor'].unique():
                    dist_items = copy_df[copy_df['Distributor'] == dist]
                    copy_text += f"📦 {dist}\n" + "-" * 30 + "\n"
                    for _, row in dist_items.iterrows():
                        copy_text += f"  • {row['Product']}: {row['Order Quantity']} {row['Unit']}\n"
                    copy_text += "\n"
                
                st.download_button(
                    label="📋 Copy Order",
                    data=copy_text,
                    file_name=f"order_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key="download_order_text"
                )
            
            st.markdown("---")
            # V2.10: Send to Verification instead of Save to History
            if st.button("📋 Send to Verification", key="send_to_verification", type="primary"):
                # Create pending order with original values for comparison
                pending_df = edited_order.copy()
                pending_df['Original Unit Cost'] = pending_df['Unit Cost']
                pending_df['Original Order Quantity'] = pending_df['Order Quantity']
                pending_df['Verification Notes'] = ''  # Initialize as empty string
                pending_df['Verification Notes'] = pending_df['Verification Notes'].astype(str)  # Ensure string type
                pending_df['Modified'] = False
                pending_df['Order Date'] = datetime.now().strftime("%Y-%m-%d")
                
                st.session_state.pending_order = pending_df
                st.session_state.current_order = pd.DataFrame()  # Clear current order
                
                # Save pending order for persistence
                save_pending_order()
                save_all_inventory_data()
                
                st.success("✅ Order sent to verification! Complete Step 3 to finalize.")
                st.rerun()
        else:
            # Check if there's a pending order waiting for verification
            if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
                st.info("📋 An order is pending verification. Complete Step 3 below to finalize.")
            else:
                st.info("👆 Update inventory counts above and click 'Generate Orders' to see what needs ordering.")
        
        # =====================================================================
        # V2.10: STEP 3 - ORDER VERIFICATION
        # =====================================================================
        
        st.markdown("---")
        st.markdown("### Step 3: Order Verification")
        st.markdown("Verify received products against the order. Update quantities and costs as needed, then finalize.")
        
        if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
            pending_df = st.session_state.pending_order.copy()
            
            # Ensure all required columns exist
            if 'Original Unit Cost' not in pending_df.columns:
                pending_df['Original Unit Cost'] = pending_df['Unit Cost']
            if 'Original Order Quantity' not in pending_df.columns:
                pending_df['Original Order Quantity'] = pending_df['Order Quantity']
            if 'Verification Notes' not in pending_df.columns:
                pending_df['Verification Notes'] = ''
            if 'Modified' not in pending_df.columns:
                pending_df['Modified'] = False
            if 'Order Date' not in pending_df.columns:
                pending_df['Order Date'] = datetime.now().strftime("%Y-%m-%d")
            
            # V2.12 Fix: Ensure Verification Notes is string type (fixes StreamlitAPIException)
            pending_df['Verification Notes'] = pending_df['Verification Notes'].fillna('').astype(str)
            
            # V2.15: Add Invoice # column if not present
            if 'Invoice #' not in pending_df.columns:
                pending_df['Invoice #'] = ''
            pending_df['Invoice #'] = pending_df['Invoice #'].fillna('').astype(str)
            
            # V2.21: Add Invoice Date column if not present and convert to datetime type
            if 'Invoice Date' not in pending_df.columns:
                pending_df['Invoice Date'] = pd.NaT
            else:
                # Convert existing Invoice Date to datetime (handles strings from Google Sheets)
                pending_df['Invoice Date'] = pd.to_datetime(pending_df['Invoice Date'], errors='coerce')
            
            order_date = pending_df['Order Date'].iloc[0] if 'Order Date' in pending_df.columns else 'Unknown'
            st.markdown(f"**📅 Order Date:** {order_date}")
            st.markdown(f"**📦 {len(pending_df)} items pending verification:**")
            
            # Display columns for verification (editable: Unit Cost, Order Quantity, Verification Notes, Invoice #, Invoice Date)
            verify_display_cols = ['Product', 'Category', 'Distributor', 'Unit Cost', 'Order Quantity', 
                                   'Order Value', 'Verification Notes', 'Modified']
            
            # Calculate Modified flag based on changes
            pending_df['Modified'] = (
                (pending_df['Unit Cost'] != pending_df['Original Unit Cost']) | 
                (pending_df['Order Quantity'] != pending_df['Original Order Quantity'])
            )
            
            # V2.12 Update: Red flag for modified rows with change details
            def get_status_with_changes(row):
                if not row['Modified']:
                    return '✅'
                
                changes = []
                if row['Unit Cost'] != row['Original Unit Cost']:
                    changes.append(f"Cost: ${row['Original Unit Cost']:.2f}→${row['Unit Cost']:.2f}")
                if row['Order Quantity'] != row['Original Order Quantity']:
                    changes.append(f"Qty: {row['Original Order Quantity']}→{row['Order Quantity']}")
                
                return '🚩 ' + ', '.join(changes)
            
            pending_df['Status'] = pending_df.apply(get_status_with_changes, axis=1)
            
            # V2.21: Updated display columns with Invoice Date
            verify_display_cols = ['Status', 'Product', 'Category', 'Distributor', 'Unit', 'Unit Cost', 
                                   'Order Quantity', 'Order Value', 'Invoice #', 'Invoice Date', 'Verification Notes']
            
            edited_verification = st.data_editor(
                pending_df[verify_display_cols],
                use_container_width=True,
                hide_index=True,
                key="verification_editor",
                column_config={
                    "Status": st.column_config.TextColumn("Status", disabled=True, width="small"),
                    "Unit": st.column_config.TextColumn("Unit", disabled=True),
                    "Unit Cost": st.column_config.NumberColumn(format="$%.2f", min_value=0, step=0.01),
                    "Order Quantity": st.column_config.NumberColumn(min_value=0, step=0.5),
                    "Order Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                    "Invoice #": st.column_config.TextColumn("Invoice #", width="small"),
                    "Invoice Date": st.column_config.DateColumn("Invoice Date", width="small", format="MM/DD/YYYY"),
                    "Verification Notes": st.column_config.TextColumn("Order Notes", width="medium"),
                },
                disabled=["Status", "Product", "Category", "Distributor", "Unit", "Order Value"]
            )
            
            col_recalc, col_save_progress = st.columns([1, 1])
            
            with col_recalc:
                if st.button("💰 Recalculate Total", key="recalc_verification", help="Update totals in display (does not save)"):
                    # Update pending order with edited values (session state only, no save)
                    for idx, row in edited_verification.iterrows():
                        mask = st.session_state.pending_order['Product'] == row['Product']
                        st.session_state.pending_order.loc[mask, 'Unit Cost'] = row['Unit Cost']
                        st.session_state.pending_order.loc[mask, 'Order Quantity'] = row['Order Quantity']
                        st.session_state.pending_order.loc[mask, 'Verification Notes'] = row['Verification Notes']
                        st.session_state.pending_order.loc[mask, 'Invoice #'] = row['Invoice #']
                        st.session_state.pending_order.loc[mask, 'Invoice Date'] = row['Invoice Date']
                    
                    # Recalculate Order Value
                    st.session_state.pending_order['Order Value'] = (
                        st.session_state.pending_order['Order Quantity'] * 
                        st.session_state.pending_order['Unit Cost']
                    )
                    
                    # Update Modified flag
                    st.session_state.pending_order['Modified'] = (
                        (st.session_state.pending_order['Unit Cost'] != st.session_state.pending_order['Original Unit Cost']) | 
                        (st.session_state.pending_order['Order Quantity'] != st.session_state.pending_order['Original Order Quantity'])
                    )
                    
                    # No save - just refresh display
                    st.success("✅ Totals recalculated!")
                    st.rerun()
            
            with col_save_progress:
                if st.button("💾 Save Progress", key="save_verification_progress", help="Save verification progress to Google Sheets"):
                    # Update pending order with edited values
                    for idx, row in edited_verification.iterrows():
                        mask = st.session_state.pending_order['Product'] == row['Product']
                        st.session_state.pending_order.loc[mask, 'Unit Cost'] = row['Unit Cost']
                        st.session_state.pending_order.loc[mask, 'Order Quantity'] = row['Order Quantity']
                        st.session_state.pending_order.loc[mask, 'Verification Notes'] = row['Verification Notes']
                        st.session_state.pending_order.loc[mask, 'Invoice #'] = row['Invoice #']
                        st.session_state.pending_order.loc[mask, 'Invoice Date'] = row['Invoice Date']
                    
                    # Recalculate
                    st.session_state.pending_order['Order Value'] = (
                        st.session_state.pending_order['Order Quantity'] * 
                        st.session_state.pending_order['Unit Cost']
                    )
                    st.session_state.pending_order['Modified'] = (
                        (st.session_state.pending_order['Unit Cost'] != st.session_state.pending_order['Original Unit Cost']) | 
                        (st.session_state.pending_order['Order Quantity'] != st.session_state.pending_order['Original Order Quantity'])
                    )
                    
                    # Save to Google Sheets for persistence
                    save_pending_order()
                    st.success("✅ Progress saved to Google Sheets!")
                    st.rerun()
            
            # Verification Summary
            st.markdown("---")
            st.markdown("### Verification Summary")
            
            # Recalculate for display
            display_pending = pending_df.copy()
            display_pending['Order Value'] = display_pending['Order Quantity'] * display_pending['Unit Cost']
            
            modified_count = display_pending['Modified'].sum()
            
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            with col_v1:
                st.metric("Total Items", len(display_pending))
            with col_v2:
                st.metric("Modified Items", int(modified_count))
            with col_v3:
                st.metric("Total Units", f"{display_pending['Order Quantity'].sum():.1f}")
            with col_v4:
                st.metric("Final Order Value", format_currency(display_pending['Order Value'].sum()))
            
            # Finalize section
            st.markdown("---")
            st.markdown("### Finalize Order")
            st.markdown("Enter your initials to sign off and save the verified order to history.")
            
            col_initials, col_finalize, col_cancel = st.columns([1, 1, 1])
            
            with col_initials:
                verifier_initials = st.text_input(
                    "Verifier Initials:",
                    max_chars=5,
                    key="verifier_initials",
                    placeholder="e.g., JD"
                )
            
            with col_finalize:
                st.write("")  # Spacer
                finalize_disabled = len(verifier_initials.strip()) == 0
                if st.button("✅ Finalize & Save Order", key="finalize_order", type="primary", disabled=finalize_disabled):
                    # Update with final edited values
                    for idx, row in edited_verification.iterrows():
                        mask = st.session_state.pending_order['Product'] == row['Product']
                        st.session_state.pending_order.loc[mask, 'Unit Cost'] = row['Unit Cost']
                        st.session_state.pending_order.loc[mask, 'Order Quantity'] = row['Order Quantity']
                        st.session_state.pending_order.loc[mask, 'Verification Notes'] = row['Verification Notes']
                        st.session_state.pending_order.loc[mask, 'Invoice #'] = row['Invoice #']
                        st.session_state.pending_order.loc[mask, 'Invoice Date'] = row['Invoice Date']
                    
                    st.session_state.pending_order['Order Value'] = (
                        st.session_state.pending_order['Order Quantity'] * 
                        st.session_state.pending_order['Unit Cost']
                    )
                    
                    # Save to order history
                    order_date = st.session_state.pending_order['Order Date'].iloc[0]
                    new_orders = []
                    for _, row in st.session_state.pending_order.iterrows():
                        if row['Order Quantity'] > 0:
                            # V2.21: Format Invoice Date for storage
                            invoice_date_val = row.get('Invoice Date', None)
                            if pd.notna(invoice_date_val):
                                if hasattr(invoice_date_val, 'strftime'):
                                    invoice_date_str = invoice_date_val.strftime('%Y-%m-%d')
                                else:
                                    invoice_date_str = str(invoice_date_val)
                            else:
                                invoice_date_str = ''
                            
                            new_orders.append({
                                'Week': order_date,
                                'Product': row['Product'],
                                'Category': row['Category'],
                                'Quantity Ordered': row['Order Quantity'],
                                'Unit': row.get('Unit', ''),
                                'Unit Cost': row['Unit Cost'],
                                'Total Cost': row['Order Value'],
                                'Distributor': row['Distributor'],
                                'Status': 'Verified',
                                'Verified By': verifier_initials.strip().upper(),
                                'Invoice #': row.get('Invoice #', ''),
                                'Invoice Date': invoice_date_str,
                                'Verification Notes': row.get('Verification Notes', '')
                            })
                    
                    if new_orders:
                        st.session_state.order_history = pd.concat([
                            st.session_state.order_history, pd.DataFrame(new_orders)
                        ], ignore_index=True)
                        
                        # Clear pending order
                        clear_pending_order()
                        
                        # Save to files for persistence
                        save_all_inventory_data()
                        
                        st.success(f"✅ Order verified by {verifier_initials.strip().upper()} and saved to history!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning("No items with quantity > 0 to save.")
            
            with col_cancel:
                st.write("")  # Spacer
                if st.button("❌ Cancel Verification", key="cancel_verification"):
                    clear_pending_order()
                    st.warning("Verification cancelled. Order has been discarded.")
                    st.rerun()
            
            if finalize_disabled:
                st.caption("⚠️ Enter your initials above to enable the Finalize button.")
        
        else:
            st.info("📋 No orders pending verification. Complete Steps 1 and 2 to create an order.")
    
    with tab_history:
        st.markdown("### 📜 Previous Orders")
        
        # V2.10: Show pending verification notice
        if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
            pending_date = st.session_state.pending_order['Order Date'].iloc[0] if 'Order Date' in st.session_state.pending_order.columns else 'Unknown'
            pending_value = st.session_state.pending_order['Order Value'].sum() if 'Order Value' in st.session_state.pending_order.columns else 0
            st.warning(f"⏳ **Pending Verification:** Order from {pending_date} ({format_currency(pending_value)}) - Complete Step 3 to finalize.")
        
        if len(order_history) > 0:
            # V2.10: Ensure Status column exists for display
            display_history = order_history.copy()
            if 'Status' not in display_history.columns:
                display_history['Status'] = 'Verified'  # Default for legacy orders
            if 'Verified By' not in display_history.columns:
                display_history['Verified By'] = ''
            # V2.18: Ensure Unit column exists for display
            if 'Unit' not in display_history.columns:
                display_history['Unit'] = ''  # Default for legacy orders without Unit
            # V2.21: Ensure Invoice # and Invoice Date columns exist for display
            if 'Invoice #' not in display_history.columns:
                display_history['Invoice #'] = ''  # Default for legacy orders without Invoice #
            if 'Invoice Date' not in display_history.columns:
                display_history['Invoice Date'] = ''  # Default for legacy orders without Invoice Date
            
            # V2.17: Add Month column for filtering
            display_history['Week'] = pd.to_datetime(display_history['Week'])
            display_history['Month'] = display_history['Week'].dt.to_period('M').astype(str)
            display_history['Week'] = display_history['Week'].dt.strftime('%Y-%m-%d')
            
            # V2.17: Updated filter row with Month filter
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                # Month filter
                months = sorted(display_history['Month'].unique(), reverse=True)
                selected_months = st.multiselect("Filter by Month:", options=months,
                    default=months[:2] if len(months) >= 2 else months, key="history_month_filter")
            
            with col_f2:
                # Week filter - dynamically update based on selected months
                if selected_months:
                    available_weeks = display_history[display_history['Month'].isin(selected_months)]['Week'].unique()
                else:
                    available_weeks = display_history['Week'].unique()
                weeks = sorted(available_weeks, reverse=True)
                selected_weeks = st.multiselect("Filter by Week:", options=weeks,
                    default=weeks, key="history_week_filter")
            
            with col_f3:
                categories = display_history['Category'].unique().tolist()
                selected_categories = st.multiselect("Filter by Category:", options=categories,
                    default=categories, key="history_category_filter")
            
            with col_f4:
                status_options = display_history['Status'].unique().tolist()
                selected_statuses = st.multiselect("Filter by Status:", options=status_options,
                    default=status_options, key="history_status_filter")
            
            filtered_history = display_history.copy()
            if selected_months:
                filtered_history = filtered_history[filtered_history['Month'].isin(selected_months)]
            if selected_weeks:
                filtered_history = filtered_history[filtered_history['Week'].isin(selected_weeks)]
            if selected_categories:
                filtered_history = filtered_history[filtered_history['Category'].isin(selected_categories)]
            if selected_statuses:
                filtered_history = filtered_history[filtered_history['Status'].isin(selected_statuses)]
            
            st.markdown("#### Weekly Order Totals")
            weekly_totals = filtered_history.groupby('Week').agg({
                'Total Cost': 'sum',
                'Verified By': 'first'
            }).reset_index()
            weekly_totals = weekly_totals.sort_values('Week', ascending=False)
            weekly_totals['Status'] = '✅ Verified'
            
            # V2.17: Add total row at the bottom
            if len(weekly_totals) > 0:
                total_cost = weekly_totals['Total Cost'].sum()
                total_row = pd.DataFrame([{
                    'Week': '📊 TOTAL',
                    'Total Cost': total_cost,
                    'Status': '',
                    'Verified By': f'{len(weekly_totals)} orders'
                }])
                weekly_totals_with_total = pd.concat([weekly_totals, total_row], ignore_index=True)
            else:
                weekly_totals_with_total = weekly_totals
            
            st.dataframe(weekly_totals_with_total[['Week', 'Total Cost', 'Status', 'Verified By']], 
                        use_container_width=True, hide_index=True,
                        column_config={"Total Cost": st.column_config.NumberColumn(format="$%.2f")})
            
            st.markdown("#### Order Details")
            # Select columns to display - V2.21: Added Invoice Date column
            detail_cols = ['Week', 'Product', 'Category', 'Quantity Ordered', 'Unit', 'Unit Cost', 
                          'Total Cost', 'Distributor', 'Invoice #', 'Invoice Date', 'Status', 'Verified By']
            # Only include columns that exist
            detail_cols = [c for c in detail_cols if c in filtered_history.columns]
            
            st.dataframe(filtered_history[detail_cols].sort_values(['Week', 'Product'], ascending=[False, True]),
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Total Cost": st.column_config.NumberColumn(format="$%.2f")
                        })
        else:
            st.info("No order history yet. Complete all 3 steps to save an order.")
    
    with tab_analytics:
        st.markdown("### 📈 Order Analytics")
        if len(order_history) > 0:
            # =================================================================
            # V2.20: CONSISTENT CATEGORY COLORS
            # =================================================================
            category_colors = {
                'Spirits': '#8B5CF6',    # Purple
                'Wine': '#EC4899',       # Pink
                'Beer': '#F59E0B',       # Amber
                'Ingredients': '#10B981' # Emerald
            }
            
            # =================================================================
            # V2.20: DATE RANGE FILTER
            # =================================================================
            st.markdown("#### 📅 Date Range Filter")
            
            # Convert Week to datetime for filtering
            analytics_data = order_history.copy()
            analytics_data['Week'] = pd.to_datetime(analytics_data['Week'])
            
            min_date = analytics_data['Week'].min().date()
            max_date = analytics_data['Week'].max().date()
            
            col_date1, col_date2, col_date3 = st.columns([1, 1, 2])
            
            with col_date1:
                start_date = st.date_input(
                    "Start Date:",
                    value=min_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="analytics_start_date"
                )
            
            with col_date2:
                end_date = st.date_input(
                    "End Date:",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date,
                    key="analytics_end_date"
                )
            
            with col_date3:
                # Quick date range buttons
                st.write("")  # Spacer
                col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                # Note: These are display-only labels since date_input handles the actual filtering
            
            # Filter data by date range
            filtered_analytics = analytics_data[
                (analytics_data['Week'].dt.date >= start_date) & 
                (analytics_data['Week'].dt.date <= end_date)
            ].copy()
            
            # Calculate comparison period (same length, immediately prior)
            date_range_days = (end_date - start_date).days
            prior_start = start_date - timedelta(days=date_range_days + 1)
            prior_end = start_date - timedelta(days=1)
            
            prior_period_data = analytics_data[
                (analytics_data['Week'].dt.date >= prior_start) & 
                (analytics_data['Week'].dt.date <= prior_end)
            ]
            
            st.caption(f"Showing data from {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')} ({len(filtered_analytics)} orders)")
            
            st.markdown("---")
            
            # =================================================================
            # V2.22: KEY METRICS DASHBOARD - Simplified to 4 key metrics
            # =================================================================
            st.markdown("#### 📊 Key Metrics")
            
            # Calculate current period metrics
            total_spend = filtered_analytics['Total Cost'].sum()
            num_orders = len(filtered_analytics['Week'].unique())
            avg_weekly_spend = total_spend / max(num_orders, 1)
            total_items_ordered = len(filtered_analytics)
            
            # Calculate top category and product (used in export report)
            top_category = filtered_analytics.groupby('Category')['Total Cost'].sum().idxmax() if len(filtered_analytics) > 0 else "N/A"
            top_product = filtered_analytics.groupby('Product')['Total Cost'].sum().idxmax() if len(filtered_analytics) > 0 else "N/A"
            
            # Calculate prior period metrics for trend indicators
            prior_total_spend = prior_period_data['Total Cost'].sum() if len(prior_period_data) > 0 else 0
            prior_num_orders = len(prior_period_data['Week'].unique()) if len(prior_period_data) > 0 else 0
            prior_avg_weekly = prior_total_spend / max(prior_num_orders, 1) if prior_num_orders > 0 else 0
            
            # Calculate deltas
            spend_delta = total_spend - prior_total_spend
            spend_delta_pct = (spend_delta / prior_total_spend * 100) if prior_total_spend > 0 else 0
            avg_delta = avg_weekly_spend - prior_avg_weekly
            avg_delta_pct = (avg_delta / prior_avg_weekly * 100) if prior_avg_weekly > 0 else 0
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            
            with col_m1:
                delta_str = f"{'↑' if spend_delta >= 0 else '↓'} ${abs(spend_delta):,.0f}" if prior_total_spend > 0 else None
                st.metric(
                    "💰 Total Spend",
                    f"${total_spend:,.2f}",
                    delta=delta_str,
                    delta_color="inverse"  # Red for increase (spending), green for decrease
                )
            
            with col_m2:
                delta_avg_str = f"{'↑' if avg_delta >= 0 else '↓'} ${abs(avg_delta):,.0f}" if prior_avg_weekly > 0 else None
                st.metric(
                    "📅 Avg Weekly Spend",
                    f"${avg_weekly_spend:,.2f}",
                    delta=delta_avg_str,
                    delta_color="inverse"
                )
            
            with col_m3:
                st.metric("📦 Total Orders", f"{total_items_ordered:,}")
            
            with col_m4:
                # Spend Comparison to previous period
                if prior_total_spend > 0:
                    comparison_pct = spend_delta_pct
                    comparison_str = f"{'↑' if comparison_pct >= 0 else '↓'} {abs(comparison_pct):.1f}%"
                    comparison_color = "🔴" if comparison_pct > 0 else "🟢"
                    st.metric(
                        "📈 vs Prior Period",
                        f"{comparison_color} {abs(comparison_pct):.1f}%",
                        delta=f"${abs(spend_delta):,.0f} {'more' if spend_delta >= 0 else 'less'}",
                        delta_color="inverse"
                    )
                else:
                    st.metric("📈 vs Prior Period", "N/A", delta="No prior data")
            
            st.markdown("---")
            
            # =================================================================
            # V2.22: SPENDING BY CATEGORY - Pie chart with Top Products dropdowns
            # =================================================================
            st.markdown("#### 📊 Spending by Category")
            
            cat_spend = filtered_analytics.groupby('Category')['Total Cost'].sum().reset_index()
            cat_spend = cat_spend.sort_values('Total Cost', ascending=False)
            
            col_cat_pie, col_cat_dropdowns = st.columns([1, 1])
            
            with col_cat_pie:
                fig_pie = px.pie(
                    cat_spend, 
                    values='Total Cost', 
                    names='Category', 
                    title='Category Distribution',
                    color='Category',
                    color_discrete_map=category_colors
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_cat_dropdowns:
                st.markdown("**🏆 Top Products by Category**")
                st.markdown("Expand each category to see top 10 products by spend.")
                
                categories = sorted(filtered_analytics['Category'].unique())
                
                for category in categories:
                    category_data = filtered_analytics[filtered_analytics['Category'] == category]
                    category_total = category_data['Total Cost'].sum()
                    
                    with st.expander(f"**{category}** - ${category_total:,.2f}", expanded=False):
                        top_in_category = category_data.groupby('Product').agg({
                            'Quantity Ordered': 'sum',
                            'Total Cost': 'sum'
                        }).sort_values('Total Cost', ascending=False).head(10)
                        
                        if len(top_in_category) > 0:
                            st.dataframe(
                                top_in_category.reset_index().rename(columns={
                                    'Product': 'Product', 
                                    'Quantity Ordered': 'Units', 
                                    'Total Cost': 'Spend'
                                }),
                                use_container_width=True, 
                                hide_index=True,
                                column_config={
                                    "Spend": st.column_config.NumberColumn(format="$%.2f")
                                }
                            )
                        else:
                            st.info(f"No orders found for {category}.")
            
            st.markdown("---")
            
            # =================================================================
            # V2.22: PRICE CHANGE TRACKER - Enhanced with date and acknowledgment
            # =================================================================
            st.markdown("#### 💲 Price Change Tracker")
            st.markdown("Products with unit cost changes from their first recorded order. Check the box when you've reviewed and updated Master Inventory if needed.")
            
            # Find price changes
            price_changes = []
            for product in analytics_data['Product'].unique():
                product_data = analytics_data[analytics_data['Product'] == product].sort_values('Week')
                if len(product_data) >= 2:
                    first_price = product_data.iloc[0]['Unit Cost']
                    latest_price = product_data.iloc[-1]['Unit Cost']
                    
                    if first_price != latest_price:
                        change = latest_price - first_price
                        change_pct = (change / first_price * 100) if first_price > 0 else 0
                        # Get the date when the price change was recorded (latest order date)
                        change_date = product_data.iloc[-1]['Week']
                        if hasattr(change_date, 'strftime'):
                            change_date_str = change_date.strftime('%Y-%m-%d')
                        else:
                            change_date_str = str(change_date)[:10]
                        
                        # Check if this price change has been acknowledged
                        ack_key = f"{product}_{change_date_str}"
                        acknowledged = st.session_state.price_change_acks.get(ack_key, False)
                        
                        price_changes.append({
                            'Product': product,
                            'Category': product_data.iloc[0]['Category'],
                            'First Price': first_price,
                            'Current Price': latest_price,
                            'Change ($)': change,
                            'Change (%)': change_pct,
                            'Direction': '🔺 Increase' if change > 0 else '🔻 Decrease',
                            'Date Recorded': change_date_str,
                            'Reviewed': acknowledged,
                            '_ack_key': ack_key
                        })
            
            if price_changes:
                price_df = pd.DataFrame(price_changes)
                price_df = price_df.sort_values('Change (%)', ascending=False, key=abs)
                
                # Display columns without the internal ack_key
                display_cols = ['Reviewed', 'Product', 'Category', 'First Price', 'Current Price', 
                               'Change ($)', 'Change (%)', 'Direction', 'Date Recorded']
                
                edited_price_df = st.data_editor(
                    price_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Reviewed": st.column_config.CheckboxColumn("✅ Reviewed", help="Check when you've reviewed and updated Master Inventory", width="small"),
                        "First Price": st.column_config.NumberColumn(format="$%.2f"),
                        "Current Price": st.column_config.NumberColumn(format="$%.2f"),
                        "Change ($)": st.column_config.NumberColumn(format="$%.2f"),
                        "Change (%)": st.column_config.NumberColumn(format="%.1f%%"),
                        "Date Recorded": st.column_config.TextColumn("Date Recorded", width="small")
                    },
                    disabled=['Product', 'Category', 'First Price', 'Current Price', 'Change ($)', 'Change (%)', 'Direction', 'Date Recorded'],
                    key="price_change_editor"
                )
                
                # Save acknowledgments back to session state and Google Sheets
                for idx, row in edited_price_df.iterrows():
                    original_row = price_df.loc[idx]  # Use .loc (by label) not .iloc (by position)
                    ack_key = original_row['_ack_key']
                    st.session_state.price_change_acks[ack_key] = row['Reviewed']
                
                # V2.22: Persist to Google Sheets
                save_price_change_acks()
                
                # Show summary and download button
                col_summary, col_download = st.columns([2, 1])
                
                with col_summary:
                    reviewed_count = edited_price_df['Reviewed'].sum()
                    total_count = len(edited_price_df)
                    if reviewed_count == total_count:
                        st.success(f"✅ All {total_count} price changes have been reviewed!")
                    else:
                        st.info(f"📋 {reviewed_count} of {total_count} price changes reviewed.")
                
                with col_download:
                    price_csv = pd.DataFrame(price_changes).to_csv(index=False)
                    st.download_button(
                        label="💲 Download Price Changes",
                        data=price_csv,
                        file_name=f"price_changes_{start_date}_{end_date}.csv",
                        mime="text/csv",
                        key="download_price_changes"
                    )
            else:
                st.info("✅ No price changes detected in your order history.")
            
            st.markdown("---")
            
            # =================================================================
            # PRODUCT ANALYSIS
            # =================================================================
            st.markdown("#### 📈 Product Analysis")
            st.markdown("Select products below to view order trends, spending patterns, and summary statistics over time.")
            
            products = sorted(filtered_analytics['Product'].unique())
            selected_products = st.multiselect("Select products:", options=products,
                default=products[:3] if len(products) >= 3 else products, key="analytics_products")
            
            if selected_products:
                plot_data = filtered_analytics[filtered_analytics['Product'].isin(selected_products)]
                
                col_qty_chart, col_cost_chart = st.columns(2)
                
                with col_qty_chart:
                    st.markdown("**Quantity Ordered Over Time**")
                    fig_qty = px.line(plot_data, x='Week', y='Quantity Ordered', color='Product',
                                     markers=True)
                    fig_qty.update_layout(height=350)
                    st.plotly_chart(fig_qty, use_container_width=True)
                
                with col_cost_chart:
                    st.markdown("**Spending Over Time**")
                    fig_cost = px.line(plot_data, x='Week', y='Total Cost', color='Product',
                                      markers=True)
                    fig_cost.update_layout(
                        yaxis_tickprefix='$', 
                        yaxis_tickformat=',.2f',
                        height=350
                    )
                    st.plotly_chart(fig_cost, use_container_width=True)
                
                st.markdown("**Product Summary Statistics**")
                summary = plot_data.groupby('Product').agg({
                    'Quantity Ordered': ['sum', 'mean', 'std'],
                    'Total Cost': ['sum', 'mean']
                }).round(2)
                summary.columns = ['Total Qty', 'Avg Qty/Week', 'Std Dev', 'Total Spend', 'Avg Spend/Week']
                st.dataframe(summary.reset_index(), use_container_width=True, hide_index=True,
                            column_config={
                                "Total Spend": st.column_config.NumberColumn(format="$%.2f"),
                                "Avg Spend/Week": st.column_config.NumberColumn(format="$%.2f")
                            })
            
            st.markdown("---")
            
            # =================================================================
            # DISTRIBUTOR ANALYTICS
            # =================================================================
            st.markdown("#### 🚚 Distributor Analytics")
            
            dist_spend = filtered_analytics.groupby('Distributor').agg({
                'Total Cost': 'sum',
                'Quantity Ordered': 'sum',
                'Product': 'nunique'
            }).reset_index()
            dist_spend.columns = ['Distributor', 'Total Spend', 'Total Units', '# Products']
            dist_spend = dist_spend.sort_values('Total Spend', ascending=False)
            
            col_dist_chart, col_dist_table = st.columns([1, 1])
            
            with col_dist_chart:
                fig_dist = px.pie(
                    dist_spend, 
                    values='Total Spend', 
                    names='Distributor', 
                    title='Spend by Distributor',
                    hole=0.4  # Donut chart
                )
                fig_dist.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col_dist_table:
                st.dataframe(
                    dist_spend,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Total Spend": st.column_config.NumberColumn(format="$%.2f"),
                        "Total Units": st.column_config.NumberColumn(format="%.1f")
                    }
                )
            
            st.markdown("---")
            
            # =================================================================
            # V2.20: DOWNLOAD ANALYTICS REPORT
            # =================================================================
            st.markdown("#### 📥 Export Analytics")
            
            col_export1, col_export2 = st.columns(2)
            
            with col_export1:
                # Export filtered order data
                csv_orders = filtered_analytics.to_csv(index=False)
                st.download_button(
                    label="📊 Download Order Data (CSV)",
                    data=csv_orders,
                    file_name=f"order_analytics_{start_date}_{end_date}.csv",
                    mime="text/csv",
                    key="download_analytics_csv"
                )
            
            with col_export2:
                # Export summary report
                summary_report = f"""BEVERAGE ORDER ANALYTICS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Period: {start_date} to {end_date}
{'='*50}

KEY METRICS
-----------
Total Spend: ${total_spend:,.2f}
Average Weekly Spend: ${avg_weekly_spend:,.2f}
Number of Order Weeks: {num_orders}
Top Category: {top_category}
Top Product: {top_product}

SPENDING BY CATEGORY
--------------------
"""
                for _, row in cat_spend.iterrows():
                    summary_report += f"{row['Category']}: ${row['Total Cost']:,.2f}\n"
                
                summary_report += f"""
SPENDING BY DISTRIBUTOR
-----------------------
"""
                for _, row in dist_spend.iterrows():
                    summary_report += f"{row['Distributor']}: ${row['Total Spend']:,.2f} ({row['# Products']} products)\n"
                
                if price_changes:
                    summary_report += f"""
PRICE CHANGES DETECTED
----------------------
"""
                    for pc in price_changes:
                        summary_report += f"{pc['Product']}: ${pc['First Price']:.2f} → ${pc['Current Price']:.2f} ({pc['Change (%)']:.1f}%)\n"
                
                st.download_button(
                    label="📝 Download Summary Report",
                    data=summary_report,
                    file_name=f"analytics_summary_{start_date}_{end_date}.txt",
                    mime="text/plain",
                    key="download_analytics_summary"
                )
            
        else:
            st.info("No order history yet. Save some orders to see analytics.")


# =============================================================================
# PAGE: COCKTAIL BUILDS BOOK
# =============================================================================

def show_cocktails():
    """
    Renders the Cocktail Builds Book module with:
    - Dashboard showing cocktail count and average cost
    - Search functionality by name or ingredient
    - Recipe viewer with costing details
    - Add/Edit recipe functionality
    """
    
    # ----- Header -----
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🍹 Cocktail Builds Book")
    
    # =========================================================================
    # DASHBOARD
    # =========================================================================
    
    st.markdown("### 📊 Cocktails Dashboard")
    
    recipes = st.session_state.cocktail_recipes
    
    # Calculate metrics
    total_cocktails = len(recipes)
    
    # Calculate costs for all cocktails
    cocktail_costs = []
    cocktail_margins = []
    for recipe in recipes:
        cost = calculate_cocktail_cost(recipe['ingredients'])
        cocktail_costs.append(cost)
        margin = calculate_margin(cost, recipe['sale_price'])
        cocktail_margins.append(margin)
    
    avg_cost = sum(cocktail_costs) / len(cocktail_costs) if cocktail_costs else 0
    avg_margin = sum(cocktail_margins) / len(cocktail_margins) if cocktail_margins else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="📚 Total Recipes", value=total_cocktails)
    with col2:
        st.metric(label="💵 Avg Cost", value=format_currency(avg_cost))
    with col3:
        st.metric(label="📊 Avg Margin", value=f"{avg_margin:.1%}")
    with col4:
        # Count unique ingredients used across all recipes
        all_ingredients = set()
        for recipe in recipes:
            for ing in recipe['ingredients']:
                all_ingredients.add(ing['product'])
        st.metric(label="🧴 Unique Ingredients", value=len(all_ingredients))
    
    st.markdown("---")
    
    # =========================================================================
    # TABS: VIEW RECIPES / ADD NEW RECIPE
    # =========================================================================
    
    tab_view, tab_add = st.tabs(["📖 View & Search Recipes", "➕ Add New Recipe"])
    
    # -------------------------------------------------------------------------
    # TAB: VIEW & SEARCH RECIPES
    # -------------------------------------------------------------------------
    with tab_view:
        st.markdown("### 🔍 Search Cocktails")
        
        # Search bar
        search_query = st.text_input(
            "Search by cocktail name or ingredient:",
            key="cocktail_search",
            placeholder="e.g., 'Margarita' or 'bourbon'"
        )
        
        # Filter recipes based on search
        filtered_recipes = []
        for recipe in recipes:
            # Check if search matches cocktail name
            if search_query.lower() in recipe['name'].lower():
                filtered_recipes.append(recipe)
            # Check if search matches any ingredient
            elif any(search_query.lower() in ing['product'].lower() for ing in recipe['ingredients']):
                filtered_recipes.append(recipe)
            # If no search query, include all
            elif not search_query:
                filtered_recipes.append(recipe)
        
        st.caption(f"Showing {len(filtered_recipes)} of {len(recipes)} recipes")
        
        st.markdown("---")
        
        # Display recipes
        if filtered_recipes:
            for idx, recipe in enumerate(filtered_recipes):
                # Calculate cost and margin for this cocktail
                total_cost = calculate_cocktail_cost(recipe['ingredients'])
                margin = calculate_margin(total_cost, recipe['sale_price'])
                suggested_price = suggest_price_from_cost(total_cost, 0.20)
                
                # Recipe card
                with st.expander(f"🍸 **{recipe['name']}** | Cost: {format_currency(total_cost)} | Price: {format_currency(recipe['sale_price'])} | Margin: {margin:.1%}", expanded=False):
                    
                    col_info, col_pricing = st.columns([2, 1])
                    
                    with col_info:
                        st.markdown(f"**Glass:** {recipe['glass']}")
                        st.markdown("**Ingredients:**")
                        
                        # Build ingredients table
                        ing_data = []
                        for ing in recipe['ingredients']:
                            unit_cost = get_ingredient_cost_per_unit(ing['product'])
                            ing_cost = unit_cost * ing['amount']
                            ing_data.append({
                                "Ingredient": ing['product'],
                                "Amount": ing['amount'],
                                "Unit": ing['unit'],
                                "Unit Cost": unit_cost,
                                "Cost": ing_cost
                            })
                        
                        ing_df = pd.DataFrame(ing_data)
                        st.dataframe(
                            ing_df,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Unit Cost": st.column_config.NumberColumn(format="$%.4f"),
                                "Cost": st.column_config.NumberColumn(format="$%.4f"),
                            }
                        )
                        
                        st.markdown("**Build Instructions:**")
                        st.write(recipe['instructions'])
                    
                    with col_pricing:
                        st.markdown("#### 💰 Pricing")
                        st.metric("Total Cost", format_currency(total_cost))
                        st.metric("Current Price", format_currency(recipe['sale_price']))
                        st.metric("Cost Margin", f"{margin:.1%}")
                        st.caption(f"Suggested Price (20% cost): {format_currency(suggested_price)}")
                        
                        # Edit price
                        st.markdown("---")
                        new_price = st.number_input(
                            "Adjust Sale Price:",
                            min_value=0.0,
                            value=recipe['sale_price'],
                            step=0.50,
                            key=f"price_{idx}"
                        )
                        
                        if new_price != recipe['sale_price']:
                            new_margin = calculate_margin(total_cost, new_price)
                            st.caption(f"New Margin: {new_margin:.1%}")
                            
                            if st.button("💾 Update Price", key=f"update_price_{idx}"):
                                # Find and update the recipe in session state
                                for r in st.session_state.cocktail_recipes:
                                    if r['name'] == recipe['name']:
                                        r['sale_price'] = new_price
                                        break
                                
                                # Save to files for persistence
                                save_cocktail_recipes()
                                
                                st.success("✅ Price updated!")
                                st.rerun()
                    
                    # Delete button
                    st.markdown("---")
                    col_del, col_spacer = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑️ Delete Recipe", key=f"delete_{idx}"):
                            st.session_state.cocktail_recipes = [
                                r for r in st.session_state.cocktail_recipes 
                                if r['name'] != recipe['name']
                            ]
                            
                            # Save to files for persistence
                            save_cocktail_recipes()
                            
                            st.success(f"✅ {recipe['name']} deleted!")
                            st.rerun()
        else:
            st.info("No recipes found matching your search.")
    
    # -------------------------------------------------------------------------
    # TAB: ADD NEW RECIPE
    # -------------------------------------------------------------------------
    with tab_add:
        st.markdown("### ➕ Create New Cocktail Recipe")
        
        # Basic info
        col_name, col_glass = st.columns(2)
        
        with col_name:
            new_name = st.text_input("Cocktail Name:", key="new_cocktail_name")
        
        with col_glass:
            glass_options = ["Martini", "Coupe", "Rocks", "Collins", "Highball", 
                           "Copper Mug", "Nick & Nora", "Wine Glass", "Flute", "Other"]
            new_glass = st.selectbox("Glass:", options=glass_options, key="new_cocktail_glass")
        
        st.markdown("---")
        
        # Ingredients section
        st.markdown("#### 🧴 Ingredients")
        st.caption("Add ingredients one at a time. Select from Spirits and Ingredients inventory.")
        
        # Get available products
        available_products = get_available_products()
        
        # Initialize ingredient list in session state
        if 'new_recipe_ingredients' not in st.session_state:
            st.session_state.new_recipe_ingredients = []
        
        # Add ingredient form
        col_prod, col_amt, col_unit, col_add = st.columns([3, 1, 1, 1])
        
        with col_prod:
            selected_product = st.selectbox(
                "Product:",
                options=[""] + available_products,
                key="add_ingredient_product"
            )
        
        with col_amt:
            ingredient_amount = st.number_input(
                "Amount:",
                min_value=0.0,
                step=0.25,
                key="add_ingredient_amount"
            )
        
        with col_unit:
            unit_options = ["oz", "pieces", "cherries", "dashes", "barspoon", "splash"]
            ingredient_unit = st.selectbox("Unit:", options=unit_options, key="add_ingredient_unit")
        
        with col_add:
            st.write("")  # Spacer
            st.write("")  # Spacer
            if st.button("➕ Add", key="add_ingredient_btn"):
                if selected_product and ingredient_amount > 0:
                    st.session_state.new_recipe_ingredients.append({
                        "product": selected_product,
                        "amount": ingredient_amount,
                        "unit": ingredient_unit
                    })
                    st.rerun()
        
        # Display current ingredients
        if st.session_state.new_recipe_ingredients:
            st.markdown("**Current Ingredients:**")
            
            ing_display = []
            running_cost = 0
            for i, ing in enumerate(st.session_state.new_recipe_ingredients):
                unit_cost = get_ingredient_cost_per_unit(ing['product'])
                ing_cost = unit_cost * ing['amount']
                running_cost += ing_cost
                ing_display.append({
                    "#": i + 1,
                    "Product": ing['product'],
                    "Amount": ing['amount'],
                    "Unit": ing['unit'],
                    "Cost": ing_cost
                })
            
            st.dataframe(
                pd.DataFrame(ing_display),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Cost": st.column_config.NumberColumn(format="$%.4f")
                }
            )
            
            # Running cost total
            st.metric("Running Cost Total", format_currency(running_cost))
            suggested = suggest_price_from_cost(running_cost, 0.20)
            st.caption(f"Suggested Price (20% cost): {format_currency(suggested)}")
            
            # Clear ingredients button
            if st.button("🗑️ Clear All Ingredients", key="clear_ingredients"):
                st.session_state.new_recipe_ingredients = []
                st.rerun()
        
        st.markdown("---")
        
        # Instructions
        new_instructions = st.text_area(
            "Build Instructions:",
            key="new_cocktail_instructions",
            height=100,
            placeholder="Describe how to build this cocktail..."
        )
        
        # Pricing
        st.markdown("#### 💰 Pricing")
        
        col_price, col_margin = st.columns(2)
        
        # Calculate cost from ingredients
        recipe_cost = 0
        for ing in st.session_state.new_recipe_ingredients:
            unit_cost = get_ingredient_cost_per_unit(ing['product'])
            recipe_cost += unit_cost * ing['amount']
        
        with col_price:
            # Default to suggested price based on 20% margin
            default_price = suggest_price_from_cost(recipe_cost, 0.20) if recipe_cost > 0 else 12.00
            new_price = st.number_input(
                "Sale Price:",
                min_value=0.0,
                value=round(default_price, 0),
                step=0.50,
                key="new_cocktail_price"
            )
        
        with col_margin:
            if new_price > 0 and recipe_cost > 0:
                new_margin = calculate_margin(recipe_cost, new_price)
                st.metric("Calculated Margin", f"{new_margin:.1%}")
            else:
                st.metric("Calculated Margin", "N/A")
        
        st.markdown("---")
        
        # Save button
        if st.button("💾 Save Recipe", key="save_new_recipe", type="primary"):
            # Validation
            if not new_name:
                st.error("Please enter a cocktail name.")
            elif not st.session_state.new_recipe_ingredients:
                st.error("Please add at least one ingredient.")
            elif not new_instructions:
                st.error("Please enter build instructions.")
            else:
                # Check for duplicate name
                existing_names = [r['name'].lower() for r in st.session_state.cocktail_recipes]
                if new_name.lower() in existing_names:
                    st.error(f"A recipe named '{new_name}' already exists.")
                else:
                    # Create new recipe
                    new_recipe = {
                        "name": new_name,
                        "glass": new_glass,
                        "instructions": new_instructions,
                        "sale_price": new_price,
                        "ingredients": st.session_state.new_recipe_ingredients.copy()
                    }
                    
                    # Add to recipes
                    st.session_state.cocktail_recipes.append(new_recipe)
                    
                    # Clear the form
                    st.session_state.new_recipe_ingredients = []
                    
                    # Save to files for persistence
                    save_cocktail_recipes()
                    
                    st.success(f"✅ {new_name} saved successfully!")
                    st.balloons()
                    st.rerun()


# =============================================================================
# MAIN ROUTING LOGIC
# =============================================================================

def main():
    """
    Main application entry point.
    """
    
    init_session_state()
    
    if st.session_state.current_page == 'home':
        show_home()
    elif st.session_state.current_page == 'inventory':
        show_inventory()
    elif st.session_state.current_page == 'ordering':
        show_ordering()
    elif st.session_state.current_page == 'cocktails':
        show_cocktails()
    else:
        show_home()


# =============================================================================
# RUN THE APP
# =============================================================================

if __name__ == "__main__":
    main()
