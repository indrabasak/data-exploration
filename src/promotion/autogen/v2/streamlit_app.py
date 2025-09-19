import streamlit as st
import asyncio
import time
from datetime import datetime

from analyzer import team

# Avatar URL for assistant messages
avatar_url = "https://cdn-icons-png.flaticon.com/512/4712/4712027.png"

# Page configuration
st.set_page_config(
    page_title="EDH Promotion Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern chat interface
st.markdown(
    """
<style>
    /* Main app styling */
    .main {
        background-color: #f8f9fa;
        color: #333333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: white;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Chat message styling - Fix text visibility */
    .stChatMessage {
        background-color: white !important;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: #333333 !important;
    }
    
    /* Chat message content styling */
    .stChatMessage [data-testid="stMarkdownContainer"] {
        color: #333333 !important;
    }
    
    .stChatMessage p {
        color: #333333 !important;
    }
    
    .stChatMessage div {
        color: #333333 !important;
    }
    
    /* User message styling */
    [data-testid="user-message"] {
        background-color: #e3f2fd !important;
        color: #1565c0 !important;
    }
    
    [data-testid="user-message"] p {
        color: #1565c0 !important;
    }
    
    /* Assistant message styling */
    [data-testid="assistant-message"] {
        background-color: #f5f5f5 !important;
        color: #333333 !important;
    }
    
    [data-testid="assistant-message"] p {
        color: #333333 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: white;
        color: #333333 !important;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 14px;
        width: 100%;
        text-align: left;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #f0f2f6;
        border-color: #007bff;
        color: #007bff !important;
        transform: translateY(-1px);
    }
    
    /* Suggested questions styling */
    .suggested-question {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 0.25rem 0;
        cursor: pointer;
        transition: all 0.2s;
        color: #333333;
    }
    
    .suggested-question:hover {
        background-color: #f0f2f6;
        border-color: #007bff;
        transform: translateY(-1px);
    }
    
    /* Agent logs styling - Fix text visibility */
    .agent-log {
        background-color: #f8f9fa !important;
        border-left: 4px solid #007bff;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 4px;
        font-size: 0.9rem;
        color: #333333 !important;
    }
    
    .agent-log strong {
        color: #007bff !important;
    }
    
    .agent-log span {
        color: #555555 !important;
    }
    
    /* Loading spinner */
    .loading {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #666;
        font-style: italic;
    }
    
    /* Title styling */
    .main-title {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    
    /* Reset button styling */
    .reset-button {
        background-color: #dc3545 !important;
        color: white !important;
        border: none !important;
    }
    
    .reset-button:hover {
        background-color: #c82333 !important;
    }
    
    /* Sidebar text styling */
    .css-1d391kg p, .css-1d391kg div {
        color: #333333 !important;
    }
    
    /* Caption styling */
    .stCaption {
        color: #666666 !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        color: #333333 !important;
    }
    
    /* Text input styling */
    .stTextInput input {
        color: #333333 !important;
        background-color: white !important;
    }
    
    /* Chat input styling */
    .stChatInput input {
        color: #333333 !important;
        background-color: white !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Example questions
EXAMPLE_QUESTIONS = [
    "How many promotions resulted in sales?",
    "Which country-specific promotions had the greatest impact?",
    "Which financial quarters are the best times for promotions in different countries?",
    "Which types of offerings were most influenced by promotions?",
    "What new promotions can be suggested for different countries in the next three months based on historical data?",
]


def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_logs" not in st.session_state:
        st.session_state.agent_logs = []
    if "my_question" not in st.session_state:
        st.session_state.my_question = None
    if "show_suggested" not in st.session_state:
        st.session_state.show_suggested = True
    if "team" not in st.session_state:
        st.session_state.team = team


def set_question(question):
    """Set the selected question"""
    st.session_state.my_question = question
    st.session_state.show_suggested = False


def format_timestamp():
    """Format current timestamp"""
    return datetime.now().strftime("%H:%M:%S")


async def process_question_async(question: str, team):
    """Process question through agent team asynchronously"""
    try:
        # Process through agent team
        all_messages = []
        final_message = ""
        agent_logs = []

        # Add initial log
        agent_logs.append(
            {
                "agent": "System",
                "message": f"User question: {question}",
                "timestamp": format_timestamp(),
            }
        )

        async for message in team.run_stream(task=question):
            # Extract just the content, not the whole message object
            if hasattr(message, "content"):
                message_content = str(message.content).strip()
            else:
                # Skip non-content messages (like system messages)
                continue

            sender = getattr(message, "source", "Unknown")

            # Add ALL messages to agent logs (no duplicate filtering for logs)
            agent_logs.append(
                {
                    "agent": sender,
                    "message": message_content,
                    "timestamp": format_timestamp(),
                }
            )

            all_messages.append((sender, message_content))

            # Always keep the very last message with content as the final message
            if message_content and len(message_content.strip()) > 5:
                # Clean up the message (remove TERMINATE if present)
                cleaned_message = message_content.replace("TERMINATE", "").strip()
                if cleaned_message:
                    final_message = cleaned_message

        # Return results instead of modifying session state directly
        return {
            "success": True,
            "final_message": final_message
                             or "Task completed. Please check the agent logs for detailed information.",
            "agent_logs": agent_logs,
        }

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        return {
            "success": False,
            "final_message": error_msg,
            "agent_logs": [
                {
                    "agent": "System",
                    "message": f"Error: {str(e)}",
                    "timestamp": format_timestamp(),
                }
            ],
        }


def process_question_sync(question: str):
    """Synchronous wrapper for processing questions"""
    import concurrent.futures
    import threading

    # Get the team from session state before running in separate thread
    team = st.session_state.team

    def run_async():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(process_question_async(question, team))
        finally:
            loop.close()

    # Run the async function in a separate thread with its own event loop
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_async)
        result = future.result()

    # Update session state with the results
    if result:
        # Add user message to chat
        st.session_state.messages.append(
            {"role": "user", "content": question, "timestamp": format_timestamp()}
        )

        # Add assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result["final_message"],
                "timestamp": format_timestamp(),
            }
        )

        # Add agent logs
        st.session_state.agent_logs.extend(result["agent_logs"])

        return result["success"]

    return False


def display_agent_logs_sidebar():
    """Display agent logs in sidebar"""
    st.sidebar.markdown("### 🔍 Agent Logs")

    if st.session_state.agent_logs:
        # Show last 10 logs in sidebar
        recent_logs = st.session_state.agent_logs[-10:]

        for log in recent_logs:
            with st.sidebar.container():
                st.markdown(
                    f"""
                    <div class="agent-log">
                        <strong>{log['agent']}</strong> <small>({log['timestamp']})</small><br>
                        <span style="font-size: 0.85rem;">{log['message'][:100]}{'...' if len(log['message']) > 100 else ''}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # Button to view all logs
        if st.sidebar.button("📋 View All Logs", use_container_width=True):
            st.session_state.show_all_logs = True
    else:
        st.sidebar.info(
            "No agent logs yet. Ask a question to see the conversation flow!"
        )


def main():
    """Main Streamlit application"""
    # Initialize session state
    initialize_session_state()

    # Sidebar configuration
    st.sidebar.title("⚙️ Settings")

    # Output settings (keeping the reference structure)
    st.sidebar.markdown("### Output Display")
    show_timestamps = st.sidebar.checkbox(
        "Show Timestamps", value=True, key="show_timestamps"
    )
    show_agent_details = st.sidebar.checkbox(
        "Show Agent Details", value=True, key="show_agent_details"
    )

    # Reset button
    if st.sidebar.button("🔄 Reset Chat", key="reset_chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_logs = []
        st.session_state.my_question = None
        st.session_state.show_suggested = True
        st.rerun()

    st.sidebar.divider()

    # Display agent logs in sidebar
    display_agent_logs_sidebar()

    # Main content area
    st.markdown(
        '<h1 class="main-title">📊 EDH Promotion Analysis AI</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Ask intelligent questions about promotion effectiveness and sales data**"
    )

    # Suggested questions section (similar to Vanna AI)
    if st.session_state.show_suggested and not st.session_state.messages:
        assistant_message_suggested = st.chat_message("assistant", avatar=avatar_url)

        if assistant_message_suggested.button(
                "💡 Click to show suggested questions", use_container_width=True
        ):
            st.session_state.show_suggested = True

            # Display suggested questions as buttons
            st.markdown("### 💭 Try these example questions:")

            # Create columns for better layout
            cols = st.columns(2)
            for i, question in enumerate(EXAMPLE_QUESTIONS):
                with cols[i % 2]:
                    if st.button(
                            question,
                            key=f"suggested_{i}",
                            on_click=set_question,
                            args=(question,),
                            use_container_width=True,
                    ):
                        time.sleep(0.1)  # Small delay for better UX

    # Display chat messages
    for message in st.session_state.messages:
        avatar = avatar_url if message["role"] == "assistant" else None

        with st.chat_message(message["role"], avatar=avatar):
            st.write(message["content"])
            if st.session_state.get("show_timestamps", True):
                st.caption(f"🕒 {message['timestamp']}")

    # Handle question input
    my_question = st.session_state.get("my_question", None)

    if my_question is None:
        my_question = st.chat_input("Ask me a question about your promotion data...")

    # Process the question
    if my_question:
        st.session_state.my_question = my_question

        # Process the question
        with st.spinner("🤖 Analyzing your question and generating insights..."):
            success = process_question_sync(my_question)

        # Clear the question and refresh
        st.session_state.my_question = None
        if success:
            st.rerun()

    # Show all logs modal (if requested)
    if st.session_state.get("show_all_logs", False):
        with st.expander("📋 Complete Agent Logs", expanded=True):
            if st.session_state.agent_logs:
                for log in st.session_state.agent_logs:
                    with st.container():
                        col1, col2 = st.columns([1, 4])
                        with col1:
                            st.markdown(f"**{log['agent']}**")
                            st.caption(log["timestamp"])
                        with col2:
                            st.text(log["message"])
                        st.divider()

            if st.button("❌ Close Logs"):
                st.session_state.show_all_logs = False
                st.rerun()


if __name__ == "__main__":
    main()