# =============================================================================
# BEVERAGE MANAGEMENT APP - BUTTERBIRD V2.14
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients, N/A Beverages)
#   - Weekly Order Builder
#   - Cocktail Builds Book
#   - Cost of Goods Sold (COGS) Calculator
#   - Bar Prep Recipe Book
#
# Version History:
#   V1.0 - V3.7: Development versions (see previous files for detailed history)
#   BETA 1.0 - CLIENT CONFIGURATION SYSTEM (Production-Ready Template)
#   bb_V1 - Butterbird initial deployment (clean slate, no sample data)
#   bb_V1.1 - CSV upload improvements:
#           - Added column validation with missing column error messages
#           - Case-insensitive column name matching and normalization
#           - Added debugging warnings for missing columns in display functions
#           - Fixed Product column check in calculated fields display
#   bb_V1.2 - Recipe management functionality:
#           - Added "Add New Recipe" tab to Cocktail Builds Book
#           - Added "Add New Recipe" tab to Bar Prep Recipe Book
#           - Cocktail form: name, glass, sale price, up to 8 ingredients, instructions
#           - Bar Prep form: name, category, yield, shelf life, storage, up to 10 ingredients, instructions
#           - Duplicate recipe name validation
#           - Auto-save to Google Sheets on recipe creation
#   bb_V1.3 - Bar Prep ingredient selection update:
#           - Changed Bar Prep ingredients from text input to dropdown selector
#           - Ingredients now selected from Master Inventory (same as Cocktail Builds)
#   bb_V1.4 - CSV upload UX improvement:
#           - Moved CSV upload into each inventory tab (Spirits, Wine, Beer, Ingredients)
#           - Each tab now shows only its category-specific upload instructions
#           - Removed confusing category dropdown from upload section
#           - Unique button keys per category to prevent conflicts
#   bb_V1.5 - Google Sheets data type handling:
#           - Added numeric conversion for all calculation columns
#           - Handles currency-formatted strings ($25.00) from Google Sheets
#           - Handles percentage-formatted strings from Google Sheets
#           - Prevents division errors when data contains non-numeric values
#           - Applied fix to Spirits, Wine, Beer, and Ingredients inventory displays
#   bb_V1.6 - Spirits inventory field updates:
#           - Renamed "Cost" to "Bottle Cost"
#           - Renamed "Margin" to "Target Margin"
#           - Reordered Input fields: Product, Type, Bottle Cost, Size (oz.), 
#             [loc1], [loc2], [loc3], Target Margin, Use, Distributor, Order Notes
#           - Updated CSV upload instructions and validation
#           - Updated all calculation formulas to use new column names
#   bb_V1.7 - Spirits calculated fields updates:
#           - Reordered Calculated Fields: Product, Cost/Oz, Neat Price, Total Inventory, Value
#           - Removed "Suggested Retail" from calculated fields
#   bb_V1.8 - Spirits pour pricing calculations:
#           - Added new calculated fields: Shot, Single, Neat Pour, Double
#           - Shot = (1 * Cost/Oz) / Target Margin
#           - Single = (1.5 * Cost/Oz) / Target Margin
#           - Neat Pour = (2 * Cost/Oz) / Target Margin (renamed from Neat Price)
#           - Double = (3 * Cost/Oz) / Target Margin
#           - Final calculated field order: Product, Cost/Oz, Shot, Single, Neat Pour, Double, Total Inventory, Value
#   bb_V1.9 - Beer inventory field updates:
#           - Renamed "Margin" to "Target Margin"
#           - Moved Target Margin to right of Storage, left of Distributor
#           - New Input field order: Product, Type, Cost per Keg/Case, Size, UoM,
#             [loc1], [loc2], [loc3], Target Margin, Distributor, Order Notes
#   bb_V2.0 - Beer calculated fields updates:
#           - Reordered Calculated Fields: Product, Cost/Unit, Menu Price, Total Inventory, Value
#           - Fixed Menu Price calculation:
#             * Half Barrel, Quarter Barrel, Sixtel: (16 * Cost/Unit) / Target Margin
#             * Case: Cost/Unit / Target Margin
#   bb_V2.1 - Added N/A Beverages inventory category:
#           - New tab in Master Inventory module for non-alcoholic beverages
#           - Same structure as Ingredients: Product, Cost, Size/Yield, UoM, locations, Distributor, Order Notes
#           - Calculated fields: Total Inventory, Cost/Unit
#           - Full Google Sheets integration (load/save)
#           - CSV upload support with validation
#           - Added to inventory dashboard metrics (6 columns now)
#   bb_V2.2 - Dynamic ingredient addition in recipe forms:
#           - Cocktail Builds: Replaced fixed 8-ingredient form with dynamic "Add Ingredient" button
#           - Bar Prep: Replaced fixed 10-ingredient form with dynamic "Add Ingredient" button
#           - Both forms now start with 1 ingredient row and allow adding/removing as needed
#           - Added trash button to remove individual ingredients
#           - Form resets after successful recipe save
#   bb_V2.3 - Password protection:
#           - Added optional password gate before app access
#           - Password stored securely in secrets.toml (app_password)
#           - Clean login screen with branding
#           - If no password configured, app remains open access
#           - Uses try/except for robust secrets access
#   bb_V2.4 - Auto-sync Syrups to Ingredients inventory:
#           - New syrup recipes automatically added to Ingredients inventory
#           - Calculates total batch cost from recipe ingredients
#           - Sets Cost = total batch cost, Size/Yield = recipe yield, UoM = oz
#           - Distributor set to "House-made", Order Notes = "Bar Prep Recipe"
#           - Sync button to add existing syrups that weren't auto-added
#           - Syrups remain in Ingredients until manually deleted
#   bb_V2.5 - Batch scaling for Bar Prep recipes:
#           - Added scaling controls at top of each expanded recipe
#           - Preset buttons: ½×, 1×, 2×, 3×, 4×
#           - Custom multiplier input (0.1 to 20×, step 0.25)
#           - Scales ingredient amounts and total yield
#           - Shows scaled batch cost with indicator
#           - Cost/oz remains constant (doesn't change with scale)
#           - Instructions, shelf life, storage unchanged
#           - Scaling is temporary/display only - never saves over base recipe
#   bb_V2.6 - Cocktail pour cost calculation update:
#           - Changed margin calculation from (price-cost)/price to cost/price
#           - Renamed "Margin" to "Pour Cost" for clarity
#           - Pour Cost = Cocktail Cost / Menu Price × 100
#   bb_V2.7 - Bar Prep category rename:
#           - Renamed "Syrups & Infusions" tab to "Syrups, Infusions & Garnishes"
#           - Updated category dropdown to match
#           - Updated all category filters and auto-sync logic
#   bb_V2.8 - Inventory save logic improvement:
#           - Save now overwrites Google Sheet with current app data
#           - Deletions in app now sync to Google Sheets on save
#           - Simplified save logic for all inventory types (Spirits, Wine, Beer, Ingredients, N/A Beverages)
#           - Bidirectional sync: App changes save to Sheets, Sheet changes load on app refresh
#           - Added backward compatibility for old "Syrups" category in Bar Prep
#   bb_V2.9 - Ingredients and N/A Beverages display updates:
#           - Calculated fields reordered: Product, Cost/Unit, Total Inventory, Value
#           - Added Value field (Cost × Total Inventory) with total at bottom
#           - Removed index from all Input tables using reset_index(drop=True)
#           - Applied to: Spirits, Wine, Beer, Ingredients, N/A Beverages
#   bb_V2.10 - Recipe editing functionality:
#           - Added Edit button to recipe cards (Cocktails and Bar Prep)
#           - Full edit form with pre-populated values
#           - Dynamic ingredient editing (add/remove ingredients)
#           - Cancel button to return to view mode without saving
#           - Duplicate name checking (excludes current recipe being edited)
#   bb_V2.11 - Batched Cocktails sync to Spirits inventory:
#           - New batched cocktail recipes auto-add to Spirits inventory
#           - Added "Sync Batched Cocktails to Spirits" button in Batched Cocktails tab
#           - Spirits entry includes: Product, Type="Batched Cocktail", Bottle Cost, Size (oz.)
#           - Pour prices (Shot, Single, Neat Pour, Double) calculated from cost/oz and margin
#           - Distributor defaults to "House-made", Order Notes to "Bar Prep Recipe"
#   bb_V2.12 - Filtered inventory edit fix:
#           - Edits made in filtered views now persist when filters change
#           - merge_edits_to_inventory() merges edits back to full inventory immediately
#           - Save button disabled when filters are active (prevents data loss)
#           - Warning message prompts user to clear filters before saving
#           - Row add/delete disabled when filtered to prevent complexity
#           - Applied to all 5 inventory types: Spirits, Wine, Beer, Ingredients, N/A Beverages
#           - Added centralized CLIENT_CONFIG for restaurant customization
#           - Configurable restaurant name and tagline
#           - Configurable inventory location names (applied to Master Inventory + Weekly Orders)
#           - Configurable branding colors and fonts
#           - Feature toggles to enable/disable modules per client
#           - Default distributors for dropdown pre-population
#           - Default margins by category (Spirits, Wine, Beer)
#           - Google Sheets configuration moved to CLIENT_CONFIG
#           - CSS dynamically generated from config values
#           - Ready for client branch deployments
#   bb_V2.13 - Full COGS Calculator implementation:
#           - Three tabs: COGS Calculator, Trends & Analytics, Saved Calculations
#           - Inventory period selection from saved snapshots
#           - Auto-populated purchases from Order History by Invoice Date
#           - Manual override option for purchase amounts
#           - COGS calculation by category (Spirits, Wine, Beer, Ingredients)
#           - COGS as percentage of sales (Wine, Beer, Bar categories)
#           - Bar COGS combines Spirits + Ingredients for cocktail cost tracking
#           - Visual charts: pie chart distribution, horizontal bar chart by category
#           - Status indicators for COGS % targets (≤20% ✅, 20-25% 👍, 25-30% ⚠️, >30% 🚨)
#           - Save calculations to history with full period data
#           - Export COGS report as formatted text file
#           - Trends tab: COGS over time, category trends, percentage trends with target lines
#           - History tab: view all saved calculations, export as CSV
#           - Removed "Upstairs Bar" location column (now 2 locations: Main Bar, Storage)
#           - Dynamic location column handling via get_location_columns() helper
#           - All inventory functions updated to support variable number of locations
#           - Added pending edits pattern for filtered view editing (fixes double-input bug)
#   bb_V2.14 - Location and filtered editing improvements:
#           - Fixed filtered view editing bug (values now persist on first input)
#           - Enhanced merge_edits_to_inventory() to track and apply pending edits
#           - All process_uploaded_* functions now use dynamic location columns
#           - Improved handling for 2-location configuration (Main Bar, Storage)
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
        "location_1": "Main Bar",
        "location_2": "Storage",
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
        "na_beverages_inventory": "na_beverages_inventory",
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


def get_location_3() -> Optional[str]:
    """Returns the name of location 3, or None if not configured."""
    return CLIENT_CONFIG["locations"].get("location_3", None)


