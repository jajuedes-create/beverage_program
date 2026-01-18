# =============================================================================
# BEVERAGE MANAGEMENT APP - BUTTERBIRD V1
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients)
#   - Weekly Order Builder
#   - Cocktail Builds Book
#   - Cost of Goods Sold (COGS) Calculator
#   - Bar Prep Recipe Book
#
# Version History:
#   BETA 1.0 - Base template with CLIENT_CONFIG system
#   bb_V1 - Initial Butterbird deployment (clean slate, no sample data)
#
# Developed by: James Juedes utilizing Claude Opus 4.5
# Deployment: Streamlit Community Cloud via GitHub
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import math
from typing import Optional, Dict, List, Any, Tuple

# =============================================================================
# CLIENT CONFIGURATION
# =============================================================================
# Customize these settings for each client/restaurant deployment.
# When creating a new client branch, copy this file and modify CLIENT_CONFIG.

CLIENT_CONFIG = {
    # -------------------------------------------------------------------------
    # Restaurant Information
    # -------------------------------------------------------------------------
    "restaurant_name": "Butterbird",
    "restaurant_tagline": "Manage your inventory, build orders, track cost of goods sold, and store all of your recipes.",
    
    # -------------------------------------------------------------------------
    # Inventory Location Names
    # -------------------------------------------------------------------------
    # Customize these to match the restaurant's physical layout.
    # These names appear in Master Inventory and Weekly Order Builder.
    "locations": {
        "location_1": "Bar",
        "location_2": "Back Bar",
        "location_3": "Storage",
    },
    
    # -------------------------------------------------------------------------
    # Branding Colors (hex codes)
    # -------------------------------------------------------------------------
    "colors": {
        "primary": "#1E3A5F",           # Headers, primary buttons
        "primary_light": "#2E5077",     # Hover states
        "secondary": "#2E7D32",         # Success messages, accents
        "background": "#f5f5f5",        # Page background
        "card_text": "#ffffff",         # Text on colored cards
        "muted_text": "#666666",        # Subtitles, captions
        # Module card gradients
        "card_inventory": ["#11998e", "#38ef7d"],
        "card_ordering": ["#ee0979", "#ff6a00"],
        "card_cocktails": ["#8E2DE2", "#4A00E0"],
        "card_barprep": ["#10B981", "#059669"],
        "card_cogs": ["#F59E0B", "#D97706"],
    },
    
    # -------------------------------------------------------------------------
    # Branding Fonts
    # -------------------------------------------------------------------------
    # Google Fonts names - these will be imported via CSS
    "fonts": {
        "heading": "Inter",             # Used for h1, h2, card titles
        "body": "Inter",                # Used for body text, tables
        "mono": "JetBrains Mono",       # Used for code, numbers
    },
    
    # -------------------------------------------------------------------------
    # Feature Toggles
    # -------------------------------------------------------------------------
    # Set to False to hide modules from navigation and home screen
    "features": {
        "master_inventory": True,
        "weekly_orders": True,
        "cocktail_builds": True,
        "bar_prep": True,
        "cogs_calculator": True,
    },
    
    # -------------------------------------------------------------------------
    # Default Distributors
    # -------------------------------------------------------------------------
    # Pre-populate distributor dropdowns with these options
    "distributors": [
        "",
    ],
    
    # -------------------------------------------------------------------------
    # Default Margins by Category
    # -------------------------------------------------------------------------
    # Used when adding new products without specifying margin
    "default_margins": {
        "spirits": 20,
        "wine": 35,
        "beer": 20,
    },
    
    # -------------------------------------------------------------------------
    # Google Sheets Configuration
    # -------------------------------------------------------------------------
    # Sheet names for data persistence (actual spreadsheet_id is in secrets.toml)
    "google_sheets": {
        "spirits_inventory": "spirits_inventory",
        "wine_inventory": "wine_inventory",
        "beer_inventory": "beer_inventory",
        "ingredients_inventory": "ingredients_inventory",
        "weekly_inventory": "weekly_inventory",
        "order_history": "order_history",
        "pending_order": "pending_order",
        "cocktail_recipes": "cocktail_recipes",
        "bar_prep_recipes": "bar_prep_recipes",
        "inventory_history": "inventory_history",
        "cogs_history": "cogs_history",
        "price_change_acks": "price_change_acks",
    },
}


# =============================================================================
# HELPER FUNCTIONS FOR CONFIG ACCESS
# =============================================================================

def get_location_name(location_key: str) -> str:
    """Gets the display name for a location from config."""
    return CLIENT_CONFIG["locations"].get(location_key, location_key)


def get_location_1() -> str:
    """Returns the name of location 1."""
    return CLIENT_CONFIG["locations"]["location_1"]


def get_location_2() -> str:
    """Returns the name of location 2."""
    return CLIENT_CONFIG["locations"]["location_2"]


def get_location_3() -> str:
    """Returns the name of location 3."""
    return CLIENT_CONFIG["locations"]["location_3"]


def get_sheet_name(key: str) -> str:
    """Gets the Google Sheet name for a given data type."""
    return CLIENT_CONFIG["google_sheets"].get(key, key)


def is_feature_enabled(feature: str) -> bool:
    """Checks if a feature is enabled in config."""
    return CLIENT_CONFIG["features"].get(feature, True)


def get_default_margin(category: str) -> int:
    """Gets the default margin for a category."""
    return CLIENT_CONFIG["default_margins"].get(category.lower(), 20)


def get_distributors() -> list:
    """Gets the list of configured distributors."""
    return CLIENT_CONFIG["distributors"]


# =============================================================================
# PAGE CONFIG (must be first Streamlit command)
# =============================================================================

st.set_page_config(
    page_title=f"{CLIENT_CONFIG['restaurant_name']} - Beverage Management",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# GOOGLE SHEETS DATA PERSISTENCE
# =============================================================================

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSHEETS_AVAILABLE = True
except ImportError:
    GSHEETS_AVAILABLE = False


@st.cache_resource
def get_google_sheets_connection():
    """Creates and caches a connection to Google Sheets."""
    if not GSHEETS_AVAILABLE:
        return None
    try:
        if "gcp_service_account" not in st.secrets:
            return None
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        return None


@st.cache_resource
def get_spreadsheet():
    """Gets the configured spreadsheet (cached)."""
    client = get_google_sheets_connection()
    if client is None:
        return None
    try:
        spreadsheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        return client.open_by_key(spreadsheet_id)
    except Exception as e:
        st.error(f"Error opening spreadsheet: {e}")
        return None


def is_google_sheets_configured() -> bool:
    """Checks if Google Sheets is properly configured."""
    return get_google_sheets_connection() is not None


def get_or_create_worksheet(spreadsheet, sheet_name: str):
    """Gets a worksheet by name, creating it if it doesn't exist."""
    try:
        return spreadsheet.worksheet(sheet_name)
    except gspread.WorksheetNotFound:
        return spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=26)


# =============================================================================
# DATA PERSISTENCE FUNCTIONS
# =============================================================================

def save_dataframe_to_sheets(df: pd.DataFrame, sheet_name: str) -> bool:
    """Saves a DataFrame to Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        worksheet.clear()
        df_clean = df.fillna("")
        data = [df_clean.columns.tolist()] + df_clean.values.tolist()
        worksheet.update(data, value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"Error saving to Google Sheets ({sheet_name}): {e}")
        return False


def load_dataframe_from_sheets(sheet_name: str) -> Optional[pd.DataFrame]:
    """Loads a DataFrame from Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        if len(data) < 2:
            return None
        df = pd.DataFrame(data[1:], columns=data[0])
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
        return df
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        st.error(f"Error loading from Google Sheets ({sheet_name}): {e}")
        return None


