import streamlit as st
import httpx
import io
import base64
import json
import os
from PIL import Image
import streamlit.components.v1 as components

# Set page configuration
st.set_page_config(
    page_title="AI Portfolio Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoints
API_URL = "http://0.0.0.0:8000"  # FastAPI backend

# Function to display formatted error messages
def show_error(message):
    st.error(f"Error: {message}")

# Function to make API calls
async def call_api(endpoint, method="GET", data=None, files=None):
    url = f"{API_URL}{endpoint}"
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if method == "GET":
                response = await client.get(url)
            elif method == "POST":
                response = await client.post(url, data=data, files=files)
            
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

# Function to extract resume information
async def extract_resume_info(uploaded_file):
    try:
        # Call the resume extraction API
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        result = await call_api("/extract-resume", method="POST", files=files)
        
        if result["status"] == "success":
            return result["data"]
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to extract resume information: {str(e)}")

# Function to get available themes
async def get_themes():
    try:
        result = await call_api("/themes")
        if result["status"] == "success":
            return result["themes"]
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to get themes: {str(e)}")

# Function to generate portfolio
async def generate_portfolio(resume_data, theme, claude_api_key):
    try:
        # Prepare form data
        data = {
            "resume_data": str(resume_data),
            "theme": theme,
            "claude_api_key": claude_api_key
        }
        
        # Call the portfolio generation API
        result = await call_api("/generate-portfolio", method="POST", data=data)
        
        if result["status"] == "success":
            return {
                "html": result["html"],
                "preview_uri": result["preview_uri"],
                "zip_base64": result["zip_base64"]
            }
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to generate portfolio: {str(e)}")

# Function to save portfolio
async def save_portfolio(email, portfolio_name, resume_data, theme, html_content):
    try:
        # Prepare form data
        data = {
            "email": email,
            "resume_data": json.dumps(resume_data),
            "theme": theme,
            "html_content": html_content,
            "portfolio_name": portfolio_name
        }
        
        # Call the save portfolio API
        result = await call_api("/save-portfolio", method="POST", data=data)
        
        if result["status"] == "success":
            return result["portfolio_id"]
        else:
            raise Exception(result.get("message", "Unknown error"))
    except Exception as e:
        raise Exception(f"Failed to save portfolio: {str(e)}")

# Main application
def main():
    # Title and description
    st.title("🚀 AI Portfolio Generator")
    st.markdown("""
    Transform your resume into a professional portfolio website with AI assistance.
    Upload your resume, customize your theme, and download a ready-to-deploy portfolio!
    """)
    
    # Initialize session state variables if they don't exist
    if "resume_data" not in st.session_state:
        st.session_state.resume_data = None
    if "generated_portfolio" not in st.session_state:
        st.session_state.generated_portfolio = None
    if "themes" not in st.session_state:
        st.session_state.themes = []
    
    # Create tabs for the workflow
    tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "🎨 Customize Theme", "📄 Generate & Download"])
    
    # Tab 1: Upload and process resume
    with tab1:
        st.header("Resume Information")
        st.write("Upload your resume to extract information automatically.")
        
        # API Key section in sidebar
        with st.sidebar:
            st.header("API Configuration")
            # Using environment variable for API key
            import os
            claude_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
            if claude_api_key:
                st.success("Claude API key detected!")
            else:
                claude_api_key = st.text_input("Claude API Key", type="password", help="Enter your Anthropic Claude API key")
                st.info("Your API key is required to use the AI features. It's stored only in your session.")
        
        # File uploader for resume
        uploaded_file = st.file_uploader("Upload your resume (PDF format only)", type=["pdf"])
        
        if uploaded_file is not None:
            # Display file details
            st.write(f"File name: {uploaded_file.name}")
            
            # Extract resume information button
            if st.button("Extract Resume Information"):
                with st.spinner("Extracting information from your resume..."):
                    try:
                        # Use nest_asyncio to allow running asyncio in Streamlit
                        import nest_asyncio
                        nest_asyncio.apply()
                        
                        # Create a new event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Get resume information
                        st.session_state.resume_data = loop.run_until_complete(extract_resume_info(uploaded_file))
                        st.success("Resume information extracted successfully!")
                        
                        # Get available themes
                        st.session_state.themes = loop.run_until_complete(get_themes())
                        
                        # Cleanup
                        loop.close()
                        
                        # Suggest going to the next tab
                        st.info("Proceed to the 'Customize Theme' tab to continue.")
                    except Exception as e:
                        show_error(str(e))


    # Tab 2: Theme customization
    with tab2:
        st.header("Customize Your Portfolio")
        st.write("Select a theme and customize your portfolio appearance.")
        
        if st.session_state.resume_data is None:
            st.info("Please upload and extract your resume information in the 'Upload Resume' tab first.")
        else:
            # Display and edit extracted resume information
            with st.expander("Edit Resume Information"):
                # Initialize session state for editing if not already present
                if "editing_resume" not in st.session_state:
                    st.session_state.editing_resume = False
                    st.session_state.edited_resume_data = st.session_state.resume_data.copy()
                
                # Edit personal information
                st.subheader("Personal Information")
                
                # Create columns for displaying and editing
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    st.write("Name:")
                with col2:
                    st.session_state.edited_resume_data["name"] = st.text_input(
                        "Edit Name", 
                        value=st.session_state.edited_resume_data.get("name", ""),
                        label_visibility="collapsed"
                    )
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.write("Email:")
                with col2:
                    st.session_state.edited_resume_data["email"] = st.text_input(
                        "Edit Email", 
                        value=st.session_state.edited_resume_data.get("email", ""),
                        label_visibility="collapsed"
                    )
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.write("Phone:")
                with col2:
                    st.session_state.edited_resume_data["phone"] = st.text_input(
                        "Edit Phone", 
                        value=st.session_state.edited_resume_data.get("phone", ""),
                        label_visibility="collapsed"
                    )
                
                # Display and edit sections
                st.subheader("Resume Sections")
                
                # Section tabs: manage sections outside of the main expander
                section_tabs = st.tabs(["Add New Section", "Edit Existing Sections"])
                
                with section_tabs[0]:
                    # Add option to create a new section
                    st.subheader("➕ Add New Section")
                    new_section_name = st.text_input("New Section Name", key="new_section_name")
                    new_section_content = st.text_area("New Section Content", key="new_section_content", height=150)
                    if st.button("Add Section"):
                        if new_section_name and new_section_content:
                            # Create a copy of sections to avoid modifying during iteration
                            sections = st.session_state.edited_resume_data.get("sections", {}).copy()
                            # Add the new section to the edited sections
                            sections[new_section_name] = new_section_content
                            st.session_state.edited_resume_data["sections"] = sections
                            st.success(f"Added new section: {new_section_name}")
                            st.rerun()
                        else:
                            st.warning("Please provide both a section name and content.")
                
                with section_tabs[1]:
                    # Get sections
                    sections = st.session_state.edited_resume_data.get("sections", {}).copy()
                    if not sections:
                        st.info("No sections available to edit. Add sections in the 'Add New Section' tab.")
                    else:
                        # Create a selectbox to choose which section to edit
                        section_to_edit = st.selectbox("Select section to edit:", list(sections.keys()))
                        
                        if section_to_edit:
                            st.subheader(f"Editing: {section_to_edit}")
                            edited_content = st.text_area(
                                f"Section Content", 
                                value=sections[section_to_edit],
                                height=200,
                                key=f"edit_{section_to_edit}"
                            )
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                if st.button(f"Update Section", key=f"update_{section_to_edit}"):
                                    sections[section_to_edit] = edited_content
                                    st.session_state.edited_resume_data["sections"] = sections
                                    st.success(f"Updated {section_to_edit}")
                            with col2:
                                if st.button(f"Delete Section", key=f"delete_{section_to_edit}"):
                                    del sections[section_to_edit]
                                    st.session_state.edited_resume_data["sections"] = sections
                                    st.warning(f"Deleted {section_to_edit}")
                                    st.rerun()
                
                # Apply all changes button
                if st.button("Apply All Changes to Resume"):
                    # Make a deep copy to ensure all nested data is properly copied
                    st.session_state.resume_data = st.session_state.edited_resume_data.copy()
                    
                    # Ensure phone number is updated in both places
                    phone = st.session_state.edited_resume_data.get("phone", "")
                    st.session_state.resume_data["phone"] = phone
                    
                    st.success("All changes applied successfully!")
                    # Add explanation about preview
                    st.info("Click 'Preview Theme' to see your changes reflected in the portfolio.")
                    
                st.divider()
                st.info("Note: Changes will be reflected in your portfolio when you preview or generate it.")
            
            # Theme selection
            # Use the themes from session state
            theme = st.selectbox("Select a theme for your portfolio", st.session_state.themes)
            
            # Theme description
            theme_descriptions = {
                "Professional Classic": "A classic, professional portfolio with a clean, corporate aesthetic suitable for traditional industries.",
                "Modern Minimalist": "A minimalist portfolio with ample white space, subtle animations, and a focus on typography.",
                "Netflix Style": "A Netflix-inspired dark theme with card-based content layout and horizontal scrolling.",
                "Amazon Style": "An Amazon-inspired layout with a user-friendly, information-rich design and clear sections.",
                "Creative Portfolio": "An artistic portfolio with bold colors, unusual layouts, and creative elements.",
                "Tech Professional": "A tech-focused portfolio with a dark mode aesthetic and code-like elements."
            }
            
            if theme in theme_descriptions:
                st.info(theme_descriptions[theme])
            
            # Additional customization options
            st.subheader("Additional Customization")
            accent_color = st.color_picker("Select accent color", "#4169E1")
            
            # Preview theme button
            if st.button("Preview Theme"):
                if claude_api_key:
                    with st.spinner("Generating theme preview..."):
                        try:
                            # Always use the most recent edited resume data for generating the portfolio
                            if "edited_resume_data" in st.session_state:
                                resume_data = st.session_state.edited_resume_data.copy()
                                # Update the main resume data with edited data for consistency
                                st.session_state.resume_data = st.session_state.edited_resume_data.copy()
                            else:
                                resume_data = st.session_state.resume_data.copy()
                                
                            resume_data["theme_preferences"] = {
                                "theme": theme,
                                "accent_color": accent_color
                            }
                            
                            # Use nest_asyncio to allow running asyncio in Streamlit
                            import nest_asyncio
                            nest_asyncio.apply()
                            
                            # Create a new event loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            # Generate preview
                            preview_data = loop.run_until_complete(generate_portfolio(resume_data, theme, claude_api_key))
                            
                            # Cleanup
                            loop.close()
                            
                            # Show preview
                            st.subheader("Theme Preview")
                            components.html(preview_data["html"], height=500, scrolling=True)
                            
                            # Store the generated portfolio
                            st.session_state.generated_portfolio = preview_data
                            
                            # Suggest going to the next tab
                            st.info("Like what you see? Proceed to the 'Generate & Download' tab to finalize your portfolio.")
                        except Exception as e:
                            show_error(str(e))
                else:
                    st.warning("Please enter your Claude API key in the sidebar.")
    
    # Tab 3: Generate and download portfolio
    with tab3:
        st.header("Generate & Download Your Portfolio")
        st.write("Generate your final portfolio and download it for deployment.")
        
        if st.session_state.resume_data is None:
            st.info("Please upload and extract your resume information in the 'Upload Resume' tab first.")
        elif st.session_state.generated_portfolio is None:
            st.info("Please customize and preview your theme in the 'Customize Theme' tab first.")
        else:
            # Display the generated portfolio
            st.subheader("Your Generated Portfolio")
            components.html(st.session_state.generated_portfolio["html"], height=500, scrolling=True)
            
            # Save portfolio section
            st.subheader("Save Your Portfolio")
            col1, col2 = st.columns(2)
            with col1:
                email = st.text_input("Email address", key="save_email")
            with col2:
                portfolio_name = st.text_input("Portfolio name", value="My Professional Portfolio")
                
            if st.button("Save Portfolio"):
                if email:
                    with st.spinner("Saving your portfolio..."):
                        try:
                            theme = st.session_state.resume_data.get("theme_preferences", {}).get("theme", "Professional Classic")
                            
                            # Use nest_asyncio for async operations
                            import nest_asyncio
                            nest_asyncio.apply()
                            
                            # Create a new event loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            # Save portfolio
                            portfolio_id = loop.run_until_complete(save_portfolio(
                                email=email,
                                portfolio_name=portfolio_name,
                                resume_data=st.session_state.resume_data,
                                theme=theme,
                                html_content=st.session_state.generated_portfolio["html"]
                            ))
                            
                            # Cleanup
                            loop.close()
                            
                            st.success(f"Portfolio saved successfully! Portfolio ID: {portfolio_id}")
                            st.info("You can view all your saved portfolios in the 'My Portfolios' page.")
                        except Exception as e:
                            show_error(str(e))
                else:
                    st.warning("Please enter your email address to save the portfolio.")
            
            # Download options
            st.subheader("Download Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Download HTML file
                st.download_button(
                    label="Download HTML",
                    data=st.session_state.generated_portfolio["html"],
                    file_name="portfolio.html",
                    mime="text/html"
                )
            
            with col2:
                # Download ZIP file
                zip_bytes = base64.b64decode(st.session_state.generated_portfolio["zip_base64"])
                st.download_button(
                    label="Download as ZIP",
                    data=zip_bytes,
                    file_name="portfolio.zip",
                    mime="application/zip"
                )
            
            # Deployment instructions
            with st.expander("Deployment Instructions"):
                st.markdown("""
                ### How to deploy your portfolio website
                
                #### Option 1: Deploy on Netlify
                1. Create a free account on [Netlify](https://www.netlify.com/)
                2. From the Netlify dashboard, click on "Add new site" > "Deploy manually"
                3. Drag and drop your HTML file or the extracted ZIP contents
                4. Your site will be deployed instantly with a Netlify subdomain
                
                #### Option 2: Deploy on Vercel
                1. Create a free account on [Vercel](https://vercel.com/)
                2. From the Vercel dashboard, click on "New Project"
                3. Import your project from GitHub (you'll need to push your HTML file to a repository)
                4. Follow the prompts to deploy
                
                #### Option 3: Deploy on GitHub Pages
                1. Create a GitHub repository
                2. Upload your HTML file and rename it to "index.html"
                3. Go to repository settings > Pages > and enable GitHub Pages
                4. Your site will be available at https://yourusername.github.io/repositoryname/
                """)

# Run the application
if __name__ == "__main__":
    import asyncio
    
    # Add async support to Streamlit
    async def main_async():
        main()
    
    asyncio.run(main_async())