def get_location_columns() -> list:
    """Returns list of configured location column names."""
    locations = [get_location_1(), get_location_2()]
    loc3 = get_location_3()
    if loc3:
        locations.append(loc3)
    return locations


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
        ('na_beverages_inventory', get_sheet_name('na_beverages_inventory')),
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
        'na_beverages': calculate_total_value(st.session_state.get('na_beverages_inventory', pd.DataFrame())),
    }
    values['total'] = sum(values.values())
    
    new_record = {
        'Date': datetime.now().strftime("%Y-%m-%d"),
        'Spirits Value': values['spirits'],
        'Wine Value': values['wine'],
        'Beer Value': values['beer'],
        'Ingredients Value': values['ingredients'],
        'N/A Beverages Value': values['na_beverages'],
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
        for col in ['Spirits Value', 'Wine Value', 'Beer Value', 'Ingredients Value', 'N/A Beverages Value', 'Total Value']:
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


def add_syrup_to_ingredients(recipe: dict) -> bool:
    """
    Adds a Syrup/Infusion recipe to the Ingredients inventory.
    
    Args:
        recipe: Dictionary with recipe data including 'name', 'yield_oz', 'ingredients'
    
    Returns:
        True if added successfully, False if already exists
    """
    loc_cols = get_location_columns()
    
    recipe_name = recipe.get('name', '')
    yield_oz = recipe.get('yield_oz', 0)
    ingredients_list = recipe.get('ingredients', [])
    
    if not recipe_name or yield_oz <= 0:
        return False
    
    # Calculate total batch cost from ingredients
    total_cost = calculate_recipe_cost(ingredients_list)
    
    # Initialize ingredients inventory if needed
    if 'ingredients_inventory' not in st.session_state:
        st.session_state.ingredients_inventory = get_sample_ingredients()
    
    ingredients_df = st.session_state.ingredients_inventory
    
    # Check if product already exists (case-insensitive)
    if len(ingredients_df) > 0 and 'Product' in ingredients_df.columns:
        existing = ingredients_df[ingredients_df['Product'].str.lower().str.strip() == recipe_name.lower().strip()]
        if len(existing) > 0:
            # Already exists, don't add duplicate
            return False
    
    # Create new ingredient row with dynamic location columns
    new_row = {
        'Product': recipe_name,
        'Cost': round(total_cost, 2),
        'Size/Yield': yield_oz,
        'UoM': 'oz',
        'Cost/Unit': round(total_cost / yield_oz, 4) if yield_oz > 0 else 0,
        'Total Inventory': 0.0,
        'Distributor': 'House-made',
        'Order Notes': 'Bar Prep Recipe'
    }
    # Add location columns dynamically
    for loc in loc_cols:
        new_row[loc] = 0.0
    
    # Add to ingredients inventory
    new_df = pd.DataFrame([new_row])
    st.session_state.ingredients_inventory = pd.concat([ingredients_df, new_df], ignore_index=True)
    
    # Save to Google Sheets
    save_all_inventory_data()
    
    return True


def sync_syrups_to_ingredients() -> Tuple[int, int]:
    """
    Syncs all existing Syrup recipes to Ingredients inventory.
    
    Returns:
        Tuple of (added_count, skipped_count)
    """
    recipes = st.session_state.get('bar_prep_recipes', [])
    # Support both old "Syrups" and new "Syrups, Infusions & Garnishes" categories
    syrups = [r for r in recipes if r.get('category') in ['Syrups', 'Syrups, Infusions & Garnishes']]
    
    added = 0
    skipped = 0
    
    for recipe in syrups:
        if add_syrup_to_ingredients(recipe):
            added += 1
        else:
            skipped += 1
    
    return (added, skipped)


def add_batched_cocktail_to_spirits(recipe: dict) -> bool:
    """
    Adds a Batched Cocktail recipe to the Spirits inventory.
    
    Args:
        recipe: Dictionary with recipe data including 'name', 'yield_oz', 'ingredients'
    
    Returns:
        True if added successfully, False if already exists
    """
    loc_cols = get_location_columns()
    
    recipe_name = recipe.get('name', '')
    yield_oz = recipe.get('yield_oz', 0)
    ingredients_list = recipe.get('ingredients', [])
    
    if not recipe_name or yield_oz <= 0:
        return False
    
    # Calculate total batch cost from ingredients
    total_cost = calculate_recipe_cost(ingredients_list)
    cost_per_oz = total_cost / yield_oz if yield_oz > 0 else 0
    
    # Initialize spirits inventory if needed
    if 'spirits_inventory' not in st.session_state:
        st.session_state.spirits_inventory = get_sample_spirits()
    
    spirits_df = st.session_state.spirits_inventory
    
    # Check if product already exists (case-insensitive)
    if len(spirits_df) > 0 and 'Product' in spirits_df.columns:
        existing = spirits_df[spirits_df['Product'].str.lower().str.strip() == recipe_name.lower().strip()]
        if len(existing) > 0:
            # Already exists, don't add duplicate
            return False
    
    # Get default margin from config
    default_margin = CLIENT_CONFIG.get('default_margin', 80)
    
    # Calculate pour prices based on cost/oz and margin
    # Pour price = cost / (1 - margin/100)
    margin_multiplier = 1 / (1 - default_margin / 100) if default_margin < 100 else 5
    shot_price = round(cost_per_oz * 1.5 * margin_multiplier, 2)  # 1.5 oz shot
    single_price = round(cost_per_oz * 1.5 * margin_multiplier, 2)  # 1.5 oz single
    neat_price = round(cost_per_oz * 2.0 * margin_multiplier, 2)  # 2 oz neat
    double_price = round(cost_per_oz * 3.0 * margin_multiplier, 2)  # 3 oz double
    
    # Create new spirits row with dynamic location columns
    new_row = {
        'Product': recipe_name,
        'Type': 'Batched Cocktail',
        'Bottle Cost': round(total_cost, 2),
        'Size (oz.)': yield_oz,
        'Target Margin': default_margin,
        'Use': 'Batched',
        'Distributor': 'House-made',
        'Order Notes': 'Bar Prep Recipe',
        'Cost/Oz': round(cost_per_oz, 4),
        'Shot': shot_price,
        'Single': single_price,
        'Neat Pour': neat_price,
        'Double': double_price,
        'Total Inventory': 0.0,
        'Value': 0.0
    }
    # Add location columns dynamically
    for loc in loc_cols:
        new_row[loc] = 0.0
    
    # Add to spirits inventory
    new_df = pd.DataFrame([new_row])
    st.session_state.spirits_inventory = pd.concat([spirits_df, new_df], ignore_index=True)
    
    # Save to Google Sheets
    save_all_inventory_data()
    
    return True


def sync_batched_cocktails_to_spirits() -> Tuple[int, int]:
    """
    Syncs all existing Batched Cocktail recipes to Spirits inventory.
    
    Returns:
        Tuple of (added_count, skipped_count)
    """
    recipes = st.session_state.get('bar_prep_recipes', [])
    batched = [r for r in recipes if r.get('category') == 'Batched Cocktails']
    
    added = 0
    skipped = 0
    
    for recipe in batched:
        if add_batched_cocktail_to_spirits(recipe):
            added += 1
        else:
            skipped += 1
    
    return (added, skipped)


def merge_edits_to_inventory(edited_df: pd.DataFrame, inventory_key: str, original_products: list) -> None:
    """
    Merges edited rows back to the full inventory in session state.
    Also stores edits as pending to ensure they persist across reruns.
    Only updates existing products, doesn't add or remove rows.
    
    Args:
        edited_df: The edited DataFrame from the data_editor
        inventory_key: The session state key for the inventory (e.g., 'spirits_inventory')
        original_products: List of product names that were in the filtered view before editing
    """
    if inventory_key not in st.session_state:
        return
    
    full_inventory = st.session_state[inventory_key]
    if len(full_inventory) == 0 or 'Product' not in full_inventory.columns:
        return
    
    if len(edited_df) == 0 or 'Product' not in edited_df.columns:
        return
    
    # Determine the pending edits key based on inventory type
    pending_key = inventory_key.replace('_inventory', '_pending_edits')
    if pending_key not in st.session_state:
        st.session_state[pending_key] = {}
    
    # Update each row in the full inventory that matches a product in the edited df
    for idx, edited_row in edited_df.iterrows():
        product_name = edited_row.get('Product', '')
        if not product_name:
            continue
        
        # Find matching row in full inventory
        mask = full_inventory['Product'] == product_name
        if mask.any():
            # Track changes for this product
            product_edits = {}
            
            # Update all columns that exist in both dataframes
            for col in edited_df.columns:
                if col in full_inventory.columns:
                    old_val = full_inventory.loc[mask, col].iloc[0]
                    new_val = edited_row[col]
                    
                    # Check if value actually changed
                    try:
                        if pd.isna(old_val) and pd.isna(new_val):
                            continue
                        if old_val != new_val:
                            full_inventory.loc[mask, col] = new_val
                            product_edits[col] = new_val
                    except:
                        # Handle comparison errors by just updating
                        full_inventory.loc[mask, col] = new_val
                        product_edits[col] = new_val
            
            # Store pending edits for this product if any changes were made
            if product_edits:
                st.session_state[pending_key][product_name] = product_edits
    
    st.session_state[inventory_key] = full_inventory


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
    
    # Get configurable location names
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    
    orders = []
    for _, row in weekly_inv.iterrows():
        par = row.get('Par', row.get('Par Level', 0))
        
        # Calculate total inventory from configurable location columns
        # First try the new location column names, then fall back to old names
        loc1_val = row.get(loc1, row.get('Bar Inventory', 0))
        loc2_val = row.get(loc2, row.get('Storage Inventory', 0))
        
        # Sum all configured locations
        total_inv = row.get('Total Current Inventory', 
                          row.get('Total Inventory', sum(row.get(loc, 0) for loc in loc_cols)))
        
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
# SAMPLE DATA FUNCTIONS (with caching) - Using CLIENT_CONFIG locations
# =============================================================================

@st.cache_data
def get_sample_spirits():
    """Returns empty spirit inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Type", "Bottle Cost", "Size (oz.)"] + loc_cols + ["Target Margin", 
               "Use", "Distributor", "Order Notes", "Cost/Oz", "Shot", "Single", "Neat Pour", "Double", "Total Inventory", "Value"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_wines():
    """Returns empty wine inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Type", "Cost", "Size (oz.)", "Margin", "Bottle Price"] + loc_cols + ["Total Inventory",
               "Value", "Distributor", "Order Notes", "BTG", "Suggested Retail"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_beers():
    """Returns empty beer inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Type", "Cost per Keg/Case", "Size", "UoM"] + loc_cols + ["Target Margin", "Distributor", "Order Notes",
               "Total Inventory", "Cost/Unit", "Menu Price", "Value"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_ingredients():
    """Returns empty ingredient inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit"] + loc_cols + ["Total Inventory",
               "Distributor", "Order Notes"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_na_beverages():
    """Returns empty N/A beverages inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit"] + loc_cols + ["Total Inventory",
               "Distributor", "Order Notes"]
    return pd.DataFrame(columns=columns)


@st.cache_data
def get_sample_weekly_inventory():
    """Returns empty weekly inventory DataFrame with proper columns."""
    loc_cols = get_location_columns()
    
    columns = ["Product", "Category", "Par"] + loc_cols + ["Total Current Inventory", "Unit", "Unit Cost", "Distributor", "Order Notes"]
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
        'na_beverages_inventory': (get_sheet_name('na_beverages_inventory'), get_sample_na_beverages),
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
    # Calculate base costs
    base_cost = calculate_recipe_cost(recipe.get('ingredients', []))
    
    # Create a safe key from recipe name
    safe_name = recipe['name'].replace(' ', '_').replace('/', '_').replace("'", "")
    
    if recipe_type == 'bar_prep':
        yield_oz = recipe.get('yield_oz', 32)
        cost_per_oz = base_cost / yield_oz if yield_oz > 0 else 0
        header = f"**{recipe['name']}** | Yield: {recipe.get('yield_description', '')} | Batch: {format_currency(base_cost)} | Cost/oz: {format_currency(cost_per_oz)}"
    else:
        sale_price = recipe.get('sale_price', 0)
        pour_cost = (base_cost / sale_price * 100) if sale_price > 0 else 0
        header = f"**{recipe['name']}** | Cost: {format_currency(base_cost)} | Price: {format_currency(sale_price)} | Pour Cost: {pour_cost:.1f}%"
    
    with st.expander(header, expanded=False):
        # Batch scaling for bar_prep recipes
        if recipe_type == 'bar_prep':
            st.markdown("#### 📏 Batch Scaling")
            scale_col1, scale_col2, scale_col3 = st.columns([2, 1, 1])
            
            with scale_col1:
                # Preset buttons
                preset_cols = st.columns(5)
                scale_key = f"scale_{recipe_type}_{safe_name}_{idx}"
                
                # Initialize scale in session state if not exists
                if scale_key not in st.session_state:
                    st.session_state[scale_key] = 1.0
                
                with preset_cols[0]:
                    if st.button("½×", key=f"half_{safe_name}_{idx}", help="Half batch"):
                        st.session_state[scale_key] = 0.5
                        st.rerun()
                with preset_cols[1]:
                    if st.button("1×", key=f"single_{safe_name}_{idx}", help="Standard batch"):
                        st.session_state[scale_key] = 1.0
                        st.rerun()
                with preset_cols[2]:
                    if st.button("2×", key=f"double_{safe_name}_{idx}", help="Double batch"):
                        st.session_state[scale_key] = 2.0
                        st.rerun()
                with preset_cols[3]:
                    if st.button("3×", key=f"triple_{safe_name}_{idx}", help="Triple batch"):
                        st.session_state[scale_key] = 3.0
                        st.rerun()
                with preset_cols[4]:
                    if st.button("4×", key=f"quad_{safe_name}_{idx}", help="Quadruple batch"):
                        st.session_state[scale_key] = 4.0
                        st.rerun()
            
            with scale_col2:
                custom_scale = st.number_input(
                    "Custom",
                    min_value=0.1,
                    max_value=20.0,
                    value=st.session_state[scale_key],
                    step=0.25,
                    key=f"custom_scale_{safe_name}_{idx}",
                    help="Enter custom multiplier"
                )
                if custom_scale != st.session_state[scale_key]:
                    st.session_state[scale_key] = custom_scale
                    st.rerun()
            
            with scale_col3:
                current_scale = st.session_state[scale_key]
                if current_scale != 1.0:
                    st.markdown(f"**Scaling: {current_scale}×**")
                else:
                    st.markdown("**Standard Batch**")
            
            # Get the current scale factor
            scale_factor = st.session_state[scale_key]
            
            # Calculate scaled values
            scaled_cost = base_cost * scale_factor
            scaled_yield = yield_oz * scale_factor
            cost_per_oz = base_cost / yield_oz if yield_oz > 0 else 0  # Cost/oz stays same regardless of scale
            
            st.markdown("---")
        else:
            scale_factor = 1.0
            scaled_cost = base_cost
        
        col_info, col_cost = st.columns([2, 1])
        
        with col_info:
            if recipe_type == 'bar_prep':
                # Show scaled yield
                base_yield_desc = recipe.get('yield_description', '')
                if scale_factor != 1.0:
                    st.markdown(f"**Yield:** {scaled_yield:.1f} oz *(scaled from {yield_oz} oz)*")
                else:
                    st.markdown(f"**Yield:** {base_yield_desc} ({yield_oz} oz)")
                st.markdown(f"**Shelf Life:** {recipe.get('shelf_life', 'N/A')}")
                st.markdown(f"**Storage:** {recipe.get('storage', 'N/A')}")
            else:
                st.markdown(f"**Glass:** {recipe.get('glass', 'N/A')}")
                st.markdown(f"**Sale Price:** {format_currency(recipe.get('sale_price', 0))}")
            
            # Ingredients table (scaled for bar_prep)
            st.markdown("**Ingredients:**")
            ing_data = []
            for ing in recipe.get('ingredients', []):
                base_amount = ing['amount']
                scaled_amount = base_amount * scale_factor
                _, ing_cost = get_product_cost(ing['product'], scaled_amount, ing.get('unit', 'oz'))
                
                if recipe_type == 'bar_prep' and scale_factor != 1.0:
                    ing_data.append({
                        "Ingredient": ing['product'],
                        "Amount": f"{scaled_amount:.2f}",
                        "Unit": ing.get('unit', 'oz'),
                        "Cost": ing_cost
                    })
                else:
                    ing_data.append({
                        "Ingredient": ing['product'],
                        "Amount": base_amount,
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
            
            if recipe_type == 'bar_prep':
                if scale_factor != 1.0:
                    st.metric("Scaled Batch Cost", format_currency(scaled_cost), delta=f"{scale_factor}× batch")
                    st.caption(f"Base batch: {format_currency(base_cost)}")
                else:
                    st.metric("Batch Cost", format_currency(base_cost))
                st.metric("Cost/oz", format_currency(cost_per_oz))
                st.metric("Cost/quart", format_currency(cost_per_oz * 32))
            else:
                st.metric("Total Cost", format_currency(base_cost))
                st.metric("Sale Price", format_currency(recipe.get('sale_price', 0)))
                st.metric("Pour Cost", f"{pour_cost:.1f}%")
        
        if on_delete:
            st.markdown("---")
            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button("✏️ Edit Recipe", key=f"edit_{recipe_type}_{safe_name}"):
                    st.session_state[f'editing_{recipe_type}'] = recipe['name']
                    st.rerun()
            with col_delete:
                if st.button("🗑️ Delete Recipe", key=f"delete_{recipe_type}_{safe_name}"):
                    on_delete(recipe['name'])


def display_recipe_list(recipes: list, recipe_type: str, category_filter: str = None, session_key: str = None):
    """Displays a filtered list of recipes."""
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
# CSV UPLOAD PROCESSING FUNCTIONS - Using CLIENT_CONFIG locations
# =============================================================================

def process_uploaded_spirits(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Spirits inventory CSV."""
    loc_cols = get_location_columns()
    
    try:
        df = df.copy()
        for col in ['Bottle Cost', 'Cost/Oz', 'Shot', 'Single', 'Neat Pour', 'Double', 'Value']:
            df = clean_currency_column(df, col)
        if 'Target Margin' in df.columns:
            df = clean_percentage_column(df, 'Target Margin')
        for col in ['Size (oz.)', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle location columns dynamically
        for col in loc_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
        
        # Calculate Total Inventory from location columns
        df['Total Inventory'] = sum(df[col] for col in loc_cols)
        
        # Recalculate all calculated fields
        if 'Bottle Cost' in df.columns and 'Size (oz.)' in df.columns:
            df['Cost/Oz'] = df.apply(
                lambda row: round(row['Bottle Cost'] / row['Size (oz.)'], 2) if row['Size (oz.)'] > 0 else 0, axis=1)
        
        if 'Bottle Cost' in df.columns and 'Size (oz.)' in df.columns and 'Target Margin' in df.columns:
            # Shot = (1 * Cost/Oz) / Target Margin
            df['Shot'] = df.apply(
                lambda row: math.ceil((1 * (row['Bottle Cost'] / row['Size (oz.)'])) / (row['Target Margin'] / 100)) if row['Target Margin'] > 0 and row['Size (oz.)'] > 0 else 0, axis=1)
            # Single = (1.5 * Cost/Oz) / Target Margin
            df['Single'] = df.apply(
                lambda row: math.ceil((1.5 * (row['Bottle Cost'] / row['Size (oz.)'])) / (row['Target Margin'] / 100)) if row['Target Margin'] > 0 and row['Size (oz.)'] > 0 else 0, axis=1)
            # Neat Pour = (2 * Cost/Oz) / Target Margin
            df['Neat Pour'] = df.apply(
                lambda row: math.ceil((2 * (row['Bottle Cost'] / row['Size (oz.)'])) / (row['Target Margin'] / 100)) if row['Target Margin'] > 0 and row['Size (oz.)'] > 0 else 0, axis=1)
            # Double = (3 * Cost/Oz) / Target Margin
            df['Double'] = df.apply(
                lambda row: math.ceil((3 * (row['Bottle Cost'] / row['Size (oz.)'])) / (row['Target Margin'] / 100)) if row['Target Margin'] > 0 and row['Size (oz.)'] > 0 else 0, axis=1)
        
        if 'Bottle Cost' in df.columns and 'Total Inventory' in df.columns:
            df['Value'] = round(df['Bottle Cost'] * df['Total Inventory'], 2)
        return df
    except Exception as e:
        st.error(f"Error processing spirits data: {e}")
        return df


def process_uploaded_wine(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Wine inventory CSV."""
    loc_cols = get_location_columns()
    
    try:
        df = df.copy()
        for col in ['Cost', 'Bottle Price', 'BTG', 'Suggested Retail', 'Value']:
            df = clean_currency_column(df, col)
        if 'Margin' in df.columns:
            df = clean_percentage_column(df, 'Margin')
        for col in ['Size (oz.)', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle location columns dynamically
        for col in loc_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
        
        # Calculate Total Inventory from location columns
        df['Total Inventory'] = sum(df[col] for col in loc_cols)
        
        # Recalculate all calculated fields
        if 'Cost' in df.columns and 'Margin' in df.columns:
            df['Bottle Price'] = df.apply(
                lambda row: math.ceil(row['Cost'] / (row['Margin'] / 100)) if row['Margin'] > 0 else 0, axis=1)
        if 'Cost' in df.columns and 'Total Inventory' in df.columns:
            df['Value'] = round(df['Cost'] * df['Total Inventory'], 2)
        if 'Cost' in df.columns:
            df['BTG'] = df['Cost'].apply(lambda x: math.ceil(x / 4))
            df['Suggested Retail'] = df['Cost'].apply(lambda x: math.ceil(x * 1.44))
        return df
    except Exception as e:
        st.error(f"Error processing wine data: {e}")
        return df


def process_uploaded_beer(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Beer inventory CSV."""
    loc_cols = get_location_columns()
    
    try:
        df = df.copy()
        for col in ['Cost per Keg/Case', 'Cost/Unit', 'Menu Price', 'Value']:
            df = clean_currency_column(df, col)
        if 'Target Margin' in df.columns:
            df = clean_percentage_column(df, 'Target Margin')
        for col in ['Size', 'Inventory']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Handle location columns dynamically
        for col in loc_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
        
        # Calculate Total Inventory from location columns
        df['Total Inventory'] = sum(df[col] for col in loc_cols)
        
        # Recalculate all calculated fields
        if 'Cost per Keg/Case' in df.columns and 'Size' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost per Keg/Case'] / row['Size'], 2) if row['Size'] > 0 else 0, axis=1)
        if 'Cost per Keg/Case' in df.columns and 'Total Inventory' in df.columns:
            df['Value'] = round(df['Cost per Keg/Case'] * df['Total Inventory'], 2)
        
        # Menu Price calculation
        if 'Cost/Unit' in df.columns and 'Target Margin' in df.columns and 'Type' in df.columns:
            def calc_menu_price(row):
                cost_unit = row.get("Cost/Unit", 0)
                margin = row.get("Target Margin", 0)
                if margin <= 0:
                    return 0
                if row.get("Type", "") in ["Half Barrel", "Quarter Barrel", "Sixtel"]:
                    # For kegs: (16 * Cost/Unit) / Target Margin
                    return round((cost_unit * 16) / (margin / 100))
                elif row.get("Type", "") == "Case":
                    # For cases: Cost/Unit / Target Margin
                    return round(cost_unit / (margin / 100))
                return 0
            df['Menu Price'] = df.apply(calc_menu_price, axis=1)
        return df
    except Exception as e:
        st.error(f"Error processing beer data: {e}")
        return df


def process_uploaded_ingredients(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded Ingredients inventory CSV."""
    loc_cols = get_location_columns()
    
    try:
        df = df.copy()
        for col in ['Cost', 'Cost/Unit']:
            df = clean_currency_column(df, col)
        if 'Size/Yield' in df.columns:
            df['Size/Yield'] = pd.to_numeric(df['Size/Yield'], errors='coerce').fillna(0)
        
        # Handle location columns dynamically
        for col in loc_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
        
        # Calculate Total Inventory from location columns
        df['Total Inventory'] = sum(df[col] for col in loc_cols)
        
        if 'Cost' in df.columns and 'Size/Yield' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost'] / row['Size/Yield'], 2) if row['Size/Yield'] > 0 else 0, axis=1)
        return df
    except Exception as e:
        st.error(f"Error processing ingredients data: {e}")
        return df


def process_uploaded_na_beverages(df: pd.DataFrame) -> pd.DataFrame:
    """Processes an uploaded N/A Beverages inventory CSV."""
    loc_cols = get_location_columns()
    
    try:
        df = df.copy()
        for col in ['Cost', 'Cost/Unit']:
            df = clean_currency_column(df, col)
        if 'Size/Yield' in df.columns:
            df['Size/Yield'] = pd.to_numeric(df['Size/Yield'], errors='coerce').fillna(0)
        
        # Handle location columns dynamically
        for col in loc_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                df[col] = 0.0
        
        # Calculate Total Inventory from location columns
        df['Total Inventory'] = sum(df[col] for col in loc_cols)
        
        if 'Cost' in df.columns and 'Size/Yield' in df.columns:
            df['Cost/Unit'] = df.apply(
                lambda row: round(row['Cost'] / row['Size/Yield'], 2) if row['Size/Yield'] > 0 else 0, axis=1)
        return df
    except Exception as e:
        st.error(f"Error processing N/A beverages data: {e}")
        return df


# =============================================================================
# PAGE: HOME (with Feature Toggles)
# =============================================================================

def show_home():
    """Renders the homescreen with navigation cards and feature toggles applied."""
    restaurant_name = CLIENT_CONFIG['restaurant_name']
    tagline = CLIENT_CONFIG['restaurant_tagline']
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🍸 {restaurant_name}</h1>
        <p>{tagline}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Build list of enabled modules
    enabled_modules = []
    
    if is_feature_enabled('master_inventory'):
        enabled_modules.append({
            'id': 'inventory',
            'icon': '📦',
            'title': 'Master Inventory',
            'description': 'Track spirits, wine, beer, and ingredients.<br>View values, costs, and stock levels.',
            'card_class': 'card-inventory',
        })
    
    if is_feature_enabled('weekly_orders'):
        enabled_modules.append({
            'id': 'ordering',
            'icon': '📋',
            'title': 'Weekly Order Builder',
            'description': 'Build weekly orders based on par levels.<br>Track order history and spending.',
            'card_class': 'card-ordering',
        })
    
    if is_feature_enabled('cocktail_builds'):
        enabled_modules.append({
            'id': 'cocktails',
            'icon': '🍹',
            'title': 'Cocktail Builds Book',
            'description': 'Store and cost cocktail recipes.<br>Calculate margins and pricing.',
            'card_class': 'card-cocktails',
        })
    
    if is_feature_enabled('bar_prep'):
        enabled_modules.append({
            'id': 'bar_prep',
            'icon': '🧪',
            'title': 'Bar Prep Recipe Book',
            'description': 'Syrups, infusions, and batched cocktails.<br>Calculate batch costs and cost/oz.',
            'card_class': 'card-barprep',
        })
    
    if is_feature_enabled('cogs_calculator'):
        enabled_modules.append({
            'id': 'cogs',
            'icon': '📊',
            'title': 'Cost of Goods Sold',
            'description': 'Calculate COGS by category.<br>Track trends and export reports.',
            'card_class': 'card-cogs',
        })
    
    # Display modules in rows of 3
    for i in range(0, len(enabled_modules), 3):
        row_modules = enabled_modules[i:i+3]
        
        # Create columns based on number of modules in this row
        if len(row_modules) == 3:
            cols = st.columns(3)
        elif len(row_modules) == 2:
            # Center 2 cards
            spacer_left, col1, col2, spacer_right = st.columns([0.5, 1, 1, 0.5])
            cols = [col1, col2]
        else:
            # Center 1 card
            spacer_left, col1, spacer_right = st.columns([1, 1, 1])
            cols = [col1]
        
        for j, module in enumerate(row_modules):
            with cols[j]:
                st.markdown(f"""
                <div class="module-card {module['card_class']}">
                    <div class="card-icon">{module['icon']}</div>
                    <div class="card-title">{module['title']}</div>
                    <div class="card-description">{module['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(module['title'], key=f"btn_{module['id']}", use_container_width=True, type="primary"):
                    navigate_to(module['id'])
                    st.rerun()
    
    st.markdown("---")
    
    # Last activity indicator
    last_update = st.session_state.get('last_inventory_date', None)
    if last_update:
        st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.9rem;'>📅 Last inventory update: {last_update}</p>", unsafe_allow_html=True)
    
    # Only show warning if not configured
    if not is_google_sheets_configured():
        st.warning("⚠️ Google Sheets not configured - Data will reset on app restart")
    
    st.markdown(f"<p style='text-align: center; color: #888;'>Developed by James Juedes utilizing Claude Opus 4.5</p>", unsafe_allow_html=True)


# =============================================================================
# PAGE: MASTER INVENTORY - Using CLIENT_CONFIG locations
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
        'na_beverages': calculate_total_value(st.session_state.get('na_beverages_inventory', pd.DataFrame())),
    }
    total = sum(values.values())
    
    cols = st.columns(6)
    labels = [('🥃 Spirits', values['spirits']), ('🍷 Wine', values['wine']), 
              ('🍺 Beer', values['beer']), ('🧴 Ingredients', values['ingredients']),
              ('🥤 N/A Bev', values['na_beverages']), ('💰 Total', total)]
    for col, (label, val) in zip(cols, labels):
        with col:
            st.metric(label=label, value=format_currency(val))
    
    st.caption(f"Last inventory recorded: {st.session_state.get('last_inventory_date', 'N/A')}")
    st.markdown("---")
    
    # Tabs
    tab_spirits, tab_wine, tab_beer, tab_ingredients, tab_na_beverages = st.tabs(["🥃 Spirits", "🍷 Wine", "🍺 Beer", "🧴 Ingredients", "🥤 N/A Beverages"])
    
    with tab_spirits:
        show_spirits_inventory_split(st.session_state.get('spirits_inventory', pd.DataFrame()), ["Type", "Distributor", "Use"])
        with st.expander("📤 Upload Spirits Inventory (CSV)", expanded=False):
            show_csv_upload_section("Spirits")
    
    with tab_wine:
        show_wine_inventory_split(st.session_state.get('wine_inventory', pd.DataFrame()), ["Type", "Distributor"])
        with st.expander("📤 Upload Wine Inventory (CSV)", expanded=False):
            show_csv_upload_section("Wine")
    
    with tab_beer:
        show_beer_inventory_split(st.session_state.get('beer_inventory', pd.DataFrame()), ["Type", "Distributor"])
        with st.expander("📤 Upload Beer Inventory (CSV)", expanded=False):
            show_csv_upload_section("Beer")
    
    with tab_ingredients:
        show_ingredients_inventory_split(st.session_state.get('ingredients_inventory', pd.DataFrame()), ["Distributor"])
        with st.expander("📤 Upload Ingredients Inventory (CSV)", expanded=False):
            show_csv_upload_section("Ingredients")
    
    with tab_na_beverages:
        show_na_beverages_inventory_split(st.session_state.get('na_beverages_inventory', pd.DataFrame()), ["Distributor"])
        with st.expander("📤 Upload N/A Beverages Inventory (CSV)", expanded=False):
            show_csv_upload_section("N/A Beverages")


def show_csv_upload_section(upload_category: str):
    """Shows the CSV upload section with instructions and column validation for a specific category."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc_names = ", ".join(loc_cols)
    
    # Required columns for each category (used for validation)
    required_columns = {
        "Spirits": ["Product", "Type", "Bottle Cost", "Size (oz.)"] + loc_cols + ["Target Margin", "Use", "Distributor", "Order Notes"],
        "Wine": ["Product", "Type", "Cost", "Size (oz.)", "Margin"] + loc_cols + ["Distributor", "Order Notes"],
        "Beer": ["Product", "Type", "Cost per Keg/Case", "Size", "UoM"] + loc_cols + ["Target Margin", "Distributor", "Order Notes"],
        "Ingredients": ["Product", "Cost", "Size/Yield", "UoM"] + loc_cols + ["Distributor", "Order Notes"],
        "N/A Beverages": ["Product", "Cost", "Size/Yield", "UoM"] + loc_cols + ["Distributor", "Order Notes"],
    }
    
    # CSV Upload Instructions
    instructions = {
        "Spirits": f"""
**Required columns:** Product, Type, Bottle Cost, Size (oz.), {loc_names}, Target Margin, Use, Distributor, Order Notes

**Calculated columns (auto-generated):** Cost/Oz, Shot, Single, Neat Pour, Double, Total Inventory, Value
""",
        "Wine": f"""
**Required columns:** Product, Type, Cost, Size (oz.), Margin, {loc_names}, Distributor, Order Notes

**Calculated columns (auto-generated):** Total Inventory, Bottle Price, Value, BTG, Suggested Retail
""",
        "Beer": f"""
**Required columns:** Product, Type, Cost per Keg/Case, Size, UoM, {loc_names}, Target Margin, Distributor, Order Notes

**Calculated columns (auto-generated):** Cost/Unit, Menu Price, Total Inventory, Value
""",
        "Ingredients": f"""
**Required columns:** Product, Cost, Size/Yield, UoM, {loc_names}, Distributor, Order Notes

**Calculated columns (auto-generated):** Total Inventory, Cost/Unit
""",
        "N/A Beverages": f"""
**Required columns:** Product, Cost, Size/Yield, UoM, {loc_names}, Distributor, Order Notes

**Calculated columns (auto-generated):** Total Inventory, Cost/Unit
""",
    }
    
    st.info(instructions[upload_category])
    
    uploaded_file = st.file_uploader(f"Upload {upload_category} CSV", type=['csv'], key=f"upload_{upload_category.lower()}")
    
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            
            # Strip whitespace from column names
            new_data.columns = [col.strip() for col in new_data.columns]
            
            # Create case-insensitive column mapping for normalization
            # This allows "product" to match "Product", etc.
            required = required_columns[upload_category]
            uploaded_columns = new_data.columns.tolist()
            
            # Build a mapping of lowercase -> expected case
            column_mapping = {}
            for req_col in required:
                for up_col in uploaded_columns:
                    if up_col.lower() == req_col.lower() and up_col != req_col:
                        column_mapping[up_col] = req_col
            
            # Rename columns to match expected case
            if column_mapping:
                new_data = new_data.rename(columns=column_mapping)
                uploaded_columns = new_data.columns.tolist()
                st.info(f"ℹ️ Normalized column names: {', '.join([f'{k} → {v}' for k, v in column_mapping.items()])}")
            
            # Validate required columns
            missing_columns = [col for col in required if col not in uploaded_columns]
            
            if missing_columns:
                st.error(f"❌ **Missing required columns:** {', '.join(missing_columns)}")
                st.warning("Please update your CSV file to include all required columns and try again.")
                st.markdown("**Your file contains these columns:**")
                st.code(", ".join(uploaded_columns))
            else:
                st.success("✅ All required columns found!")
                st.dataframe(new_data.head(), use_container_width=True)
                
                if st.button("✅ Import Data", key=f"confirm_upload_{upload_category.lower().replace('/', '_')}"):
                    processors = {
                        "Spirits": (process_uploaded_spirits, 'spirits_inventory'),
                        "Wine": (process_uploaded_wine, 'wine_inventory'),
                        "Beer": (process_uploaded_beer, 'beer_inventory'),
                        "Ingredients": (process_uploaded_ingredients, 'ingredients_inventory'),
                        "N/A Beverages": (process_uploaded_na_beverages, 'na_beverages_inventory'),
                    }
                    func, key = processors[upload_category]
                    st.session_state[key] = func(new_data)
                    st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
                    save_all_inventory_data()
                    st.success(f"✅ {upload_category} inventory uploaded!")
                    st.rerun()
        except Exception as e:
            st.error(f"❌ **Error reading CSV file:** {e}")
            st.warning("Please check that your file is a valid CSV format and try again.")


# =============================================================================
# SPLIT DISPLAY FOR SPIRITS - Using CLIENT_CONFIG locations
# =============================================================================

def show_spirits_inventory_split(df: pd.DataFrame, filter_columns: list):
    """Renders spirits inventory with split display approach."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()  # May be None
    
    if df is None or len(df) == 0:
        st.info("No spirits inventory data.")
        return
    
    st.markdown("#### Search & Filter Spirits")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key="search_spirits", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_spirits_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    # Check if any filters are active
    is_filtered = bool(search_term) or bool(column_filters)
    
    # Store original products list before filtering
    original_products = df['Product'].tolist() if 'Product' in df.columns else []
    
    # Apply any pending edits from previous interactions BEFORE filtering
    pending_key = 'spirits_pending_edits'
    if pending_key in st.session_state and st.session_state[pending_key]:
        for product, edits in st.session_state[pending_key].items():
            mask = df['Product'] == product
            if mask.any():
                for col, val in edits.items():
                    if col in df.columns:
                        df.loc[mask, col] = val
        # Also update the session state inventory
        st.session_state.spirits_inventory = df.copy()
        # Clear pending edits after applying
        st.session_state[pending_key] = {}
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show filter status
    if is_filtered:
        st.caption(f"🔍 Showing {len(filtered_df)} of {len(df)} products (filtered)")
    else:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # Add location columns if they don't exist
    for col in loc_cols:
        if col not in filtered_df.columns:
            filtered_df[col] = 0.0
        if col not in st.session_state.spirits_inventory.columns:
            st.session_state.spirits_inventory[col] = 0.0
    
    # Define editable vs calculated columns - dynamically include locations
    editable_cols = ["Product", "Type", "Bottle Cost", "Size (oz.)"] + loc_cols + ["Target Margin", "Use", "Distributor", "Order Notes"]
    calculated_cols = ["Cost/Oz", "Shot", "Single", "Neat Pour", "Double", "Total Inventory", "Value"]
    
    # Filter to only columns that exist and warn about missing ones
    missing_cols = [c for c in editable_cols if c not in filtered_df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns in data: {', '.join(missing_cols)}. These fields will not be displayed.")
        st.caption(f"Available columns: {', '.join(filtered_df.columns.tolist())}")
    
    editable_cols = [c for c in editable_cols if c in filtered_df.columns]
    
    if not editable_cols:
        st.error("❌ No editable columns found in the data. Please check your CSV file format.")
        return
    
    st.markdown("#### ✏️ Inputs")
    if is_filtered:
        st.caption("Edit values below. Edits are preserved when filters change. Clear filters to save to Google Sheets.")
    else:
        st.caption("Edit values below. Calculated fields will update automatically in the preview.")
    
    # Store products in filtered view for tracking
    filtered_products = filtered_df['Product'].tolist() if 'Product' in filtered_df.columns else []
    
    # Build column config for location columns
    loc_column_config = {}
    for loc in loc_cols:
        loc_column_config[loc] = st.column_config.NumberColumn(f"📍 {loc}", format="%.1f", min_value=0.0, step=0.5, help=f"Inventory at {loc}")
    
    # Show only editable columns in the data editor
    # Disable adding/deleting rows when filtered to avoid complexity
    edited_df = st.data_editor(
        filtered_df[editable_cols].copy().reset_index(drop=True),
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        key="editor_spirits_split",
        column_config={
            "Bottle Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Size (oz.)": st.column_config.NumberColumn(format="%.1f"),
            "Target Margin": st.column_config.NumberColumn(format="%.0f%%"),
            **loc_column_config
        }
    )
    
    # Immediately merge edits back to full inventory (so edits persist when filters change)
    if is_filtered:
        merge_edits_to_inventory(edited_df, 'spirits_inventory', filtered_products)
    
    # Calculate computed columns from edited data
    calc_df = edited_df.copy()
    
    # Convert numeric columns to proper numeric types (handles strings from Google Sheets)
    numeric_cols = ["Bottle Cost", "Size (oz.)", "Target Margin"] + loc_cols
    for col in numeric_cols:
        if col in calc_df.columns:
            # Remove currency symbols and convert to numeric
            calc_df[col] = pd.to_numeric(
                calc_df[col].astype(str).str.replace(r'[$,%]', '', regex=True).str.strip(),
                errors='coerce'
            ).fillna(0)
    
    # Total Inventory = sum of all locations
    calc_df["Total Inventory"] = sum(calc_df[loc].fillna(0) for loc in loc_cols if loc in calc_df.columns)
    
    # Cost/Oz calculation
    if "Bottle Cost" in calc_df.columns and "Size (oz.)" in calc_df.columns:
        calc_df["Cost/Oz"] = calc_df.apply(
            lambda r: round(r['Bottle Cost'] / r['Size (oz.)'], 2) if r['Size (oz.)'] > 0 else 0, axis=1)
    
    # Pour price calculations based on Cost/Oz and Target Margin
    if "Bottle Cost" in calc_df.columns and "Size (oz.)" in calc_df.columns and "Target Margin" in calc_df.columns:
        # Shot = (1 * Cost/Oz) / Target Margin
        calc_df["Shot"] = calc_df.apply(
            lambda r: math.ceil((1 * (r['Bottle Cost'] / r['Size (oz.)'])) / (r['Target Margin'] / 100)) if r['Target Margin'] > 0 and r['Size (oz.)'] > 0 else 0, axis=1)
        
        # Single = (1.5 * Cost/Oz) / Target Margin
        calc_df["Single"] = calc_df.apply(
            lambda r: math.ceil((1.5 * (r['Bottle Cost'] / r['Size (oz.)'])) / (r['Target Margin'] / 100)) if r['Target Margin'] > 0 and r['Size (oz.)'] > 0 else 0, axis=1)
        
        # Neat Pour = (2 * Cost/Oz) / Target Margin
        calc_df["Neat Pour"] = calc_df.apply(
            lambda r: math.ceil((2 * (r['Bottle Cost'] / r['Size (oz.)'])) / (r['Target Margin'] / 100)) if r['Target Margin'] > 0 and r['Size (oz.)'] > 0 else 0, axis=1)
        
        # Double = (3 * Cost/Oz) / Target Margin
        calc_df["Double"] = calc_df.apply(
            lambda r: math.ceil((3 * (r['Bottle Cost'] / r['Size (oz.)'])) / (r['Target Margin'] / 100)) if r['Target Margin'] > 0 and r['Size (oz.)'] > 0 else 0, axis=1)
    
    if "Bottle Cost" in calc_df.columns and "Total Inventory" in calc_df.columns:
        calc_df["Value"] = round(calc_df["Bottle Cost"] * calc_df["Total Inventory"], 2)
    
    # Display calculated columns in read-only table
    st.markdown("#### 📊 Calculated Fields (Live Preview)")
    st.caption("These values update automatically based on your edits above.")
    
    # Build display columns, only include Product if it exists
    display_calc_cols = []
    if "Product" in calc_df.columns:
        display_calc_cols.append("Product")
    display_calc_cols.extend([c for c in calculated_cols if c in calc_df.columns])
    
    st.dataframe(
        calc_df[display_calc_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost/Oz": st.column_config.NumberColumn(format="$%.2f"),
            "Shot": st.column_config.NumberColumn(format="$%.0f"),
            "Single": st.column_config.NumberColumn(format="$%.0f"),
            "Neat Pour": st.column_config.NumberColumn(format="$%.0f"),
            "Double": st.column_config.NumberColumn(format="$%.0f"),
            "Total Inventory": st.column_config.NumberColumn(format="%.1f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    # Show totals
    if "Value" in calc_df.columns:
        total_value = calc_df["Value"].sum()
        st.metric("💰 Total Inventory Value", format_currency(total_value))
    
    # Save button - disabled when filtered
    if is_filtered:
        st.warning("⚠️ Clear all filters before saving to Google Sheets. Your edits are preserved.")
        st.button("💾 Save Changes", key="save_spirits_split", type="primary", disabled=True)
    else:
        if st.button("💾 Save Changes", key="save_spirits_split", type="primary"):
            # Save the edited data directly (overwrites Google Sheet)
            st.session_state.spirits_inventory = calc_df.copy()
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            save_all_inventory_data()
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# SPLIT DISPLAY FOR WINE - Using CLIENT_CONFIG locations
# =============================================================================

def show_wine_inventory_split(df: pd.DataFrame, filter_columns: list):
    """Renders wine inventory with split display approach."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()  # May be None
    
    if df is None or len(df) == 0:
        st.info("No wine inventory data.")
        return
    
    st.markdown("#### Search & Filter Wine")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key="search_wine", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_wine_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    # Check if any filters are active
    is_filtered = bool(search_term) or bool(column_filters)
    
    # Apply any pending edits from previous interactions BEFORE filtering
    pending_key = 'wine_pending_edits'
    if pending_key in st.session_state and st.session_state[pending_key]:
        for product, edits in st.session_state[pending_key].items():
            mask = df['Product'] == product
            if mask.any():
                for col, val in edits.items():
                    if col in df.columns:
                        df.loc[mask, col] = val
        st.session_state.wine_inventory = df.copy()
        st.session_state[pending_key] = {}
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show filter status
    if is_filtered:
        st.caption(f"🔍 Showing {len(filtered_df)} of {len(df)} products (filtered)")
    else:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # Add location columns if they don't exist
    for col in loc_cols:
        if col not in filtered_df.columns:
            filtered_df[col] = 0.0
        if col not in st.session_state.wine_inventory.columns:
            st.session_state.wine_inventory[col] = 0.0
    
    editable_cols = ["Product", "Type", "Cost", "Size (oz.)", "Margin"] + loc_cols + ["Distributor", "Order Notes"]
    calculated_cols = ["Total Inventory", "Bottle Price", "Value", "BTG", "Suggested Retail"]
    
    # Filter to only columns that exist and warn about missing ones
    missing_cols = [c for c in editable_cols if c not in filtered_df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns in data: {', '.join(missing_cols)}. These fields will not be displayed.")
        st.caption(f"Available columns: {', '.join(filtered_df.columns.tolist())}")
    
    editable_cols = [c for c in editable_cols if c in filtered_df.columns]
    
    if not editable_cols:
        st.error("❌ No editable columns found in the data. Please check your CSV file format.")
        return
    
    st.markdown("#### ✏️ Inputs")
    if is_filtered:
        st.caption("Edit values below. Edits are preserved when filters change. Clear filters to save to Google Sheets.")
    else:
        st.caption("Edit values below. Calculated fields will update automatically in the preview.")
    
    # Store products in filtered view for tracking
    filtered_products = filtered_df['Product'].tolist() if 'Product' in filtered_df.columns else []
    
    # Build column config for location columns
    loc_column_config = {}
    for loc in loc_cols:
        loc_column_config[loc] = st.column_config.NumberColumn(f"📍 {loc}", format="%.1f", min_value=0.0, step=0.5, help=f"Inventory at {loc}")
    
    edited_df = st.data_editor(
        filtered_df[editable_cols].copy().reset_index(drop=True),
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        key="editor_wine_split",
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Size (oz.)": st.column_config.NumberColumn(format="%.1f"),
            "Margin": st.column_config.NumberColumn(format="%.0f%%"),
            **loc_column_config
        }
    )
    
    # Immediately merge edits back to full inventory (so edits persist when filters change)
    if is_filtered:
        merge_edits_to_inventory(edited_df, 'wine_inventory', filtered_products)
    
    # Calculate computed columns
    calc_df = edited_df.copy()
    
    # Convert numeric columns to proper numeric types (handles strings from Google Sheets)
    numeric_cols = ["Cost", "Size (oz.)", "Margin"] + loc_cols
    for col in numeric_cols:
        if col in calc_df.columns:
            # Remove currency symbols and convert to numeric
            calc_df[col] = pd.to_numeric(
                calc_df[col].astype(str).str.replace(r'[$,%]', '', regex=True).str.strip(),
                errors='coerce'
            ).fillna(0)
    
    calc_df["Total Inventory"] = sum(calc_df[loc].fillna(0) for loc in loc_cols if loc in calc_df.columns)
    
    if "Cost" in calc_df.columns and "Margin" in calc_df.columns:
        calc_df["Bottle Price"] = calc_df.apply(
            lambda r: math.ceil(r['Cost'] / (r['Margin'] / 100)) if r['Margin'] > 0 else 0, axis=1)
    
    if "Cost" in calc_df.columns and "Total Inventory" in calc_df.columns:
        calc_df["Value"] = round(calc_df["Cost"] * calc_df["Total Inventory"], 2)
    
    if "Cost" in calc_df.columns:
        calc_df["BTG"] = calc_df["Cost"].apply(lambda x: math.ceil(x / 4) if pd.notna(x) and x > 0 else 0)
        calc_df["Suggested Retail"] = calc_df["Cost"].apply(lambda x: math.ceil(x * 1.44) if pd.notna(x) and x > 0 else 0)
    
    # Display calculated columns
    st.markdown("#### 📊 Calculated Fields (Live Preview)")
    st.caption("These values update automatically based on your edits above.")
    
    # Build display columns, only include Product if it exists
    display_calc_cols = []
    if "Product" in calc_df.columns:
        display_calc_cols.append("Product")
    display_calc_cols.extend([c for c in calculated_cols if c in calc_df.columns])
    
    st.dataframe(
        calc_df[display_calc_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Total Inventory": st.column_config.NumberColumn(format="%.1f"),
            "Bottle Price": st.column_config.NumberColumn(format="$%.0f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
            "BTG": st.column_config.NumberColumn(format="$%.0f"),
            "Suggested Retail": st.column_config.NumberColumn(format="$%.0f"),
        }
    )
    
    if "Value" in calc_df.columns:
        total_value = calc_df["Value"].sum()
        st.metric("💰 Total Inventory Value", format_currency(total_value))
    
    # Save button - disabled when filtered
    if is_filtered:
        st.warning("⚠️ Clear all filters before saving to Google Sheets. Your edits are preserved.")
        st.button("💾 Save Changes", key="save_wine_split", type="primary", disabled=True)
    else:
        if st.button("💾 Save Changes", key="save_wine_split", type="primary"):
            # Save the edited data directly (overwrites Google Sheet)
            st.session_state.wine_inventory = calc_df.copy()
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            save_all_inventory_data()
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# SPLIT DISPLAY FOR BEER - Using CLIENT_CONFIG locations
# =============================================================================

def show_beer_inventory_split(df: pd.DataFrame, filter_columns: list):
    """Renders beer inventory with split display approach."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()  # May be None
    
    if df is None or len(df) == 0:
        st.info("No beer inventory data.")
        return
    
    st.markdown("#### Search & Filter Beer")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key="search_beer", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_beer_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    # Check if any filters are active
    is_filtered = bool(search_term) or bool(column_filters)
    
    # Apply any pending edits from previous interactions BEFORE filtering
    pending_key = 'beer_pending_edits'
    if pending_key in st.session_state and st.session_state[pending_key]:
        for product, edits in st.session_state[pending_key].items():
            mask = df['Product'] == product
            if mask.any():
                for col, val in edits.items():
                    if col in df.columns:
                        df.loc[mask, col] = val
        st.session_state.beer_inventory = df.copy()
        st.session_state[pending_key] = {}
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show filter status
    if is_filtered:
        st.caption(f"🔍 Showing {len(filtered_df)} of {len(df)} products (filtered)")
    else:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # Add location columns if they don't exist
    for col in loc_cols:
        if col not in filtered_df.columns:
            filtered_df[col] = 0.0
        if col not in st.session_state.beer_inventory.columns:
            st.session_state.beer_inventory[col] = 0.0
    
    editable_cols = ["Product", "Type", "Cost per Keg/Case", "Size", "UoM"] + loc_cols + ["Target Margin", "Distributor", "Order Notes"]
    calculated_cols = ["Cost/Unit", "Menu Price", "Total Inventory", "Value"]
    
    # Filter to only columns that exist and warn about missing ones
    missing_cols = [c for c in editable_cols if c not in filtered_df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns in data: {', '.join(missing_cols)}. These fields will not be displayed.")
        st.caption(f"Available columns: {', '.join(filtered_df.columns.tolist())}")
    
    editable_cols = [c for c in editable_cols if c in filtered_df.columns]
    
    if not editable_cols:
        st.error("❌ No editable columns found in the data. Please check your CSV file format.")
        return
    
    st.markdown("#### ✏️ Inputs")
    if is_filtered:
        st.caption("Edit values below. Edits are preserved when filters change. Clear filters to save to Google Sheets.")
    else:
        st.caption("Edit values below. Calculated fields will update automatically in the preview.")
    
    # Store products in filtered view for tracking
    filtered_products = filtered_df['Product'].tolist() if 'Product' in filtered_df.columns else []
    
    # Build column config for location columns
    loc_column_config = {}
    for loc in loc_cols:
        loc_column_config[loc] = st.column_config.NumberColumn(f"📍 {loc}", format="%.1f", min_value=0.0, step=0.5, help=f"Inventory at {loc}")
    
    edited_df = st.data_editor(
        filtered_df[editable_cols].copy().reset_index(drop=True),
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        key="editor_beer_split",
        column_config={
            "Cost per Keg/Case": st.column_config.NumberColumn(format="$%.2f"),
            "Size": st.column_config.NumberColumn(format="%.1f"),
            "Target Margin": st.column_config.NumberColumn(format="%.0f%%"),
            **loc_column_config
        }
    )
    
    # Immediately merge edits back to full inventory (so edits persist when filters change)
    if is_filtered:
        merge_edits_to_inventory(edited_df, 'beer_inventory', filtered_products)
    
    # Calculate computed columns
    calc_df = edited_df.copy()
    
    # Convert numeric columns to proper numeric types (handles strings from Google Sheets)
    numeric_cols = ["Cost per Keg/Case", "Size", "Target Margin"] + loc_cols
    for col in numeric_cols:
        if col in calc_df.columns:
            # Remove currency symbols and convert to numeric
            calc_df[col] = pd.to_numeric(
                calc_df[col].astype(str).str.replace(r'[$,%]', '', regex=True).str.strip(),
                errors='coerce'
            ).fillna(0)
    
    calc_df["Total Inventory"] = sum(calc_df[loc].fillna(0) for loc in loc_cols if loc in calc_df.columns)
    
    if "Cost per Keg/Case" in calc_df.columns and "Size" in calc_df.columns:
        calc_df["Cost/Unit"] = calc_df.apply(
            lambda r: round(r['Cost per Keg/Case'] / r['Size'], 2) if r['Size'] > 0 else 0, axis=1)
    
    # Menu Price calculation
    if "Cost/Unit" in calc_df.columns and "Target Margin" in calc_df.columns and "Type" in calc_df.columns:
        def calc_menu_price(row):
            cost_unit = row["Cost/Unit"]
            margin = row["Target Margin"]
            if margin <= 0:
                return 0
            if row["Type"] in ["Half Barrel", "Quarter Barrel", "Sixtel"]:
                # For kegs: (16 * Cost/Unit) / Target Margin
                return round((cost_unit * 16) / (margin / 100))
            elif row["Type"] == "Case":
                # For cases: Cost/Unit / Target Margin
                return round(cost_unit / (margin / 100))
            return 0
        calc_df["Menu Price"] = calc_df.apply(calc_menu_price, axis=1)
    
    if "Cost per Keg/Case" in calc_df.columns and "Total Inventory" in calc_df.columns:
        calc_df["Value"] = round(calc_df["Cost per Keg/Case"] * calc_df["Total Inventory"], 2)
    
    # Display calculated columns
    st.markdown("#### 📊 Calculated Fields (Live Preview)")
    st.caption("These values update automatically based on your edits above.")
    
    # Build display columns, only include Product if it exists
    display_calc_cols = []
    if "Product" in calc_df.columns:
        display_calc_cols.append("Product")
    display_calc_cols.extend([c for c in calculated_cols if c in calc_df.columns])
    
    st.dataframe(
        calc_df[display_calc_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost/Unit": st.column_config.NumberColumn(format="$%.2f"),
            "Menu Price": st.column_config.NumberColumn(format="$%.0f"),
            "Total Inventory": st.column_config.NumberColumn(format="%.1f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    if "Value" in calc_df.columns:
        total_value = calc_df["Value"].sum()
        st.metric("💰 Total Inventory Value", format_currency(total_value))
    
    # Save button - disabled when filtered
    if is_filtered:
        st.warning("⚠️ Clear all filters before saving to Google Sheets. Your edits are preserved.")
        st.button("💾 Save Changes", key="save_beer_split", type="primary", disabled=True)
    else:
        if st.button("💾 Save Changes", key="save_beer_split", type="primary"):
            # Save the edited data directly (overwrites Google Sheet)
            st.session_state.beer_inventory = calc_df.copy()
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            save_all_inventory_data()
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# SPLIT DISPLAY FOR INGREDIENTS - Using CLIENT_CONFIG locations
# =============================================================================

def show_ingredients_inventory_split(df: pd.DataFrame, filter_columns: list):
    """Renders ingredients inventory with split display approach."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()  # May be None
    
    if df is None or len(df) == 0:
        st.info("No ingredients inventory data.")
        return
    
    st.markdown("#### Search & Filter Ingredients")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key="search_ingredients", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_ingredients_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    # Check if any filters are active
    is_filtered = bool(search_term) or bool(column_filters)
    
    # Apply any pending edits from previous interactions BEFORE filtering
    pending_key = 'ingredients_pending_edits'
    if pending_key in st.session_state and st.session_state[pending_key]:
        for product, edits in st.session_state[pending_key].items():
            mask = df['Product'] == product
            if mask.any():
                for col, val in edits.items():
                    if col in df.columns:
                        df.loc[mask, col] = val
        st.session_state.ingredients_inventory = df.copy()
        st.session_state[pending_key] = {}
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show filter status
    if is_filtered:
        st.caption(f"🔍 Showing {len(filtered_df)} of {len(df)} products (filtered)")
    else:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # Add location columns if they don't exist
    for col in loc_cols:
        if col not in filtered_df.columns:
            filtered_df[col] = 0.0
        if col not in st.session_state.ingredients_inventory.columns:
            st.session_state.ingredients_inventory[col] = 0.0
    
    editable_cols = ["Product", "Cost", "Size/Yield", "UoM"] + loc_cols + ["Distributor", "Order Notes"]
    calculated_cols = ["Cost/Unit", "Total Inventory", "Value"]
    
    # Filter to only columns that exist and warn about missing ones
    missing_cols = [c for c in editable_cols if c not in filtered_df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns in data: {', '.join(missing_cols)}. These fields will not be displayed.")
        st.caption(f"Available columns: {', '.join(filtered_df.columns.tolist())}")
    
    editable_cols = [c for c in editable_cols if c in filtered_df.columns]
    
    if not editable_cols:
        st.error("❌ No editable columns found in the data. Please check your CSV file format.")
        return
    
    st.markdown("#### ✏️ Inputs")
    if is_filtered:
        st.caption("Edit values below. Edits are preserved when filters change. Clear filters to save to Google Sheets.")
    else:
        st.caption("Edit values below. Calculated fields will update automatically in the preview.")
    
    # Store products in filtered view for tracking
    filtered_products = filtered_df['Product'].tolist() if 'Product' in filtered_df.columns else []
    
    # Build column config for location columns
    loc_column_config = {}
    for loc in loc_cols:
        loc_column_config[loc] = st.column_config.NumberColumn(f"📍 {loc}", format="%.1f", min_value=0.0, step=0.5, help=f"Inventory at {loc}")
    
    edited_df = st.data_editor(
        filtered_df[editable_cols].copy().reset_index(drop=True),
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        key="editor_ingredients_split",
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Size/Yield": st.column_config.NumberColumn(format="%.1f"),
            **loc_column_config
        }
    )
    
    # Immediately merge edits back to full inventory (so edits persist when filters change)
    if is_filtered:
        merge_edits_to_inventory(edited_df, 'ingredients_inventory', filtered_products)
    
    # Calculate computed columns
    calc_df = edited_df.copy()
    
    # Convert numeric columns to proper numeric types (handles strings from Google Sheets)
    numeric_cols = ["Cost", "Size/Yield"] + loc_cols
    for col in numeric_cols:
        if col in calc_df.columns:
            # Remove currency symbols and convert to numeric
            calc_df[col] = pd.to_numeric(
                calc_df[col].astype(str).str.replace(r'[$,%]', '', regex=True).str.strip(),
                errors='coerce'
            ).fillna(0)
    
    calc_df["Total Inventory"] = sum(calc_df[loc].fillna(0) for loc in loc_cols if loc in calc_df.columns)
    
    if "Cost" in calc_df.columns and "Size/Yield" in calc_df.columns:
        calc_df["Cost/Unit"] = calc_df.apply(
            lambda r: round(r['Cost'] / r['Size/Yield'], 4) if r['Size/Yield'] > 0 else 0, axis=1)
    
    # Calculate Value = Cost * Total Inventory
    if "Cost" in calc_df.columns:
        calc_df["Value"] = round(calc_df["Cost"] * calc_df["Total Inventory"], 2)
    
    # Display calculated columns
    st.markdown("#### 📊 Calculated Fields (Live Preview)")
    st.caption("These values update automatically based on your edits above.")
    
    # Build display columns, only include Product if it exists
    display_calc_cols = []
    if "Product" in calc_df.columns:
        display_calc_cols.append("Product")
    display_calc_cols.extend([c for c in calculated_cols if c in calc_df.columns])
    
    st.dataframe(
        calc_df[display_calc_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost/Unit": st.column_config.NumberColumn(format="$%.4f"),
            "Total Inventory": st.column_config.NumberColumn(format="%.1f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    if "Value" in calc_df.columns:
        total_value = calc_df["Value"].sum()
        st.metric("💰 Total Inventory Value", format_currency(total_value))
    
    # Save button - disabled when filtered
    if is_filtered:
        st.warning("⚠️ Clear all filters before saving to Google Sheets. Your edits are preserved.")
        st.button("💾 Save Changes", key="save_ingredients_split", type="primary", disabled=True)
    else:
        if st.button("💾 Save Changes", key="save_ingredients_split", type="primary"):
            # Save the edited data directly (overwrites Google Sheet)
            st.session_state.ingredients_inventory = calc_df.copy()
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            save_all_inventory_data()
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# SPLIT DISPLAY FOR N/A BEVERAGES - Using CLIENT_CONFIG locations
# =============================================================================

def show_na_beverages_inventory_split(df: pd.DataFrame, filter_columns: list):
    """Renders N/A beverages inventory with split display approach."""
    loc_cols = get_location_columns()
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()  # May be None
    
    if df is None or len(df) == 0:
        st.info("No N/A beverages inventory data.")
        return
    
    st.markdown("#### Search & Filter N/A Beverages")
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    with filter_cols[0]:
        search_term = st.text_input("🔍 Search", key="search_na_beverages", placeholder="Type to search...")
    
    column_filters = {}
    for i, col_name in enumerate(filter_columns):
        with filter_cols[i + 1]:
            if col_name in df.columns:
                unique_values = df[col_name].dropna().unique().tolist()
                selected = st.multiselect(f"Filter by {col_name}", options=unique_values, key=f"filter_na_beverages_{col_name}")
                if selected:
                    column_filters[col_name] = selected
    
    # Check if any filters are active
    is_filtered = bool(search_term) or bool(column_filters)
    
    # Apply any pending edits from previous interactions BEFORE filtering
    pending_key = 'na_beverages_pending_edits'
    if pending_key in st.session_state and st.session_state[pending_key]:
        for product, edits in st.session_state[pending_key].items():
            mask = df['Product'] == product
            if mask.any():
                for col, val in edits.items():
                    if col in df.columns:
                        df.loc[mask, col] = val
        st.session_state.na_beverages_inventory = df.copy()
        st.session_state[pending_key] = {}
    
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show filter status
    if is_filtered:
        st.caption(f"🔍 Showing {len(filtered_df)} of {len(df)} products (filtered)")
    else:
        st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # Add location columns if they don't exist
    for col in loc_cols:
        if col not in filtered_df.columns:
            filtered_df[col] = 0.0
        if col not in st.session_state.na_beverages_inventory.columns:
            st.session_state.na_beverages_inventory[col] = 0.0
    
    editable_cols = ["Product", "Cost", "Size/Yield", "UoM"] + loc_cols + ["Distributor", "Order Notes"]
    calculated_cols = ["Cost/Unit", "Total Inventory", "Value"]
    
    # Filter to only columns that exist and warn about missing ones
    missing_cols = [c for c in editable_cols if c not in filtered_df.columns]
    if missing_cols:
        st.warning(f"⚠️ Missing columns in data: {', '.join(missing_cols)}. These fields will not be displayed.")
        st.caption(f"Available columns: {', '.join(filtered_df.columns.tolist())}")
    
    editable_cols = [c for c in editable_cols if c in filtered_df.columns]
    
    if not editable_cols:
        st.error("❌ No editable columns found in the data. Please check your CSV file format.")
        return
    
    st.markdown("#### ✏️ Inputs")
    if is_filtered:
        st.caption("Edit values below. Edits are preserved when filters change. Clear filters to save to Google Sheets.")
    else:
        st.caption("Edit values below. Calculated fields will update automatically in the preview.")
    
    # Store products in filtered view for tracking
    filtered_products = filtered_df['Product'].tolist() if 'Product' in filtered_df.columns else []
    
    # Build column config for location columns
    loc_column_config = {}
    for loc in loc_cols:
        loc_column_config[loc] = st.column_config.NumberColumn(f"📍 {loc}", format="%.1f", min_value=0.0, step=0.5, help=f"Inventory at {loc}")
    
    edited_df = st.data_editor(
        filtered_df[editable_cols].copy().reset_index(drop=True),
        use_container_width=True,
        num_rows="fixed" if is_filtered else "dynamic",
        key="editor_na_beverages_split",
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Size/Yield": st.column_config.NumberColumn(format="%.1f"),
            **loc_column_config
        }
    )
    
    # Immediately merge edits back to full inventory (so edits persist when filters change)
    if is_filtered:
        merge_edits_to_inventory(edited_df, 'na_beverages_inventory', filtered_products)
    
    # Calculate computed columns
    calc_df = edited_df.copy()
    
    # Convert numeric columns to proper numeric types (handles strings from Google Sheets)
    numeric_cols = ["Cost", "Size/Yield"] + loc_cols
    for col in numeric_cols:
        if col in calc_df.columns:
            # Remove currency symbols and convert to numeric
            calc_df[col] = pd.to_numeric(
                calc_df[col].astype(str).str.replace(r'[$,%]', '', regex=True).str.strip(),
                errors='coerce'
            ).fillna(0)
    
    calc_df["Total Inventory"] = sum(calc_df[loc].fillna(0) for loc in loc_cols if loc in calc_df.columns)
    
    if "Cost" in calc_df.columns and "Size/Yield" in calc_df.columns:
        calc_df["Cost/Unit"] = calc_df.apply(
            lambda r: round(r['Cost'] / r['Size/Yield'], 4) if r['Size/Yield'] > 0 else 0, axis=1)
    
    # Calculate Value = Cost * Total Inventory
    if "Cost" in calc_df.columns:
        calc_df["Value"] = round(calc_df["Cost"] * calc_df["Total Inventory"], 2)
    
    # Display calculated columns
    st.markdown("#### 📊 Calculated Fields (Live Preview)")
    st.caption("These values update automatically based on your edits above.")
    
    # Build display columns, only include Product if it exists
    display_calc_cols = []
    if "Product" in calc_df.columns:
        display_calc_cols.append("Product")
    display_calc_cols.extend([c for c in calculated_cols if c in calc_df.columns])
    
    st.dataframe(
        calc_df[display_calc_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cost/Unit": st.column_config.NumberColumn(format="$%.4f"),
            "Total Inventory": st.column_config.NumberColumn(format="%.1f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    if "Value" in calc_df.columns:
        total_value = calc_df["Value"].sum()
        st.metric("💰 Total Inventory Value", format_currency(total_value))
    
    # Save button - disabled when filtered
    if is_filtered:
        st.warning("⚠️ Clear all filters before saving to Google Sheets. Your edits are preserved.")
        st.button("💾 Save Changes", key="save_na_beverages_split", type="primary", disabled=True)
    else:
        if st.button("💾 Save Changes", key="save_na_beverages_split", type="primary"):
            # Save the edited data directly (overwrites Google Sheet)
            st.session_state.na_beverages_inventory = calc_df.copy()
            st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
            save_all_inventory_data()
            st.success("✅ Changes saved!")
            st.rerun()


# =============================================================================
# PLACEHOLDER PAGES (to be completed in next iteration)
# =============================================================================

def show_ordering():
    """
    Renders the Weekly Order Builder module.
    V3.8: Step 1 uses configurable location names from CLIENT_CONFIG.
    Steps 2 and 3 use Total Current Inventory only.
    """
    show_sidebar_navigation()
    
    # Get configured location names for Step 1
    loc1 = get_location_1()
    loc2 = get_location_2()
    loc3 = get_location_3()
    
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
    
    # Check for pending verification
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
        # ADD/REMOVE PRODUCTS FROM WEEKLY INVENTORY
        # =====================================================================
        
        with st.expander("➕ Add Products to your Weekly Order Inventory", expanded=False):
            st.markdown("**Add a product from Master Inventory:**")
            
            # Get products not already in weekly inventory
            available_products = get_products_not_in_weekly_inventory()
            
            if len(available_products) > 0:
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
                                
                                # V3.8: Create new row with configurable location column names
                                new_row = pd.DataFrame([{
                                    'Product': selected_row['Product'],
                                    'Category': selected_row['Category'],
                                    'Par': new_par,
                                    loc1: 0,
                                    loc2: 0,
                                    loc3: 0,
                                    'Total Current Inventory': 0,
                                    'Unit': new_unit,
                                    'Unit Cost': selected_row['Cost'],
                                    'Distributor': selected_row['Distributor'],
                                    'Order Notes': ''
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
            # CSV UPLOAD FOR WEEKLY INVENTORY
            # =================================================================
            st.markdown("---")
            st.markdown("**📤 Upload CSV to populate Weekly Inventory:**")
            
            with st.expander("ℹ️ CSV Format Requirements", expanded=False):
                st.markdown(f"""
                Your CSV file should include the following columns:
                
                | Column | Required | Description |
                |--------|----------|-------------|
                | Product | ✅ Yes | Product name |
                | Category | ✅ Yes | Spirits, Wine, Beer, or Ingredients |
                | Par | ✅ Yes | Par level (number) |
                | {loc1} | Optional | Inventory at {loc1} (default: 0) |
                | {loc2} | Optional | Inventory at {loc2} (default: 0) |
                | {loc3} | Optional | Inventory in {loc3} (default: 0) |
                | Unit | Optional | Bottle, Case, Sixtel, Keg, Each, Quart, Gallon (default: Bottle) |
                | Unit Cost | Optional | Cost per unit (default: 0) |
                | Distributor | Optional | Distributor name (default: blank) |
                | Order Notes | Optional | Notes for ordering (default: blank) |
                
                **Note:** Products already in Weekly Inventory will be skipped.
                """)
                
                # Download template button with configurable location names
                template_df = pd.DataFrame({
                    'Product': ['Example Product 1', 'Example Product 2'],
                    'Category': ['Spirits', 'Beer'],
                    'Par': [3, 2],
                    loc1: [1, 0.5],
                    loc2: [1, 0.5],
                    loc3: [0, 0],
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
                                    
                                    # V3.8: Add default values for configurable location columns
                                    if loc1 not in import_df.columns:
                                        import_df[loc1] = 0
                                    if loc2 not in import_df.columns:
                                        import_df[loc2] = 0
                                    if loc3 not in import_df.columns:
                                        import_df[loc3] = 0
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
                                    
                                    # Calculate Total Current Inventory from configurable locations
                                    import_df['Total Current Inventory'] = import_df[loc1] + import_df[loc2] + import_df[loc3]
                                    
                                    # Ensure numeric columns are proper types
                                    import_df['Par'] = pd.to_numeric(import_df['Par'], errors='coerce').fillna(0)
                                    import_df[loc1] = pd.to_numeric(import_df[loc1], errors='coerce').fillna(0)
                                    import_df[loc2] = pd.to_numeric(import_df[loc2], errors='coerce').fillna(0)
                                    import_df[loc3] = pd.to_numeric(import_df[loc3], errors='coerce').fillna(0)
                                    import_df['Unit Cost'] = pd.to_numeric(import_df['Unit Cost'], errors='coerce').fillna(0)
                                    
                                    # Select and order columns to match existing structure
                                    cols_to_keep = ['Product', 'Category', 'Par', loc1, loc2, loc3,
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
        # CATEGORY AND DISTRIBUTOR FILTERS FOR WEEKLY INVENTORY
        # V3.8: Uses configurable location columns
        # =====================================================================
        
        weekly_inv = st.session_state.weekly_inventory.copy()
        
        # V3.8: Ensure configurable location columns exist (backwards compatibility)
        # First check for old column names and migrate if needed
        if 'Bar Inventory' in weekly_inv.columns and loc1 not in weekly_inv.columns:
            weekly_inv[loc1] = weekly_inv['Bar Inventory']
        if 'Storage Inventory' in weekly_inv.columns and loc2 not in weekly_inv.columns:
            weekly_inv[loc2] = weekly_inv['Storage Inventory']
        
        # Add location columns if they don't exist
        if loc1 not in weekly_inv.columns:
            if 'Current Inventory' in weekly_inv.columns:
                weekly_inv[loc1] = weekly_inv['Current Inventory'] / 2
            else:
                weekly_inv[loc1] = 0
        if loc2 not in weekly_inv.columns:
            weekly_inv[loc2] = 0
        if loc3 not in weekly_inv.columns:
            weekly_inv[loc3] = 0
        
        # Calculate Total Current Inventory from configurable locations
        weekly_inv['Total Current Inventory'] = weekly_inv[loc1] + weekly_inv[loc2] + weekly_inv[loc3]
        
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
        # V3.8: DISPLAY TABLE WITH CONFIGURABLE LOCATION COLUMNS
        # =====================================================================
        
        display_df = filtered_weekly_inv.copy()
        display_df.insert(0, 'Select', False)  # Add checkbox column at the beginning
        
        # V3.8: Use configurable location names in display columns
        display_cols = ['Select', 'Product', 'Category', 'Par', loc1, loc2, loc3,
                       'Total Current Inventory', 'Status', 'Unit', 'Unit Cost', 'Distributor', 'Order Notes']
        
        # Only include columns that exist
        display_cols = [c for c in display_cols if c in display_df.columns]
        
        edited_weekly = st.data_editor(
            display_df[display_cols],
            use_container_width=True,
            hide_index=True,
            key="weekly_inv_editor",
            column_config={
                "Select": st.column_config.CheckboxColumn("🗑️", help="Select rows to delete", width="small"),
                "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                # V3.8: Configurable location column labels
                loc1: st.column_config.NumberColumn(f"📍 {loc1}", min_value=0, step=0.5),
                loc2: st.column_config.NumberColumn(f"📍 {loc2}", min_value=0, step=0.5),
                loc3: st.column_config.NumberColumn(f"📍 {loc3}", min_value=0, step=0.5),
                "Total Current Inventory": st.column_config.NumberColumn("Total", disabled=True),
                "Par": st.column_config.NumberColumn(min_value=0, step=1),
                "Status": st.column_config.TextColumn(disabled=True),
                "Order Notes": st.column_config.TextColumn("Order Deals", disabled=True),
            },
            disabled=["Product", "Category", "Status", "Total Current Inventory", "Unit", "Unit Cost", "Distributor", "Order Notes"]
        )
        
        # Recalculate Total Current Inventory in real-time from edited values
        edited_weekly['Total Current Inventory'] = edited_weekly[loc1] + edited_weekly[loc2] + edited_weekly[loc3]
        edited_weekly['Status'] = edited_weekly.apply(
            lambda row: "🔴 Order" if row['Total Current Inventory'] < row['Par'] else "✅ OK", axis=1
        )
        
        # Check for selected rows to delete
        selected_for_deletion = edited_weekly[edited_weekly['Select'] == True]['Product'].tolist()
        
        # Action buttons - Save, Generate Order, and Delete
        col_save, col_update, col_delete, col_spacer = st.columns([1, 1, 1, 3])
        
        with col_save:
            if st.button("💾 Update Table", key="save_weekly_only", help="Save inventory changes without generating an order"):
                # Update values only for products that were displayed (filtered view)
                for idx, row in edited_weekly.iterrows():
                    mask = st.session_state.weekly_inventory['Product'] == row['Product']
                    st.session_state.weekly_inventory.loc[mask, loc1] = row[loc1]
                    st.session_state.weekly_inventory.loc[mask, loc2] = row[loc2]
                    st.session_state.weekly_inventory.loc[mask, loc3] = row[loc3]
                    st.session_state.weekly_inventory.loc[mask, 'Total Current Inventory'] = row[loc1] + row[loc2] + row[loc3]
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
                    st.session_state.weekly_inventory.loc[mask, loc1] = row[loc1]
                    st.session_state.weekly_inventory.loc[mask, loc2] = row[loc2]
                    st.session_state.weekly_inventory.loc[mask, loc3] = row[loc3]
                    st.session_state.weekly_inventory.loc[mask, 'Total Current Inventory'] = row[loc1] + row[loc2] + row[loc3]
                    st.session_state.weekly_inventory.loc[mask, 'Par'] = row['Par']
                
                # Generate order based on updated inventory
                st.session_state.current_order = generate_order_from_inventory(st.session_state.weekly_inventory)
                save_all_inventory_data()
                st.rerun()
        
        with col_delete:
            if st.button("🗑️ Delete Selected", key="delete_selected_weekly", disabled=len(selected_for_deletion) == 0):
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
        
        # =====================================================================
        # STEP 2: ORDER REVIEW (Uses Total Current Inventory only - no location columns)
        # =====================================================================
        
        if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
            order_df = st.session_state.current_order.copy()
            
            # Migration - rename old column names if present
            if 'Order Qty' in order_df.columns and 'Order Quantity' not in order_df.columns:
                order_df = order_df.rename(columns={'Order Qty': 'Order Quantity'})
                st.session_state.current_order = order_df
            
            st.markdown(f"**{len(order_df)} items need ordering:**")
            
            edited_order = st.data_editor(
                order_df,
                use_container_width=True,
                hide_index=True,
                key="order_editor",
                column_config={
                    "Current Stock": st.column_config.NumberColumn(format="%.1f", disabled=True),
                    "Par Level": st.column_config.NumberColumn(format="%.1f", disabled=True),
                    "Order Quantity": st.column_config.NumberColumn(min_value=0, step=0.5),
                    "Unit Cost": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                    "Order Value": st.column_config.NumberColumn(format="$%.2f", disabled=True),
                },
                disabled=["Product", "Category", "Current Stock", "Par Level", 
                         "Unit Cost", "Distributor"]
            )
            
            # Action buttons row with Recalculate and Copy options
            col_recalc, col_copy_order, col_spacer = st.columns([1, 1, 3])
            
            with col_recalc:
                if st.button("💰 Recalculate Total", key="recalc_order"):
                    edited_order['Order Value'] = edited_order['Order Quantity'] * edited_order['Unit Cost']
                    st.session_state.current_order = edited_order
                    st.rerun()
            
            with col_copy_order:
                # Group by distributor for organized copying
                copy_text = "ORDER LIST\n" + "=" * 40 + "\n\n"
                for dist in edited_order['Distributor'].unique():
                    dist_items = edited_order[edited_order['Distributor'] == dist]
                    copy_text += f"📦 {dist}\n" + "-" * 30 + "\n"
                    for _, row in dist_items.iterrows():
                        copy_text += f"  • {row['Product']}: {row['Order Quantity']}\n"
                    copy_text += "\n"
                
                st.download_button(
                    label="📋 Copy Order",
                    data=copy_text,
                    file_name=f"order_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key="download_order_text"
                )
            
            st.markdown("---")
            # Send to Verification
            if st.button("📋 Send to Verification", key="send_to_verification", type="primary"):
                # Create pending order with original values for comparison
                pending_df = edited_order.copy()
                pending_df['Original Unit Cost'] = pending_df['Unit Cost']
                pending_df['Original Order Quantity'] = pending_df['Order Quantity']
                pending_df['Verification Notes'] = ''
                pending_df['Verification Notes'] = pending_df['Verification Notes'].astype(str)
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
        # STEP 3: ORDER VERIFICATION (Uses totals only - no location columns)
        # =====================================================================
        
        st.markdown("---")
        st.markdown("### Step 3: Order Verification")
        st.markdown("Verify received products against the order. Update quantities and costs as needed, then finalize.")
        
        if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
            pending_df = st.session_state.pending_order.copy()
            
            # Migration - rename old column names if present
            if 'Order Qty' in pending_df.columns and 'Order Quantity' not in pending_df.columns:
                pending_df = pending_df.rename(columns={'Order Qty': 'Order Quantity'})
            if 'Original Order Qty' in pending_df.columns and 'Original Order Quantity' not in pending_df.columns:
                pending_df = pending_df.rename(columns={'Original Order Qty': 'Original Order Quantity'})
            
            # Add Unit column if missing from old session data
            if 'Unit' not in pending_df.columns:
                pending_df['Unit'] = ''
            
            # Update session state with migrated data
            st.session_state.pending_order = pending_df.copy()
            
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
            
            # Ensure Verification Notes is string type
            pending_df['Verification Notes'] = pending_df['Verification Notes'].fillna('').astype(str)
            
            # Add Invoice # column if not present
            if 'Invoice #' not in pending_df.columns:
                pending_df['Invoice #'] = ''
            pending_df['Invoice #'] = pending_df['Invoice #'].fillna('').astype(str)
            
            # Add Invoice Date column if not present
            if 'Invoice Date' not in pending_df.columns:
                pending_df['Invoice Date'] = pd.NaT
            else:
                pending_df['Invoice Date'] = pd.to_datetime(pending_df['Invoice Date'], errors='coerce')
            
            order_date = pending_df['Order Date'].iloc[0] if 'Order Date' in pending_df.columns else 'Unknown'
            st.markdown(f"**📅 Order Date:** {order_date}")
            st.markdown(f"**📦 {len(pending_df)} items pending verification:**")
            
            # Calculate Modified flag based on changes
            pending_df['Modified'] = (
                (pending_df['Unit Cost'] != pending_df['Original Unit Cost']) | 
                (pending_df['Order Quantity'] != pending_df['Original Order Quantity'])
            )
            
            # Red flag for modified rows with change details
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
            
            # Updated display columns with Invoice Date
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
                st.metric("Total Value", format_currency(display_pending['Order Value'].sum()))
            
            # Finalize section
            st.markdown("---")
            col_finalize, col_cancel = st.columns([2, 1])
            
            with col_finalize:
                verifier_initials = st.text_input("Verified by (initials):", key="verifier_initials", max_chars=5)
                finalize_disabled = len(verifier_initials.strip()) < 2
                
                if st.button("✅ Finalize Order", key="finalize_order", type="primary", disabled=finalize_disabled):
                    # Save to order history
                    order_date = st.session_state.pending_order['Order Date'].iloc[0]
                    new_orders = []
                    for _, row in st.session_state.pending_order.iterrows():
                        if row['Order Quantity'] > 0:
                            # Format Invoice Date for storage
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
                        
                        # Clear pending order from both Google Sheets and session state
                        clear_pending_order()
                        st.session_state.pending_order = pd.DataFrame()
                        
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
                    # Clear pending order from both Google Sheets and session state
                    clear_pending_order()
                    st.session_state.pending_order = pd.DataFrame()
                    st.warning("Verification cancelled. Order has been discarded.")
                    st.rerun()
            
            if finalize_disabled:
                st.caption("⚠️ Enter your initials above to enable the Finalize button.")
        
        else:
            st.info("📋 No orders pending verification. Complete Steps 1 and 2 to create an order.")
    
    # =====================================================================
    # ORDER HISTORY TAB
    # =====================================================================
    
    with tab_history:
        st.markdown("### 📜 Previous Orders")
        
        # Show pending verification notice
        if 'pending_order' in st.session_state and len(st.session_state.pending_order) > 0:
            pending_date = st.session_state.pending_order['Order Date'].iloc[0] if 'Order Date' in st.session_state.pending_order.columns else 'Unknown'
            pending_value = st.session_state.pending_order['Order Value'].sum() if 'Order Value' in st.session_state.pending_order.columns else 0
            st.warning(f"⏳ **Pending Verification:** Order from {pending_date} ({format_currency(pending_value)}) - Complete Step 3 to finalize.")
        
        if len(order_history) > 0:
            # Ensure columns exist for display
            display_history = order_history.copy()
            if 'Status' not in display_history.columns:
                display_history['Status'] = 'Verified'
            if 'Verified By' not in display_history.columns:
                display_history['Verified By'] = ''
            if 'Unit' not in display_history.columns:
                display_history['Unit'] = ''
            if 'Invoice #' not in display_history.columns:
                display_history['Invoice #'] = ''
            if 'Invoice Date' not in display_history.columns:
                display_history['Invoice Date'] = ''
            
            # Add Month column for filtering
            display_history['Week'] = pd.to_datetime(display_history['Week'])
            display_history['Month'] = display_history['Week'].dt.to_period('M').astype(str)
            display_history['Week'] = display_history['Week'].dt.strftime('%Y-%m-%d')
            
            # Filter row
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            
            with col_f1:
                months = sorted(display_history['Month'].unique(), reverse=True)
                selected_months = st.multiselect("Filter by Month:", options=months,
                    default=months[:2] if len(months) >= 2 else months, key="history_month_filter")
            
            with col_f2:
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
            detail_cols = ['Week', 'Product', 'Category', 'Quantity Ordered', 'Unit', 'Unit Cost', 
                          'Total Cost', 'Distributor', 'Invoice #', 'Invoice Date', 'Status', 'Verified By']
            detail_cols = [c for c in detail_cols if c in filtered_history.columns]
            
            st.dataframe(filtered_history[detail_cols].sort_values(['Week', 'Product'], ascending=[False, True]),
                        use_container_width=True, hide_index=True,
                        column_config={
                            "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                            "Total Cost": st.column_config.NumberColumn(format="$%.2f")
                        })
        else:
            st.info("No order history yet. Complete all 3 steps to save an order.")
    
    # =====================================================================
    # ORDER ANALYTICS TAB
    # =====================================================================
    
    with tab_analytics:
        st.markdown("### 📈 Order Analytics")
        if len(order_history) > 0:
            # Category colors
            category_colors = {
                'Spirits': '#8B5CF6',
                'Wine': '#EC4899',
                'Beer': '#F59E0B',
                'Ingredients': '#10B981'
            }
            
            # Date range filter
            st.markdown("#### 📅 Date Range Filter")
            
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
            
            # Filter data by date range
            filtered_analytics = analytics_data[
                (analytics_data['Week'].dt.date >= start_date) & 
                (analytics_data['Week'].dt.date <= end_date)
            ].copy()
            
            # Calculate comparison period
            date_range_days = (end_date - start_date).days
            prior_start = start_date - timedelta(days=date_range_days + 1)
            prior_end = start_date - timedelta(days=1)
            
            prior_period_data = analytics_data[
                (analytics_data['Week'].dt.date >= prior_start) & 
                (analytics_data['Week'].dt.date <= prior_end)
            ]
            
            st.caption(f"Showing data from {start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')} ({len(filtered_analytics)} orders)")
            
            st.markdown("---")
            
            # Key metrics
            st.markdown("#### 📊 Key Metrics")
            
            total_spend = filtered_analytics['Total Cost'].sum()
            num_orders = len(filtered_analytics['Week'].unique())
            avg_weekly_spend = total_spend / max(num_orders, 1)
            total_items_ordered = len(filtered_analytics)
            
            prior_total_spend = prior_period_data['Total Cost'].sum() if len(prior_period_data) > 0 else 0
            prior_num_orders = len(prior_period_data['Week'].unique()) if len(prior_period_data) > 0 else 0
            prior_avg_weekly = prior_total_spend / max(prior_num_orders, 1) if prior_num_orders > 0 else 0
            
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
    """Cocktail Builds Book with view, add, and edit recipe functionality."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🍹 Cocktail Builds Book")
    
    recipes = st.session_state.get('cocktail_recipes', [])
    available_products = get_all_available_products()
    
    # Check if we're in edit mode
    editing_recipe_name = st.session_state.get('editing_cocktail', None)
    editing_recipe = None
    if editing_recipe_name:
        editing_recipe = next((r for r in recipes if r['name'] == editing_recipe_name), None)
        if not editing_recipe:
            # Recipe not found, clear edit mode
            del st.session_state['editing_cocktail']
            editing_recipe_name = None
    
    # Show edit form if editing
    if editing_recipe:
        st.markdown(f"### ✏️ Editing: {editing_recipe['name']}")
        
        # Cancel button
        if st.button("← Cancel Edit", key="cancel_cocktail_edit"):
            del st.session_state['editing_cocktail']
            # Clear edit form state
            for key in list(st.session_state.keys()):
                if key.startswith("edit_cocktail_"):
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # Initialize edit form state if not exists
        edit_prefix = "edit_cocktail_"
        if f"{edit_prefix}initialized" not in st.session_state:
            st.session_state[f"{edit_prefix}ingredient_count"] = len(editing_recipe.get('ingredients', []))
            if st.session_state[f"{edit_prefix}ingredient_count"] == 0:
                st.session_state[f"{edit_prefix}ingredient_count"] = 1
            # Pre-populate ingredients
            for i, ing in enumerate(editing_recipe.get('ingredients', [])):
                st.session_state[f"{edit_prefix}ing_prod_{i}"] = ing.get('product', '')
                st.session_state[f"{edit_prefix}ing_amt_{i}"] = ing.get('amount', 0.0)
                st.session_state[f"{edit_prefix}ing_unit_{i}"] = ing.get('unit', 'oz')
            st.session_state[f"{edit_prefix}initialized"] = True
        
        col1, col2 = st.columns(2)
        
        glass_options = ["Rocks", "Coupe", "Highball", "Collins", "Nick & Nora", "Martini", "Wine", "Flute", "Mug", "Copper Mug", "Tiki", "Other"]
        current_glass = editing_recipe.get('glass', 'Rocks')
        glass_index = glass_options.index(current_glass) if current_glass in glass_options else 0
        
        with col1:
            recipe_name = st.text_input("Recipe Name *", value=editing_recipe.get('name', ''), key=f"{edit_prefix}name")
            glass_type = st.selectbox("Glass Type", glass_options, index=glass_index, key=f"{edit_prefix}glass")
        
        with col2:
            sale_price = st.number_input("Menu Sale Price ($) *", min_value=0.0, step=0.50, value=float(editing_recipe.get('sale_price', 14.0)), key=f"{edit_prefix}price")
        
        st.markdown("#### Ingredients")
        
        # Column headers
        col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
        with col_prod:
            st.caption("Product")
        with col_amt:
            st.caption("Amount")
        with col_unit:
            st.caption("Unit")
        with col_remove:
            st.caption("")
        
        unit_options = ["oz", "dashes", "barspoon", "drops", "rinse", "each", "ml"]
        
        # Dynamic ingredient rows
        ingredients_to_remove = []
        for i in range(st.session_state[f"{edit_prefix}ingredient_count"]):
            col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
            
            # Get current values or defaults
            current_prod = st.session_state.get(f"{edit_prefix}ing_prod_{i}", "")
            current_amt = st.session_state.get(f"{edit_prefix}ing_amt_{i}", 0.0)
            current_unit = st.session_state.get(f"{edit_prefix}ing_unit_{i}", "oz")
            
            prod_options = [""] + available_products
            prod_index = prod_options.index(current_prod) if current_prod in prod_options else 0
            unit_index = unit_options.index(current_unit) if current_unit in unit_options else 0
            
            with col_prod:
                st.selectbox(f"Product {i+1}", options=prod_options, index=prod_index, key=f"{edit_prefix}ing_prod_{i}", label_visibility="collapsed")
            with col_amt:
                st.number_input(f"Amount {i+1}", min_value=0.0, step=0.25, value=float(current_amt), key=f"{edit_prefix}ing_amt_{i}", label_visibility="collapsed")
            with col_unit:
                st.selectbox(f"Unit {i+1}", options=unit_options, index=unit_index, key=f"{edit_prefix}ing_unit_{i}", label_visibility="collapsed")
            with col_remove:
                if st.session_state[f"{edit_prefix}ingredient_count"] > 1:
                    if st.button("🗑️", key=f"{edit_prefix}remove_ing_{i}", help="Remove ingredient"):
                        ingredients_to_remove.append(i)
        
        # Handle ingredient removal
        if ingredients_to_remove:
            for remove_idx in sorted(ingredients_to_remove, reverse=True):
                for j in range(remove_idx, st.session_state[f"{edit_prefix}ingredient_count"] - 1):
                    if f"{edit_prefix}ing_prod_{j+1}" in st.session_state:
                        st.session_state[f"{edit_prefix}ing_prod_{j}"] = st.session_state[f"{edit_prefix}ing_prod_{j+1}"]
                        st.session_state[f"{edit_prefix}ing_amt_{j}"] = st.session_state[f"{edit_prefix}ing_amt_{j+1}"]
                        st.session_state[f"{edit_prefix}ing_unit_{j}"] = st.session_state[f"{edit_prefix}ing_unit_{j+1}"]
                st.session_state[f"{edit_prefix}ingredient_count"] -= 1
            st.rerun()
        
        # Add ingredient button
        if st.button("➕ Add Ingredient", key=f"{edit_prefix}add_ingredient"):
            st.session_state[f"{edit_prefix}ingredient_count"] += 1
            st.rerun()
        
        st.markdown("#### Instructions")
        instructions = st.text_area("Build/Preparation Instructions", value=editing_recipe.get('instructions', ''), height=100, key=f"{edit_prefix}instructions")
        
        st.markdown("---")
        
        # Save button
        if st.button("💾 Save Changes", type="primary", use_container_width=True, key=f"{edit_prefix}save_btn"):
            # Collect ingredient data
            ingredients_data = []
            for i in range(st.session_state[f"{edit_prefix}ingredient_count"]):
                product = st.session_state.get(f"{edit_prefix}ing_prod_{i}", "")
                amount = st.session_state.get(f"{edit_prefix}ing_amt_{i}", 0.0)
                unit = st.session_state.get(f"{edit_prefix}ing_unit_{i}", "oz")
                if product and amount > 0:
                    ingredients_data.append({"product": product, "amount": amount, "unit": unit})
            
            if not recipe_name:
                st.error("❌ Recipe name is required.")
            elif not ingredients_data:
                st.error("❌ At least one ingredient with amount > 0 is required.")
            elif sale_price <= 0:
                st.error("❌ Sale price must be greater than $0.")
            else:
                # Check for duplicate name (excluding current recipe)
                other_names = [r['name'].lower() for r in recipes if r['name'] != editing_recipe_name]
                if recipe_name.lower() in other_names:
                    st.error(f"❌ A recipe named '{recipe_name}' already exists.")
                else:
                    # Update the recipe
                    for r in st.session_state.cocktail_recipes:
                        if r['name'] == editing_recipe_name:
                            r['name'] = recipe_name
                            r['glass'] = glass_type
                            r['sale_price'] = sale_price
                            r['ingredients'] = ingredients_data
                            r['instructions'] = instructions
                            break
                    
                    save_recipes('cocktail')
                    
                    # Clear edit mode
                    del st.session_state['editing_cocktail']
                    for key in list(st.session_state.keys()):
                        if key.startswith(edit_prefix):
                            del st.session_state[key]
                    
                    st.success(f"✅ '{recipe_name}' updated successfully!")
                    st.rerun()
    
    else:
        # Normal view/add mode
        tab_view, tab_add = st.tabs(["📖 View Recipes", "➕ Add New Recipe"])
        
        with tab_view:
            if recipes:
                display_recipe_list(recipes, 'cocktail', session_key='cocktail_recipes')
            else:
                st.info("No cocktail recipes found. Add one in the 'Add New Recipe' tab to get started!")
        
        with tab_add:
            st.markdown("### Create New Cocktail Recipe")
            
            if not available_products:
                st.warning("⚠️ No products found in Master Inventory. Add spirits and ingredients to the Master Inventory first to build recipes.")
            
            # Initialize session state for dynamic ingredients if not exists
            if 'cocktail_ingredient_count' not in st.session_state:
                st.session_state.cocktail_ingredient_count = 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                recipe_name = st.text_input("Recipe Name *", placeholder="e.g., Old Fashioned", key="cocktail_recipe_name")
                glass_type = st.selectbox("Glass Type", ["Rocks", "Coupe", "Highball", "Collins", "Nick & Nora", "Martini", "Wine", "Flute", "Mug", "Copper Mug", "Tiki", "Other"], key="cocktail_glass_type")
            
            with col2:
                sale_price = st.number_input("Menu Sale Price ($) *", min_value=0.0, step=0.50, value=14.00, key="cocktail_sale_price")
            
            st.markdown("#### Ingredients")
            
            # Column headers
            col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
            with col_prod:
                st.caption("Product")
            with col_amt:
                st.caption("Amount")
            with col_unit:
                st.caption("Unit")
            with col_remove:
                st.caption("")
            
            # Dynamic ingredient rows
            ingredients_to_remove = []
            for i in range(st.session_state.cocktail_ingredient_count):
                col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
                with col_prod:
                    st.selectbox(
                        f"Product {i+1}",
                        options=[""] + available_products,
                        key=f"cocktail_ing_prod_{i}",
                        label_visibility="collapsed"
                    )
                with col_amt:
                    st.number_input(
                        f"Amount {i+1}",
                        min_value=0.0,
                        step=0.25,
                        value=0.0,
                        key=f"cocktail_ing_amt_{i}",
                        label_visibility="collapsed"
                    )
                with col_unit:
                    st.selectbox(
                        f"Unit {i+1}",
                        options=["oz", "dashes", "barspoon", "drops", "rinse", "each", "ml"],
                        key=f"cocktail_ing_unit_{i}",
                        label_visibility="collapsed"
                    )
                with col_remove:
                    if st.session_state.cocktail_ingredient_count > 1:
                        if st.button("🗑️", key=f"cocktail_remove_ing_{i}", help="Remove ingredient"):
                            ingredients_to_remove.append(i)
            
            # Handle ingredient removal
            if ingredients_to_remove:
                # Shift ingredients up to fill gaps
                for remove_idx in sorted(ingredients_to_remove, reverse=True):
                    for j in range(remove_idx, st.session_state.cocktail_ingredient_count - 1):
                        # Copy values from j+1 to j
                        if f"cocktail_ing_prod_{j+1}" in st.session_state:
                            st.session_state[f"cocktail_ing_prod_{j}"] = st.session_state[f"cocktail_ing_prod_{j+1}"]
                            st.session_state[f"cocktail_ing_amt_{j}"] = st.session_state[f"cocktail_ing_amt_{j+1}"]
                            st.session_state[f"cocktail_ing_unit_{j}"] = st.session_state[f"cocktail_ing_unit_{j+1}"]
                    st.session_state.cocktail_ingredient_count -= 1
                st.rerun()
            
            # Add ingredient button
            if st.button("➕ Add Ingredient", key="cocktail_add_ingredient"):
                st.session_state.cocktail_ingredient_count += 1
                st.rerun()
            
            st.markdown("#### Instructions")
            instructions = st.text_area("Build/Preparation Instructions", placeholder="e.g., Stir with ice, strain into rocks glass with large ice cube. Express orange peel.", height=100, key="cocktail_instructions")
            
            st.markdown("---")
            
            # Save button
            if st.button("💾 Save Recipe", type="primary", use_container_width=True, key="cocktail_save_btn"):
                # Collect ingredient data
                ingredients_data = []
                for i in range(st.session_state.cocktail_ingredient_count):
                    product = st.session_state.get(f"cocktail_ing_prod_{i}", "")
                    amount = st.session_state.get(f"cocktail_ing_amt_{i}", 0.0)
                    unit = st.session_state.get(f"cocktail_ing_unit_{i}", "oz")
                    if product and amount > 0:
                        ingredients_data.append({"product": product, "amount": amount, "unit": unit})
                
                if not recipe_name:
                    st.error("❌ Recipe name is required.")
                elif not ingredients_data:
                    st.error("❌ At least one ingredient with amount > 0 is required.")
                elif sale_price <= 0:
                    st.error("❌ Sale price must be greater than $0.")
                else:
                    # Check for duplicate name
                    existing_names = [r['name'].lower() for r in recipes]
                    if recipe_name.lower() in existing_names:
                        st.error(f"❌ A recipe named '{recipe_name}' already exists.")
                    else:
                        new_recipe = {
                            "name": recipe_name,
                            "glass": glass_type,
                            "sale_price": sale_price,
                            "ingredients": ingredients_data,
                            "instructions": instructions
                        }
                        
                        if 'cocktail_recipes' not in st.session_state:
                            st.session_state.cocktail_recipes = []
                        
                        st.session_state.cocktail_recipes.append(new_recipe)
                        save_recipes('cocktail')
                        
                        # Reset form
                        st.session_state.cocktail_ingredient_count = 1
                        for key in list(st.session_state.keys()):
                            if key.startswith("cocktail_ing_") or key in ["cocktail_recipe_name", "cocktail_instructions"]:
                                del st.session_state[key]
                        
                        st.success(f"✅ '{recipe_name}' added successfully!")
                        st.rerun()


def show_bar_prep():
    """Bar Prep Recipe Book with view, add, and edit recipe functionality."""
    show_sidebar_navigation()
    
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("🧪 Bar Prep Recipe Book")
    
    recipes = st.session_state.get('bar_prep_recipes', [])
    available_products = get_all_available_products()
    
    def handle_delete(recipe_name):
        st.session_state.bar_prep_recipes = [r for r in st.session_state.bar_prep_recipes if r['name'] != recipe_name]
        save_recipes('bar_prep')
        st.success(f"✅ {recipe_name} deleted!")
        st.rerun()
    
    # Check if we're in edit mode
    editing_recipe_name = st.session_state.get('editing_bar_prep', None)
    editing_recipe = None
    if editing_recipe_name:
        editing_recipe = next((r for r in recipes if r['name'] == editing_recipe_name), None)
        if not editing_recipe:
            # Recipe not found, clear edit mode
            del st.session_state['editing_bar_prep']
            editing_recipe_name = None
    
    # Show edit form if editing
    if editing_recipe:
        st.markdown(f"### ✏️ Editing: {editing_recipe['name']}")
        
        # Cancel button
        if st.button("← Cancel Edit", key="cancel_barprep_edit"):
            del st.session_state['editing_bar_prep']
            # Clear edit form state
            for key in list(st.session_state.keys()):
                if key.startswith("edit_barprep_"):
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # Initialize edit form state if not exists
        edit_prefix = "edit_barprep_"
        if f"{edit_prefix}initialized" not in st.session_state:
            st.session_state[f"{edit_prefix}ingredient_count"] = len(editing_recipe.get('ingredients', []))
            if st.session_state[f"{edit_prefix}ingredient_count"] == 0:
                st.session_state[f"{edit_prefix}ingredient_count"] = 1
            # Pre-populate ingredients
            for i, ing in enumerate(editing_recipe.get('ingredients', [])):
                st.session_state[f"{edit_prefix}ing_prod_{i}"] = ing.get('product', '')
                st.session_state[f"{edit_prefix}ing_amt_{i}"] = ing.get('amount', 0.0)
                st.session_state[f"{edit_prefix}ing_unit_{i}"] = ing.get('unit', 'oz')
            st.session_state[f"{edit_prefix}initialized"] = True
        
        col1, col2 = st.columns(2)
        
        category_options = ["Syrups, Infusions & Garnishes", "Batched Cocktails"]
        current_category = editing_recipe.get('category', 'Syrups, Infusions & Garnishes')
        # Handle old "Syrups" category
        if current_category == 'Syrups':
            current_category = 'Syrups, Infusions & Garnishes'
        category_index = category_options.index(current_category) if current_category in category_options else 0
        
        with col1:
            recipe_name = st.text_input("Recipe Name *", value=editing_recipe.get('name', ''), key=f"{edit_prefix}name")
            category = st.selectbox("Category *", category_options, index=category_index, key=f"{edit_prefix}category")
            yield_oz = st.number_input("Yield (oz) *", min_value=1.0, step=1.0, value=float(editing_recipe.get('yield_oz', 32)), key=f"{edit_prefix}yield_oz")
        
        with col2:
            yield_description = st.text_input("Yield Description", value=editing_recipe.get('yield_description', ''), key=f"{edit_prefix}yield_desc")
            shelf_life = st.text_input("Shelf Life", value=editing_recipe.get('shelf_life', ''), key=f"{edit_prefix}shelf_life")
            storage = st.text_input("Storage Instructions", value=editing_recipe.get('storage', ''), key=f"{edit_prefix}storage")
        
        st.markdown("#### Ingredients")
        
        # Column headers
        col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
        with col_prod:
            st.caption("Product")
        with col_amt:
            st.caption("Amount")
        with col_unit:
            st.caption("Unit")
        with col_remove:
            st.caption("")
        
        unit_options = ["oz", "cups", "ml", "each", "lbs", "grams", "dashes", "barspoon"]
        
        # Dynamic ingredient rows
        ingredients_to_remove = []
        for i in range(st.session_state[f"{edit_prefix}ingredient_count"]):
            col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
            
            # Get current values or defaults
            current_prod = st.session_state.get(f"{edit_prefix}ing_prod_{i}", "")
            current_amt = st.session_state.get(f"{edit_prefix}ing_amt_{i}", 0.0)
            current_unit = st.session_state.get(f"{edit_prefix}ing_unit_{i}", "oz")
            
            prod_options = [""] + available_products
            prod_index = prod_options.index(current_prod) if current_prod in prod_options else 0
            unit_index = unit_options.index(current_unit) if current_unit in unit_options else 0
            
            with col_prod:
                st.selectbox(f"Product {i+1}", options=prod_options, index=prod_index, key=f"{edit_prefix}ing_prod_{i}", label_visibility="collapsed")
            with col_amt:
                st.number_input(f"Amount {i+1}", min_value=0.0, step=0.5, value=float(current_amt), key=f"{edit_prefix}ing_amt_{i}", label_visibility="collapsed")
            with col_unit:
                st.selectbox(f"Unit {i+1}", options=unit_options, index=unit_index, key=f"{edit_prefix}ing_unit_{i}", label_visibility="collapsed")
            with col_remove:
                if st.session_state[f"{edit_prefix}ingredient_count"] > 1:
                    if st.button("🗑️", key=f"{edit_prefix}remove_ing_{i}", help="Remove ingredient"):
                        ingredients_to_remove.append(i)
        
        # Handle ingredient removal
        if ingredients_to_remove:
            for remove_idx in sorted(ingredients_to_remove, reverse=True):
                for j in range(remove_idx, st.session_state[f"{edit_prefix}ingredient_count"] - 1):
                    if f"{edit_prefix}ing_prod_{j+1}" in st.session_state:
                        st.session_state[f"{edit_prefix}ing_prod_{j}"] = st.session_state[f"{edit_prefix}ing_prod_{j+1}"]
                        st.session_state[f"{edit_prefix}ing_amt_{j}"] = st.session_state[f"{edit_prefix}ing_amt_{j+1}"]
                        st.session_state[f"{edit_prefix}ing_unit_{j}"] = st.session_state[f"{edit_prefix}ing_unit_{j+1}"]
                st.session_state[f"{edit_prefix}ingredient_count"] -= 1
            st.rerun()
        
        # Add ingredient button
        if st.button("➕ Add Ingredient", key=f"{edit_prefix}add_ingredient"):
            st.session_state[f"{edit_prefix}ingredient_count"] += 1
            st.rerun()
        
        st.markdown("#### Instructions")
        instructions = st.text_area("Preparation Instructions", value=editing_recipe.get('instructions', ''), height=100, key=f"{edit_prefix}instructions")
        
        st.markdown("---")
        
        # Save button
        if st.button("💾 Save Changes", type="primary", use_container_width=True, key=f"{edit_prefix}save_btn"):
            # Collect ingredient data
            ingredients_data = []
            for i in range(st.session_state[f"{edit_prefix}ingredient_count"]):
                product = st.session_state.get(f"{edit_prefix}ing_prod_{i}", "")
                amount = st.session_state.get(f"{edit_prefix}ing_amt_{i}", 0.0)
                unit = st.session_state.get(f"{edit_prefix}ing_unit_{i}", "oz")
                if product and amount > 0:
                    ingredients_data.append({"product": product, "amount": amount, "unit": unit})
            
            if not recipe_name:
                st.error("❌ Recipe name is required.")
            elif not ingredients_data:
                st.error("❌ At least one ingredient with amount > 0 is required.")
            elif yield_oz <= 0:
                st.error("❌ Yield must be greater than 0 oz.")
            else:
                # Check for duplicate name (excluding current recipe)
                other_names = [r['name'].lower() for r in recipes if r['name'] != editing_recipe_name]
                if recipe_name.lower() in other_names:
                    st.error(f"❌ A recipe named '{recipe_name}' already exists.")
                else:
                    # Update the recipe
                    for r in st.session_state.bar_prep_recipes:
                        if r['name'] == editing_recipe_name:
                            r['name'] = recipe_name
                            r['category'] = category
                            r['yield_oz'] = yield_oz
                            r['yield_description'] = yield_description
                            r['shelf_life'] = shelf_life
                            r['storage'] = storage
                            r['ingredients'] = ingredients_data
                            r['instructions'] = instructions
                            break
                    
                    save_recipes('bar_prep')
                    
                    # Clear edit mode
                    del st.session_state['editing_bar_prep']
                    for key in list(st.session_state.keys()):
                        if key.startswith(edit_prefix):
                            del st.session_state[key]
                    
                    st.success(f"✅ '{recipe_name}' updated successfully!")
                    st.rerun()
    
    else:
        # Normal view/add mode
        tab_syrups, tab_batched, tab_add = st.tabs(["🫙 Syrups, Infusions & Garnishes", "🍸 Batched Cocktails", "➕ Add New Recipe"])
        
        with tab_syrups:
            # Support both old "Syrups" and new "Syrups, Infusions & Garnishes" categories for backward compatibility
            syrups = [r for r in recipes if r.get('category') in ['Syrups', 'Syrups, Infusions & Garnishes']]
            if syrups:
                # Sync button for existing recipes
                with st.expander("🔄 Sync Recipes to Ingredients Inventory", expanded=False):
                    st.caption("This will add any syrup/infusion/garnish recipes that aren't already in your Ingredients inventory.")
                    if st.button("Sync All to Ingredients", key="sync_syrups_btn"):
                        added, skipped = sync_syrups_to_ingredients()
                        if added > 0:
                            st.success(f"✅ Added {added} recipe(s) to Ingredients inventory!")
                        if skipped > 0:
                            st.info(f"ℹ️ {skipped} recipe(s) already exist in Ingredients and were skipped.")
                        if added == 0 and skipped == 0:
                            st.info("No recipes to sync.")
                        if added > 0:
                            st.rerun()
                
                # Display recipes from both categories
                for recipe in syrups:
                    display_recipe_card(recipe, 'bar_prep', recipes.index(recipe), on_delete=lambda name: handle_delete(name))
            else:
                st.info("No recipes found. Add one in the 'Add New Recipe' tab to get started!")
        
        with tab_batched:
            batched = [r for r in recipes if r.get('category') == 'Batched Cocktails']
            if batched:
                # Sync button for existing recipes
                with st.expander("🔄 Sync Batched Cocktails to Spirits Inventory", expanded=False):
                    st.caption("This will add any batched cocktail recipes that aren't already in your Spirits inventory.")
                    if st.button("Sync All to Spirits", key="sync_batched_btn"):
                        added, skipped = sync_batched_cocktails_to_spirits()
                        if added > 0:
                            st.success(f"✅ Added {added} batched cocktail(s) to Spirits inventory!")
                        if skipped > 0:
                            st.info(f"ℹ️ {skipped} batched cocktail(s) already exist in Spirits and were skipped.")
                        if added == 0 and skipped == 0:
                            st.info("No batched cocktails to sync.")
                        if added > 0:
                            st.rerun()
                
                display_recipe_list(recipes, 'bar_prep', category_filter='Batched Cocktails', session_key='bar_prep_recipes')
            else:
                st.info("No batched cocktail recipes found. Add one in the 'Add New Recipe' tab to get started!")
        
        with tab_add:
            st.markdown("### Create New Bar Prep Recipe")
            
            if not available_products:
                st.warning("⚠️ No products found in Master Inventory. Add spirits and ingredients to the Master Inventory first to build recipes.")
            
            # Initialize session state for dynamic ingredients if not exists
            if 'barprep_ingredient_count' not in st.session_state:
                st.session_state.barprep_ingredient_count = 1
            
            col1, col2 = st.columns(2)
            
            with col1:
                recipe_name = st.text_input("Recipe Name *", placeholder="e.g., Simple Syrup", key="barprep_recipe_name")
                category = st.selectbox("Category *", ["Syrups, Infusions & Garnishes", "Batched Cocktails"], key="barprep_category")
                yield_oz = st.number_input("Yield (oz) *", min_value=1.0, step=1.0, value=32.0, key="barprep_yield_oz")
            
            with col2:
                yield_description = st.text_input("Yield Description", placeholder="e.g., 1 quart, ~22 cocktails", key="barprep_yield_desc")
                shelf_life = st.text_input("Shelf Life", placeholder="e.g., 2-3 weeks refrigerated", key="barprep_shelf_life")
                storage = st.text_input("Storage Instructions", placeholder="e.g., Refrigerate in sealed container", key="barprep_storage")
            
            st.markdown("#### Ingredients")
            
            # Column headers
            col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
            with col_prod:
                st.caption("Product")
            with col_amt:
                st.caption("Amount")
            with col_unit:
                st.caption("Unit")
            with col_remove:
                st.caption("")
            
            # Dynamic ingredient rows
            ingredients_to_remove = []
            for i in range(st.session_state.barprep_ingredient_count):
                col_prod, col_amt, col_unit, col_remove = st.columns([3, 1, 1, 0.5])
                with col_prod:
                    st.selectbox(
                        f"Product {i+1}",
                        options=[""] + available_products,
                        key=f"barprep_ing_prod_{i}",
                        label_visibility="collapsed"
                    )
                with col_amt:
                    st.number_input(
                        f"Amount {i+1}",
                        min_value=0.0,
                        step=0.5,
                        value=0.0,
                        key=f"barprep_ing_amt_{i}",
                        label_visibility="collapsed"
                    )
                with col_unit:
                    st.selectbox(
                        f"Unit {i+1}",
                        options=["oz", "cups", "ml", "each", "lbs", "grams", "dashes", "barspoon"],
                        key=f"barprep_ing_unit_{i}",
                        label_visibility="collapsed"
                    )
                with col_remove:
                    if st.session_state.barprep_ingredient_count > 1:
                        if st.button("🗑️", key=f"barprep_remove_ing_{i}", help="Remove ingredient"):
                            ingredients_to_remove.append(i)
            
            # Handle ingredient removal
            if ingredients_to_remove:
                # Shift ingredients up to fill gaps
                for remove_idx in sorted(ingredients_to_remove, reverse=True):
                    for j in range(remove_idx, st.session_state.barprep_ingredient_count - 1):
                        # Copy values from j+1 to j
                        if f"barprep_ing_prod_{j+1}" in st.session_state:
                            st.session_state[f"barprep_ing_prod_{j}"] = st.session_state[f"barprep_ing_prod_{j+1}"]
                            st.session_state[f"barprep_ing_amt_{j}"] = st.session_state[f"barprep_ing_amt_{j+1}"]
                            st.session_state[f"barprep_ing_unit_{j}"] = st.session_state[f"barprep_ing_unit_{j+1}"]
                    st.session_state.barprep_ingredient_count -= 1
                st.rerun()
            
            # Add ingredient button
            if st.button("➕ Add Ingredient", key="barprep_add_ingredient"):
                st.session_state.barprep_ingredient_count += 1
                st.rerun()
            
            st.markdown("#### Instructions")
            instructions = st.text_area("Preparation Instructions", placeholder="e.g., Combine equal parts sugar and hot water. Stir until dissolved. Cool before use.", height=100, key="barprep_instructions")
            
            st.markdown("---")
            
            # Save button
            if st.button("💾 Save Recipe", type="primary", use_container_width=True, key="barprep_save_btn"):
                # Collect ingredient data
                ingredients_data = []
                for i in range(st.session_state.barprep_ingredient_count):
                    product = st.session_state.get(f"barprep_ing_prod_{i}", "")
                    amount = st.session_state.get(f"barprep_ing_amt_{i}", 0.0)
                    unit = st.session_state.get(f"barprep_ing_unit_{i}", "oz")
                    if product and amount > 0:
                        ingredients_data.append({"product": product, "amount": amount, "unit": unit})
                
                if not recipe_name:
                    st.error("❌ Recipe name is required.")
                elif not ingredients_data:
                    st.error("❌ At least one ingredient with amount > 0 is required.")
                elif yield_oz <= 0:
                    st.error("❌ Yield must be greater than 0 oz.")
                else:
                    # Check for duplicate name
                    existing_names = [r['name'].lower() for r in recipes]
                    if recipe_name.lower() in existing_names:
                        st.error(f"❌ A recipe named '{recipe_name}' already exists.")
                    else:
                        new_recipe = {
                            "name": recipe_name,
                            "category": category,
                            "yield_oz": yield_oz,
                            "yield_description": yield_description,
                            "shelf_life": shelf_life,
                            "storage": storage,
                            "ingredients": ingredients_data,
                            "instructions": instructions
                        }
                        
                        if 'bar_prep_recipes' not in st.session_state:
                            st.session_state.bar_prep_recipes = []
                        
                        st.session_state.bar_prep_recipes.append(new_recipe)
                        save_recipes('bar_prep')
                        
                        # If this is a Syrup/Infusion/Garnish recipe, add it to Ingredients inventory
                        added_to_ingredients = False
                        added_to_spirits = False
                        if category == "Syrups, Infusions & Garnishes":
                            added_to_ingredients = add_syrup_to_ingredients(new_recipe)
                        # If this is a Batched Cocktail recipe, add it to Spirits inventory
                        elif category == "Batched Cocktails":
                            added_to_spirits = add_batched_cocktail_to_spirits(new_recipe)
                        
                        # Reset form
                        st.session_state.barprep_ingredient_count = 1
                        for key in list(st.session_state.keys()):
                            if key.startswith("barprep_ing_") or key in ["barprep_recipe_name", "barprep_instructions", "barprep_yield_desc", "barprep_shelf_life", "barprep_storage"]:
                                del st.session_state[key]
                        
                        if added_to_ingredients:
                            st.success(f"✅ '{recipe_name}' added successfully and synced to Ingredients inventory!")
                        elif added_to_spirits:
                            st.success(f"✅ '{recipe_name}' added successfully and synced to Spirits inventory!")
                        else:
                            st.success(f"✅ '{recipe_name}' added successfully!")
                        st.rerun()


def show_cogs():
    """Renders the Cost of Goods Sold module."""
    
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
        
        # COGS as Percentage of Sales - Granular by Category
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
            if 'Total COGS %' in cogs_history.columns and cogs_history['Total COGS %'].sum() > 0:
                st.markdown("#### COGS Percentage Trend")
                
                pct_df = cogs_history[cogs_history['Total COGS %'] > 0]
                
                if len(pct_df) > 0:
                    fig_pct = px.line(
                        pct_df,
                        x='Calculation Date',
                        y='Total COGS %',
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
                    "Bar COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Total COGS": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Purchases": st.column_config.NumberColumn(format="$%.2f"),
                    "Wine Sales": st.column_config.NumberColumn(format="$%.2f"),
                    "Beer Sales": st.column_config.NumberColumn(format="$%.2f"),
                    "Bar Sales": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Sales": st.column_config.NumberColumn(format="$%.2f"),
                    "Wine COGS %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Beer COGS %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Bar COGS %": st.column_config.NumberColumn(format="%.1f%%"),
                    "Total COGS %": st.column_config.NumberColumn(format="%.1f%%")
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

def check_password():
    """Returns True if the user has entered the correct password."""
    
    # Check if password is configured in secrets
    try:
        app_password = st.secrets["app_password"]
        if not app_password or app_password == "":
            # Password is empty, allow access
            return True
    except (KeyError, FileNotFoundError):
        # No password configured, allow access
        return True
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state.get("password_input") == app_password:
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # First run or password not yet correct
    if "password_correct" not in st.session_state:
        st.markdown(
            """
            <style>
            .password-container {
                max-width: 400px;
                margin: 100px auto;
                padding: 40px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🍸 Butterbird")
            st.markdown("#### Beverage Management System")
            st.markdown("---")
            st.text_input(
                "Enter Password", 
                type="password", 
                key="password_input",
                on_change=password_entered
            )
            st.button("Login", on_click=password_entered, type="primary", use_container_width=True)
        return False
    
    # Password was entered but incorrect
    elif not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("## 🍸 Butterbird")
            st.markdown("#### Beverage Management System")
            st.markdown("---")
            st.text_input(
                "Enter Password", 
                type="password", 
                key="password_input",
                on_change=password_entered
            )
            st.button("Login", on_click=password_entered, type="primary", use_container_width=True)
            st.error("😕 Incorrect password. Please try again.")
        return False
    
    # Password correct
    return True


def main():
    """Main application entry point."""
    
    # Check password before allowing access
    if not check_password():
        return
    
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
