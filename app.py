import streamlit as st
import time
from datetime import datetime
from src.agents.agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# Page Configuration
st.set_page_config(
    page_title="Research Pipeline",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 16px;
        font-weight: 600;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 15px;
        border-radius: 8px;
        color: #155724;
        margin: 10px 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        padding: 15px;
        border-radius: 8px;
        color: #0c5460;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 15px;
        border-radius: 8px;
        color: #856404;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🔬 AI Research Pipeline")
    st.markdown("*Automated research, content scraping, report generation & feedback*")
with col2:
    st.metric("Status", "Ready ✓", delta="Active")

st.divider()

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    st.subheader("Pipeline Settings")
    max_search_results = st.slider(
        "Max Search Results",
        min_value=1,
        max_value=10,
        value=5,
        help="Number of search results to consider"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Controls creativity of responses (0=deterministic, 1=creative)"
    )
    
    st.divider()
    st.subheader("About")
    st.info(
        "This pipeline automates:\n"
        "1. 🔍 Search for relevant information\n"
        "2. 📄 Scrape detailed content\n"
        "3. ✍️ Generate comprehensive report\n"
        "4. 💬 Provide expert feedback"
    )

# Main Input Section
st.subheader("📝 Research Topic")

col1, col2 = st.columns([4, 1])
with col1:
    topic = st.text_input(
        label="Enter your research topic",
        placeholder="e.g., 'Latest advancements in quantum computing in 2024'",
        label_visibility="collapsed",
        key="topic_input"
    )

with col2:
    run_pipeline = st.button(
        "🚀 Start Research",
        use_container_width=True,
        type="primary",
        key="run_btn"
    )

st.divider()

# Pipeline Execution
if run_pipeline and topic:
    
    # Initialize session state for storing results
    if "pipeline_state" not in st.session_state:
        st.session_state.pipeline_state = {}
    
    progress_placeholder = st.empty()
    state = {}
    
    try:
        # Step 1: Search Agent
        with progress_placeholder.container():
            st.info("⏳ Step 1/4: Searching for relevant information...")
            progress_bar = st.progress(0)
        
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        state["search_results"] = search_result['messages'][-1].content
        st.session_state.pipeline_state["search_results"] = state["search_results"]
        
        progress_bar.progress(25)
        time.sleep(0.5)
        
        # Step 2: Reader Agent
        with progress_placeholder.container():
            st.info("⏳ Step 2/4: Scraping top resources for deeper content...")
            progress_bar = st.progress(50)
        
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                         f"Based on the following search results about '{topic}',"
                         f"pick the most relevant URL and scrape it for deeper content.\n\n"
                         f"Search Result:\n{state['search_results'][:800]}")]
        })
        state["scraped_content"] = reader_result['messages'][-1].content
        st.session_state.pipeline_state["scraped_content"] = state["scraped_content"]
        
        progress_bar.progress(50)
        time.sleep(0.5)
        
        # Step 3: Writer Chain
        with progress_placeholder.container():
            st.info("⏳ Step 3/4: Generating comprehensive report...")
            progress_bar = st.progress(75)
        
        research_combined = (
            f"SEARCH RESULTS:\n{state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        )
        
        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        st.session_state.pipeline_state["report"] = state["report"]
        
        progress_bar.progress(75)
        time.sleep(0.5)
        
        # Step 4: Critic Chain
        with progress_placeholder.container():
            st.info("⏳ Step 4/4: Generating expert feedback...")
            progress_bar = st.progress(90)
        
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })
        st.session_state.pipeline_state["feedback"] = state["feedback"]
        
        progress_bar.progress(100)
        time.sleep(0.5)
        progress_placeholder.empty()
        
        # Success Message
        st.markdown('<div class="success-box">✅ Research pipeline completed successfully!</div>', unsafe_allow_html=True)
        
        # Results Tabs
        st.subheader("📊 Results")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Report", "🔍 Search Results", "📄 Scraped Content", "💬 Feedback"])
        
        with tab1:
            st.subheader("Generated Report")
            st.markdown(state["report"])
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Report (TXT)",
                    data=state["report"],
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="📥 Download Report (MD)",
                    data=state["report"],
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        with tab2:
            st.subheader("Search Results")
            st.markdown(state["search_results"])
            st.download_button(
                label="📥 Download Search Results",
                data=state["search_results"],
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with tab3:
            st.subheader("Scraped Content")
            st.markdown(state["scraped_content"])
            st.download_button(
                label="📥 Download Scraped Content",
                data=state["scraped_content"],
                file_name=f"scraped_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with tab4:
            st.subheader("Expert Feedback & Critique")
            st.markdown(state["feedback"])
            st.download_button(
                label="📥 Download Feedback",
                data=state["feedback"],
                file_name=f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        # Summary Section
        st.divider()
        st.subheader("📈 Pipeline Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Topic", topic[:30] + "..." if len(topic) > 30 else topic)
        
        with col2:
            search_lines = state["search_results"].count("\n")
            st.metric("Search Results Lines", search_lines)
        
        with col3:
            content_length = len(state["scraped_content"])
            st.metric("Scraped Content (chars)", f"{content_length:,}")
        
        with col4:
            report_words = len(state["report"].split())
            st.metric("Report Words", report_words)
        
        # Execution Time (simulated)
        st.markdown(
            f"<div class='info-box'>"
            f"✓ Pipeline executed on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"</div>",
            unsafe_allow_html=True
        )
    
    except Exception as e:
        st.markdown(
            f"<div class='warning-box'>"
            f"⚠️ Error: {str(e)}"
            f"</div>",
            unsafe_allow_html=True
        )
        st.error(f"Pipeline encountered an error:\n\n{e}")

elif run_pipeline and not topic:
    st.warning("⚠️ Please enter a research topic to get started.")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("🚀 Powered by LangChain + Streamlit")
with col2:
    st.caption("Made for Team Research")
with col3:
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
