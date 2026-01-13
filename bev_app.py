# =============================================================================
# BEVERAGE MANAGEMENT APP V3.2
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients)
#   - Weekly Order Builder
#   - Cocktail Builds Book
#   - Cost of Goods Sold (COGS) Calculator
#   - Bar Prep Recipe Book
#
# Version History:
#   V1.0 - V2.27: See previous version files for detailed history
#   V3.0 - MAJOR OPTIMIZATION RELEASE
#           - Added Streamlit caching (@st.cache_resource, @st.cache_data)
#           - Unified get_product_cost() function (replaces duplicate cost lookups)
#           - Consolidated recipe display with display_recipe_card() helper
#           - Reduced code duplication in Bar Prep tabs
#           - Optimized session state initialization
#           - ~24% code reduction while maintaining all functionality
#   V3.1 - Bar Prep UI improvements
#           - Changed Syrups/Infusions emoji from 🧴 to 🍯 (honey pot)
#           - Clarified header to show "Cost/oz:" instead of "$/oz:"
#   V3.2 - UI and attribution updates
#           - Changed Syrups/Infusions emoji from 🍯 to 🫙 (jar)
#           - Updated author attribution
#
# Author: James Juedes, developed in collaboration with Claude Opus 4.5 (Anthropic)
# Location: Canter Inn, Madison, WI
# Deployment: Streamlit Community Cloud via GitHub
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import Optional, Dict, List, Any, Tuple

# =============================================================================
# PAGE CONFIG (must be first Streamlit command)
# =============================================================================

