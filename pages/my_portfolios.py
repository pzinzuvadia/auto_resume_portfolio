import streamlit as st
import httpx
import json
import base64
import asyncio
import os

# Configure page
st.set_page_config(
    page_title="My Portfolios",
    page_icon="📁",
    layout="wide"
)

# API URL
API_URL = "http://0.0.0.0:8000"

# Function to make API calls
async def call_api(endpoint, method="GET", data=None, files=None):
    url = f"{API_URL}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, data=data, files=files)
            elif method == "DELETE":
                response = await client.delete(url)
            
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        error_message = f"HTTP error: {e.response.status_code}"
        try:
            error_data = e.response.json()
            if "message" in error_data:
                error_message = error_data["message"]
        except:
            pass
        raise Exception(error_message)
    except httpx.RequestError as e:
        raise Exception(f"Request error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: {str(e)}")

# Function to get user portfolios
async def get_user_portfolios(email):
    try:
        result = await call_api(f"/user-portfolios/{email}")
        if result["status"] == "success":
            return result["portfolios"]
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to get portfolios: {str(e)}")

# Function to get portfolio details
async def get_portfolio(portfolio_id):
    try:
        result = await call_api(f"/portfolio/{portfolio_id}")
        if result["status"] == "success":
            return result["portfolio"]
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to get portfolio: {str(e)}")

# Function to delete portfolio
async def delete_portfolio(portfolio_id):
    try:
        result = await call_api(f"/portfolio/{portfolio_id}", method="DELETE")
        if result["status"] == "success":
            return True
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to delete portfolio: {str(e)}")

# Main function
def main():
    st.title("📁 My Saved Portfolios")
    st.write("View and manage your saved portfolio websites.")
    
    # Get user email
    email = st.text_input("Enter your email to view your portfolios:")
    
    if email:
        try:
            # Get user portfolios
            with st.spinner("Loading portfolios..."):
                # Use nest_asyncio to allow running asyncio in Streamlit
                import nest_asyncio
                nest_asyncio.apply()
                
                # Create a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                portfolios = loop.run_until_complete(get_user_portfolios(email))
                
                # Cleanup
                loop.close()
            
            if not portfolios:
                st.info("You don't have any saved portfolios yet.")
                st.write("Go to the home page to create a new portfolio.")
                return
            
            # Display portfolios
            st.subheader(f"Your Portfolios ({len(portfolios)})")
            
            # Initialize session state for selected portfolio
            if "selected_portfolio_id" not in st.session_state:
                st.session_state.selected_portfolio_id = None
            if "selected_portfolio_data" not in st.session_state:
                st.session_state.selected_portfolio_data = None
            
            # Create portfolio cards
            cols = st.columns(3)
            for i, portfolio in enumerate(portfolios):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.subheader(portfolio["name"])
                        st.write(f"Theme: {portfolio['theme']}")
                        st.write(f"Created: {portfolio['created_at'].split('T')[0]}")
                        
                        if st.button("View", key=f"view_{portfolio['id']}"):
                            st.session_state.selected_portfolio_id = portfolio["id"]
                            # Get portfolio details
                            with st.spinner("Loading portfolio..."):
                                # Use nest_asyncio to allow running asyncio in Streamlit
                                import nest_asyncio
                                nest_asyncio.apply()
                                
                                # Create a new event loop
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                                st.session_state.selected_portfolio_data = loop.run_until_complete(get_portfolio(portfolio["id"]))
                                
                                # Cleanup
                                loop.close()
            
            # Display selected portfolio
            if st.session_state.selected_portfolio_id and st.session_state.selected_portfolio_data:
                portfolio_data = st.session_state.selected_portfolio_data
                
                st.divider()
                st.subheader(f"Portfolio: {portfolio_data['name']}")
                
                # Portfolio tabs
                tab1, tab2, tab3 = st.tabs(["Preview", "Download", "Details"])
                
                # Preview tab
                with tab1:
                    st.components.v1.html(portfolio_data["html_content"], height=600, scrolling=True)
                
                # Download tab
                with tab2:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Download HTML file
                        st.download_button(
                            label="Download HTML",
                            data=portfolio_data["html_content"],
                            file_name=f"{portfolio_data['name'].replace(' ', '_')}.html",
                            mime="text/html"
                        )
                    
                # Details tab
                with tab3:
                    st.write("Portfolio Information:")
                    st.write(f"Theme: {portfolio_data['theme']}")
                    st.write(f"Created: {portfolio_data['created_at'].split('T')[0]}")
                    
                    # Resume information
                    st.subheader("Resume Information")
                    st.write(f"Name: {portfolio_data['resume']['name']}")
                    st.write(f"Email: {portfolio_data['resume']['email']}")
                    st.write(f"Phone: {portfolio_data['resume']['phone']}")
                    
                    # Resume sections
                    if portfolio_data['resume']['sections']:
                        st.subheader("Resume Sections")
                        for section_name, section_content in portfolio_data['resume']['sections'].items():
                            with st.expander(section_name):
                                st.write(section_content)
                
                # Delete portfolio
                if st.button("Delete Portfolio", type="primary", use_container_width=True):
                    if st.session_state.selected_portfolio_id:
                        with st.spinner("Deleting portfolio..."):
                            try:
                                # Use nest_asyncio to allow running asyncio in Streamlit
                                import nest_asyncio
                                nest_asyncio.apply()
                                
                                # Create a new event loop
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                                deleted = loop.run_until_complete(delete_portfolio(st.session_state.selected_portfolio_id))
                                
                                # Cleanup
                                loop.close()
                                
                                if deleted:
                                    st.success("Portfolio deleted successfully!")
                                    st.session_state.selected_portfolio_id = None
                                    st.session_state.selected_portfolio_data = None
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting portfolio: {str(e)}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()