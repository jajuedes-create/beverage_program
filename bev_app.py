# =============================================================================
# BEVERAGE MANAGEMENT APP V1
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients)
#   - Weekly Order Builder
#   - Cocktail Builds Book
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
    
    # Save historical snapshot for comparison tracking
    save_inventory_snapshot()

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
    page_title="Beverage Management App V1",
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
    """
    data = [
        {"Product": "New Glarus Moon Man", "Category": "Beer", "Par": 3, 
         "Current Inventory": 2, "Unit": "Case", "Unit Cost": 26.40, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Coors Light", "Category": "Beer", "Par": 2, 
         "Current Inventory": 1, "Unit": "Case", "Unit Cost": 24.51, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Fat Squirrel", "Category": "Beer", "Par": 2, 
         "Current Inventory": 1, "Unit": "Case", "Unit Cost": 26.40, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Hop Haus Yard Work IPA", "Category": "Beer", "Par": 1, 
         "Current Inventory": 0.5, "Unit": "Sixtel", "Unit Cost": 75.00, 
         "Distributor": "GB Beer", "Order Notes": ""},
        {"Product": "High Life", "Category": "Beer", "Par": 3, 
         "Current Inventory": 2, "Unit": "Case", "Unit Cost": 21.15, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Tito's", "Category": "Spirits", "Par": 4, 
         "Current Inventory": 3, "Unit": "Bottle", "Unit Cost": 24.50, 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal"},
        {"Product": "Espolòn Blanco", "Category": "Spirits", "Par": 3, 
         "Current Inventory": 2, "Unit": "Bottle", "Unit Cost": 25.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Buffalo Trace", "Category": "Spirits", "Par": 3, 
         "Current Inventory": 2, "Unit": "Bottle", "Unit Cost": 31.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Rittenhouse Rye", "Category": "Spirits", "Par": 2, 
         "Current Inventory": 1, "Unit": "Bottle", "Unit Cost": 28.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Botanist", "Category": "Spirits", "Par": 2, 
         "Current Inventory": 1, "Unit": "Bottle", "Unit Cost": 33.74, 
         "Distributor": "General Beverage", "Order Notes": ""},
        {"Product": "Natalie's Lime Juice", "Category": "Ingredients", "Par": 4, 
         "Current Inventory": 2, "Unit": "Bottle", "Unit Cost": 8.34, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Natalie's Lemon Juice", "Category": "Ingredients", "Par": 4, 
         "Current Inventory": 3, "Unit": "Bottle", "Unit Cost": 8.34, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Agave Nectar", "Category": "Ingredients", "Par": 2, 
         "Current Inventory": 1, "Unit": "Bottle", "Unit Cost": 17.56, 
         "Distributor": "US Foods", "Order Notes": ""},
        {"Product": "Q Club Soda", "Category": "Ingredients", "Par": 3, 
         "Current Inventory": 1, "Unit": "Case", "Unit Cost": 12.48, 
         "Distributor": "Breakthru", "Order Notes": "3cs mix n' match + 1cs Ginger Beer NC"},
        {"Product": "Heavy Cream", "Category": "Ingredients", "Par": 2, 
         "Current Inventory": 1, "Unit": "Quart", "Unit Cost": 9.59, 
         "Distributor": "US Foods", "Order Notes": ""},
    ]
    
    return pd.DataFrame(data)


# =============================================================================
# SAMPLE DATA - ORDER HISTORY
# =============================================================================

def get_sample_order_history():
    """
    Returns a DataFrame with sample historical order data.
    """
    today = datetime.now()
    weeks = []
    for i in range(6, 0, -1):
        week_start = today - timedelta(weeks=i)
        weeks.append(week_start.strftime("%Y-%m-%d"))
    
    data = [
        {"Week": weeks[0], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[0], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[0], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 3, "Unit Cost": 8.34, "Total Cost": 25.02, "Distributor": "US Foods"},
        {"Week": weeks[1], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 24.50, "Total Cost": 24.50, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 31.00, "Total Cost": 62.00, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Coors Light", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 24.51, "Total Cost": 24.51, "Distributor": "Frank Beer"},
        {"Week": weeks[2], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 25.00, "Total Cost": 50.00, "Distributor": "Breakthru"},
        {"Week": weeks[2], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 26.40, "Total Cost": 26.40, "Distributor": "Frank Beer"},
        {"Week": weeks[2], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[2], "Product": "Natalie's Lemon Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[3], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 3, "Unit Cost": 24.50, "Total Cost": 73.50, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "Rittenhouse Rye", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 28.00, "Total Cost": 28.00, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "High Life", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit Cost": 21.15, "Total Cost": 42.30, "Distributor": "Frank Beer"},
        {"Week": weeks[4], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 31.00, "Total Cost": 31.00, "Distributor": "Breakthru"},
        {"Week": weeks[4], "Product": "Botanist", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 33.74, "Total Cost": 67.48, "Distributor": "General Beverage"},
        {"Week": weeks[4], "Product": "Hop Haus Yard Work IPA", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 75.00, "Total Cost": 75.00, "Distributor": "GB Beer"},
        {"Week": weeks[4], "Product": "Q Club Soda", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 12.48, "Total Cost": 24.96, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 25.00, "Total Cost": 25.00, "Distributor": "Breakthru"},
        {"Week": weeks[5], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[5], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[5], "Product": "Heavy Cream", "Category": "Ingredients", 
         "Quantity Ordered": 1, "Unit Cost": 9.59, "Total Cost": 9.59, "Distributor": "US Foods"},
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
                lambda row: row['Cost'] / row['Size (oz.)'] if row['Size (oz.)'] > 0 else 0, 
                axis=1
            )
        
        if 'Cost' in df.columns and 'Inventory' in df.columns:
            df['Value'] = df['Cost'] * df['Inventory']
        
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
            df['Value'] = df['Cost'] * df['Inventory']
        
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
                lambda row: row['Cost per Keg/Case'] / row['Size'] if row['Size'] > 0 else 0, 
                axis=1
            )
        
        if 'Cost per Keg/Case' in df.columns and 'Inventory' in df.columns:
            df['Value'] = df['Cost per Keg/Case'] * df['Inventory']
        
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
                lambda row: row['Cost'] / row['Size/Yield'] if row['Size/Yield'] > 0 else 0, 
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
    """
    needs_order = weekly_inv[weekly_inv['Current Inventory'] < weekly_inv['Par']].copy()
    
    if len(needs_order) == 0:
        return pd.DataFrame()
    
    needs_order['Suggested Order'] = needs_order['Par'] - needs_order['Current Inventory']
    needs_order['Order Quantity'] = needs_order['Suggested Order']
    needs_order['Order Value'] = needs_order['Order Quantity'] * needs_order['Unit Cost']
    
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
# PAGE: HOMESCREEN
# =============================================================================

