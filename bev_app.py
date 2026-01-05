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
from datetime import datetime

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
# This must be the first Streamlit command in the script.
# Sets the browser tab title, icon, and default layout.

st.set_page_config(
    page_title="Beverage Management App V1",
    page_icon="🍸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================
# Injects custom CSS for navigation cards and inventory display.

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
    
    /* ----- Metric Card Styling for Dashboard ----- */
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        border-left: 4px solid #11998e;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: bold;
        color: #1f1f1f;
    }
    
    .metric-label {
        font-size: 14px;
        color: #666;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SAMPLE DATA - SPIRITS INVENTORY
# =============================================================================
# Sample data from Canter Inn's spirit inventory.
# Columns: Product, Type, Cost, Size (oz.), Cost/Oz, Margin, Neat Price,
#          Inventory, Value, Use, Distributor, Order Notes, Suggested Retail

def get_sample_spirits():
    """
    Returns a DataFrame with sample spirit inventory data.
    Calculated fields:
        - Cost/Oz = Cost / Size (oz.)
        - Value = Cost × Inventory
    """
    data = [
        {"Product": "Hendrick's", "Type": "Gin", "Cost": 30.80, "Size (oz.)": 33.8, 
         "Margin": 0.20, "Neat Price": 9.0, "Inventory": 1.0, "Use": "Backbar", 
         "Distributor": "Breakthru", "Order Notes": "6 pk deal", "Suggested Retail": 44},
        {"Product": "Tito's", "Type": "Vodka", "Cost": 24.50, "Size (oz.)": 33.8, 
         "Margin": 0.18, "Neat Price": 8.0, "Inventory": 3.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal", "Suggested Retail": 35},
        {"Product": "Ketel One", "Type": "Vodka", "Cost": 32.25, "Size (oz.)": 33.8, 
         "Margin": 0.19, "Neat Price": 10.0, "Inventory": 3.0, "Use": "Backbar", 
         "Distributor": "Breakthru", "Order Notes": "3 bttl deal", "Suggested Retail": 46},
        {"Product": "Tempus Fugit Crème de Cacao", "Type": "Cordial & Digestif", "Cost": 32.50, "Size (oz.)": 23.7, 
         "Margin": 0.22, "Neat Price": 12.0, "Inventory": 6.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "6 pk deal", "Suggested Retail": 47},
        {"Product": "St. George Absinthe", "Type": "Cordial & Digestif", "Cost": 54.00, "Size (oz.)": 25.3, 
         "Margin": 0.23, "Neat Price": 19.0, "Inventory": 1.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 78},
        {"Product": "Espolòn Blanco", "Type": "Tequila", "Cost": 25.00, "Size (oz.)": 33.8, 
         "Margin": 0.20, "Neat Price": 8.0, "Inventory": 4.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 36},
        {"Product": "Lustau Vermut Rojo", "Type": "Vermouth & Aperitif", "Cost": 16.00, "Size (oz.)": 25.3, 
         "Margin": 0.18, "Neat Price": 7.0, "Inventory": 2.0, "Use": "Menu", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 23},
        {"Product": "Buffalo Trace", "Type": "Whiskey", "Cost": 31.00, "Size (oz.)": 33.8, 
         "Margin": 0.20, "Neat Price": 9.0, "Inventory": 2.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 44},
        {"Product": "Rittenhouse Rye", "Type": "Whiskey", "Cost": 28.00, "Size (oz.)": 25.3, 
         "Margin": 0.19, "Neat Price": 9.0, "Inventory": 3.0, "Use": "Rail", 
         "Distributor": "Breakthru", "Order Notes": "", "Suggested Retail": 40},
        {"Product": "Botanist", "Type": "Gin", "Cost": 33.74, "Size (oz.)": 33.8, 
         "Margin": 0.21, "Neat Price": 10.0, "Inventory": 4.0, "Use": "Menu", 
         "Distributor": "General Beverage", "Order Notes": "", "Suggested Retail": 48},
    ]
    
    df = pd.DataFrame(data)
    
    # Calculate derived fields
    df["Cost/Oz"] = df["Cost"] / df["Size (oz.)"]
    df["Value"] = df["Cost"] * df["Inventory"]
    
    # Reorder columns to match expected structure
    column_order = ["Product", "Type", "Cost", "Size (oz.)", "Cost/Oz", "Margin", 
                    "Neat Price", "Inventory", "Value", "Use", "Distributor", 
                    "Order Notes", "Suggested Retail"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - WINE INVENTORY
# =============================================================================
# Sample data from Canter Inn's wine inventory.

def get_sample_wines():
    """
    Returns a DataFrame with sample wine inventory data.
    Calculated fields:
        - Value = Cost × Inventory
    """
    data = [
        {"Product": "Mauzac Nature, 2022, Domaine Plageoles, Gaillac, France", 
         "Type": "Bubbles", "Cost": 22.0, "Size (oz.)": 25.3, "Margin": 0.35, 
         "Bottle Price": 63.0, "Inventory": 18.0, "Distributor": "Chromatic", 
         "BTG": 14.0, "Suggested Retail": 32},
        {"Product": "Savagnin, 2022, Domaine de la Pinte, 'Sav'Or' Vin de France (Jura)", 
         "Type": "Rosé/Orange", "Cost": 29.0, "Size (oz.)": 25.3, "Margin": 0.37, 
         "Bottle Price": 79.0, "Inventory": 5.0, "Distributor": "Chromatic", 
         "BTG": 18.0, "Suggested Retail": 42},
        {"Product": "Sémillon, 2015, Forlorn Hope, 'Nacré', Napa Valley, CA", 
         "Type": "White", "Cost": 17.0, "Size (oz.)": 25.3, "Margin": 0.33, 
         "Bottle Price": 51.0, "Inventory": 2.0, "Distributor": "Chromatic", 
         "BTG": 11.0, "Suggested Retail": 24},
        {"Product": "Blanc de Blancs Extra Brut, 2012, Le Brun Servenay, Champagne, France", 
         "Type": "Bubbles", "Cost": 65.0, "Size (oz.)": 25.3, "Margin": 0.35, 
         "Bottle Price": 186.0, "Inventory": 2.0, "Distributor": "Left Bank", 
         "BTG": 41.0, "Suggested Retail": 94},
        {"Product": "Rosé of Gewürtztraminer/Pinot Noir, 2023, Teutonic, Willamette Valley, OR", 
         "Type": "Rosé/Orange", "Cost": 23.0, "Size (oz.)": 25.3, "Margin": 0.33, 
         "Bottle Price": 69.0, "Inventory": 2.0, "Distributor": "Left Bank", 
         "BTG": 15.0, "Suggested Retail": 33},
        {"Product": "Chardonnay, 2023, Jean Dauvissat, Chablis, France", 
         "Type": "White", "Cost": 31.5, "Size (oz.)": 25.3, "Margin": 0.35, 
         "Bottle Price": 90.0, "Inventory": 6.0, "Distributor": "Vino Veritas", 
         "BTG": 20.0, "Suggested Retail": 45},
        {"Product": "Pinot Noir, 2021, Domaine de la Côte, Sta. Rita Hills, CA", 
         "Type": "Red", "Cost": 55.0, "Size (oz.)": 25.3, "Margin": 0.34, 
         "Bottle Price": 162.0, "Inventory": 3.0, "Distributor": "Vino Veritas", 
         "BTG": 36.0, "Suggested Retail": 79},
        {"Product": "Nebbiolo, 2019, Cantina Massara, Barolo, Piedmont, Italy", 
         "Type": "Red", "Cost": 31.0, "Size (oz.)": 25.3, "Margin": 0.32, 
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
# Sample data from Canter Inn's beer inventory.

def get_sample_beers():
    """
    Returns a DataFrame with sample beer inventory data.
    Calculated fields:
        - Cost/Unit = Cost per Keg/Case / Size
        - Value = Cost per Keg/Case × Inventory
    """
    data = [
        {"Product": "New Glarus Staghorn Oktoberfest", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 0.21, "Menu Price": 5.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Moon Man", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 0.21, "Menu Price": 5.0, "Inventory": 2.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Coors Light", "Type": "Can", 
         "Cost per Keg/Case": 24.51, "Size": 30.0, "UoM": "cans", 
         "Margin": 0.19, "Menu Price": 4.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "New Glarus Fat Squirrel", "Type": "Can", 
         "Cost per Keg/Case": 26.40, "Size": 24.0, "UoM": "cans", 
         "Margin": 0.22, "Menu Price": 5.0, "Inventory": 1.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
        {"Product": "Hop Haus Yard Work IPA", "Type": "Sixtel", 
         "Cost per Keg/Case": 75.00, "Size": 1.0, "UoM": "keg", 
         "Margin": 0.22, "Menu Price": 7.0, "Inventory": 1.0, 
         "Distributor": "GB Beer", "Order Notes": ""},
        {"Product": "High Life", "Type": "Bottles", 
         "Cost per Keg/Case": 21.15, "Size": 24.0, "UoM": "bottles", 
         "Margin": 0.18, "Menu Price": 4.0, "Inventory": 2.0, 
         "Distributor": "Frank Beer", "Order Notes": ""},
    ]
    
    df = pd.DataFrame(data)
    
    # Calculate derived fields
    df["Cost/Unit"] = df["Cost per Keg/Case"] / df["Size"]
    df["Value"] = df["Cost per Keg/Case"] * df["Inventory"]
    
    column_order = ["Product", "Type", "Cost per Keg/Case", "Size", "UoM", 
                    "Cost/Unit", "Margin", "Menu Price", "Inventory", "Value", 
                    "Distributor", "Order Notes"]
    
    return df[column_order]


# =============================================================================
# SAMPLE DATA - INGREDIENT INVENTORY
# =============================================================================
# Sample data from Canter Inn's ingredient inventory.

def get_sample_ingredients():
    """
    Returns a DataFrame with sample ingredient inventory data.
    Calculated fields:
        - Cost/Unit = Cost / Size/Yield
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
    ]
    
    df = pd.DataFrame(data)
    
    # Calculate derived fields
    df["Cost/Unit"] = df["Cost"] / df["Size/Yield"]
    
    column_order = ["Product", "Cost", "Size/Yield", "UoM", "Cost/Unit", 
                    "Distributor", "Order Notes"]
    
    return df[column_order]


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
# Initialize all session state variables for navigation and data storage.

def init_session_state():
    """
    Initializes all session state variables.
    Called at app startup to ensure all required state exists.
    """
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Inventory data storage - each category stored separately
    if 'spirits_inventory' not in st.session_state:
        st.session_state.spirits_inventory = get_sample_spirits()
    
    if 'wine_inventory' not in st.session_state:
        st.session_state.wine_inventory = get_sample_wines()
    
    if 'beer_inventory' not in st.session_state:
        st.session_state.beer_inventory = get_sample_beers()
    
    if 'ingredients_inventory' not in st.session_state:
        st.session_state.ingredients_inventory = get_sample_ingredients()
    
    # Track last inventory date (for dashboard display)
    if 'last_inventory_date' not in st.session_state:
        st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")


# =============================================================================
# NAVIGATION FUNCTION
# =============================================================================

def navigate_to(page: str):
    """
    Sets the current page in session state to navigate between modules.
    
    Args:
        page (str): The page identifier ('home', 'inventory', 'ordering', 'cocktails')
    """
    st.session_state.current_page = page


# =============================================================================
# UTILITY FUNCTIONS FOR INVENTORY
# =============================================================================

def calculate_total_value(df: pd.DataFrame) -> float:
    """
    Calculates the total inventory value from a DataFrame.
    
    Args:
        df: DataFrame with a 'Value' column
        
    Returns:
        float: Sum of the Value column, or 0 if column doesn't exist
    """
    if 'Value' in df.columns:
        return df['Value'].sum()
    return 0.0


def format_currency(value: float) -> str:
    """
    Formats a number as USD currency.
    
    Args:
        value: Number to format
        
    Returns:
        str: Formatted currency string (e.g., "$1,234.56")
    """
    return f"${value:,.2f}"


def filter_dataframe(df: pd.DataFrame, search_term: str, column_filters: dict) -> pd.DataFrame:
    """
    Filters a DataFrame based on search term and column filters.
    
    Args:
        df: DataFrame to filter
        search_term: Text to search for in Product column
        column_filters: Dict of {column_name: selected_values} for filtering
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Apply text search on Product column
    if search_term:
        filtered_df = filtered_df[
            filtered_df['Product'].str.contains(search_term, case=False, na=False)
        ]
    
    # Apply column filters
    for column, values in column_filters.items():
        if values and column in filtered_df.columns:
            filtered_df = filtered_df[filtered_df[column].isin(values)]
    
    return filtered_df


# =============================================================================
# PAGE: HOMESCREEN
# =============================================================================

def show_home():
    """
    Renders the homescreen with navigation cards to each module.
    """
    
    # ----- Header Section -----
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Beverage Management App V1</h1>
        <p>Manage your inventory, orders, and cocktail recipes in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ----- Navigation Cards Grid -----
    col1, col2, col3 = st.columns(3)
    
    # Card 1: Master Inventory
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
    
    # Card 2: Weekly Order Builder
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
    
    # Card 3: Cocktail Builds Book
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
    
    # ----- Footer Info -----
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>Canter Inn • Madison, WI</p>",
        unsafe_allow_html=True
    )


# =============================================================================
# PAGE: MASTER INVENTORY
# =============================================================================

def show_inventory():
    """
    Renders the Master Inventory module with:
    - Dashboard showing total values per category
    - Tabbed interface for each inventory category
    - Search/filter functionality
    - Add/Edit/Remove capabilities
    - CSV upload for data import
    """
    
    # ----- Header with Back Button -----
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📦 Master Inventory")
    
    # =========================================================================
    # DASHBOARD SECTION - Summary Metrics
    # =========================================================================
    
    st.markdown("### 📊 Inventory Dashboard")
    
    # Calculate totals for each category
    spirits_value = calculate_total_value(st.session_state.spirits_inventory)
    wine_value = calculate_total_value(st.session_state.wine_inventory)
    beer_value = calculate_total_value(st.session_state.beer_inventory)
    ingredients_value = calculate_total_value(st.session_state.ingredients_inventory)
    total_value = spirits_value + wine_value + beer_value + ingredients_value
    
    # Display metrics in columns
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="🥃 Spirits",
            value=format_currency(spirits_value)
        )
    
    with col2:
        st.metric(
            label="🍷 Wine",
            value=format_currency(wine_value)
        )
    
    with col3:
        st.metric(
            label="🍺 Beer",
            value=format_currency(beer_value)
        )
    
    with col4:
        st.metric(
            label="🧴 Ingredients",
            value=format_currency(ingredients_value)
        )
    
    with col5:
        st.metric(
            label="💰 Total Value",
            value=format_currency(total_value)
        )
    
    # Last inventory date
    st.caption(f"Last inventory recorded: {st.session_state.last_inventory_date}")
    
    st.markdown("---")
    
    # =========================================================================
    # CSV UPLOAD SECTION
    # =========================================================================
    
    with st.expander("📤 Upload Inventory Data (CSV)", expanded=False):
        st.markdown("""
        Upload a CSV file to replace inventory data for any category.
        The CSV should have matching column headers.
        """)
        
        upload_category = st.selectbox(
            "Select category to upload:",
            ["Spirits", "Wine", "Beer", "Ingredients"],
            key="upload_category"
        )
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            key="csv_uploader"
        )
        
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(new_data.head())
                
                if st.button("✅ Confirm Upload", key="confirm_upload"):
                    # Store uploaded data in appropriate session state
                    if upload_category == "Spirits":
                        st.session_state.spirits_inventory = new_data
                    elif upload_category == "Wine":
                        st.session_state.wine_inventory = new_data
                    elif upload_category == "Beer":
                        st.session_state.beer_inventory = new_data
                    elif upload_category == "Ingredients":
                        st.session_state.ingredients_inventory = new_data
                    
                    st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
                    st.success(f"✅ {upload_category} inventory updated successfully!")
                    st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
    
    st.markdown("---")
    
    # =========================================================================
    # TABBED INVENTORY VIEWS
    # =========================================================================
    
    # Create tabs for each inventory category
    tab_spirits, tab_wine, tab_beer, tab_ingredients = st.tabs([
        "🥃 Spirits", "🍷 Wine", "🍺 Beer", "🧴 Ingredients"
    ])
    
    # -------------------------------------------------------------------------
    # TAB: SPIRITS INVENTORY
    # -------------------------------------------------------------------------
    with tab_spirits:
        show_inventory_tab(
            df=st.session_state.spirits_inventory,
            category="spirits",
            filter_columns=["Type", "Distributor", "Use"],
            display_name="Spirits"
        )
    
    # -------------------------------------------------------------------------
    # TAB: WINE INVENTORY
    # -------------------------------------------------------------------------
    with tab_wine:
        show_inventory_tab(
            df=st.session_state.wine_inventory,
            category="wine",
            filter_columns=["Type", "Distributor"],
            display_name="Wine"
        )
    
    # -------------------------------------------------------------------------
    # TAB: BEER INVENTORY
    # -------------------------------------------------------------------------
    with tab_beer:
        show_inventory_tab(
            df=st.session_state.beer_inventory,
            category="beer",
            filter_columns=["Type", "Distributor"],
            display_name="Beer"
        )
    
    # -------------------------------------------------------------------------
    # TAB: INGREDIENTS INVENTORY
    # -------------------------------------------------------------------------
    with tab_ingredients:
        show_inventory_tab(
            df=st.session_state.ingredients_inventory,
            category="ingredients",
            filter_columns=["Distributor"],
            display_name="Ingredients"
        )


def show_inventory_tab(df: pd.DataFrame, category: str, filter_columns: list, display_name: str):
    """
    Renders an inventory tab with search, filter, and data editing capabilities.
    
    Args:
        df: DataFrame containing the inventory data
        category: String identifier for the category (used in session state keys)
        filter_columns: List of column names to create filter dropdowns for
        display_name: Human-readable name for the category
    """
    
    # -------------------------------------------------------------------------
    # SEARCH AND FILTER CONTROLS
    # -------------------------------------------------------------------------
    
    st.markdown(f"#### Search & Filter {display_name}")
    
    # Create columns for search and filters
    filter_cols = st.columns([2] + [1] * len(filter_columns))
    
    # Search box
    with filter_cols[0]:
        search_term = st.text_input(
            "🔍 Search by Product",
            key=f"search_{category}",
            placeholder="Type to search..."
        )
    
    # Filter dropdowns
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
    
    # Apply filters
    filtered_df = filter_dataframe(df, search_term, column_filters)
    
    # Show result count
    st.caption(f"Showing {len(filtered_df)} of {len(df)} products")
    
    # -------------------------------------------------------------------------
    # DATA DISPLAY WITH EDITING
    # -------------------------------------------------------------------------
    
    st.markdown(f"#### {display_name} Inventory")
    
    # Use st.data_editor for inline editing
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",  # Allows adding/deleting rows
        key=f"editor_{category}",
        column_config={
            "Cost": st.column_config.NumberColumn(format="$%.2f"),
            "Cost/Oz": st.column_config.NumberColumn(format="$%.4f"),
            "Cost/Unit": st.column_config.NumberColumn(format="$%.4f"),
            "Value": st.column_config.NumberColumn(format="$%.2f"),
            "Neat Price": st.column_config.NumberColumn(format="$%.2f"),
            "Bottle Price": st.column_config.NumberColumn(format="$%.2f"),
            "Menu Price": st.column_config.NumberColumn(format="$%.2f"),
            "BTG": st.column_config.NumberColumn(format="$%.2f"),
            "Margin": st.column_config.NumberColumn(format="%.0%%"),
            "Cost per Keg/Case": st.column_config.NumberColumn(format="$%.2f"),
            "Suggested Retail": st.column_config.NumberColumn(format="$%.2f"),
        }
    )
    
    # -------------------------------------------------------------------------
    # SAVE CHANGES BUTTON
    # -------------------------------------------------------------------------
    
    col_save, col_recalc, col_spacer = st.columns([1, 1, 4])
    
    with col_save:
        if st.button(f"💾 Save Changes", key=f"save_{category}"):
            # Recalculate derived fields before saving
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
            st.success("✅ Changes saved!")
            st.rerun()
    
    with col_recalc:
        if st.button(f"🔄 Recalculate", key=f"recalc_{category}"):
            st.rerun()


# =============================================================================
# PAGE: WEEKLY ORDER BUILDER (Placeholder)
# =============================================================================

def show_ordering():
    """
    Placeholder for the Weekly Order Builder module.
    """
    
    if st.button("← Home"):
        navigate_to('home')
        st.rerun()
    
    st.title("📋 Weekly Order Builder")
    st.info("🚧 This module is under construction. Coming soon!")


# =============================================================================
# PAGE: COCKTAIL BUILDS BOOK (Placeholder)
# =============================================================================

def show_cocktails():
    """
    Placeholder for the Cocktail Builds Book module.
    """
    
    if st.button("← Home"):
        navigate_to('home')
        st.rerun()
    
    st.title("🍹 Cocktail Builds Book")
    st.info("🚧 This module is under construction. Coming soon!")


# =============================================================================
# MAIN ROUTING LOGIC
# =============================================================================

def main():
    """
    Main application entry point.
    Initializes session state and routes to the correct page.
    """
    
    # Initialize session state on app load
    init_session_state()
    
    # Route to the appropriate page
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
