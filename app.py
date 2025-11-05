"""Main Streamlit application."""

import streamlit as st
from datetime import datetime
import uuid

from src.services import LinkedInScraper, LLMService
from src.memory import MemoryManager
from src.graph import create_workflow, GraphState
from src.config.settings import settings
from src.utils.helpers import format_profile_data


# Page configuration
st.set_page_config(
    page_title=settings.app_title,
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = MemoryManager(st.session_state.session_id)
    
    if 'workflow' not in st.session_state:
        st.session_state.workflow = create_workflow(st.session_state.memory_manager)
    
    if 'profile_loaded' not in st.session_state:
        st.session_state.profile_loaded = False
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'profile_data' not in st.session_state:
        st.session_state.profile_data = None


def display_sidebar():
    """Display sidebar with profile info and controls."""
    with st.sidebar:
        st.title("🎯 Profile Optimizer")
        
        st.markdown("---")
        
        # LinkedIn URL Input
        st.subheader("📎 LinkedIn Profile")
        linkedin_url = st.text_input(
            "Enter LinkedIn Profile URL",
            placeholder="https://www.linkedin.com/in/username",
            help="Paste your LinkedIn profile URL here"
        )
        
        if st.button("🔄 Load Profile", type="primary", use_container_width=True):
            if linkedin_url:
                with st.spinner("Scraping LinkedIn profile..."):
                    load_linkedin_profile(linkedin_url)
            else:
                st.error("Please enter a valid LinkedIn URL")
        
        st.markdown("---")
        
        # Profile Status
        if st.session_state.profile_loaded:
            st.success("✅ Profile Loaded")
            profile = st.session_state.memory_manager.get_profile()
            if profile:
                st.write(f"**Name:** {profile.get('full_name', 'N/A')}")
                st.write(f"**Headline:** {profile.get('headline', 'N/A')[:50]}...")
        else:
            st.info("📝 No profile loaded yet")
        
        st.markdown("---")
        
        # Career Goals
        st.subheader("🎯 Career Goals")
        target_role = st.text_input(
            "Target Role",
            value=st.session_state.memory_manager.get_target_role() or "",
            placeholder="e.g., Data Analyst"
        )
        
        if target_role:
            st.session_state.memory_manager.set_target_role(target_role)
        
        career_goals = st.text_area(
            "Career Goals",
            value=st.session_state.memory_manager.get_career_goals() or "",
            placeholder="Describe your career aspirations...",
            height=100
        )
        
        if career_goals:
            st.session_state.memory_manager.set_career_goals(career_goals)
        
        st.markdown("---")
        
        # Job Description Section
        st.subheader("📋 Job Description")
        
        # Toggle between custom JD and online search
        jd_option = st.radio(
            "JD Source",
            options=["Use Default/Search Online", "Paste Custom JD"],
            help="Choose how to provide the job description"
        )
        
        if jd_option == "Paste Custom JD":
            custom_jd = st.text_area(
                "Paste Job Description",
                value=st.session_state.get('custom_jd', ''),
                placeholder="""Paste the full job description here...

Example:
We are looking for a Software Engineer with 3+ years experience in Python, React, and AWS. 

Responsibilities:
- Build scalable web applications
- Collaborate with cross-functional teams

Requirements:
- Strong Python and JavaScript skills
- Experience with cloud platforms
- Excellent communication skills
                """,
                height=200,
                key="custom_jd_input"
            )
            
            # Save to session state
            if custom_jd:
                st.session_state.custom_jd = custom_jd
                st.info(f"✅ Custom JD loaded ({len(custom_jd)} characters)")
            else:
                st.session_state.custom_jd = ""
            
            # Clear online search settings
            st.session_state.use_online_search = False
            
        else:
            # Clear custom JD if switching modes
            st.session_state.custom_jd = ""
            
            # Location input for online search
            location = st.text_input(
                "Location (Optional)",
                value=st.session_state.get('job_location', ''),
                placeholder="e.g., San Francisco, CA",
                help="For online job search"
            )
            
            if location:
                st.session_state.job_location = location
            
            use_online_search = st.checkbox(
                "🔍 Search for real job postings online",
                value=st.session_state.get('use_online_search', False),
                help="Uses Tavily API to fetch actual job descriptions (requires API key)"
            )
            
            st.session_state.use_online_search = use_online_search
            
            if use_online_search and not settings.tavily_api_key:
                st.warning("⚠️ Tavily API key not configured. Will use default JD database.")
        
        st.markdown("---")
        
        # Quick Actions
        st.subheader("⚡ Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Analyze Profile", use_container_width=True):
                handle_quick_action("Analyze my LinkedIn profile")
        
        with col2:
            if st.button("🎯 Job Match", use_container_width=True):
                if target_role:
                    # Build query with custom JD info
                    if st.session_state.get('custom_jd'):
                        handle_quick_action(
                            f"Analyze my fit for {target_role} using the custom job description I provided"
                        )
                    else:
                        handle_quick_action(f"Analyze my fit for {target_role}")
                else:
                    st.warning("Set target role first")
        
        st.markdown("---")
        
        # Clear Chat
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.memory_manager.clear_session()
            st.rerun()


def load_linkedin_profile(url: str):
    """Load LinkedIn profile from URL."""
    try:
        print(f"\n[APP] Starting profile load for URL: {url}")
        scraper = LinkedInScraper()
        profile_data = scraper.scrape_profile(url)
        
        if profile_data:
            st.session_state.profile_data = profile_data
            st.session_state.profile_loaded = True
            st.session_state.memory_manager.set_profile(profile_data)
            
            # Display success message
            st.success("✅ Profile loaded successfully!")
            
            # DEBUG: Show raw JSON data in expandable section
            with st.expander("🔍 Debug: Raw Profile Data (JSON)"):
                st.json(profile_data)
                st.caption("This is the exact data returned by the Apify actor")
            
            # Get values with fallbacks for different field name variations
            full_name = profile_data.get('full_name') or profile_data.get('fullName') or profile_data.get('firstName', 'N/A')
            headline = profile_data.get('headline', 'N/A')
            experience_count = len(profile_data.get('experience', []) or profile_data.get('positions', []))
            education_count = len(profile_data.get('education', []) or profile_data.get('schools', []))
            skills_count = len(profile_data.get('skills', []))
            
            # Add welcome message
            welcome_msg = f"""
Welcome! I've loaded your LinkedIn profile.

**Profile Summary:**
- **Name:** {full_name}
- **Headline:** {headline}
- **Experience:** {experience_count} positions
- **Education:** {education_count} institutions
- **Skills:** {skills_count} skills listed

How can I help you optimize your profile today?
"""
            
            # If profile seems empty, add debug info
            if not full_name or full_name == "N/A" or not headline or headline == "N/A":
                debug_info = f"""

⚠️ **Some profile fields appear empty. Check the debug section above to see the raw data.**

**Available fields in response:** {', '.join(list(profile_data.keys())[:15])}
"""
                welcome_msg += debug_info
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome_msg
            })
            st.rerun()
        else:
            st.error("❌ Failed to load profile. The scraper returned no data.")
            st.info("""
**Possible reasons:**
- The LinkedIn profile is private or restricted
- The Apify API key may be invalid
- The profile URL may be incorrect
- Check the terminal/console for detailed error logs
""")
    
    except ValueError as ve:
        # Validation errors (e.g., invalid URL format)
        st.error(f"❌ {str(ve)}")
        st.info("Please use format: https://www.linkedin.com/in/username")
    
    except Exception as e:
        st.error(f"❌ Error loading profile: {str(e)}")
        print(f"[APP ERROR] {str(e)}")
        import traceback
        print(f"[APP ERROR TRACEBACK]\n{traceback.format_exc()}")
        with st.expander("🔍 Error Details (Check terminal for full logs)"):
            st.code(str(e))
            st.caption("Full error details are printed in the terminal/console")