st.set_page_config(
    page_title="Beverage Management App V3.2",
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
# SAVE FUNCTIONS (Consolidated)
# =============================================================================

def save_all_inventory_data():
    """Saves all inventory DataFrames to Google Sheets."""
    if not is_google_sheets_configured():
        return
    for key, sheet in [
        ('spirits_inventory', 'spirits_inventory'),
        ('wine_inventory', 'wine_inventory'),
        ('beer_inventory', 'beer_inventory'),
        ('ingredients_inventory', 'ingredients_inventory'),
        ('weekly_inventory', 'weekly_inventory'),
        ('order_history', 'order_history'),
    ]:
        if key in st.session_state:
            save_dataframe_to_sheets(st.session_state[key], sheet)


def save_pending_order():
    """Saves pending order to Google Sheets."""
    if not is_google_sheets_configured():
        return
    if 'current_order' in st.session_state:
        save_dataframe_to_sheets(st.session_state.current_order, 'pending_order')


def clear_pending_order():
    """Clears pending order from Google Sheets."""
    spreadsheet = get_spreadsheet()
    if spreadsheet is None:
        return
    try:
        worksheet = get_or_create_worksheet(spreadsheet, 'pending_order')
        worksheet.clear()
    except Exception:
        pass


def save_price_change_acks():
    """Saves price change acknowledgments."""
    if not is_google_sheets_configured():
        return
    if 'price_change_acks' in st.session_state:
        acks_text = json.dumps(st.session_state.price_change_acks)
        save_text_to_sheets(acks_text, 'price_change_acks')


def load_price_change_acks() -> dict:
    """Loads price change acknowledgments."""
    if not is_google_sheets_configured():
        return {}
    text = load_text_from_sheets('price_change_acks')
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
        save_json_to_sheets(st.session_state[key], key)


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
    save_dataframe_to_sheets(history, 'inventory_history')


def load_inventory_history() -> Optional[pd.DataFrame]:
    """Loads inventory history."""
    if not is_google_sheets_configured():
        return None
    history = load_dataframe_from_sheets('inventory_history')
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
    return save_dataframe_to_sheets(history, 'cogs_history')


def load_cogs_history() -> Optional[pd.DataFrame]:
    """Loads COGS calculation history."""
    if not is_google_sheets_configured():
        return None
    history = load_dataframe_from_sheets('cogs_history')
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
# CUSTOM CSS
# =============================================================================

st.markdown("""
<style>
    .main-header { text-align: center; padding: 1rem 0 2rem 0; }
    .main-header h1 { color: #1E3A5F; margin-bottom: 0.5rem; }
    .main-header p { color: #666; font-size: 1.1rem; }
    
    .module-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 2rem;
        color: white;
        margin-bottom: 1rem;
        min-height: 180px;
    }
    .card-inventory { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
    .card-ordering { background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); }
    .card-cocktails { background: linear-gradient(135deg, #8E2DE2 0%, #4A00E0 100%); }
    
    .card-icon { font-size: 3rem; margin-bottom: 1rem; }
    .card-title { font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem; }
    .card-description { font-size: 0.95rem; opacity: 0.9; }
    
    .stMetric { background-color: #f8f9fa; padding: 1rem; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


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
    """Gets all products from Spirits and Ingredients inventories."""
    products = []
    for df_key in ['spirits_inventory', 'ingredients_inventory']:
        df = st.session_state.get(df_key, pd.DataFrame())
        if len(df) > 0 and 'Product' in df.columns:
            products.extend(df['Product'].tolist())
    return sorted(list(set(products)))


def get_master_inventory_products() -> pd.DataFrame:
    """Gets all products from master inventory with details."""
    all_products = []
    
    inventory_configs = [
        ('spirits_inventory', 'Spirits', 'Cost'),
        ('wine_inventory', 'Wine', 'Cost'),
        ('beer_inventory', 'Beer', 'Cost per Keg/Case'),
        ('ingredients_inventory', 'Ingredients', 'Cost'),
    ]
    
    for key, category, cost_col in inventory_configs:
        df = st.session_state.get(key, pd.DataFrame())
        if len(df) > 0 and 'Product' in df.columns:
            for _, row in df.iterrows():
                product_info = {
                    'Product': row['Product'],
                    'Category': category,
                    'Cost': row.get(cost_col, 0),
                    'Distributor': row.get('Distributor', 'N/A'),
                }
                all_products.append(product_info)
    
    return pd.DataFrame(all_products) if all_products else pd.DataFrame()


def get_products_not_in_weekly_inventory() -> pd.DataFrame:
    """Returns products from Master Inventory not already in Weekly Inventory."""
    master_products = get_master_inventory_products()
    if master_products.empty:
        return pd.DataFrame()
    
    weekly = st.session_state.get('weekly_inventory', pd.DataFrame())
    if len(weekly) == 0 or 'Product' not in weekly.columns:
        return master_products
    
    weekly_products = weekly['Product'].tolist()
    available = master_products[~master_products['Product'].isin(weekly_products)]
    return available


def generate_order_from_inventory(weekly_inv: pd.DataFrame) -> pd.DataFrame:
    """Generates order suggestions from weekly inventory."""
    if len(weekly_inv) == 0:
        return pd.DataFrame()
    
    orders = []
    for _, row in weekly_inv.iterrows():
        par = row.get('Par Level', 0)
        total_inv = row.get('Total Inventory', row.get('Bar Inventory', 0) + row.get('Storage Inventory', 0))
        if total_inv < par:
            order_qty = par - total_inv
            unit_cost = row.get('Unit Cost', 0)
            orders.append({
                'Product': row['Product'],
                'Category': row.get('Category', 'Unknown'),
                'Current Stock': total_inv,
                'Par Level': par,
                'Order Qty': order_qty,
                'Unit Cost': unit_cost,
                'Order Value': order_qty * unit_cost,
                'Distributor': row.get('Distributor', 'N/A'),
            })
    
    return pd.DataFrame(orders) if orders else pd.DataFrame()



# =============================================================================
# SAMPLE DATA FUNCTIONS (with caching)
# =============================================================================

@st.cache_data
def get_sample_spirits():
    """Returns sample spirit inventory data (cached)."""
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
    return df[["Product", "Type", "Cost", "Size (oz.)", "Cost/Oz", "Margin", 
               "Neat Price", "Inventory", "Value", "Use", "Distributor", 
               "Order Notes", "Suggested Retail"]]


@st.cache_data
def get_sample_wines():
    """Returns sample wine inventory data (cached)."""
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
    return df[["Product", "Type", "Cost", "Size (oz.)", "Margin", "Bottle Price", 
               "Inventory", "Value", "Distributor", "BTG", "Suggested Retail"]]


@st.cache_data
def get_sample_beers():
    """Returns sample beer inventory data (cached)."""
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
    return df[["Product", "Type", "Cost per Keg/Case", "Size", "UoM", 
               "Cost/Unit", "Margin", "Menu Price", "Inventory", "Value", 
               "Distributor", "Order Notes"]]


@st.cache_data
def get_sample_ingredients():
    """Returns sample ingredient inventory data (cached)."""
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
         "UoM": "oz", "Distributor": "Breakthru", "Order Notes": "3cs mix"},
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
    return df[["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit", 
               "Distributor", "Order Notes"]]


@st.cache_data
def get_sample_weekly_inventory():
    """Returns sample weekly inventory data (cached)."""
    data = [
        {"Product": "New Glarus Moon Man", "Category": "Beer", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Case", "Unit Cost": 26.40, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Coors Light", "Category": "Beer", "Par": 2, 
         "Bar Inventory": 0.5, "Storage Inventory": 0.5, "Unit": "Case", "Unit Cost": 24.51, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Tito's", "Category": "Spirits", "Par": 4, 
         "Bar Inventory": 1, "Storage Inventory": 2, "Unit": "Bottle", "Unit Cost": 24.50, 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal"},
        {"Product": "Buffalo Trace", "Category": "Spirits", "Par": 3, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Bottle", "Unit Cost": 31.00, 
         "Distributor": "Breakthru", "Order Notes": ""},
        {"Product": "Natalie's Lime Juice", "Category": "Ingredients", "Par": 4, 
         "Bar Inventory": 1, "Storage Inventory": 1, "Unit": "Bottle", "Unit Cost": 8.34, 
         "Distributor": "US Foods", "Order Notes": ""},
    ]
    df = pd.DataFrame(data)
    df['Total Current Inventory'] = df['Bar Inventory'] + df['Storage Inventory']
    return df


def get_sample_order_history():
    """Returns sample order history data."""
    today = datetime.now()
    weeks = [(today - timedelta(weeks=i)).strftime("%Y-%m-%d") for i in range(6, 0, -1)]
    data = [
        {"Week": weeks[0], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[0], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit": "Case", "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[1], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 31.00, "Total Cost": 62.00, "Distributor": "Breakthru"},
        {"Week": weeks[2], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 25.00, "Total Cost": 50.00, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 3, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 73.50, "Distributor": "Breakthru"},
        {"Week": weeks[4], "Product": "Botanist", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 33.74, "Total Cost": 67.48, "Distributor": "General Beverage"},
        {"Week": weeks[5], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit": "Bottle", "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
    ]
    return pd.DataFrame(data)


@st.cache_data
def get_sample_cocktails():
    """Returns sample cocktail recipes (cached)."""
    return [
        {"name": "Martini at The Inn", "glass": "Martini", "sale_price": 14.00,
         "instructions": "Combine gin, vermouth, and bitters in mixing glass. Add ice and stir until ice cold. Strain into chilled martini glass.",
         "ingredients": [
             {"product": "Botanist", "amount": 2.5, "unit": "oz"},
             {"product": "Bordiga Extra Dry Vermouth", "amount": 0.5, "unit": "oz"},
             {"product": "Angostura Orange Bitters", "amount": 0.03, "unit": "oz"},
             {"product": "Olives", "amount": 2, "unit": "pieces"},
         ]},
        {"name": "Old Fashioned", "glass": "Rocks", "sale_price": 13.00,
         "instructions": "Add sugar, bitters, and splash of water to rocks glass. Muddle. Add bourbon and ice, stir.",
         "ingredients": [
             {"product": "Buffalo Trace", "amount": 2.0, "unit": "oz"},
             {"product": "Demerara Syrup (House)", "amount": 0.25, "unit": "oz"},
             {"product": "Angostura Bitters", "amount": 0.1, "unit": "oz"},
             {"product": "Orange Peel", "amount": 1, "unit": "pieces"},
             {"product": "Luxardo Cherry", "amount": 1, "unit": "cherries"},
         ]},
        {"name": "Margarita", "glass": "Coupe", "sale_price": 12.00,
         "instructions": "Combine tequila, lime juice, and agave in shaker with ice. Shake and strain into salt-rimmed coupe.",
         "ingredients": [
             {"product": "Espolòn Blanco", "amount": 2.0, "unit": "oz"},
             {"product": "Natalie's Lime Juice", "amount": 1.0, "unit": "oz"},
             {"product": "Agave Nectar", "amount": 0.75, "unit": "oz"},
         ]},
        {"name": "Negroni", "glass": "Rocks", "sale_price": 13.00,
         "instructions": "Add all ingredients to rocks glass with ice. Stir until well chilled.",
         "ingredients": [
             {"product": "Botanist", "amount": 1.0, "unit": "oz"},
             {"product": "Campari", "amount": 1.0, "unit": "oz"},
             {"product": "Lustau Vermut Rojo", "amount": 1.0, "unit": "oz"},
             {"product": "Orange Peel", "amount": 1, "unit": "pieces"},
         ]},
        {"name": "Moscow Mule", "glass": "Copper Mug", "sale_price": 11.00,
         "instructions": "Add vodka and lime juice to copper mug. Fill with ice and top with ginger beer.",
         "ingredients": [
             {"product": "Tito's", "amount": 2.0, "unit": "oz"},
             {"product": "Natalie's Lime Juice", "amount": 0.75, "unit": "oz"},
             {"product": "Q Ginger Beer", "amount": 4.0, "unit": "oz"},
         ]},
    ]


@st.cache_data
def get_sample_bar_prep_recipes():
    """Returns sample bar prep recipes (cached)."""
    return [
        # Syrups/Infusions
        {"name": "Simple Syrup", "category": "Syrups/Infusions", "yield_oz": 48,
         "yield_description": "1.5 quarts", "shelf_life": "1 month",
         "storage": "Refrigerate in quart container",
         "instructions": "1. Heat Sugar and Water until dissolved.\n2. Remove from heat and cool.\n3. Add vodka.\n4. Label and date.",
         "ingredients": [
             {"product": "White Granulated Sugar", "amount": 800, "unit": "g"},
             {"product": "Water", "amount": 32, "unit": "oz"},
             {"product": "Vodka", "amount": 0.5, "unit": "oz"},
         ]},
        {"name": "Demerara Syrup", "category": "Syrups/Infusions", "yield_oz": 48,
         "yield_description": "1.5 quarts", "shelf_life": "1 month",
         "storage": "Refrigerate in quart container",
         "instructions": "1. Heat Sugar and Water until dissolved.\n2. Remove from heat and cool.\n3. Add vodka.\n4. Label and date.",
         "ingredients": [
             {"product": "Demerara Sugar", "amount": 800, "unit": "g"},
             {"product": "Water", "amount": 32, "unit": "oz"},
             {"product": "Vodka", "amount": 0.5, "unit": "oz"},
         ]},
        {"name": "Sea Salt Saline", "category": "Syrups/Infusions", "yield_oz": 32,
         "yield_description": "1 quart", "shelf_life": "6 months",
         "storage": "Room temp in quart container",
         "instructions": "1. Combine salt and water until dissolved.\n2. Label and date.",
         "ingredients": [
             {"product": "Sea Salt", "amount": 360, "unit": "g"},
             {"product": "Water", "amount": 32, "unit": "oz"},
         ]},
        {"name": "Sour Mix", "category": "Syrups/Infusions", "yield_oz": 32,
         "yield_description": "1 quart", "shelf_life": "1 week",
         "storage": "Refrigerate",
         "instructions": "1. Combine juice and simple.\n2. Stir well.\n3. Label and date.",
         "ingredients": [
             {"product": "Lemon Juice", "amount": 8, "unit": "oz"},
             {"product": "Lime Juice", "amount": 8, "unit": "oz"},
             {"product": "Simple Syrup", "amount": 16, "unit": "oz"},
         ]},
        # Batched Cocktails
        {"name": "Martini Batch", "category": "Batched Cocktails", "yield_oz": 66,
         "yield_description": "~2 liters (22 cocktails)", "shelf_life": "2-3 months",
         "storage": "Room temp",
         "instructions": "Pour 3oz batch into mixing glass. Add bitters, olive juice, ice and stir. Strain into chilled glass.",
         "ingredients": [
             {"product": "Botanist Gin", "amount": 55, "unit": "oz"},
             {"product": "Bordiga Extra Dry", "amount": 11, "unit": "oz"},
         ]},
        {"name": "Old Pal", "category": "Batched Cocktails", "yield_oz": 66,
         "yield_description": "~2 liters (22 cocktails)", "shelf_life": "2-3 months",
         "storage": "Room temp",
         "instructions": "Pour 3oz batch into mixing glass. Add ice and stir. Strain into Nick and Nora.",
         "ingredients": [
             {"product": "Berto Bitter", "amount": 16.5, "unit": "oz"},
             {"product": "Sazerac Rye", "amount": 33, "unit": "oz"},
             {"product": "Bordiga Extra Dry", "amount": 16.5, "unit": "oz"},
         ]},
        {"name": "Mezcal Sour", "category": "Batched Cocktails", "yield_oz": 66,
         "yield_description": "~2 liters (24 cocktails)", "shelf_life": "2-3 months",
         "storage": "Room temp",
         "instructions": "Pour 2.75oz batch into tin. Add lime juice and egg white. Dry shake, add ice, shake. Double strain.",
         "ingredients": [
             {"product": "Yuu Baal Reposado", "amount": 36, "unit": "oz"},
             {"product": "Pasubio", "amount": 24, "unit": "oz"},
             {"product": "Agave Nectar", "amount": 6, "unit": "oz"},
         ]},
        {"name": "Black Walnut Manhattan", "category": "Batched Cocktails", "yield_oz": 66,
         "yield_description": "~2 liters (22 cocktails)", "shelf_life": "2-3 months",
         "storage": "Room temp",
         "instructions": "Pour 3oz into mixing glass. Add bitters, ice, and stir. Strain into chilled coupe.",
         "ingredients": [
             {"product": "Four Roses Bourbon", "amount": 44, "unit": "oz"},
             {"product": "Sweet Vermouth", "amount": 11, "unit": "oz"},
             {"product": "Nux Alpina Walnut Liqueur", "amount": 11, "unit": "oz"},
         ]},
        {"name": "Sazerac", "category": "Batched Cocktails", "yield_oz": 64,
         "yield_description": "~2 liters (28 cocktails)", "shelf_life": "2-3 months",
         "storage": "Room temp",
         "instructions": "Rinse glass with absinthe. Pour 2.25oz batch. Add bitters, ice, stir. Strain.",
         "ingredients": [
             {"product": "Sazerac Rye", "amount": 50, "unit": "oz"},
             {"product": "Delord Armagnac", "amount": 7, "unit": "oz"},
             {"product": "Demerara Syrup", "amount": 7, "unit": "oz"},
         ]},
    ]


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
        'spirits_inventory': ('spirits_inventory', get_sample_spirits),
        'wine_inventory': ('wine_inventory', get_sample_wines),
        'beer_inventory': ('beer_inventory', get_sample_beers),
        'ingredients_inventory': ('ingredients_inventory', get_sample_ingredients),
        'weekly_inventory': ('weekly_inventory', get_sample_weekly_inventory),
        'order_history': ('order_history', get_sample_order_history),
    }
    
    for key, (sheet_name, sample_func) in inventory_loaders.items():
        if key not in st.session_state:
            saved_data = load_dataframe_from_sheets(sheet_name) if sheets_configured else None
            st.session_state[key] = saved_data if saved_data is not None and len(saved_data) > 0 else sample_func()
    
    # Recipe data
    recipe_loaders = {
        'cocktail_recipes': ('cocktail_recipes', get_sample_cocktails),
        'bar_prep_recipes': ('bar_prep_recipes', get_sample_bar_prep_recipes),
    }
    
    for key, (sheet_name, sample_func) in recipe_loaders.items():
        if key not in st.session_state:
            saved_data = load_json_from_sheets(sheet_name) if sheets_configured else None
            st.session_state[key] = saved_data if saved_data and len(saved_data) > 0 else sample_func()
    
    # Other state
    if 'last_inventory_date' not in st.session_state:
        st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
    
    if 'current_order' not in st.session_state:
        saved_order = load_dataframe_from_sheets('pending_order') if sheets_configured else None
        st.session_state.current_order = saved_order if saved_order is not None and len(saved_order) > 0 else pd.DataFrame()
    
    if 'price_change_acks' not in st.session_state:
        st.session_state.price_change_acks = load_price_change_acks() if sheets_configured else {}


# =============================================================================
# NAVIGATION
# =============================================================================

def navigate_to(page: str):
    """Sets the current page in session state."""
    st.session_state.current_page = page


def show_sidebar_navigation():
    """Displays sidebar navigation (V3.0 optimized)."""
    with st.sidebar:
        st.markdown("### 🍸 Navigation")
        st.markdown("---")
        
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            navigate_to('home')
            st.rerun()
        
        st.markdown("")
        current = st.session_state.current_page
        
        nav_items = [
            ('inventory', '📦 Master Inventory'),
            ('ordering', '📋 Weekly Orders'),
            ('cocktails', '🍹 Cocktail Builds'),
            ('bar_prep', '🧪 Bar Prep'),
            ('cogs', '📊 COGS Calculator'),
        ]
        
        for page_id, label in nav_items:
            display_label = label + (" ●" if current == page_id else "")
            if st.button(display_label, key=f"nav_{page_id}", use_container_width=True, disabled=(current == page_id)):
                navigate_to(page_id)
                st.rerun()
        
        st.markdown("---")
        st.caption("Beverage Management App")


# =============================================================================
# REUSABLE UI COMPONENTS (V3.0 Optimization)
# =============================================================================

def display_recipe_card(recipe: dict, recipe_type: str, idx: int, on_delete=None):
    """
    Reusable recipe card display for both Cocktails and Bar Prep.
    
    Args:
        recipe: Recipe dictionary
        recipe_type: 'cocktail' or 'bar_prep'
        idx: Index for unique keys
        on_delete: Optional callback for delete action
    """
    # Calculate costs
    total_cost = calculate_recipe_cost(recipe.get('ingredients', []))
    
    # Create a safe key from recipe name (remove spaces and special chars)
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
            # Recipe-specific info
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
            
            # Instructions
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
        
        # Delete button - use recipe name for unique key
        if on_delete:
            st.markdown("---")
            if st.button("🗑️ Delete Recipe", key=f"delete_{recipe_type}_{safe_name}"):
                on_delete(recipe['name'])


def display_recipe_list(recipes: list, recipe_type: str, category_filter: str = None, session_key: str = None):
    """
    Displays a filtered list of recipes.
    
    Args:
        recipes: List of recipe dictionaries
        recipe_type: 'cocktail' or 'bar_prep'
        category_filter: Optional category to filter by (for bar_prep)
        session_key: Session state key for recipes (for deletion)
    """
    filtered = recipes
    if category_filter:
        filtered = [r for r in recipes if r.get('category') == category_filter]
    
    if not filtered:
        st.info(f"No recipes found. Add one in the 'Add New Recipe' tab.")
        return
    
    def handle_delete(recipe_name):
        if session_key:
            st.session_state[session_key] = [r for r in st.session_state[session_key] if r['name'] != recipe_name]
            save_recipes(recipe_type)
            st.success(f"✅ {recipe_name} deleted!")
            st.rerun()
    
    for idx, recipe in enumerate(filtered):
        display_recipe_card(recipe, recipe_type, idx, on_delete=handle_delete)


# =============================================================================
# CSV UPLOAD PROCESSING FUNCTIONS
# =============================================================================

def process_uploaded_spirits(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Spirits inventory CSV."""
    try:
        df = df.copy()
        for col in ['Cost', 'Cost/Oz', 'Neat Price', 'Suggested Retail', 'Value']:
            df = clean_currency_column(df, col)
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        for col in ['Size (oz.)', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        if 'Cost' in df.columns and 'Size (oz.)' in df.columns:
            df['Cost/Oz'] = df.apply(
                lambda row: round(row['Cost'] / row['Size (oz.)'], 2) if row['Size (oz.)'] > 0 else 0, axis=1)
        if 'Cost' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost'] * df['Inventory'], 2)
        return df
    except Exception as e:
        st.error(f"Error processing spirits data: {e}")
        return df


def process_uploaded_wine(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Wine inventory CSV."""
    try:
        df = df.copy()
        for col in ['Cost', 'Bottle Price', 'BTG', 'Suggested Retail', 'Value']:
            df = clean_currency_column(df, col)
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        for col in ['Size (oz.)', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        if 'Cost' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost'] * df['Inventory'], 2)
        return df
    except Exception as e:
        st.error(f"Error processing wine data: {e}")
        return df


def process_uploaded_beer(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Beer inventory CSV."""
    try:
        df = df.copy()
        for col in ['Cost per Keg/Case', 'Cost/Unit', 'Menu Price', 'Value']:
            df = clean_currency_column(df, col)
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        for col in ['Size', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        if 'Cost per Keg/Case' in df.columns and 'Size' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost per Keg/Case'] / row['Size'], 2) if row['Size'] > 0 else 0, axis=1)
        if 'Cost per Keg/Case' in df.columns and 'Inventory' in df.columns:
            df['Value'] = round(df['Cost per Keg/Case'] * df['Inventory'], 2)
        return df
    except Exception as e:
        st.error(f"Error processing beer data: {e}")
        return df


def process_uploaded_ingredients(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Ingredients inventory CSV."""
    try:
        df = df.copy()
        for col in ['Cost', 'Cost/Unit']:
            df = clean_currency_column(df, col)
        if 'Size/Yield' in df.columns:
            df['Size/Yield'] = pd.to_numeric(df['Size/Yield'], errors='coerce').fillna(0)
        if 'Cost' in df.columns and 'Size/Yield' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost'] / row['Size/Yield'], 2) if row['Size/Yield'] > 0 else 0, axis=1)
        return df
    except Exception as e:
        st.error(f"Error processing ingredients data: {e}")
        return df


# =============================================================================
# PAGE: HOME
# =============================================================================

def show_home():
    """Renders the homescreen with navigation cards."""
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Beverage Management App V3.2</h1>
        <p>Manage your inventory, orders, and cocktail recipes in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    modules = [
        ('inventory', '📦', 'Master Inventory', 'Track spirits, wine, beer, and ingredients.<br>View values, costs, and stock levels.', 'card-inventory'),
        ('ordering', '📋', 'Weekly Order Builder', 'Build weekly orders based on par levels.<br>Track order history and spending.', 'card-ordering'),
        ('cocktails', '🍹', 'Cocktail Builds Book', 'Store and cost cocktail recipes.<br>Calculate margins and pricing.', 'card-cocktails'),
    ]
    
    for col, (page_id, icon, title, desc, css_class) in zip([col1, col2, col3], modules):
        with col:
            st.markdown(f"""
            <div class="module-card {css_class}">
                <div class="card-icon">{icon}</div>
                <div class="card-title">{title}</div>
                <div class="card-description">{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title.split()[0]}", key=f"btn_{page_id}", use_container_width=True):
                navigate_to(page_id)
                st.rerun()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="module-card" style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);">
            <div class="card-icon">🧪</div>
            <div class="card-title">Bar Prep Recipe Book</div>
            <div class="card-description">Syrups, infusions, and batched cocktails.<br>Calculate batch costs and cost/oz.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open Bar Prep", key="btn_bar_prep", use_container_width=True):
            navigate_to('bar_prep')
            st.rerun()
    
    with col5:
        st.markdown("""
        <div class="module-card" style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);">
            <div class="card-icon">📊</div>
            <div class="card-title">Cost of Goods Sold</div>
            <div class="card-description">Calculate COGS by category.<br>Track trends and export reports.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Open COGS", key="btn_cogs", use_container_width=True):
            navigate_to('cogs')
            st.rerun()
    
    st.markdown("---")
    if is_google_sheets_configured():
        st.success("✅ Connected to Google Sheets - Data will persist permanently")
    else:
        st.warning("⚠️ Google Sheets not configured - Data will reset on app restart")
    st.markdown("<p style='text-align: center; color: #888;'>Developed by James Juedes utilizing Claude Opus 4.5</p>", unsafe_allow_html=True)


# =============================================================================
# PAGE: MASTER INVENTORY
# =============================================================================

def show_inventory():
    """Renders the Master Inventory module."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📦 Master Inventory")
    
    # Dashboard
    st.markdown("### 📊 Inventory Dashboard")
    values = {
        'spirits': calculate_total_value(st.session_state.get('spirits_inventory', pd.DataFrame())),
        'wine': calculate_total_value(st.session_state.get('wine_inventory', pd.DataFrame())),
        'beer': calculate_total_value(st.session_state.get('beer_inventory', pd.DataFrame())),
        'ingredients': calculate_total_value(st.session_state.get('ingredients_inventory', pd.DataFrame())),
    }
    total = sum(values.values())
    
    cols = st.columns(5)
    labels = [('🥃 Spirits', values['spirits']), ('🍷 Wine', values['wine']), 
              ('🍺 Beer', values['beer']), ('🧴 Ingredients', values['ingredients']),
              ('💰 Total', total)]
    for col, (label, val) in zip(cols, labels):
        with col:
            st.metric(label=label, value=format_currency(val))
    
    st.caption(f"Last inventory recorded: {st.session_state.get('last_inventory_date', 'N/A')}")
    st.markdown("---")
    
    # Tabs
    tab_spirits, tab_wine, tab_beer, tab_ingredients = st.tabs(["🥃 Spirits", "🍷 Wine", "🍺 Beer", "🧴 Ingredients"])
    
    tab_configs = [
        (tab_spirits, 'spirits_inventory', 'spirits', ["Type", "Distributor", "Use"], "Spirits"),
        (tab_wine, 'wine_inventory', 'wine', ["Type", "Distributor"], "Wine"),
        (tab_beer, 'beer_inventory', 'beer', ["Type", "Distributor"], "Beer"),
        (tab_ingredients, 'ingredients_inventory', 'ingredients', ["Distributor"], "Ingredients"),
    ]
    
    for tab, key, category, filters, name in tab_configs:
        with tab:
            show_inventory_tab(st.session_state.get(key, pd.DataFrame()), category, filters, name)
    
    st.markdown("---")
    
    # CSV Upload
    with st.expander("📤 Upload Inventory Data (CSV)", expanded=False):
        st.markdown("Upload a CSV file to replace inventory data for any category.")
        upload_category = st.selectbox("Select category:", ["Spirits", "Wine", "Beer", "Ingredients"], key="upload_category")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                st.write("Preview:")
                st.dataframe(new_data.head())
                if st.button("✅ Confirm Upload", key="confirm_upload"):
                    processors = {
                        "Spirits": (process_uploaded_spirits, 'spirits_inventory'),
                        "Wine": (process_uploaded_wine, 'wine_inventory'),
                        "Beer": (process_uploaded_beer, 'beer_inventory'),
                        "Ingredients": (process_uploaded_ingredients, 'ingredients_inventory'),
                    }
                    func, key = processors[upload_category]
                    st.session_state[key] = func(new_data)
                    st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
                    save_all_inventory_data()
                    st.success(f"✅ {upload_category} inventory uploaded!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def show_inventory_tab(df: pd.DataFrame, category: str, filter_columns: list, display_name: str):
    """Renders an inventory tab with search, filter, and editing."""
    if df is None or len(df) == 0:
        st.info(f"No {display_name.lower()} inventory data.")
        return
    
    st.markdown(f"#### Search & Filter {display_name}")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key=f"search_{category}", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_{category}_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    st.markdown(f"#### {display_name} Inventory")
    
    disabled_cols = {
        'spirits': ["Cost/Oz", "Value"],
        'wine': ["Value"],
        'beer': ["Cost/Unit", "Value"],
        'ingredients': ["Cost/Unit"],
    }.get(category, [])
    
    edited_df = st.data_editor(
        filtered_df, use_container_width=True, num_rows="dynamic",
        key=f"editor_{category}", disabled=disabled_cols,
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Cost/Oz": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "Cost/Unit": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
            "Neat Price": st.column_config.NumberColumn(format="$%.2f"),
            "Bottle Price": st.column_config.NumberColumn(format="$%.2f"),
            "Menu Price": st.column_config.NumberColumn(format="$%.2f"),
            "BTG": st.column_config.NumberColumn(format="$%.2f"),
            "Margin": st.column_config.NumberColumn(format="%.0f%%"),
            "Cost per Keg/Case": st.column_config.NumberColumn(format="$%.2f"),
        })
    
    if st.button(f"💾 Save Changes", key=f"save_{category}"):
        # Recalculate derived fields
        if category == "spirits":
            if "Cost" in edited_df.columns and "Size (oz.)" in edited_df.columns:
                edited_df["Cost/Oz"] = edited_df.apply(lambda r: round(r['Cost'] / r['Size (oz.)'], 2) if r['Size (oz.)'] > 0 else 0, axis=1)
            if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                edited_df["Value"] = round(edited_df["Cost"] * edited_df["Inventory"], 2)
            st.session_state.spirits_inventory = edited_df
        elif category == "wine":
            if "Cost" in edited_df.columns and "Inventory" in edited_df.columns:
                edited_df["Value"] = round(edited_df["Cost"] * edited_df["Inventory"], 2)
            st.session_state.wine_inventory = edited_df
        elif category == "beer":
            if "Cost per Keg/Case" in edited_df.columns and "Size" in edited_df.columns:
                edited_df["Cost/Unit"] = edited_df.apply(lambda r: round(r['Cost per Keg/Case'] / r['Size'], 2) if r['Size'] > 0 else 0, axis=1)
            if "Cost per Keg/Case" in edited_df.columns and "Inventory" in edited_df.columns:
                edited_df["Value"] = round(edited_df["Cost per Keg/Case"] * edited_df["Inventory"], 2)
            st.session_state.beer_inventory = edited_df
        elif category == "ingredients":
            if "Cost" in edited_df.columns and "Size/Yield" in edited_df.columns:
                edited_df["Cost/Unit"] = edited_df.apply(lambda r: round(r['Cost'] / r['Size/Yield'], 2) if r['Size/Yield'] > 0 else 0, axis=1)
            st.session_state.ingredients_inventory = edited_df
        
        st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
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
    
    # V2.25: Sidebar navigation
    show_sidebar_navigation()
    
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

# =============================================================================
# PAGE: COCKTAIL BUILDS BOOK (V3.0 Optimized)
# =============================================================================

def show_cocktails():
    """Renders the Cocktail Builds Book module (V3.0 optimized)."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🍹 Cocktail Builds Book")
    
    # Dashboard
    st.markdown("### 📊 Cocktail Dashboard")
    recipes = st.session_state.get('cocktail_recipes', [])
    
    total_cost = sum(calculate_recipe_cost(r.get('ingredients', [])) for r in recipes)
    avg_cost = total_cost / len(recipes) if recipes else 0
    avg_price = sum(r.get('sale_price', 0) for r in recipes) / len(recipes) if recipes else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Recipes", len(recipes))
    with col2:
        st.metric("Avg Cost", format_currency(avg_cost))
    with col3:
        st.metric("Avg Price", format_currency(avg_price))
    with col4:
        avg_margin = ((avg_price - avg_cost) / avg_price * 100) if avg_price > 0 else 0
        st.metric("Avg Margin", f"{avg_margin:.1f}%")
    
    st.markdown("---")
    
    tab_view, tab_add = st.tabs(["📖 View & Search Recipes", "➕ Add New Recipe"])
    
    with tab_view:
        st.markdown("### 📖 All Cocktail Recipes")
        
        if recipes:
            search = st.text_input("🔍 Search recipes", key="cocktail_search")
            filtered = [r for r in recipes if search.lower() in r['name'].lower()] if search else recipes
            display_recipe_list(filtered, 'cocktail', session_key='cocktail_recipes')
        else:
            st.info("No cocktail recipes yet. Add one in the 'Add New Recipe' tab.")
    
    with tab_add:
        st.markdown("### ➕ Add New Cocktail Recipe")
        
        if 'new_cocktail_ingredients' not in st.session_state:
            st.session_state.new_cocktail_ingredients = []
        
        col_name, col_glass, col_price = st.columns(3)
        with col_name:
            new_name = st.text_input("Cocktail Name:", key="cocktail_name")
        with col_glass:
            new_glass = st.selectbox("Glass:", ["Rocks", "Coupe", "Martini", "Nick & Nora", "Collins", "Copper Mug", "Wine Glass"], key="cocktail_glass")
        with col_price:
            new_price = st.number_input("Sale Price ($):", min_value=0.0, value=12.0, step=0.5, key="cocktail_price")
        
        new_instructions = st.text_area("Instructions:", key="cocktail_instructions", height=80)
        
        st.markdown("---")
        st.markdown("#### 🧴 Add Ingredients")
        
        available = get_all_available_products()
        col_prod, col_amt, col_unit, col_add = st.columns([3, 1, 1, 1])
        
        with col_prod:
            ing_product = st.selectbox("Product:", options=[""] + available, key="cocktail_ing_product")
        with col_amt:
            ing_amount = st.number_input("Amount:", min_value=0.0, step=0.25, value=1.0, key="cocktail_ing_amount")
        with col_unit:
            ing_unit = st.selectbox("Unit:", options=["oz", "pieces", "dashes", "cherries"], key="cocktail_ing_unit")
        with col_add:
            st.write("")
            st.write("")
            if st.button("➕ Add", key="cocktail_add_ing"):
                if ing_product and ing_amount > 0:
                    st.session_state.new_cocktail_ingredients.append({
                        "product": ing_product, "amount": ing_amount, "unit": ing_unit
                    })
                    st.rerun()
        
        if st.session_state.new_cocktail_ingredients:
            st.markdown("**Current Ingredients:**")
            ing_data = [{"Product": i['product'], "Amount": i['amount'], "Unit": i['unit'],
                        "Cost": get_product_cost(i['product'], i['amount'], i['unit'])[1]}
                       for i in st.session_state.new_cocktail_ingredients]
            st.dataframe(pd.DataFrame(ing_data), use_container_width=True, hide_index=True,
                        column_config={"Cost": st.column_config.NumberColumn(format="$%.4f")})
            
            running_cost = sum(d['Cost'] for d in ing_data)
            margin = ((new_price - running_cost) / new_price * 100) if new_price > 0 else 0
            st.metric("Running Cost", format_currency(running_cost))
            st.caption(f"Margin at ${new_price:.2f}: {margin:.1f}%")
            
            if st.button("🗑️ Clear Ingredients", key="cocktail_clear"):
                st.session_state.new_cocktail_ingredients = []
                st.rerun()
        
        st.markdown("---")
        if st.button("💾 Save Recipe", key="cocktail_save", type="primary"):
            if not new_name:
                st.error("Please enter a cocktail name.")
            elif not st.session_state.new_cocktail_ingredients:
                st.error("Please add at least one ingredient.")
            elif new_name.lower() in [r['name'].lower() for r in recipes]:
                st.error(f"'{new_name}' already exists.")
            else:
                new_recipe = {
                    "name": new_name, "glass": new_glass, "sale_price": new_price,
                    "instructions": new_instructions,
                    "ingredients": st.session_state.new_cocktail_ingredients.copy()
                }
                st.session_state.cocktail_recipes.append(new_recipe)
                save_recipes('cocktail')
                st.session_state.new_cocktail_ingredients = []
                st.success(f"✅ {new_name} added!")
                st.rerun()


# =============================================================================
# PAGE: BAR PREP RECIPE BOOK (V3.0 Optimized)
# =============================================================================

def show_bar_prep():
    """Renders the Bar Prep Recipe Book module (V3.0 optimized with reusable components)."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🧪 Bar Prep Recipe Book")
    
    # Dashboard
    st.markdown("### 📊 Bar Prep Dashboard")
    recipes = st.session_state.get('bar_prep_recipes', [])
    syrups = [r for r in recipes if r.get('category') == 'Syrups/Infusions']
    batches = [r for r in recipes if r.get('category') == 'Batched Cocktails']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Recipes", len(recipes))
    with col2:
        st.metric("🫙 Syrups/Infusions", len(syrups))
    with col3:
        st.metric("🍸 Batched Cocktails", len(batches))
    
    st.markdown("---")
    
    tab_syrups, tab_batches, tab_add = st.tabs([
        "🫙 Syrups/Infusions/Tinctures", "🍸 Batched Cocktails", "➕ Add New Recipe"
    ])
    
    # V3.0: Use reusable display_recipe_list for both tabs
    with tab_syrups:
        st.markdown("### 🫙 Syrups, Infusions & Tinctures")
        display_recipe_list(recipes, 'bar_prep', category_filter='Syrups/Infusions', session_key='bar_prep_recipes')
    
    with tab_batches:
        st.markdown("### 🍸 Batched Cocktails")
        display_recipe_list(recipes, 'bar_prep', category_filter='Batched Cocktails', session_key='bar_prep_recipes')
    
    with tab_add:
        st.markdown("### ➕ Add New Bar Prep Recipe")
        
        if 'new_bar_prep_ingredients' not in st.session_state:
            st.session_state.new_bar_prep_ingredients = []
        
        col_name, col_cat = st.columns(2)
        with col_name:
            new_name = st.text_input("Recipe Name:", key="bar_prep_name")
        with col_cat:
            new_category = st.selectbox("Category:", ["Syrups/Infusions", "Batched Cocktails"], key="bar_prep_category")
        
        col_yield, col_yield_desc = st.columns(2)
        with col_yield:
            new_yield_oz = st.number_input("Yield (oz):", min_value=0.0, value=32.0, step=1.0, key="bar_prep_yield_oz")
        with col_yield_desc:
            new_yield_desc = st.text_input("Yield Description:", key="bar_prep_yield_desc", placeholder="e.g., 1 quart")
        
        col_shelf, col_storage = st.columns(2)
        with col_shelf:
            new_shelf_life = st.text_input("Shelf Life:", key="bar_prep_shelf_life", placeholder="e.g., 1 month")
        with col_storage:
            new_storage = st.text_input("Storage Notes:", key="bar_prep_storage")
        
        new_instructions = st.text_area("Instructions:", key="bar_prep_instructions", height=80)
        
        st.markdown("---")
        st.markdown("#### 🧴 Add Ingredients")
        
        available = get_all_available_products()
        col_prod, col_amt, col_unit, col_add = st.columns([3, 1, 1, 1])
        
        with col_prod:
            ing_product = st.selectbox("Product:", options=[""] + available, key="bar_prep_ing_product")
        with col_amt:
            ing_amount = st.number_input("Amount:", min_value=0.0, step=0.5, value=1.0, key="bar_prep_ing_amount")
        with col_unit:
            ing_unit = st.selectbox("Unit:", options=["oz", "g", "pieces"], key="bar_prep_ing_unit")
        with col_add:
            st.write("")
            st.write("")
            if st.button("➕ Add", key="bar_prep_add_ing"):
                if ing_product and ing_amount > 0:
                    st.session_state.new_bar_prep_ingredients.append({
                        "product": ing_product, "amount": ing_amount, "unit": ing_unit
                    })
                    st.rerun()
        
        if st.session_state.new_bar_prep_ingredients:
            st.markdown("**Current Ingredients:**")
            ing_data = [{"Product": i['product'], "Amount": i['amount'], "Unit": i['unit'],
                        "Cost": get_product_cost(i['product'], i['amount'], i['unit'])[1]}
                       for i in st.session_state.new_bar_prep_ingredients]
            st.dataframe(pd.DataFrame(ing_data), use_container_width=True, hide_index=True,
                        column_config={"Cost": st.column_config.NumberColumn(format="$%.4f")})
            
            running_cost = sum(d['Cost'] for d in ing_data)
            st.metric("Batch Cost", format_currency(running_cost))
            if new_yield_oz > 0:
                st.caption(f"Cost/oz: {format_currency(running_cost / new_yield_oz)}")
            
            if st.button("🗑️ Clear Ingredients", key="bar_prep_clear"):
                st.session_state.new_bar_prep_ingredients = []
                st.rerun()
        
        st.markdown("---")
        if st.button("💾 Save Recipe", key="bar_prep_save", type="primary"):
            if not new_name:
                st.error("Please enter a recipe name.")
            elif not st.session_state.new_bar_prep_ingredients:
                st.error("Please add at least one ingredient.")
            elif new_yield_oz <= 0:
                st.error("Please enter a valid yield.")
            elif new_name.lower() in [r['name'].lower() for r in recipes]:
                st.error(f"'{new_name}' already exists.")
            else:
                new_recipe = {
                    "name": new_name, "category": new_category,
                    "yield_oz": new_yield_oz, "yield_description": new_yield_desc or f"{new_yield_oz} oz",
                    "shelf_life": new_shelf_life or "Not specified",
                    "storage": new_storage or "Not specified",
                    "instructions": new_instructions or "No instructions provided.",
                    "ingredients": st.session_state.new_bar_prep_ingredients.copy()
                }
                st.session_state.bar_prep_recipes.append(new_recipe)
                save_recipes('bar_prep')
                st.session_state.new_bar_prep_ingredients = []
                st.success(f"✅ {new_name} added!")
                st.rerun()


# =============================================================================
# PAGE: COST OF GOODS SOLD (COGS)
# =============================================================================

def show_cogs():
    """Renders the Cost of Goods Sold module."""
    
    # V2.25: Sidebar navigation
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📊 Cost of Goods Sold")
    
    # Load inventory history for date selection
    history = load_inventory_history()
    
    if history is None or len(history) == 0:
        st.warning("⚠️ No inventory snapshots available. Please save inventory data in Master Inventory first to create snapshots for COGS calculation.")
        st.info("💡 Tip: Go to Master Inventory, make any change, and click 'Save Changes' to create your first inventory snapshot.")
        return
    
    # Tabs for COGS Calculator and History
    tab_calculator, tab_trends, tab_history = st.tabs(["🧮 COGS Calculator", "📈 Trends & Analytics", "📜 Saved Calculations"])
    
    with tab_calculator:
        st.markdown("### 📅 Select Inventory Period")
        st.markdown("Choose starting and ending inventory snapshot dates to calculate COGS for the period.")
        
        available_dates = sorted(history['Date'].unique().tolist(), reverse=True)
        
        col_start, col_end = st.columns(2)
        
        with col_start:
            # Default to oldest date for starting inventory
            start_date = st.selectbox(
                "📦 Starting Inventory Date:",
                options=available_dates,
                index=len(available_dates) - 1 if len(available_dates) > 1 else 0,
                key="cogs_start_date",
                help="Beginning inventory period"
            )
        
        with col_end:
            # Default to most recent date for ending inventory
            end_date = st.selectbox(
                "📦 Ending Inventory Date:",
                options=available_dates,
                index=0,
                key="cogs_end_date",
                help="Ending inventory period"
            )
        
        # Get inventory values for selected dates
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
        
        st.markdown("---")
        
        # Auto-populate purchases from Order History
        st.markdown("### 🛒 Purchases")
        st.markdown("Purchases are auto-populated from Order History based on Invoice Date. You can override if needed.")
        
        # Get auto-calculated purchases
        auto_purchases = get_purchases_by_category_and_date(start_date, end_date)
        
        # Toggle for manual override
        use_manual_override = st.checkbox("✏️ Enable manual override for purchases", key="cogs_manual_override")
        
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        
        with col_p1:
            if use_manual_override:
                purchase_spirits = st.number_input(
                    "🥃 Spirits Purchases",
                    min_value=0.0,
                    value=auto_purchases['Spirits'],
                    step=50.0,
                    format="%.2f",
                    key="cogs_purchase_spirits"
                )
            else:
                purchase_spirits = auto_purchases['Spirits']
                st.metric("🥃 Spirits Purchases", format_currency(purchase_spirits))
        
        with col_p2:
            if use_manual_override:
                purchase_wine = st.number_input(
                    "🍷 Wine Purchases",
                    min_value=0.0,
                    value=auto_purchases['Wine'],
                    step=50.0,
                    format="%.2f",
                    key="cogs_purchase_wine"
                )
            else:
                purchase_wine = auto_purchases['Wine']
                st.metric("🍷 Wine Purchases", format_currency(purchase_wine))
        
        with col_p3:
            if use_manual_override:
                purchase_beer = st.number_input(
                    "🍺 Beer Purchases",
                    min_value=0.0,
                    value=auto_purchases['Beer'],
                    step=50.0,
                    format="%.2f",
                    key="cogs_purchase_beer"
                )
            else:
                purchase_beer = auto_purchases['Beer']
                st.metric("🍺 Beer Purchases", format_currency(purchase_beer))
        
        with col_p4:
            if use_manual_override:
                purchase_ingredients = st.number_input(
                    "🧴 Ingredients Purchases",
                    min_value=0.0,
                    value=auto_purchases['Ingredients'],
                    step=50.0,
                    format="%.2f",
                    key="cogs_purchase_ingredients"
                )
            else:
                purchase_ingredients = auto_purchases['Ingredients']
                st.metric("🧴 Ingredients Purchases", format_currency(purchase_ingredients))
        
        total_purchases = purchase_spirits + purchase_wine + purchase_beer + purchase_ingredients
        
        st.markdown("---")
        
        # Calculate COGS by category
        cogs_spirits = (start_spirits + purchase_spirits) - end_spirits
        cogs_wine = (start_wine + purchase_wine) - end_wine
        cogs_beer = (start_beer + purchase_beer) - end_beer
        cogs_ingredients = (start_ingredients + purchase_ingredients) - end_ingredients
        cogs_total = cogs_spirits + cogs_wine + cogs_beer + cogs_ingredients
        
        # COGS Results
        st.markdown("### 📊 COGS Calculation Results")
        
        # Create detailed breakdown table
        cogs_table_data = {
            'Category': ['🥃 Spirits', '🍷 Wine', '🍺 Beer', '🧴 Ingredients', '**💰 TOTAL**'],
            'Starting Inventory': [start_spirits, start_wine, start_beer, start_ingredients, start_total],
            'Purchases': [purchase_spirits, purchase_wine, purchase_beer, purchase_ingredients, total_purchases],
            'Ending Inventory': [end_spirits, end_wine, end_beer, end_ingredients, end_total],
            'COGS': [cogs_spirits, cogs_wine, cogs_beer, cogs_ingredients, cogs_total]
        }
        
        cogs_df = pd.DataFrame(cogs_table_data)
        
        st.dataframe(
            cogs_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Starting Inventory": st.column_config.NumberColumn(format="$%.2f"),
                "Purchases": st.column_config.NumberColumn(format="$%.2f"),
                "Ending Inventory": st.column_config.NumberColumn(format="$%.2f"),
                "COGS": st.column_config.NumberColumn(format="$%.2f")
            }
        )
        
        st.caption("**COGS Formula:** (Starting Inventory + Purchases) − Ending Inventory")
        
        st.markdown("---")
        
        # V2.26: COGS as Percentage of Sales - Granular by Category
        st.markdown("### 💵 COGS as Percentage of Sales")
        st.markdown("Enter sales by category to calculate COGS percentage for Wine, Beer, and Bar (Spirits + Ingredients).")
        
        # Calculate Bar COGS (Spirits + Ingredients combined)
        cogs_bar = cogs_spirits + cogs_ingredients
        
        # Sales input fields
        col_wine_sales, col_beer_sales, col_bar_sales = st.columns(3)
        
        with col_wine_sales:
            wine_sales = st.number_input(
                "🍷 Wine Sales:",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="cogs_wine_sales",
                help="Total wine sales for the period"
            )
        
        with col_beer_sales:
            beer_sales = st.number_input(
                "🍺 Beer Sales:",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="cogs_beer_sales",
                help="Total beer sales for the period"
            )
        
        with col_bar_sales:
            bar_sales = st.number_input(
                "🍸 Bar Sales:",
                min_value=0.0,
                value=0.0,
                step=100.0,
                format="%.2f",
                key="cogs_bar_sales",
                help="Total bar sales (cocktails, spirits, etc.) for the period"
            )
        
        # Calculate totals
        total_sales = wine_sales + beer_sales + bar_sales
        
        # Calculate percentages
        wine_pct = (cogs_wine / wine_sales * 100) if wine_sales > 0 else 0
        beer_pct = (cogs_beer / beer_sales * 100) if beer_sales > 0 else 0
        bar_pct = (cogs_bar / bar_sales * 100) if bar_sales > 0 else 0
        total_pct = (cogs_total / total_sales * 100) if total_sales > 0 else 0
        
        st.markdown("")
        
        # Display table
        cogs_pct_data = pd.DataFrame({
            'Category': ['🍷 Wine', '🍺 Beer', '🍸 Bar', '💰 TOTAL'],
            'COGS': [cogs_wine, cogs_beer, cogs_bar, cogs_total],
            'Sales': [wine_sales, beer_sales, bar_sales, total_sales],
            'COGS %': [wine_pct, beer_pct, bar_pct, total_pct]
        })
        
        st.dataframe(
            cogs_pct_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "COGS": st.column_config.NumberColumn(format="$%.2f"),
                "Sales": st.column_config.NumberColumn(format="$%.2f"),
                "COGS %": st.column_config.NumberColumn(format="%.1f%%")
            }
        )
        
        # Status indicators for each category
        def get_status_indicator(pct, sales):
            if sales == 0:
                return ""
            elif pct <= 20:
                return "✅"
            elif pct <= 25:
                return "👍"
            elif pct <= 30:
                return "⚠️"
            else:
                return "🚨"
        
        # Show overall status
        if total_sales > 0:
            col_status1, col_status2, col_status3 = st.columns(3)
            
            with col_status1:
                if wine_sales > 0:
                    status = get_status_indicator(wine_pct, wine_sales)
                    st.caption(f"Wine: {status} {wine_pct:.1f}%")
            
            with col_status2:
                if beer_sales > 0:
                    status = get_status_indicator(beer_pct, beer_sales)
                    st.caption(f"Beer: {status} {beer_pct:.1f}%")
            
            with col_status3:
                if bar_sales > 0:
                    status = get_status_indicator(bar_pct, bar_sales)
                    st.caption(f"Bar: {status} {bar_pct:.1f}%")
            
            st.caption("Target: ≤20% ✅ | Acceptable: 20-25% 👍 | Caution: 25-30% ⚠️ | High: >30% 🚨")
        
        st.markdown("---")
        
        # Category Breakdown Visualization - Updated for Wine, Beer, Bar
        st.markdown("### 📈 COGS Breakdown by Category")
        
        col_pie, col_bar_chart = st.columns(2)
        
        with col_pie:
            # Pie chart - Wine, Beer, Bar
            pie_data = pd.DataFrame({
                'Category': ['Wine', 'Beer', 'Bar'],
                'COGS': [max(0, cogs_wine), max(0, cogs_beer), max(0, cogs_bar)]
            })
            
            # Only show pie if there's positive COGS
            if pie_data['COGS'].sum() > 0:
                fig_pie = px.pie(
                    pie_data,
                    values='COGS',
                    names='Category',
                    title='COGS Distribution',
                    color='Category',
                    color_discrete_map={
                        'Wine': '#EC4899',
                        'Beer': '#F59E0B',
                        'Bar': '#8B5CF6'
                    }
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No positive COGS to display in chart.")
        
        with col_bar_chart:
            # Horizontal bar chart - Wine, Beer, Bar
            bar_chart_data = pd.DataFrame({
                'Category': ['Wine', 'Beer', 'Bar'],
                'COGS': [cogs_wine, cogs_beer, cogs_bar]
            })
            
            fig_bar = px.bar(
                bar_chart_data,
                x='COGS',
                y='Category',
                orientation='h',
                title='COGS by Category',
                color='Category',
                color_discrete_map={
                    'Wine': '#EC4899',
                    'Beer': '#F59E0B',
                    'Bar': '#8B5CF6'
                }
            )
            fig_bar.update_layout(
                xaxis_tickprefix='$',
                xaxis_tickformat=',.0f',
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("---")
        
        # Save and Export Options
        st.markdown("### 💾 Save & Export")
        
        col_save, col_export = st.columns(2)
        
        with col_save:
            if st.button("💾 Save Calculation to History", key="save_cogs", type="primary"):
                cogs_record = {
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'Period Start': start_date,
                    'Period End': end_date,
                    'Spirits COGS': cogs_spirits,
                    'Wine COGS': cogs_wine,
                    'Beer COGS': cogs_beer,
                    'Ingredients COGS': cogs_ingredients,
                    'Bar COGS': cogs_bar,
                    'Total COGS': cogs_total,
                    'Total Purchases': total_purchases,
                    'Wine Sales': wine_sales,
                    'Beer Sales': beer_sales,
                    'Bar Sales': bar_sales,
                    'Total Sales': total_sales,
                    'Wine COGS %': wine_pct,
                    'Beer COGS %': beer_pct,
                    'Bar COGS %': bar_pct,
                    'Total COGS %': total_pct
                }
                
                if save_cogs_calculation(cogs_record):
                    st.success("✅ COGS calculation saved to history!")
                else:
                    st.error("Failed to save. Check Google Sheets connection.")
        
        with col_export:
            # Create export report
            report = f"""COST OF GOODS SOLD REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Period: {start_date} to {end_date}
{'='*50}

INVENTORY VALUES
----------------
                Starting        Ending          Change
Spirits:        {format_currency(start_spirits):>12}  {format_currency(end_spirits):>12}  {format_currency(end_spirits - start_spirits):>12}
Wine:           {format_currency(start_wine):>12}  {format_currency(end_wine):>12}  {format_currency(end_wine - start_wine):>12}
Beer:           {format_currency(start_beer):>12}  {format_currency(end_beer):>12}  {format_currency(end_beer - start_beer):>12}
Ingredients:    {format_currency(start_ingredients):>12}  {format_currency(end_ingredients):>12}  {format_currency(end_ingredients - start_ingredients):>12}
TOTAL:          {format_currency(start_total):>12}  {format_currency(end_total):>12}  {format_currency(end_total - start_total):>12}

PURCHASES
---------
Spirits:        {format_currency(purchase_spirits)}
Wine:           {format_currency(purchase_wine)}
Beer:           {format_currency(purchase_beer)}
Ingredients:    {format_currency(purchase_ingredients)}
TOTAL:          {format_currency(total_purchases)}

COGS CALCULATION
----------------
Formula: (Starting Inventory + Purchases) - Ending Inventory

Spirits:        {format_currency(cogs_spirits)}
Wine:           {format_currency(cogs_wine)}
Beer:           {format_currency(cogs_beer)}
Ingredients:    {format_currency(cogs_ingredients)}
TOTAL COGS:     {format_currency(cogs_total)}

COGS BY SALES CATEGORY
----------------------
Category        COGS            Sales           COGS %
Wine:           {format_currency(cogs_wine):>12}  {format_currency(wine_sales):>12}  {wine_pct:>10.1f}%
Beer:           {format_currency(cogs_beer):>12}  {format_currency(beer_sales):>12}  {beer_pct:>10.1f}%
Bar:            {format_currency(cogs_bar):>12}  {format_currency(bar_sales):>12}  {bar_pct:>10.1f}%
TOTAL:          {format_currency(cogs_total):>12}  {format_currency(total_sales):>12}  {total_pct:>10.1f}%

Note: Bar = Spirits + Ingredients combined
"""
            
            st.download_button(
                label="📥 Export COGS Report",
                data=report,
                file_name=f"cogs_report_{start_date}_to_{end_date}.txt",
                mime="text/plain",
                key="export_cogs"
            )
    
    with tab_trends:
        st.markdown("### 📈 COGS Trends Over Time")
        
        # Load COGS history for trends
        cogs_history = load_cogs_history()
        
        if cogs_history is not None and len(cogs_history) > 0:
            # COGS over time chart
            st.markdown("#### Total COGS by Period")
            
            trend_df = cogs_history.copy()
            trend_df['Period'] = trend_df['Period Start'] + ' to ' + trend_df['Period End']
            
            fig_trend = px.line(
                trend_df,
                x='Calculation Date',
                y='Total COGS',
                markers=True,
                title='Total COGS Trend'
            )
            fig_trend.update_layout(
                yaxis_tickprefix='$',
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # COGS by category over time
            st.markdown("#### COGS by Category Over Time")
            
            category_trend = trend_df.melt(
                id_vars=['Calculation Date'],
                value_vars=['Spirits COGS', 'Wine COGS', 'Beer COGS', 'Ingredients COGS'],
                var_name='Category',
                value_name='COGS'
            )
            category_trend['Category'] = category_trend['Category'].str.replace(' COGS', '')
            
            fig_cat_trend = px.line(
                category_trend,
                x='Calculation Date',
                y='COGS',
                color='Category',
                markers=True,
                title='COGS by Category',
                color_discrete_map={
                    'Spirits': '#8B5CF6',
                    'Wine': '#EC4899',
                    'Beer': '#F59E0B',
                    'Ingredients': '#10B981'
                }
            )
            fig_cat_trend.update_layout(
                yaxis_tickprefix='$',
                yaxis_tickformat=',.0f'
            )
            st.plotly_chart(fig_cat_trend, use_container_width=True)
            
            # COGS Percentage trend (if sales data exists)
            if 'COGS Percentage' in cogs_history.columns and cogs_history['COGS Percentage'].sum() > 0:
                st.markdown("#### COGS Percentage Trend")
                
                pct_df = cogs_history[cogs_history['COGS Percentage'] > 0]
                
                if len(pct_df) > 0:
                    fig_pct = px.line(
                        pct_df,
                        x='Calculation Date',
                        y='COGS Percentage',
                        markers=True,
                        title='COGS % of Sales'
                    )
                    fig_pct.update_layout(yaxis_ticksuffix='%')
                    
                    # Add target line at 20%
                    fig_pct.add_hline(y=20, line_dash="dash", line_color="green", 
                                      annotation_text="Target (20%)")
                    fig_pct.add_hline(y=25, line_dash="dash", line_color="orange",
                                      annotation_text="Caution (25%)")
                    
                    st.plotly_chart(fig_pct, use_container_width=True)
        else:
            st.info("📊 No COGS history available yet. Save calculations from the Calculator tab to see trends over time.")
    
    with tab_history:
        st.markdown("### 📜 Saved COGS Calculations")
        
        cogs_history = load_cogs_history()
        
        if cogs_history is not None and len(cogs_history) > 0:
            st.dataframe(
                cogs_history,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Spirits COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Wine COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Beer COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Ingredients COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Total COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Purchases": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Sales": st.column_config.NumberColumn(format="$%.2f"),
                    "COGS Percentage": st.column_config.NumberColumn(format="%.1f%%")
                }
            )
            
            # Export all history
            st.markdown("---")
            csv_export = cogs_history.to_csv(index=False)
            st.download_button(
                label="📥 Export All COGS History (CSV)",
                data=csv_export,
                file_name=f"cogs_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                key="export_cogs_history"
            )
        else:
            st.info("📊 No saved COGS calculations yet. Use the Calculator tab to create and save calculations.")


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