def show_home():
    """
    Renders the homescreen with navigation cards.
    """
    
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Beverage Management App V1</h1>
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
                format="$%.4f", 
                help="🔒 Calculated: Cost ÷ Size (oz.)",
                disabled=True
            ),
            "Cost/Unit": st.column_config.NumberColumn(
                format="$%.4f",
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
    
    col_save, col_recalc, col_spacer = st.columns([1, 1, 4])
    
    with col_save:
        if st.button(f"💾 Save Changes", key=f"save_{category}"):
            if category == "spirits":
                if "Cost" in edited_df.columns and "Size (oz.)" in edited_df.columns:
                    edited_df["Cost/Oz"] = edited_df["Cost"] / edited_df["Size (oz.)"]
                if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = edited_df["Cost"] * edited_df["Inventory"]
                st.session_state.spirits_inventory = edited_df
            elif category == "wine":
                if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = edited_df["Cost"] * edited_df["Inventory"]
                st.session_state.wine_inventory = edited_df
            elif category == "beer":
                if "Cost per Keg/Case" in edited_df.columns and "Size" in edited_df.columns:
                    edited_df["Cost/Unit"] = edited_df["Cost per Keg/Case"] / edited_df["Size"]
                if "Cost per Keg/Case" in edited_df.columns and "Inventory" in edited_df.columns:
                    edited_df["Value"] = edited_df["Cost per Keg/Case"] * edited_df["Inventory"]
                st.session_state.beer_inventory = edited_df
            elif category == "ingredients":
                if "Cost" in edited_df.columns and "Size/Yield" in edited_df.columns:
                    edited_df["Cost/Unit"] = edited_df["Cost"] / edited_df["Size/Yield"]
                st.session_state.ingredients_inventory = edited_df
            
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            
            # Save to files for persistence
            save_all_inventory_data()
            
            st.success("✅ Changes saved!")
            st.rerun()
    
    with col_recalc:
        if st.button(f"🔄 Recalculate", key=f"recalc_{category}"):
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
        top_products = order_history.groupby('Product').agg({
            'Quantity Ordered': 'sum',
            'Total Cost': 'sum'
        }).sort_values('Total Cost', ascending=False).head(5)
    else:
        prev_week_total = 0
        top_products = pd.DataFrame()
    
    if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
        current_order_total = st.session_state.current_order['Order Value'].sum()
    else:
        current_order_total = 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="📅 Previous Week's Order", value=format_currency(prev_week_total))
    with col2:
        st.metric(label="🛒 Current Order (Building)", value=format_currency(current_order_total))
    with col3:
        st.metric(label="📈 6-Week Avg Order", 
                  value=format_currency(order_history.groupby('Week')['Total Cost'].sum().mean() if len(order_history) > 0 else 0))
    
    if len(top_products) > 0:
        with st.expander("🏆 Top Products (by total spend)", expanded=False):
            st.dataframe(
                top_products.reset_index().rename(columns={
                    'Product': 'Product', 'Quantity Ordered': 'Total Units Ordered', 'Total Cost': 'Total Spend'
                }),
                use_container_width=True, hide_index=True,
                column_config={"Total Spend": st.column_config.NumberColumn(format="$%.2f")}
            )
    
    st.markdown("---")
    
    # Tabs
    tab_build, tab_history, tab_analytics = st.tabs([
        "🛒 Build This Week's Order", "📜 Order History", "📈 Demand Analytics"
    ])
    
    with tab_build:
        st.markdown("### Step 1: Update Current Inventory Counts")
        st.markdown("Enter your current inventory counts below. Products below par will be added to the order.")
        
        weekly_inv = st.session_state.weekly_inventory.copy()
        weekly_inv['Status'] = weekly_inv.apply(
            lambda row: "🔴 Order" if row['Current Inventory'] < row['Par'] else "✅ OK", axis=1
        )
        
        display_cols = ['Product', 'Category', 'Par', 'Current Inventory', 'Status', 
                       'Unit', 'Unit Cost', 'Distributor', 'Order Notes']
        
        edited_weekly = st.data_editor(
            weekly_inv[display_cols],
            use_container_width=True,
            key="weekly_inv_editor",
            column_config={
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Current Inventory": st.column_config.NumberColumn(min_value=0, step=0.5),
                "Par": st.column_config.NumberColumn(min_value=0, step=1),
                "Status": st.column_config.TextColumn(disabled=True),
            },
            disabled=["Product", "Category", "Status", "Unit", "Unit Cost", "Distributor", "Order Notes"]
        )
        
        if st.button("🔄 Update Inventory & Generate Order", key="update_weekly"):
            st.session_state.weekly_inventory['Current Inventory'] = edited_weekly['Current Inventory'].values
            st.session_state.weekly_inventory['Par'] = edited_weekly['Par'].values
            order = generate_order_from_inventory(st.session_state.weekly_inventory)
            st.session_state.current_order = order
            
            # Save weekly inventory to files for persistence
            save_all_inventory_data()
            
            st.success("✅ Inventory updated and order generated!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Step 2: Review & Adjust This Week's Order")
        
        if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
            order_df = st.session_state.current_order.copy()
            st.markdown(f"**{len(order_df)} items need ordering:**")
            
            edited_order = st.data_editor(
                order_df,
                use_container_width=True,
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
            
            if st.button("💰 Recalculate Order Total", key="recalc_order"):
                edited_order['Order Value'] = edited_order['Order Quantity'] * edited_order['Unit Cost']
                st.session_state.current_order = edited_order
                st.rerun()
            
            st.markdown("---")
            st.markdown("### Order Summary")
            
            col_s1, col_s2, col_s3 = st.columns(3)
            with col_s1:
                st.metric("Total Items", len(edited_order))
            with col_s2:
                st.metric("Total Units", f"{edited_order['Order Quantity'].sum():.1f}")
            with col_s3:
                st.metric("Total Order Value", format_currency(edited_order['Order Value'].sum()))
            
            st.markdown("#### By Distributor:")
            dist_summary = edited_order.groupby('Distributor').agg({
                'Order Quantity': 'sum', 'Order Value': 'sum'
            }).reset_index()
            st.dataframe(dist_summary, use_container_width=True, hide_index=True,
                        column_config={"Order Value": st.column_config.NumberColumn(format="$%.2f")})
            
            st.markdown("---")
            if st.button("✅ Save Order to History", key="save_order", type="primary"):
                today = datetime.now().strftime("%Y-%m-%d")
                new_orders = []
                for _, row in edited_order.iterrows():
                    if row['Order Quantity'] > 0:
                        new_orders.append({
                            'Week': today, 'Product': row['Product'], 'Category': row['Category'],
                            'Quantity Ordered': row['Order Quantity'], 'Unit Cost': row['Unit Cost'],
                            'Total Cost': row['Order Value'], 'Distributor': row['Distributor']
                        })
                if new_orders:
                    st.session_state.order_history = pd.concat([
                        st.session_state.order_history, pd.DataFrame(new_orders)
                    ], ignore_index=True)
                    st.session_state.current_order = pd.DataFrame()
                    
                    # Save to files for persistence
                    save_all_inventory_data()
                    
                    st.success("✅ Order saved to history!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("No items with quantity > 0 to save.")
        else:
            st.info("👆 Update inventory counts above and click 'Update Inventory & Generate Order' to see what needs ordering.")
    
    with tab_history:
        st.markdown("### 📜 Previous Orders")
        if len(order_history) > 0:
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                weeks = sorted(order_history['Week'].unique(), reverse=True)
                selected_weeks = st.multiselect("Filter by Week:", options=weeks,
                    default=weeks[:4] if len(weeks) >= 4 else weeks, key="history_week_filter")
            with col_f2:
                categories = order_history['Category'].unique().tolist()
                selected_categories = st.multiselect("Filter by Category:", options=categories,
                    default=categories, key="history_category_filter")
            
            filtered_history = order_history.copy()
            if selected_weeks:
                filtered_history = filtered_history[filtered_history['Week'].isin(selected_weeks)]
            if selected_categories:
                filtered_history = filtered_history[filtered_history['Category'].isin(selected_categories)]
            
            st.markdown("#### Weekly Order Totals")
            weekly_totals = filtered_history.groupby('Week')['Total Cost'].sum().reset_index()
            weekly_totals = weekly_totals.sort_values('Week', ascending=False)
            st.dataframe(weekly_totals, use_container_width=True, hide_index=True,
                        column_config={"Total Cost": st.column_config.NumberColumn(format="$%.2f")})
            
            st.markdown("#### Order Details")
            st.dataframe(filtered_history.sort_values(['Week', 'Product'], ascending=[False, True]),
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Total Cost": st.column_config.NumberColumn(format="$%.2f")
                        })
        else:
            st.info("No order history yet. Save an order to see it here.")
    
    with tab_analytics:
        st.markdown("### 📈 Demand Analytics")
        if len(order_history) > 0:
            products = sorted(order_history['Product'].unique())
            selected_products = st.multiselect("Select products to analyze:", options=products,
                default=products[:3] if len(products) >= 3 else products, key="analytics_products")
            
            if selected_products:
                plot_data = order_history[order_history['Product'].isin(selected_products)]
                
                st.markdown("#### Quantity Ordered Over Time")
                fig_qty = px.line(plot_data, x='Week', y='Quantity Ordered', color='Product',
                                 markers=True, title='Weekly Order Quantities by Product')
                st.plotly_chart(fig_qty, use_container_width=True)
                
                st.markdown("#### Spending Over Time")
                fig_cost = px.line(plot_data, x='Week', y='Total Cost', color='Product',
                                  markers=True, title='Weekly Spending by Product')
                st.plotly_chart(fig_cost, use_container_width=True)
                
                st.markdown("#### Product Summary Statistics")
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
            st.markdown("#### Spending by Category")
            cat_spend = order_history.groupby('Category')['Total Cost'].sum().reset_index()
            fig_pie = px.pie(cat_spend, values='Total Cost', names='Category', title='Total Spending by Category')
            st.plotly_chart(fig_pie, use_container_width=True)
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