def handle_quick_action(query: str):
    """Handle quick action button clicks."""
    if not st.session_state.profile_loaded:
        st.warning("Please load a LinkedIn profile first!")
        return
    
    # Add query as user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })
    
    # Process query
    process_user_query(query)
    
    st.rerun()


def process_user_query(query: str):
    """Process user query through the workflow."""
    try:
        memory_manager = st.session_state.memory_manager
        
        # Save user message
        memory_manager.add_message("user", query)
        
        # Get custom JD and search preferences from session state
        custom_jd = st.session_state.get('custom_jd', '')
        use_online_search = st.session_state.get('use_online_search', False)
        location = st.session_state.get('job_location', '')
        
        # Create initial state
        initial_state = GraphState(
            messages=[{"role": "user", "content": query}],
            profile_data=st.session_state.profile_data,
            profile_url=None,
            target_role=memory_manager.get_target_role(),
            career_goals=memory_manager.get_career_goals(),
            job_description=custom_jd if custom_jd else None,
            use_online_search=use_online_search,
            job_location=location,
            profile_analysis=None,
            job_match_results=None,
            generated_content=None,
            career_guidance=None,
            next_agent=None,
            session_id=st.session_state.session_id,
            user_query=query
        )
        
        # Run workflow
        workflow_app = st.session_state.workflow.compile()
        result = workflow_app.invoke(initial_state)
        
        # Get assistant response
        if result["messages"]:
            last_message = result["messages"][-1]
            if last_message["role"] == "assistant":
                st.session_state.messages.append(last_message)
    
    except Exception as e:
        error_msg = f"❌ Error processing query: {str(e)}"
        st.session_state.messages.append({
            "role": "assistant",
            "content": error_msg
        })


def display_chat_interface():
    """Display the main chat interface."""
    st.title("💼 LinkedIn Profile Optimizer")
    st.markdown("*AI-powered career guidance and profile optimization*")
    
    # Display chat messages
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about your profile..."):
        if not st.session_state.profile_loaded:
            st.warning("⚠️ Please load your LinkedIn profile first using the sidebar!")
        else:
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    process_user_query(prompt)
                    
                    # Display the response
                    if st.session_state.messages:
                        last_msg = st.session_state.messages[-1]
                        if last_msg["role"] == "assistant":
                            st.markdown(last_msg["content"])
            
            st.rerun()


def main():
    """Main application entry point."""
    initialize_session_state()
    display_sidebar()
    display_chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <small>Built with ❤️ using Streamlit, LangChain & LangGraph</small>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()