def save_json_to_sheets(data: list, sheet_name: str) -> bool:
    """Saves JSON data to Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        worksheet.clear()
        json_str = json.dumps(data)
        worksheet.update([[json_str]], value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"Error saving JSON to Google Sheets ({sheet_name}): {e}")
        return False


def load_json_from_sheets(sheet_name: str) -> Optional[list]:
    """Loads JSON data from Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        if len(data) < 1 or len(data[0]) < 1:
            return None
        return json.loads(data[0][0])
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        st.error(f"Error loading JSON from Google Sheets ({sheet_name}): {e}")
        return None


def save_text_to_sheets(text: str, sheet_name: str) -> bool:
    """Saves text data to Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return False
    try:
        worksheet = get_or_create_worksheet(spreadsheet, sheet_name)
        worksheet.clear()
        worksheet.update([[text]], value_input_option='RAW')
        return True
    except Exception as e:
        st.error(f"Error saving text to Google Sheets ({sheet_name}): {e}")
        return False


def load_text_from_sheets(sheet_name: str) -> Optional[str]:
    """Loads text data from Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return None
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
        data = worksheet.get_all_values()
        if len(data) < 1 or len(data[0]) < 1:
            return None
        return data[0][0]
    except gspread.WorksheetNotFound:
        return None
    except Exception as e:
        return None


# =============================================================================
# SAVE FUNCTIONS (Consolidated) - Using CLIENT_CONFIG sheet names
# =============================================================================

def save_all_inventory_data():
    """Saves all inventory DataFrames to Google Sheets."""
    if not is_google_sheets_configured():
        return
    inventory_mappings = [
        ('spirits_inventory', get_sheet_name('spirits_inventory')),
        ('wine_inventory', get_sheet_name('wine_inventory')),
        ('beer_inventory', get_sheet_name('beer_inventory')),
        ('ingredients_inventory', get_sheet_name('ingredients_inventory')),
        ('weekly_inventory', get_sheet_name('weekly_inventory')),
        ('order_history', get_sheet_name('order_history')),
    ]
    for key, sheet in inventory_mappings:
        if key in st.session_state:
            save_dataframe_to_sheets(st.session_state[key], sheet)


def save_pending_order():
    """Saves pending order to Google Sheets."""
    if not is_google_sheets_configured():
        return
    if 'current_order' in st.session_state:
        save_dataframe_to_sheets(st.session_state.current_order, get_sheet_name('pending_order'))


def clear_pending_order():
    """Clears pending order from Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return
    try:
        worksheet = get_or_create_worksheet(spreadsheet, get_sheet_name('pending_order'))
        worksheet.clear()
    except Exception:
        pass


def save_price_change_acks():
    """Saves price change acknowledgments."""
    if not is_google_sheets_configured():
        return
    if 'price_change_acks' in st.session_state:
        acks_text = json.dumps(st.session_state.price_change_acks)
        save_text_to_sheets(acks_text, get_sheet_name('price_change_acks'))


def load_price_change_acks() -> dict:
    """Loads price change acknowledgments."""
    if not is_google_sheets_configured():
        return {}
    text = load_text_from_sheets(get_sheet_name('price_change_acks'))
    if text:
        try:
            return json.loads(text)
        except:
            return {}
    return {}


def save_recipes(recipe_type: str):
    """Generic function to save recipes (cocktails or bar_prep)."""
    if not is_google_sheets_configured():
        return
    key = f'{recipe_type}_recipes'
    if key in st.session_state:
        save_json_to_sheets(st.session_state[key], get_sheet_name(key))


def save_inventory_snapshot():
    """Saves a snapshot of current inventory values."""
    if not is_google_sheets_configured():
        return
    
    values = {
        'spirits': calculate_total_value(st.session_state.get('spirits_inventory', pd.DataFrame())),
        'wine': calculate_total_value(st.session_state.get('wine_inventory', pd.DataFrame())),
        'beer': calculate_total_value(st.session_state.get('beer_inventory', pd.DataFrame())),
        'ingredients': calculate_total_value(st.session_state.get('ingredients_inventory', pd.DataFrame())),
    }
    values['total'] = sum(values.values())
    
    new_record = {
        'Date': datetime.now().strftime("%Y-%m-%d"),
        'Spirits Value': values['spirits'],
        'Wine Value': values['wine'],
        'Beer Value': values['beer'],
        'Ingredients Value': values['ingredients'],
        'Total Value': values['total']
    }
    
    history = load_inventory_history()
    if history is None:
        history = pd.DataFrame(columns=new_record.keys())
    
    history = pd.concat([history, pd.DataFrame([new_record])], ignore_index=True)
    save_dataframe_to_sheets(history, get_sheet_name('inventory_history'))


def load_inventory_history() -> Optional[pd.DataFrame]:
    """Loads inventory history."""
    if not is_google_sheets_configured():
        return None
    history = load_dataframe_from_sheets(get_sheet_name('inventory_history'))
    if history is not None and len(history) > 0:
        for col in ['Spirits Value', 'Wine Value', 'Beer Value', 'Ingredients Value', 'Total Value']:
            if col in history.columns:
                history[col] = pd.to_numeric(history[col], errors='coerce').fillna(0)
    return history


def save_cogs_calculation(cogs_data: dict) -> bool:
    """Saves a COGS calculation to history."""
    if not is_google_sheets_configured():
        return False
    history = load_cogs_history()
    if history is None:
        history = pd.DataFrame()
    history = pd.concat([history, pd.DataFrame([cogs_data])], ignore_index=True)
    return save_dataframe_to_sheets(history, get_sheet_name('cogs_history'))


def load_cogs_history() -> Optional[pd.DataFrame]:
    """Loads COGS calculation history."""
    if not is_google_sheets_configured():
        return None
    history = load_dataframe_from_sheets(get_sheet_name('cogs_history'))
    if history is not None and len(history) > 0:
        numeric_cols = ['Spirits COGS', 'Wine COGS', 'Beer COGS', 'Ingredients COGS',
                       'Bar COGS', 'Total COGS', 'Total Purchases',
                       'Wine Sales', 'Beer Sales', 'Bar Sales', 'Total Sales',
                       'Wine COGS %', 'Beer COGS %', 'Bar COGS %', 'Total COGS %',
                       'COGS Percentage']
        for col in numeric_cols:
            if col in history.columns:
                history[col] = pd.to_numeric(history[col], errors='coerce').fillna(0)
        if 'Calculation Date' in history.columns:
            history = history.sort_values('Calculation Date', ascending=False)
    return history


def get_purchases_by_category_and_date(start_date: str, end_date: str) -> dict:
    """Calculates total purchases by category from Order History."""
    purchases = {'Spirits': 0.0, 'Wine': 0.0, 'Beer': 0.0, 'Ingredients': 0.0}
    
    order_history = st.session_state.get('order_history', pd.DataFrame())
    if len(order_history) == 0:
        return purchases
    
    df = order_history.copy()
    
    # Use Invoice Date if available, otherwise Week
    date_col = 'Invoice Date' if 'Invoice Date' in df.columns else 'Week'
    if date_col not in df.columns:
        return purchases
    
    # Filter by date range
    try:
        if date_col == 'Invoice Date':
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            mask = (df[date_col] >= start) & (df[date_col] <= end)
        else:
            mask = (df[date_col] >= start_date) & (df[date_col] <= end_date)
        df = df[mask]
    except Exception:
        pass
    
    if len(df) == 0:
        return purchases
    
    # Sum by category
    if 'Category' in df.columns and 'Total Cost' in df.columns:
        for cat in purchases.keys():
            cat_df = df[df['Category'] == cat]
            if len(cat_df) > 0:
                purchases[cat] = float(cat_df['Total Cost'].sum())
    
    return purchases


# =============================================================================
# CUSTOM CSS (Generated from CLIENT_CONFIG)
# =============================================================================

def generate_custom_css() -> str:
    """Generates CSS based on CLIENT_CONFIG values."""
    colors = CLIENT_CONFIG["colors"]
    fonts = CLIENT_CONFIG["fonts"]
    
    # Build Google Fonts import URL
    font_families = set([fonts["heading"], fonts["body"], fonts["mono"]])
    font_import = ", ".join([f"family={f.replace(' ', '+')}:wght@400;500;600;700" for f in font_families])
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?{font_import}&display=swap');
        
        /* Base font settings */
        html, body, [class*="css"] {{
            font-family: '{fonts["body"]}', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        h1, h2, h3, .card-title {{
            font-family: '{fonts["heading"]}', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        code, pre, .stDataFrame {{
            font-family: '{fonts["mono"]}', 'Courier New', monospace;
        }}
        
        .main-header {{ text-align: center; padding: 1rem 0 2rem 0; }}
        .main-header h1 {{ color: {colors["primary"]}; margin-bottom: 0.5rem; }}
        .main-header p {{ color: {colors["muted_text"]}; font-size: 1.1rem; max-width: 600px; margin: 0 auto; }}
        
        .module-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 2rem;
            color: {colors["card_text"]};
            margin-bottom: 0.5rem;
            min-height: 180px;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .module-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .card-inventory {{ background: linear-gradient(135deg, {colors["card_inventory"][0]} 0%, {colors["card_inventory"][1]} 100%); }}
        .card-ordering {{ background: linear-gradient(135deg, {colors["card_ordering"][0]} 0%, {colors["card_ordering"][1]} 100%); }}
        .card-cocktails {{ background: linear-gradient(135deg, {colors["card_cocktails"][0]} 0%, {colors["card_cocktails"][1]} 100%); }}
        .card-barprep {{ background: linear-gradient(135deg, {colors["card_barprep"][0]} 0%, {colors["card_barprep"][1]} 100%); }}
        .card-cogs {{ background: linear-gradient(135deg, {colors["card_cogs"][0]} 0%, {colors["card_cogs"][1]} 100%); }}
        
        .card-icon {{ font-size: 3rem; margin-bottom: 1rem; }}
        .card-title {{ font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }}
        .card-description {{ font-size: 0.95rem; opacity: 0.9; }}
        
        .stMetric {{ background-color: #f8f9fa; padding: 1rem; border-radius: 10px; }}
        
        /* Primary button styling */
        .stButton > button[kind="primary"] {{
            background-color: {colors["primary"]};
            border-color: {colors["primary"]};
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {colors["primary_light"]};
            border-color: {colors["primary_light"]};
        }}
        
        /* Hide button borders for card buttons */
        .card-button > button {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            width: 100%;
        }}
    </style>
    """
    return css


