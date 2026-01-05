# =============================================================================
# BEVERAGE MANAGEMENT APP V1
# =============================================================================
# A Streamlit application for managing restaurant beverage operations including:
#   - Master Inventory (Spirits, Wine, Beer, Ingredients)
#   - Weekly Order Builder
#   - Cocktail Builds Book
#
# Author: James Juedes
# Deployment: Streamlit Community Cloud via GitHub
# =============================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

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
    
    /* ----- Order Status Styling ----- */
    .order-needed {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    
    .order-ok {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SAMPLE DATA - SPIRITS INVENTORY
# =============================================================================

def get_sample_spirits():
    """
    Returns a DataFrame with sample spirit inventory data.
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

def get_sample_beers():
    """
    Returns a DataFrame with sample beer inventory data.
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
    Returns a DataFrame with weekly inventory items and their par levels.
    This is used for the Weekly Order Builder to track what needs ordering.
    
    Columns:
        - Product: Name of the product
        - Category: Spirits, Wine, Beer, or Ingredients
        - Par: Target inventory level
        - Current Inventory: Current count (user updates weekly)
        - Unit: Unit of measurement for ordering
        - Unit Cost: Cost per unit (pulled from master inventory)
        - Distributor: Supplier
        - Order Notes: Special ordering instructions
    """
    data = [
        # Beer items
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
        
        # Spirits items
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
        
        # Ingredients items
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
    Used to demonstrate order history and demand visualization features.
    """
    
    # Generate dates for past 6 weeks
    today = datetime.now()
    weeks = []
    for i in range(6, 0, -1):
        week_start = today - timedelta(weeks=i)
        weeks.append(week_start.strftime("%Y-%m-%d"))
    
    data = [
        # Week 1
        {"Week": weeks[0], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 24.50, "Total Cost": 49.00, "Distributor": "Breakthru"},
        {"Week": weeks[0], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit Cost": 26.40, "Total Cost": 52.80, "Distributor": "Frank Beer"},
        {"Week": weeks[0], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 3, "Unit Cost": 8.34, "Total Cost": 25.02, "Distributor": "US Foods"},
        
        # Week 2
        {"Week": weeks[1], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 24.50, "Total Cost": 24.50, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 31.00, "Total Cost": 62.00, "Distributor": "Breakthru"},
        {"Week": weeks[1], "Product": "Coors Light", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 24.51, "Total Cost": 24.51, "Distributor": "Frank Beer"},
        
        # Week 3
        {"Week": weeks[2], "Product": "Espolòn Blanco", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 25.00, "Total Cost": 50.00, "Distributor": "Breakthru"},
        {"Week": weeks[2], "Product": "New Glarus Moon Man", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 26.40, "Total Cost": 26.40, "Distributor": "Frank Beer"},
        {"Week": weeks[2], "Product": "Natalie's Lime Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        {"Week": weeks[2], "Product": "Natalie's Lemon Juice", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 8.34, "Total Cost": 16.68, "Distributor": "US Foods"},
        
        # Week 4
        {"Week": weeks[3], "Product": "Tito's", "Category": "Spirits", 
         "Quantity Ordered": 3, "Unit Cost": 24.50, "Total Cost": 73.50, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "Rittenhouse Rye", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 28.00, "Total Cost": 28.00, "Distributor": "Breakthru"},
        {"Week": weeks[3], "Product": "High Life", "Category": "Beer", 
         "Quantity Ordered": 2, "Unit Cost": 21.15, "Total Cost": 42.30, "Distributor": "Frank Beer"},
        
        # Week 5
        {"Week": weeks[4], "Product": "Buffalo Trace", "Category": "Spirits", 
         "Quantity Ordered": 1, "Unit Cost": 31.00, "Total Cost": 31.00, "Distributor": "Breakthru"},
        {"Week": weeks[4], "Product": "Botanist", "Category": "Spirits", 
         "Quantity Ordered": 2, "Unit Cost": 33.74, "Total Cost": 67.48, "Distributor": "General Beverage"},
        {"Week": weeks[4], "Product": "Hop Haus Yard Work IPA", "Category": "Beer", 
         "Quantity Ordered": 1, "Unit Cost": 75.00, "Total Cost": 75.00, "Distributor": "GB Beer"},
        {"Week": weeks[4], "Product": "Q Club Soda", "Category": "Ingredients", 
         "Quantity Ordered": 2, "Unit Cost": 12.48, "Total Cost": 24.96, "Distributor": "Breakthru"},
        
        # Week 6 (most recent)
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
# SESSION STATE INITIALIZATION
# =============================================================================

def init_session_state():
    """
    Initializes all session state variables.
    """
    
    # Navigation state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Inventory data storage
    if 'spirits_inventory' not in st.session_state:
        st.session_state.spirits_inventory = get_sample_spirits()
    
    if 'wine_inventory' not in st.session_state:
        st.session_state.wine_inventory = get_sample_wines()
    
    if 'beer_inventory' not in st.session_state:
        st.session_state.beer_inventory = get_sample_beers()
    
    if 'ingredients_inventory' not in st.session_state:
        st.session_state.ingredients_inventory = get_sample_ingredients()
    
    if 'last_inventory_date' not in st.session_state:
        st.session_state.last_inventory_date = datetime.now().strftime("%Y-%m-%d")
    
    # Weekly Order Builder data
    if 'weekly_inventory' not in st.session_state:
        st.session_state.weekly_inventory = get_sample_weekly_inventory()
    
    if 'order_history' not in st.session_state:
        st.session_state.order_history = get_sample_order_history()
    
    if 'current_order' not in st.session_state:
        st.session_state.current_order = pd.DataFrame()


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

def calculate_total_value(df: pd.DataFrame) -> float:
    """
    Calculates total inventory value from a DataFrame.
    """
    if 'Value' in df.columns:
        return df['Value'].sum()
    return 0.0


def format_currency(value: float) -> str:
    """
    Formats a number as USD currency.
    """
    return f"${value:,.2f}"


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
    
    Args:
        weekly_inv: DataFrame with Par and Current Inventory columns
        
    Returns:
        DataFrame with products that need ordering and suggested quantities
    """
    # Find items where inventory is below par
    needs_order = weekly_inv[weekly_inv['Current Inventory'] < weekly_inv['Par']].copy()
    
    if len(needs_order) == 0:
        return pd.DataFrame()
    
    # Calculate suggested order amount
    needs_order['Suggested Order'] = needs_order['Par'] - needs_order['Current Inventory']
    needs_order['Order Quantity'] = needs_order['Suggested Order']  # User can modify this
    needs_order['Order Value'] = needs_order['Order Quantity'] * needs_order['Unit Cost']
    
    # Select and reorder columns for display
    order_columns = ['Product', 'Category', 'Current Inventory', 'Par', 
                     'Suggested Order', 'Order Quantity', 'Unit', 'Unit Cost', 
                     'Order Value', 'Distributor', 'Order Notes']
    
    return needs_order[order_columns]


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
    st.markdown(
        "<p style='text-align: center; color: #888;'>Dev by JAJ • Madison, WI</p>",
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
    
    spirits_value = calculate_total_value(st.session_state.spirits_inventory)
    wine_value = calculate_total_value(st.session_state.wine_inventory)
    beer_value = calculate_total_value(st.session_state.beer_inventory)
    ingredients_value = calculate_total_value(st.session_state.ingredients_inventory)
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
    
    # CSV Upload
    with st.expander("📤 Upload Inventory Data (CSV)", expanded=False):
        st.markdown("Upload a CSV file to replace inventory data for any category.")
        
        upload_category = st.selectbox(
            "Select category to upload:",
            ["Spirits", "Wine", "Beer", "Ingredients"],
            key="upload_category"
        )
        
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")
        
        if uploaded_file is not None:
            try:
                new_data = pd.read_csv(uploaded_file)
                st.write("Preview of uploaded data:")
                st.dataframe(new_data.head())
                
                if st.button("✅ Confirm Upload", key="confirm_upload"):
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


def show_inventory_tab(df: pd.DataFrame, category: str, filter_columns: list, display_name: str):
    """
    Renders an inventory tab with search, filter, and editing.
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
    
    edited_df = st.data_editor(
        filtered_df,
        use_container_width=True,
        num_rows="dynamic",
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
    Renders the Weekly Order Builder module with:
    - Dashboard showing order costs and top products
    - Weekly inventory input with par levels
    - Auto-generated order based on items below par
    - Order history and demand visualization
    """
    
    # ----- Header -----
    col_back, col_title = st.columns([1, 11])
    with col_back:
        if st.button("← Home"):
            navigate_to('home')
            st.rerun()
    with col_title:
        st.title("📋 Weekly Order Builder")
    
    # =========================================================================
    # DASHBOARD SECTION
    # =========================================================================
    
    st.markdown("### 📊 Order Dashboard")
    
    # Calculate metrics from order history
    order_history = st.session_state.order_history
    
    if len(order_history) > 0:
        # Get unique weeks and sort them
        weeks = sorted(order_history['Week'].unique())
        
        # Previous week's total (most recent in history)
        if len(weeks) >= 1:
            prev_week = weeks[-1]
            prev_week_total = order_history[order_history['Week'] == prev_week]['Total Cost'].sum()
        else:
            prev_week_total = 0
        
        # Calculate top products by frequency and total spend
        top_products = order_history.groupby('Product').agg({
            'Quantity Ordered': 'sum',
            'Total Cost': 'sum'
        }).sort_values('Total Cost', ascending=False).head(5)
    else:
        prev_week_total = 0
        top_products = pd.DataFrame()
    
    # Current order total (being built)
    if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
        current_order_total = st.session_state.current_order['Order Value'].sum()
    else:
        current_order_total = 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📅 Previous Week's Order",
            value=format_currency(prev_week_total)
        )
    
    with col2:
        st.metric(
            label="🛒 Current Order (Building)",
            value=format_currency(current_order_total)
        )
    
    with col3:
        st.metric(
            label="📈 6-Week Avg Order",
            value=format_currency(order_history.groupby('Week')['Total Cost'].sum().mean() if len(order_history) > 0 else 0)
        )
    
    # Top products display
    if len(top_products) > 0:
        with st.expander("🏆 Top Products (by total spend)", expanded=False):
            st.dataframe(
                top_products.reset_index().rename(columns={
                    'Product': 'Product',
                    'Quantity Ordered': 'Total Units Ordered',
                    'Total Cost': 'Total Spend'
                }),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total Spend": st.column_config.NumberColumn(format="$%.2f")
                }
            )
    
    st.markdown("---")
    
    # =========================================================================
    # TABS: BUILD ORDER / ORDER HISTORY / ANALYTICS
    # =========================================================================
    
    tab_build, tab_history, tab_analytics = st.tabs([
        "🛒 Build This Week's Order", 
        "📜 Order History", 
        "📈 Demand Analytics"
    ])
    
    # -------------------------------------------------------------------------
    # TAB: BUILD ORDER
    # -------------------------------------------------------------------------
    with tab_build:
        st.markdown("### Step 1: Update Current Inventory Counts")
        st.markdown("Enter your current inventory counts below. Products below par will be added to the order.")
        
        # Weekly inventory editor
        weekly_inv = st.session_state.weekly_inventory.copy()
        
        # Add a status column to show if order is needed
        weekly_inv['Status'] = weekly_inv.apply(
            lambda row: "🔴 Order" if row['Current Inventory'] < row['Par'] else "✅ OK",
            axis=1
        )
        
        # Reorder columns for display
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
        
        # Update session state with edited values
        if st.button("🔄 Update Inventory & Generate Order", key="update_weekly"):
            # Update the weekly inventory with edited values
            st.session_state.weekly_inventory['Current Inventory'] = edited_weekly['Current Inventory'].values
            st.session_state.weekly_inventory['Par'] = edited_weekly['Par'].values
            
            # Generate order
            order = generate_order_from_inventory(st.session_state.weekly_inventory)
            st.session_state.current_order = order
            st.success("✅ Inventory updated and order generated!")
            st.rerun()
        
        st.markdown("---")
        st.markdown("### Step 2: Review & Adjust This Week's Order")
        
        # Display and edit current order
        if 'current_order' in st.session_state and len(st.session_state.current_order) > 0:
            order_df = st.session_state.current_order.copy()
            
            st.markdown(f"**{len(order_df)} items need ordering:**")
            
            # Editable order table
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
            
            # Recalculate order values when quantity changes
            if st.button("💰 Recalculate Order Total", key="recalc_order"):
                edited_order['Order Value'] = edited_order['Order Quantity'] * edited_order['Unit Cost']
                st.session_state.current_order = edited_order
                st.rerun()
            
            # Order summary
            st.markdown("---")
            st.markdown("### Order Summary")
            
            col_summary1, col_summary2, col_summary3 = st.columns(3)
            
            with col_summary1:
                st.metric("Total Items", len(edited_order))
            
            with col_summary2:
                st.metric("Total Units", f"{edited_order['Order Quantity'].sum():.1f}")
            
            with col_summary3:
                order_total = edited_order['Order Value'].sum()
                st.metric("Total Order Value", format_currency(order_total))
            
            # Order by distributor breakdown
            st.markdown("#### By Distributor:")
            distributor_summary = edited_order.groupby('Distributor').agg({
                'Order Quantity': 'sum',
                'Order Value': 'sum'
            }).reset_index()
            
            st.dataframe(
                distributor_summary,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Order Value": st.column_config.NumberColumn(format="$%.2f")
                }
            )
            
            # Save order button
            st.markdown("---")
            if st.button("✅ Save Order to History", key="save_order", type="primary"):
                # Create order history entries
                today = datetime.now().strftime("%Y-%m-%d")
                
                new_orders = []
                for _, row in edited_order.iterrows():
                    if row['Order Quantity'] > 0:
                        new_orders.append({
                            'Week': today,
                            'Product': row['Product'],
                            'Category': row['Category'],
                            'Quantity Ordered': row['Order Quantity'],
                            'Unit Cost': row['Unit Cost'],
                            'Total Cost': row['Order Value'],
                            'Distributor': row['Distributor']
                        })
                
                if new_orders:
                    new_orders_df = pd.DataFrame(new_orders)
                    st.session_state.order_history = pd.concat([
                        st.session_state.order_history, 
                        new_orders_df
                    ], ignore_index=True)
                    
                    # Reset current order
                    st.session_state.current_order = pd.DataFrame()
                    
                    # Update weekly inventory (reset current inventory to par after ordering)
                    # This simulates receiving the order
                    st.success("✅ Order saved to history!")
                    st.balloons()
                    st.rerun()
                else:
                    st.warning("No items with quantity > 0 to save.")
        
        else:
            st.info("👆 Update inventory counts above and click 'Update Inventory & Generate Order' to see what needs ordering.")
    
    # -------------------------------------------------------------------------
    # TAB: ORDER HISTORY
    # -------------------------------------------------------------------------
    with tab_history:
        st.markdown("### 📜 Previous Orders")
        
        order_history = st.session_state.order_history
        
        if len(order_history) > 0:
            # Filter options
            col_filter1, col_filter2 = st.columns(2)
            
            with col_filter1:
                weeks = sorted(order_history['Week'].unique(), reverse=True)
                selected_weeks = st.multiselect(
                    "Filter by Week:",
                    options=weeks,
                    default=weeks[:4] if len(weeks) >= 4 else weeks,
                    key="history_week_filter"
                )
            
            with col_filter2:
                categories = order_history['Category'].unique().tolist()
                selected_categories = st.multiselect(
                    "Filter by Category:",
                    options=categories,
                    default=categories,
                    key="history_category_filter"
                )
            
            # Apply filters
            filtered_history = order_history.copy()
            if selected_weeks:
                filtered_history = filtered_history[filtered_history['Week'].isin(selected_weeks)]
            if selected_categories:
                filtered_history = filtered_history[filtered_history['Category'].isin(selected_categories)]
            
            # Weekly totals
            st.markdown("#### Weekly Order Totals")
            weekly_totals = filtered_history.groupby('Week')['Total Cost'].sum().reset_index()
            weekly_totals = weekly_totals.sort_values('Week', ascending=False)
            
            st.dataframe(
                weekly_totals,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Total Cost": st.column_config.NumberColumn(format="$%.2f")
                }
            )
            
            # Detailed order history
            st.markdown("#### Order Details")
            st.dataframe(
                filtered_history.sort_values(['Week', 'Product'], ascending=[False, True]),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Unit Cost": st.column_config.NumberColumn(format="$%.2f"),
                    "Total Cost": st.column_config.NumberColumn(format="$%.2f")
                }
            )
        else:
            st.info("No order history yet. Save an order to see it here.")
    
    # -------------------------------------------------------------------------
    # TAB: DEMAND ANALYTICS
    # -------------------------------------------------------------------------
    with tab_analytics:
        st.markdown("### 📈 Demand Analytics")
        
        order_history = st.session_state.order_history
        
        if len(order_history) > 0:
            # Product selector for line plot
            products = sorted(order_history['Product'].unique())
            
            selected_products = st.multiselect(
                "Select products to analyze:",
                options=products,
                default=products[:3] if len(products) >= 3 else products,
                key="analytics_products"
            )
            
            if selected_products:
                # Filter data for selected products
                plot_data = order_history[order_history['Product'].isin(selected_products)]
                
                # Line plot of quantity ordered over time
                st.markdown("#### Quantity Ordered Over Time")
                
                fig_qty = px.line(
                    plot_data,
                    x='Week',
                    y='Quantity Ordered',
                    color='Product',
                    markers=True,
                    title='Weekly Order Quantities by Product'
                )
                fig_qty.update_layout(
                    xaxis_title="Week",
                    yaxis_title="Quantity Ordered",
                    legend_title="Product",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_qty, use_container_width=True)
                
                # Line plot of spending over time
                st.markdown("#### Spending Over Time")
                
                fig_cost = px.line(
                    plot_data,
                    x='Week',
                    y='Total Cost',
                    color='Product',
                    markers=True,
                    title='Weekly Spending by Product'
                )
                fig_cost.update_layout(
                    xaxis_title="Week",
                    yaxis_title="Total Cost ($)",
                    legend_title="Product",
                    hovermode='x unified'
                )
                st.plotly_chart(fig_cost, use_container_width=True)
                
                # Summary statistics
                st.markdown("#### Product Summary Statistics")
                
                summary_stats = plot_data.groupby('Product').agg({
                    'Quantity Ordered': ['sum', 'mean', 'std'],
                    'Total Cost': ['sum', 'mean']
                }).round(2)
                
                summary_stats.columns = ['Total Qty', 'Avg Qty/Week', 'Std Dev', 'Total Spend', 'Avg Spend/Week']
                summary_stats = summary_stats.reset_index()
                
                st.dataframe(
                    summary_stats,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Total Spend": st.column_config.NumberColumn(format="$%.2f"),
                        "Avg Spend/Week": st.column_config.NumberColumn(format="$%.2f")
                    }
                )
            
            # Category breakdown
            st.markdown("---")
            st.markdown("#### Spending by Category")
            
            category_spending = order_history.groupby('Category')['Total Cost'].sum().reset_index()
            
            fig_pie = px.pie(
                category_spending,
                values='Total Cost',
                names='Category',
                title='Total Spending by Category'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        else:
            st.info("No order history yet. Save some orders to see analytics.")


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
