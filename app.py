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

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
# This must be the first Streamlit command in the script.
# Sets the browser tab title, icon, and default layout.

st.set_page_config(
    page_title="Beverage Management App V1",
    page_icon="🍸",                    # Emoji displayed in browser tab
    layout="wide",                      # Use full width of the browser
    initial_sidebar_state="collapsed"   # Start with sidebar hidden for cleaner home
)

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================
# Injects custom CSS to style the navigation cards.
# This creates a professional, clickable card interface for module navigation.

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
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
# Streamlit reruns the script on every interaction. Session state persists
# data across reruns. We use it to track which page/module the user is viewing.

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'home'


# =============================================================================
# NAVIGATION FUNCTION
# =============================================================================
# Updates the session state to navigate between pages.

def navigate_to(page: str):
    """
    Sets the current page in session state to navigate between modules.
    
    Args:
        page (str): The page identifier ('home', 'inventory', 'ordering', 'cocktails')
    """
    st.session_state.current_page = page


# =============================================================================
# PAGE: HOMESCREEN
# =============================================================================
# Displays the main dashboard with navigation cards to each module.

def show_home():
    """
    Renders the homescreen with:
    - App title and welcome message
    - Three navigation cards (Inventory, Ordering, Cocktails)
    """
    
    # ----- Header Section -----
    st.markdown("""
    <div class="main-header">
        <h1>🍸 Beverage Management App V1</h1>
        <p>Manage your inventory, orders, and cocktail recipes in one place</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ----- Navigation Cards Grid -----
    # Using Streamlit columns to create a 3-card layout
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
        
        # Streamlit button placed below the card for navigation
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
# PAGE: MASTER INVENTORY (Placeholder)
# =============================================================================
# This will be expanded in the next code block with full inventory functionality.

def show_inventory():
    """
    Placeholder for the Master Inventory module.
    Will include submodules for Spirits, Wine, Beer, and Ingredients.
    """
    
    # Back button to return home
    if st.button("← Back to Home"):
        navigate_to('home')
        st.rerun()
    
    st.title("📦 Master Inventory")
    st.info("🚧 This module is under construction. We'll build it in the next step!")


# =============================================================================
# PAGE: WEEKLY ORDER BUILDER (Placeholder)
# =============================================================================

def show_ordering():
    """
    Placeholder for the Weekly Order Builder module.
    """
    
    if st.button("← Back to Home"):
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
    
    if st.button("← Back to Home"):
        navigate_to('home')
        st.rerun()
    
    st.title("🍹 Cocktail Builds Book")
    st.info("🚧 This module is under construction. Coming soon!")


# =============================================================================
# MAIN ROUTING LOGIC
# =============================================================================
# Checks session state and renders the appropriate page.

def main():
    """
    Main application entry point.
    Routes to the correct page based on session state.
    """
    
    # Route to the appropriate page based on current_page state
    if st.session_state.current_page == 'home':
        show_home()
    elif st.session_state.current_page == 'inventory':
        show_inventory()
    elif st.session_state.current_page == 'ordering':
        show_ordering()
    elif st.session_state.current_page == 'cocktails':
        show_cocktails()
    else:
        # Fallback to home if unknown page
        show_home()


# =============================================================================
# RUN THE APP
# =============================================================================
# Standard Python idiom to run main() when script is executed directly.

if __name__ == "__main__":
    main()