# Inject the CSS
st.markdown(generate_custom_css(), unsafe_allow_html=True)


# =============================================================================
# UTILITY FUNCTIONS (Consolidated)
# =============================================================================

def format_currency(value: float) -> str:
    """Formats a number as currency."""
    try:
        return f"${float(value):,.2f}"
    except (ValueError, TypeError):
        return "$0.00"


def clean_currency_value(value) -> float:
    """Cleans a currency value to float."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace('$', '').replace(',', '').replace('%', '').strip()
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    return 0.0


def clean_currency_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Cleans currency formatting from a DataFrame column."""
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(clean_currency_value)
    return df


def clean_percentage_value(value) -> float:
    """Cleans a percentage value."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        val = float(value)
        return val if val <= 100 else val / 100
    if isinstance(value, str):
        cleaned = value.replace('%', '').replace('$', '').replace(',', '').strip()
        try:
            val = float(cleaned) if cleaned else 0.0
            return val if val <= 100 else val / 100
        except ValueError:
            return 0.0
    return 0.0


def clean_percentage_column(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Cleans percentage formatting from a DataFrame column."""
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(clean_percentage_value)
    return df


def calculate_total_value(df: pd.DataFrame) -> float:
    """Calculates total value from a DataFrame."""
    if df is None or len(df) == 0:
        return 0.0
    if 'Value' in df.columns:
        try:
            return float(df['Value'].sum())
        except:
            return 0.0
    return 0.0


def filter_dataframe(df: pd.DataFrame, search_term: str, column_filters: dict) -> pd.DataFrame:
    """Filters a DataFrame by search term and column filters."""
    filtered = df.copy()
    if search_term and 'Product' in filtered.columns:
        filtered = filtered[filtered['Product'].str.contains(search_term, case=False, na=False)]
    for col, values in column_filters.items():
        if col in filtered.columns and values:
            filtered = filtered[filtered[col].isin(values)]
    return filtered


# =============================================================================
# UNIFIED COST LOOKUP (V3.0 Optimization)
# =============================================================================

def get_product_cost(product_name: str, amount: float = 1.0, unit: str = 'oz') -> Tuple[float, float]:
    """
    Unified function to get product cost from any inventory.
    Returns (cost_per_unit, total_cost)
    
    Checks: Spirits (Cost/Oz), Ingredients (Cost/Unit)
    """
    product_lower = product_name.lower().strip()
    
    # Check Spirits inventory
    spirits_df = st.session_state.get('spirits_inventory', pd.DataFrame())
    if len(spirits_df) > 0 and 'Product' in spirits_df.columns:
        match = spirits_df[spirits_df['Product'].str.lower().str.strip() == product_lower]
        if len(match) > 0 and 'Cost/Oz' in match.columns:
            cost_per_oz = float(match['Cost/Oz'].iloc[0] or 0)
            return (cost_per_oz, cost_per_oz * amount)
    
    # Check Ingredients inventory
    ingredients_df = st.session_state.get('ingredients_inventory', pd.DataFrame())
    if len(ingredients_df) > 0 and 'Product' in ingredients_df.columns:
        match = ingredients_df[ingredients_df['Product'].str.lower().str.strip() == product_lower]
        if len(match) > 0 and 'Cost/Unit' in match.columns:
            cost_per_unit = float(match['Cost/Unit'].iloc[0] or 0)
            return (cost_per_unit, cost_per_unit * amount)
    
    return (0.0, 0.0)


def calculate_recipe_cost(ingredients: list) -> float:
    """Calculates total cost for a recipe's ingredients."""
    return sum(get_product_cost(ing['product'], ing['amount'], ing.get('unit', 'oz'))[1] 
               for ing in ingredients)


def get_all_available_products() -> list:
    """Returns a list of all available products for dropdowns."""
    products = set()
    
    # Spirits
    spirits_df = st.session_state.get('spirits_inventory', pd.DataFrame())
    if len(spirits_df) > 0 and 'Product' in spirits_df.columns:
        products.update(spirits_df['Product'].tolist())
    
    # Ingredients
    ingredients_df = st.session_state.get('ingredients_inventory', pd.DataFrame())
    if len(ingredients_df) > 0 and 'Product' in ingredients_df.columns:
        products.update(ingredients_df['Product'].tolist())
    
    return sorted(list(products))


def calculate_suggested_orders(inventory_df: pd.DataFrame) -> pd.DataFrame:
    """Generates suggested orders based on current inventory vs par levels."""
    if len(inventory_df) == 0:
        return pd.DataFrame()
    
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    orders = []
    for _, row in inventory_df.iterrows():
        par = row.get('Par', 0)
        if par <= 0:
            continue
        
        # Get location values with fallbacks
        loc1_val = row.get(loc1, row.get('Bar Inventory', 0))
        loc2_val = row.get(loc2, row.get('Storage Inventory', 0))
        loc3_val = row.get(loc3, 0)
        
        total_inv = row.get('Total Current Inventory', 
                          row.get('Total Inventory', loc1_val + loc2_val + loc3_val))
        
        if total_inv < par:
            order_qty = par - total_inv
            unit_cost = row.get('Unit Cost', 0)
            orders.append({
                'Product': row['Product'],
                'Category': row.get('Category', 'Unknown'),
                'Current Stock': total_inv,
                'Par Level': par,
                'Order Quantity': order_qty,
                'Unit': row.get('Unit', ''),
                'Unit Cost': unit_cost,
                'Order Value': order_qty * unit_cost,
                'Distributor': row.get('Distributor', 'N/A'),
            })
    
    return pd.DataFrame(orders) if orders else pd.DataFrame()


# =============================================================================
# EMPTY DATA FUNCTIONS (Clean Slate) - Using CLIENT_CONFIG locations
# =============================================================================

@st.cache_data
def get_sample_spirits():
    """Returns empty spirit inventory DataFrame with proper columns."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    columns = ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Cost/Oz", "Neat Price",
               loc1, loc2, loc3, "Total Inventory", "Value", "Use", "Distributor", "Order Notes", "Suggested Retail"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_wines():
    """Returns empty wine inventory DataFrame with proper columns."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    columns = ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Bottle Price", 
               loc1, loc2, loc3, "Total Inventory",
               "Value", "Distributor", "Order Notes", "BTG", "Suggested Retail"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_beers():
    """Returns empty beer inventory DataFrame with proper columns."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    columns = ["Product", "Type", "Cost per Keg/Case", "Size", "UoM", 
               "Cost/Unit", "Margin", "Menu Price", loc1, loc2, loc3,
               "Total Inventory", "Value", "Distributor", "Order Notes"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_ingredients():
    """Returns empty ingredient inventory DataFrame with proper columns."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    columns = ["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit", 
               loc1, loc2, loc3, "Total Inventory",
               "Distributor", "Order Notes"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_weekly_inventory():
    """Returns empty weekly inventory DataFrame with proper columns."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    columns = ["Product", "Category", "Par", loc1, loc2, loc3, 
               "Total Current Inventory", "Unit", "Unit Cost", "Distributor", "Order Notes"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_order_history():
    """Returns empty order history DataFrame with proper columns."""
    columns = ["Week", "Product", "Category", "Order Quantity", "Unit Cost", 
               "Total Cost", "Distributor", "Invoice #", "Invoice Date"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_cocktails():
    """Returns empty cocktail recipes list."""
    return []


@st.cache_data
def get_sample_bar_prep_recipes():
    """Returns empty bar prep recipes list."""
    return []


# =============================================================================
# SESSION STATE INITIALIZATION (Optimized)
# =============================================================================

def init_session_state():
    """Initializes all session state variables (optimized)."""
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    sheets_configured = is_google_sheets_configured()
    
    # Inventory data - consolidated loading
    inventory_loaders = {
        'spirits_inventory': (get_sheet_name('spirits_inventory'), get_sample_spirits),
        'wine_inventory': (get_sheet_name('wine_inventory'), get_sample_wines),
        'beer_inventory': (get_sheet_name('beer_inventory'), get_sample_beers),
        'ingredients_inventory': (get_sheet_name('ingredients_inventory'), get_sample_ingredients),
        'weekly_inventory': (get_sheet_name('weekly_inventory'), get_sample_weekly_inventory),
        'order_history': (get_sheet_name('order_history'), get_sample_order_history),
    }
    
    for key, (sheet_name, sample_func) in inventory_loaders.items():
        if key not in st.session_state:
            saved_data = load_dataframe_from_sheets(sheet_name) if sheets_configured else None
            st.session_state[key] = saved_data if saved_data is not None and len(saved_data) > 0 else sample_func()
    
    # Recipe data
    recipe_loaders = {
        'cocktail_recipes': (get_sheet_name('cocktail_recipes'), get_sample_cocktails),
        'bar_prep_recipes': (get_sheet_name('bar_prep_recipes'), get_sample_bar_prep_recipes),
    }
    
    for key, (sheet_name, sample_func) in recipe_loaders.items():
        if key not in st.session_state:
            saved_data = load_json_from_sheets(sheet_name) if sheets_configured else None
            st.session_state[key] = saved_data if saved_data and len(saved_data) > 0 else sample_func()
    
    # Other state
    if 'last_inventory_date' not in st.session_state:
        st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
    
    if 'current_order' not in st.session_state:
        saved_order = load_dataframe_from_sheets(get_sheet_name('pending_order')) if sheets_configured else None
        st.session_state.current_order = saved_order if saved_order is not None and len(saved_order) > 0 else pd.DataFrame()
    
    if 'price_change_acks' not in st.session_state:
        st.session_state.price_change_acks = load_price_change_acks() if sheets_configured else {}


# =============================================================================
# NAVIGATION (with Feature Toggles)
# =============================================================================

def navigate_to(page: str):
    """Sets the current page in session state."""
    st.session_state.current_page = page


def show_sidebar_navigation():
    """Displays sidebar navigation with feature toggles applied."""
    with st.sidebar:
        st.markdown(f"### 🍸 {CLIENT_CONFIG['restaurant_name']}")
        st.markdown("---")
        
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            navigate_to('home')
            st.rerun()
        
        st.markdown("")
        current = st.session_state.current_page
        
        # Navigation items with feature toggle checks
        nav_items = [
            ('inventory', '📦 Master Inventory', 'master_inventory'),
            ('ordering', '📋 Weekly Orders', 'weekly_orders'),
            ('cocktails', '🍹 Cocktail Builds', 'cocktail_builds'),
            ('bar_prep', '🧪 Bar Prep', 'bar_prep'),
            ('cogs', '📊 COGS Calculator', 'cogs_calculator'),
        ]
        
        for page_id, label, feature_key in nav_items:
            # Only show if feature is enabled
            if is_feature_enabled(feature_key):
                display_label = label + (" ●" if current == page_id else "")
                if st.button(display_label, key=f"nav_{page_id}", use_container_width=True, disabled=(current == page_id)):
                    navigate_to(page_id)
                    st.rerun()
        
        st.markdown("---")
        st.caption("Beverage Management App")


# =============================================================================
# REUSABLE UI COMPONENTS
# =============================================================================

def display_recipe_card(recipe: dict, recipe_type: str, idx: int, on_delete=None):
    """
    Reusable recipe card display for both Cocktails and Bar Prep.
    """
    # Calculate costs
    total_cost = calculate_recipe_cost(recipe.get('ingredients', []))
    
    # Create a safe key from recipe name
    safe_name = recipe['name'].replace(' ', '_').replace('/', '_').replace("'", "")
    
    if recipe_type == 'bar_prep':
        yield_oz = recipe.get('yield_oz', 32)
        cost_per_oz = total_cost / yield_oz if yield_oz > 0 else 0
        header = f"**{recipe['name']}** | Yield: {recipe.get('yield_description', '')} | Batch: {format_currency(total_cost)} | Cost/oz: {format_currency(cost_per_oz)}"
    else:
        sale_price = recipe.get('sale_price', 0)
        margin = ((sale_price - total_cost) / sale_price * 100) if sale_price > 0 else 0
        header = f"**{recipe['name']}** | Cost: {format_currency(total_cost)} | Price: {format_currency(sale_price)} | Margin: {margin:.1f}%"
    
    with st.expander(header, expanded=False):
        col_info, col_cost = st.columns([2, 1])
        
        with col_info:
            if recipe_type == 'bar_prep':
                st.markdown(f"**Yield:** {recipe.get('yield_description', '')} ({recipe.get('yield_oz', 0)} oz)")
                st.markdown(f"**Shelf Life:** {recipe.get('shelf_life', 'N/A')}")
                st.markdown(f"**Storage:** {recipe.get('storage', 'N/A')}")
            else:
                st.markdown(f"**Glass:** {recipe.get('glass', 'N/A')}")
                st.markdown(f"**Sale Price:** {format_currency(recipe.get('sale_price', 0))}")
            
            # Ingredients table
            st.markdown("**Ingredients:**")
            ing_data = []
            for ing in recipe.get('ingredients', []):
                _, ing_cost = get_product_cost(ing['product'], ing['amount'], ing.get('unit', 'oz'))
                ing_data.append({
                    "Ingredient": ing['product'],
                    "Amount": ing['amount'],
                    "Unit": ing.get('unit', 'oz'),
                    "Cost": ing_cost
                })
            
            if ing_data:
                st.dataframe(
                    pd.DataFrame(ing_data),
                    use_container_width=True,
                    hide_index=True,
                    column_config={"Cost": st.column_config.NumberColumn(format="$%.4f")}
                )
            
            if recipe.get('instructions'):
                st.markdown("**Instructions:**")
                st.text(recipe['instructions'])
        
        with col_cost:
            st.markdown("#### 💰 Costing")
            st.metric("Total Cost", format_currency(total_cost))
            
            if recipe_type == 'bar_prep':
                st.metric("Cost/oz", format_currency(cost_per_oz))
                st.metric("Cost/quart", format_currency(cost_per_oz * 32))
            else:
                st.metric("Sale Price", format_currency(recipe.get('sale_price', 0)))
                st.metric("Margin", f"{margin:.1f}%")
        
        if on_delete:
            st.markdown("---")
            if st.button("🗑️ Delete Recipe", key=f"delete_{recipe_type}_{safe_name}"):
                on_delete(recipe['name'])


def display_recipe_list(recipes: list, recipe_type: str, category_filter: str = None, session_key: str = None):
    """Displays a filtered list of recipes."""
    filtered = recipes
    if category_filter:
        filtered = [r for r in recipes if r.get('category') == category_filter]
    
    def delete_recipe(name):
        if session_key:
            st.session_state[session_key] = [r for r in st.session_state.get(session_key, []) if r['name'] != name]
            save_recipes(recipe_type)
            st.rerun()
    
    if filtered:
        # Search filter
        search = st.text_input("🔍 Search recipes", key=f"search_{recipe_type}_{category_filter or 'all'}")
        if search:
            filtered = [r for r in filtered if search.lower() in r['name'].lower()]
        
        for idx, recipe in enumerate(filtered):
            display_recipe_card(recipe, recipe_type, idx, on_delete=delete_recipe)
        
        st.markdown("---")
        st.markdown(f"**Total recipes:** {len(filtered)}")
    else:
        st.info(f"No {category_filter or recipe_type} recipes found. Add some to get started!")
    
    # Add new recipe button
    if st.button(f"➕ Add New {'Bar Prep' if recipe_type == 'bar_prep' else 'Cocktail'} Recipe", 
                 key=f"add_{recipe_type}_{category_filter or 'all'}"):
        show_add_recipe_form(recipe_type, category_filter)


def show_add_recipe_form(recipe_type: str, category: str = None):
    """Shows a form for adding new recipes."""
    st.markdown("---")
    st.markdown("### ➕ Add New Recipe")
    
    with st.form(f"add_{recipe_type}_form"):
        name = st.text_input("Recipe Name")
        
        if recipe_type == 'bar_prep':
            category = st.selectbox("Category", ["Syrups", "Batched Cocktails"])
            yield_desc = st.text_input("Yield Description (e.g., '1 quart')")
            yield_oz = st.number_input("Yield (oz)", min_value=1, value=32)
            shelf_life = st.text_input("Shelf Life")
            storage = st.text_input("Storage Instructions")
        else:
            glass = st.text_input("Glass Type")
            sale_price = st.number_input("Sale Price", min_value=0.0, step=0.50)
        
        instructions = st.text_area("Instructions")
        
        # Ingredients (simplified - 5 slots)
        st.markdown("**Ingredients:**")
        ingredients = []
        available_products = get_all_available_products()
        
        for i in range(5):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                product = st.selectbox(f"Ingredient {i+1}", [""] + available_products, key=f"ing_{i}")
            with col2:
                amount = st.number_input(f"Amount", min_value=0.0, step=0.25, key=f"amt_{i}")
            with col3:
                unit = st.selectbox(f"Unit", ["oz", "dashes", "pieces", "ml"], key=f"unit_{i}")
            
            if product and amount > 0:
                ingredients.append({"product": product, "amount": amount, "unit": unit})
        
        submitted = st.form_submit_button("Save Recipe")
        
        if submitted and name:
            new_recipe = {
                "name": name,
                "ingredients": ingredients,
                "instructions": instructions,
            }
            
            if recipe_type == 'bar_prep':
                new_recipe.update({
                    "category": category,
                    "yield_description": yield_desc,
                    "yield_oz": yield_oz,
                    "shelf_life": shelf_life,
                    "storage": storage,
                })
                st.session_state.bar_prep_recipes = st.session_state.get('bar_prep_recipes', []) + [new_recipe]
                save_recipes('bar_prep')
            else:
                new_recipe.update({
                    "glass": glass,
                    "sale_price": sale_price,
                })
                st.session_state.cocktail_recipes = st.session_state.get('cocktail_recipes', []) + [new_recipe]
                save_recipes('cocktail')
            
            st.success(f"✅ Recipe '{name}' added!")
            st.rerun()


# =============================================================================
# HOME PAGE (with Feature Toggles)
# =============================================================================

def show_home():
    """Displays the home dashboard."""
    
    # Header
    st.markdown(f"""
        <div class="main-header">
            <h1>🍸 {CLIENT_CONFIG['restaurant_name']}</h1>
            <p>{CLIENT_CONFIG['restaurant_tagline']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    col_s, col_w, col_b, col_i = st.columns(4)
    
    spirits_value = calculate_total_value(st.session_state.get('spirits_inventory', pd.DataFrame()))
    wine_value = calculate_total_value(st.session_state.get('wine_inventory', pd.DataFrame()))
    beer_value = calculate_total_value(st.session_state.get('beer_inventory', pd.DataFrame()))
    ingredients_value = calculate_total_value(st.session_state.get('ingredients_inventory', pd.DataFrame()))
    
    with col_s:
        st.metric("🥃 Spirits Value", format_currency(spirits_value))
    with col_w:
        st.metric("🍷 Wine Value", format_currency(wine_value))
    with col_b:
        st.metric("🍺 Beer Value", format_currency(beer_value))
    with col_i:
        st.metric("🧴 Ingredients", format_currency(ingredients_value))
    
    st.markdown("---")
    
    # Module cards (respecting feature toggles)
    modules = [
        ('master_inventory', 'inventory', 'card-inventory', '📦', 'Master Inventory', 
         'Track spirits, wine, beer, and ingredients across all locations.'),
        ('weekly_orders', 'ordering', 'card-ordering', '📋', 'Weekly Orders', 
         'Build orders based on par levels and track order history.'),
        ('cocktail_builds', 'cocktails', 'card-cocktails', '🍹', 'Cocktail Builds', 
         'Store and cost your cocktail recipes with live pricing.'),
        ('bar_prep', 'bar_prep', 'card-barprep', '🧪', 'Bar Prep', 
         'Manage syrups, infusions, and batched cocktail recipes.'),
        ('cogs_calculator', 'cogs', 'card-cogs', '📊', 'COGS Calculator', 
         'Calculate cost of goods sold and track margins.'),
    ]
    
    # Filter to only enabled modules
    enabled_modules = [(f, p, c, i, t, d) for f, p, c, i, t, d in modules if is_feature_enabled(f)]
    
    # Display in rows of 3
    for i in range(0, len(enabled_modules), 3):
        row_modules = enabled_modules[i:i+3]
        cols = st.columns(len(row_modules))
        
        for col, (feature, page, card_class, icon, title, desc) in zip(cols, row_modules):
            with col:
                st.markdown(f"""
                    <div class="module-card {card_class}">
                        <div class="card-icon">{icon}</div>
                        <div class="card-title">{title}</div>
                        <div class="card-description">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Open {title}", key=f"btn_{page}", use_container_width=True):
                    navigate_to(page)
                    st.rerun()
    
    # Footer info
    st.markdown("---")
    total_value = spirits_value + wine_value + beer_value + ingredients_value
    st.markdown(f"**Total Inventory Value:** {format_currency(total_value)}")
    
    if is_google_sheets_configured():
        st.caption("✅ Connected to Google Sheets")
    else:
        st.caption("⚠️ Running in local mode - data will not persist")


# =============================================================================
# MASTER INVENTORY PAGE
# =============================================================================

def show_inventory():
    """Displays the Master Inventory page."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📦 Master Inventory")
    
    tab_spirits, tab_wine, tab_beer, tab_ingredients = st.tabs([
        "🥃 Spirits", "🍷 Wine", "🍺 Beer", "🧴 Ingredients"
    ])
    
    with tab_spirits:
        show_spirits_inventory()
    
    with tab_wine:
        show_wine_inventory()
    
    with tab_beer:
        show_beer_inventory()
    
    with tab_ingredients:
        show_ingredients_inventory()


def show_spirits_inventory():
    """Displays spirits inventory tab."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    df = st.session_state.get('spirits_inventory', pd.DataFrame())
    
    # Summary metrics
    if len(df) > 0:
        total_value = calculate_total_value(df)
        total_products = len(df)
        avg_margin = df['Margin'].mean() if 'Margin' in df.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", format_currency(total_value))
        with col2:
            st.metric("Products", total_products)
        with col3:
            st.metric("Avg Margin", f"{avg_margin:.1f}%")
    
    # Display editable table
    st.markdown("### Inventory")
    
    if len(df) > 0:
        # Editable columns
        editable_cols = ['Product', 'Type', 'Cost', 'Size (oz.)', 'Margin', 
                        loc1, loc2, loc3, 'Use', 'Distributor', 'Order Notes']
        
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Cost/Oz": st.column_config.NumberColumn(format="$%.4f", disabled=True),
                "Neat Price": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                "Suggested Retail": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Margin": st.column_config.NumberColumn(format="%.0f%%"),
                loc1: st.column_config.NumberColumn(format="%.1f"),
                loc2: st.column_config.NumberColumn(format="%.1f"),
                loc3: st.column_config.NumberColumn(format="%.1f"),
                "Total Inventory": st.column_config.NumberColumn(format="%.1f", disabled=True),
                "Distributor": st.column_config.SelectboxColumn(options=get_distributors()),
            },
            key="spirits_editor"
        )
        
        # Recalculate computed fields
        if len(edited_df) > 0:
            edited_df["Total Inventory"] = edited_df[loc1].fillna(0) + edited_df[loc2].fillna(0) + edited_df[loc3].fillna(0)
            edited_df["Cost/Oz"] = (edited_df["Cost"] / edited_df["Size (oz.)"]).round(4)
            edited_df["Neat Price"] = edited_df.apply(
                lambda row: math.ceil(((row["Cost"] / row["Size (oz.)"]) * 2) / (row["Margin"] / 100)) if row["Margin"] > 0 else 0, axis=1)
            edited_df["Value"] = (edited_df["Cost"] * edited_df["Total Inventory"]).round(2)
            edited_df["Suggested Retail"] = edited_df["Cost"].apply(lambda x: math.ceil(x * 1.44))
        
        if st.button("💾 Save Changes", key="save_spirits"):
            st.session_state.spirits_inventory = edited_df
            save_dataframe_to_sheets(edited_df, get_sheet_name('spirits_inventory'))
            st.success("✅ Spirits inventory saved!")
            st.rerun()
    else:
        st.info("No spirits in inventory. Add products using the table above or import from CSV.")
    
    # CSV Import
    with st.expander("📥 Import from CSV"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="spirits_csv")
        if uploaded_file:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head())
                if st.button("Import Data", key="import_spirits"):
                    # Clean and process imported data
                    imported_df = clean_currency_column(imported_df, 'Cost')
                    st.session_state.spirits_inventory = imported_df
                    save_dataframe_to_sheets(imported_df, get_sheet_name('spirits_inventory'))
                    st.success("✅ Data imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def show_wine_inventory():
    """Displays wine inventory tab."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    df = st.session_state.get('wine_inventory', pd.DataFrame())
    
    # Summary metrics
    if len(df) > 0:
        total_value = calculate_total_value(df)
        total_products = len(df)
        avg_margin = df['Margin'].mean() if 'Margin' in df.columns else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Value", format_currency(total_value))
        with col2:
            st.metric("Products", total_products)
        with col3:
            st.metric("Avg Margin", f"{avg_margin:.1f}%")
    
    st.markdown("### Inventory")
    
    if len(df) > 0:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Bottle Price": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                "BTG": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Suggested Retail": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Margin": st.column_config.NumberColumn(format="%.0f%%"),
                loc1: st.column_config.NumberColumn(format="%.1f"),
                loc2: st.column_config.NumberColumn(format="%.1f"),
                loc3: st.column_config.NumberColumn(format="%.1f"),
                "Total Inventory": st.column_config.NumberColumn(format="%.1f", disabled=True),
                "Distributor": st.column_config.SelectboxColumn(options=get_distributors()),
            },
            key="wine_editor"
        )
        
        # Recalculate computed fields
        if len(edited_df) > 0:
            edited_df["Total Inventory"] = edited_df[loc1].fillna(0) + edited_df[loc2].fillna(0) + edited_df[loc3].fillna(0)
            edited_df["Bottle Price"] = edited_df.apply(
                lambda row: math.ceil(row["Cost"] / (row["Margin"] / 100)) if row["Margin"] > 0 else 0, axis=1)
            edited_df["Value"] = edited_df["Cost"] * edited_df["Total Inventory"]
            edited_df["BTG"] = edited_df["Cost"].apply(lambda x: math.ceil(x / 4))
            edited_df["Suggested Retail"] = edited_df["Cost"].apply(lambda x: math.ceil(x * 1.44))
        
        if st.button("💾 Save Changes", key="save_wine"):
            st.session_state.wine_inventory = edited_df
            save_dataframe_to_sheets(edited_df, get_sheet_name('wine_inventory'))
            st.success("✅ Wine inventory saved!")
            st.rerun()
    else:
        st.info("No wine in inventory. Add products using the table above or import from CSV.")
    
    # CSV Import
    with st.expander("📥 Import from CSV"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="wine_csv")
        if uploaded_file:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head())
                if st.button("Import Data", key="import_wine"):
                    imported_df = clean_currency_column(imported_df, 'Cost')
                    st.session_state.wine_inventory = imported_df
                    save_dataframe_to_sheets(imported_df, get_sheet_name('wine_inventory'))
                    st.success("✅ Data imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def show_beer_inventory():
    """Displays beer inventory tab."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    df = st.session_state.get('beer_inventory', pd.DataFrame())
    
    # Summary metrics
    if len(df) > 0:
        total_value = calculate_total_value(df)
        total_products = len(df)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Value", format_currency(total_value))
        with col2:
            st.metric("Products", total_products)
    
    st.markdown("### Inventory")
    
    if len(df) > 0:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Cost per Keg/Case": st.column_config.NumberColumn(format="$%.2f"),
                "Cost/Unit": st.column_config.NumberColumn(format="$%.4f", disabled=True),
                "Menu Price": st.column_config.NumberColumn(format="$%.0f", disabled=True),
                "Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                "Margin": st.column_config.NumberColumn(format="%.0f%%"),
                loc1: st.column_config.NumberColumn(format="%.1f"),
                loc2: st.column_config.NumberColumn(format="%.1f"),
                loc3: st.column_config.NumberColumn(format="%.1f"),
                "Total Inventory": st.column_config.NumberColumn(format="%.1f", disabled=True),
                "Distributor": st.column_config.SelectboxColumn(options=get_distributors()),
            },
            key="beer_editor"
        )
        
        # Recalculate computed fields
        if len(edited_df) > 0:
            edited_df["Total Inventory"] = edited_df[loc1].fillna(0) + edited_df[loc2].fillna(0) + edited_df[loc3].fillna(0)
            edited_df["Cost/Unit"] = edited_df["Cost per Keg/Case"] / edited_df["Size"]
            edited_df["Value"] = edited_df["Cost per Keg/Case"] * edited_df["Total Inventory"]
            
            def calc_menu_price(row):
                cost_unit = row["Cost/Unit"]
                margin = row["Margin"]
                if margin <= 0:
                    return 0
                if row["Type"] in ["Can", "Bottle"]:
                    return round(cost_unit / (margin / 100))
                elif row["Type"] in ["Half Barrel", "Quarter Barrel", "Sixtel"]:
                    return round((cost_unit * 16) / (margin / 100))
                return 0
            edited_df["Menu Price"] = edited_df.apply(calc_menu_price, axis=1)
        
        if st.button("💾 Save Changes", key="save_beer"):
            st.session_state.beer_inventory = edited_df
            save_dataframe_to_sheets(edited_df, get_sheet_name('beer_inventory'))
            st.success("✅ Beer inventory saved!")
            st.rerun()
    else:
        st.info("No beer in inventory. Add products using the table above or import from CSV.")
    
    # CSV Import
    with st.expander("📥 Import from CSV"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="beer_csv")
        if uploaded_file:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head())
                if st.button("Import Data", key="import_beer"):
                    imported_df = clean_currency_column(imported_df, 'Cost per Keg/Case')
                    st.session_state.beer_inventory = imported_df
                    save_dataframe_to_sheets(imported_df, get_sheet_name('beer_inventory'))
                    st.success("✅ Data imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def show_ingredients_inventory():
    """Displays ingredients inventory tab."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    df = st.session_state.get('ingredients_inventory', pd.DataFrame())
    
    # Summary metrics
    if len(df) > 0:
        total_products = len(df)
        st.metric("Products", total_products)
    
    st.markdown("### Inventory")
    
    if len(df) > 0:
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Cost/Unit": st.column_config.NumberColumn(format="$%.4f", disabled=True),
                loc1: st.column_config.NumberColumn(format="%.1f"),
                loc2: st.column_config.NumberColumn(format="%.1f"),
                loc3: st.column_config.NumberColumn(format="%.1f"),
                "Total Inventory": st.column_config.NumberColumn(format="%.1f", disabled=True),
                "Distributor": st.column_config.SelectboxColumn(options=get_distributors()),
            },
            key="ingredients_editor"
        )
        
        # Recalculate computed fields
        if len(edited_df) > 0:
            edited_df["Total Inventory"] = edited_df[loc1].fillna(0) + edited_df[loc2].fillna(0) + edited_df[loc3].fillna(0)
            edited_df["Cost/Unit"] = edited_df["Cost"] / edited_df["Size/Yield"]
        
        if st.button("💾 Save Changes", key="save_ingredients"):
            st.session_state.ingredients_inventory = edited_df
            save_dataframe_to_sheets(edited_df, get_sheet_name('ingredients_inventory'))
            st.success("✅ Ingredients inventory saved!")
            st.rerun()
    else:
        st.info("No ingredients in inventory. Add products using the table above or import from CSV.")
    
    # CSV Import
    with st.expander("📥 Import from CSV"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="ingredients_csv")
        if uploaded_file:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head())
                if st.button("Import Data", key="import_ingredients"):
                    imported_df = clean_currency_column(imported_df, 'Cost')
                    st.session_state.ingredients_inventory = imported_df
                    save_dataframe_to_sheets(imported_df, get_sheet_name('ingredients_inventory'))
                    st.success("✅ Data imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


# =============================================================================
# WEEKLY ORDERS PAGE
# =============================================================================

def show_ordering():
    """Displays the Weekly Orders page."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📋 Weekly Order Builder")
    
    tab_inventory, tab_order, tab_history, tab_analytics = st.tabs([
        "📊 Weekly Inventory", "🛒 Current Order", "📜 Order History", "📈 Analytics"
    ])
    
    with tab_inventory:
        show_weekly_inventory_tab()
    
    with tab_order:
        show_current_order_tab()
    
    with tab_history:
        show_order_history_tab()
    
    with tab_analytics:
        show_analytics_tab()


def show_weekly_inventory_tab():
    """Shows the weekly inventory counting interface."""
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
    df = st.session_state.get('weekly_inventory', pd.DataFrame())
    
    st.markdown("### 📊 Weekly Inventory Count")
    st.markdown(f"Count inventory across {loc1}, {loc2}, and {loc3}")
    
    if len(df) > 0:
        # Editable inventory table
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                loc1: st.column_config.NumberColumn(format="%.1f"),
                loc2: st.column_config.NumberColumn(format="%.1f"),
                loc3: st.column_config.NumberColumn(format="%.1f"),
                "Total Current Inventory": st.column_config.NumberColumn(format="%.1f", disabled=True),
                "Distributor": st.column_config.SelectboxColumn(options=get_distributors()),
                "Category": st.column_config.SelectboxColumn(options=["Spirits", "Wine", "Beer", "Ingredients"]),
            },
            key="weekly_inventory_editor"
        )
        
        # Recalculate totals
        if len(edited_df) > 0:
            edited_df["Total Current Inventory"] = edited_df[loc1].fillna(0) + edited_df[loc2].fillna(0) + edited_df[loc3].fillna(0)
        
        col_save, col_suggest = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Inventory Count", key="save_weekly"):
                st.session_state.weekly_inventory = edited_df
                save_dataframe_to_sheets(edited_df, get_sheet_name('weekly_inventory'))
                st.success("✅ Weekly inventory saved!")
                st.rerun()
        
        with col_suggest:
            if st.button("🛒 Generate Suggested Orders", key="gen_orders"):
                suggested = calculate_suggested_orders(edited_df)
                if len(suggested) > 0:
                    st.session_state.current_order = suggested
                    save_pending_order()
                    st.success(f"✅ Generated {len(suggested)} suggested orders!")
                    st.rerun()
                else:
                    st.info("All items are at or above par levels.")
    else:
        st.info("No weekly inventory items configured. Add products using the table above.")
    
    # CSV Import
    with st.expander("📥 Import Weekly Items from CSV"):
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'], key="weekly_csv")
        if uploaded_file:
            try:
                imported_df = pd.read_csv(uploaded_file)
                st.dataframe(imported_df.head())
                if st.button("Import Data", key="import_weekly"):
                    imported_df = clean_currency_column(imported_df, 'Unit Cost')
                    st.session_state.weekly_inventory = imported_df
                    save_dataframe_to_sheets(imported_df, get_sheet_name('weekly_inventory'))
                    st.success("✅ Data imported!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {e}")


def show_current_order_tab():
    """Shows the current order builder interface."""
    current_order = st.session_state.get('current_order', pd.DataFrame())
    
    st.markdown("### 🛒 Current Order")
    
    if len(current_order) > 0:
        # Editable order table
        edited_order = st.data_editor(
            current_order,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Order Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                "Order Quantity": st.column_config.NumberColumn(format="%.1f"),
            },
            key="order_editor"
        )
        
        # Recalculate order value
        if len(edited_order) > 0:
            edited_order["Order Value"] = edited_order["Order Quantity"] * edited_order["Unit Cost"]
        
        # Summary
        total_value = edited_order["Order Value"].sum() if "Order Value" in edited_order.columns else 0
        st.markdown(f"**Total Order Value:** {format_currency(total_value)}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save Order", key="save_order"):
                st.session_state.current_order = edited_order
                save_pending_order()
                st.success("✅ Order saved!")
        
        with col2:
            if st.button("✅ Complete Order", key="complete_order"):
                # Add to order history
                order_history = st.session_state.get('order_history', pd.DataFrame())
                
                # Prepare order records
                new_records = []
                week_date = datetime.now().strftime("%Y-%m-%d")
                
                for _, row in edited_order.iterrows():
                    new_records.append({
                        "Week": week_date,
                        "Product": row.get("Product", ""),
                        "Category": row.get("Category", ""),
                        "Order Quantity": row.get("Order Quantity", 0),
                        "Unit Cost": row.get("Unit Cost", 0),
                        "Total Cost": row.get("Order Value", 0),
                        "Distributor": row.get("Distributor", ""),
                        "Invoice #": "",
                        "Invoice Date": "",
                    })
                
                if new_records:
                    new_history = pd.DataFrame(new_records)
                    order_history = pd.concat([order_history, new_history], ignore_index=True)
                    st.session_state.order_history = order_history
                    save_dataframe_to_sheets(order_history, get_sheet_name('order_history'))
                
                # Clear current order
                st.session_state.current_order = pd.DataFrame()
                clear_pending_order()
                
                st.success("✅ Order completed and added to history!")
                st.rerun()
        
        with col3:
            if st.button("🗑️ Clear Order", key="clear_order"):
                st.session_state.current_order = pd.DataFrame()
                clear_pending_order()
                st.rerun()
    else:
        st.info("No items in current order. Generate orders from Weekly Inventory or add items manually.")


def show_order_history_tab():
    """Shows order history."""
    order_history = st.session_state.get('order_history', pd.DataFrame())
    
    st.markdown("### 📜 Order History")
    
    if len(order_history) > 0:
        # Filter by date range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From", value=datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("To", value=datetime.now())
        
        # Display history
        st.dataframe(
            order_history,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                "Total Cost": st.column_config.NumberColumn(format="$%.2f"),
            }
        )
        
        # Summary
        total_spend = order_history["Total Cost"].sum() if "Total Cost" in order_history.columns else 0
        st.markdown(f"**Total Historical Spend:** {format_currency(total_spend)}")
    else:
        st.info("No order history yet. Complete orders to see history here.")


def show_analytics_tab():
    """Shows ordering analytics."""
    order_history = st.session_state.get('order_history', pd.DataFrame())
    
    st.markdown("### 📈 Ordering Analytics")
    
    if len(order_history) > 0 and 'Total Cost' in order_history.columns:
        # Category colors for charts
        category_colors = {
            'Spirits': '#1f77b4',
            'Wine': '#9467bd',
            'Beer': '#ff7f0e',
            'Ingredients': '#2ca02c'
        }
        
        # Date range filter
        col1, col2 = st.columns(2)
        with col1:
            analysis_start = st.date_input("Analysis Start", 
                                          value=datetime.now() - timedelta(days=90),
                                          key="analytics_start")
        with col2:
            analysis_end = st.date_input("Analysis End", 
                                        value=datetime.now(),
                                        key="analytics_end")
        
        # Filter data
        filtered_analytics = order_history.copy()
        if 'Week' in filtered_analytics.columns:
            filtered_analytics['Week'] = pd.to_datetime(filtered_analytics['Week'], errors='coerce')
            mask = (filtered_analytics['Week'] >= pd.to_datetime(analysis_start)) & \
                   (filtered_analytics['Week'] <= pd.to_datetime(analysis_end))
            filtered_analytics = filtered_analytics[mask]
        
        if len(filtered_analytics) == 0:
            st.info("No orders in selected date range.")
            return
        
        # Calculate metrics
        total_spend = filtered_analytics['Total Cost'].sum()
        total_items_ordered = filtered_analytics['Order Quantity'].sum() if 'Order Quantity' in filtered_analytics.columns else len(filtered_analytics)
        
        # Calculate weeks in range
        weeks_in_range = max(1, (analysis_end - analysis_start).days / 7)
        avg_weekly_spend = total_spend / weeks_in_range
        
        # Prior period comparison
        prior_start = analysis_start - timedelta(days=(analysis_end - analysis_start).days)
        prior_mask = (order_history['Week'] >= pd.to_datetime(prior_start)) & \
                    (order_history['Week'] < pd.to_datetime(analysis_start))
        prior_data = order_history[prior_mask] if 'Week' in order_history.columns else pd.DataFrame()
        prior_total_spend = prior_data['Total Cost'].sum() if len(prior_data) > 0 else 0
        prior_avg_weekly = prior_total_spend / weeks_in_range if weeks_in_range > 0 else 0
        
        spend_delta = total_spend - prior_total_spend
        spend_delta_pct = (spend_delta / prior_total_spend * 100) if prior_total_spend > 0 else 0
        avg_delta = avg_weekly_spend - prior_avg_weekly
        
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        with col_m1:
            delta_str = f"{'↑' if spend_delta >= 0 else '↓'} ${abs(spend_delta):,.0f}" if prior_total_spend > 0 else None
            st.metric(
                "💰 Total Spend",
                f"${total_spend:,.2f}",
                delta=delta_str,
                delta_color="inverse"
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
            if prior_total_spend > 0:
                comparison_pct = spend_delta_pct
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
        
        # Spending by category
        st.markdown("#### 📊 Spending by Category")
        
        cat_spend = filtered_analytics.groupby('Category')['Total Cost'].sum().reset_index()
        cat_spend = cat_spend.sort_values('Total Cost', ascending=False)
        
        col_cat_pie, col_cat_bar = st.columns([1, 1])
        
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
        
        with col_cat_bar:
            fig_bar = px.bar(
                cat_spend,
                x='Category',
                y='Total Cost',
                title='Spending by Category',
                color='Category',
                color_discrete_map=category_colors
            )
            fig_bar.update_layout(
                yaxis_tickprefix='$',
                yaxis_tickformat=',.0f',
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Spending over time
        st.markdown("#### 📈 Spending Over Time")
        
        weekly_spend = filtered_analytics.groupby('Week')['Total Cost'].sum().reset_index()
        weekly_spend = weekly_spend.sort_values('Week')
        
        fig_time = px.line(
            weekly_spend,
            x='Week',
            y='Total Cost',
            title='Weekly Spending Trend',
            markers=True
        )
        fig_time.update_layout(
            yaxis_tickprefix='$',
            yaxis_tickformat=',.0f'
        )
        st.plotly_chart(fig_time, use_container_width=True)
        
    else:
        st.info("No order history available for analytics. Complete orders to see trends.")


def show_cocktails():
    """Placeholder for Cocktail Builds - preserved from V3.7."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🍹 Cocktail Builds Book")
    
    recipes = st.session_state.get('cocktail_recipes', [])
    
    if recipes:
        display_recipe_list(recipes, 'cocktail', session_key='cocktail_recipes')
    else:
        st.info("No cocktail recipes found. Add some to get started!")


def show_bar_prep():
    """Placeholder for Bar Prep - preserved from V3.7."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🧪 Bar Prep Recipe Book")
    
    recipes = st.session_state.get('bar_prep_recipes', [])
    
    tab_syrups, tab_batched = st.tabs(["🫙 Syrups & Infusions", "🍸 Batched Cocktails"])
    
    with tab_syrups:
        display_recipe_list(recipes, 'bar_prep', category_filter='Syrups', session_key='bar_prep_recipes')
    
    with tab_batched:
        display_recipe_list(recipes, 'bar_prep', category_filter='Batched Cocktails', session_key='bar_prep_recipes')


def show_cogs():
    """Placeholder for COGS Calculator - preserved from V3.7."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📊 Cost of Goods Sold Calculator")
    
    st.info("🚧 COGS Calculator functionality preserved from V3.7. Full implementation available in the complete version.")
    
    # Show current inventory values
    values = {
        'spirits': calculate_total_value(st.session_state.get('spirits_inventory', pd.DataFrame())),
        'wine': calculate_total_value(st.session_state.get('wine_inventory', pd.DataFrame())),
        'beer': calculate_total_value(st.session_state.get('beer_inventory', pd.DataFrame())),
        'ingredients': calculate_total_value(st.session_state.get('ingredients_inventory', pd.DataFrame())),
    }
    
    st.markdown("### Current Inventory Values")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🥃 Spirits", format_currency(values['spirits']))
    with col2:
        st.metric("🍷 Wine", format_currency(values['wine']))
    with col3:
        st.metric("🍺 Beer", format_currency(values['beer']))
    with col4:
        st.metric("🧴 Ingredients", format_currency(values['ingredients']))


# =============================================================================
# MAIN ROUTING LOGIC
# =============================================================================

def main():
    """Main application entry point."""
    init_session_state()
    
    page_handlers = {
        'home': show_home,
        'inventory': show_inventory,
        'ordering': show_ordering,
        'cocktails': show_cocktails,
        'bar_prep': show_bar_prep,
        'cogs': show_cogs,
    }
    
    current = st.session_state.get('current_page', 'home')
    handler = page_handlers.get(current, show_home)
    handler()


# =============================================================================
# RUN THE APP
# =============================================================================

if __name__ == "__main__":
    main()
