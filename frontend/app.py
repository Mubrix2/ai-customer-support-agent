# frontend/app.py
import streamlit as st
from api_client import check_health, create_session, send_message

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechMart Support",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state initialisation ──────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "conversation_started" not in st.session_state:
    st.session_state.conversation_started = False


# ── Helper: start a new session ───────────────────────────────────────────────
def start_new_conversation():
    """Reset all conversation state and get a fresh session ID."""
    result = create_session()
    if result["success"]:
        st.session_state.session_id = result["data"]["session_id"]
        st.session_state.chat_history = []
        st.session_state.conversation_started = True
    else:
        st.error(f"Failed to start session: {result['error']}")


# ── Tool name formatter ───────────────────────────────────────────────────────
TOOL_LABELS = {
    "check_order_status": "🔍 Checked order status",
    "get_orders_by_email": "📧 Retrieved orders by email",
    "log_complaint": "📝 Logged complaint",
    "get_business_info": "ℹ️ Retrieved business info",
    "escalate_to_human": "🚨 Escalated to human agent",
}


def format_tool(tool_name: str) -> str:
    return TOOL_LABELS.get(tool_name, f"🔧 Used tool: {tool_name}")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🛍️ TechMart Support")
    st.caption("AI-powered customer support agent")

    st.divider()

    # API health
    is_healthy = check_health()
    if is_healthy:
        st.success("API connected", icon="🟢")
    else:
        st.error("API unreachable", icon="🔴")
        st.caption("Start the FastAPI server: `uvicorn app.main:app --reload`")

    st.divider()

    # Session control
    st.subheader("Conversation")

    if st.session_state.session_id:
        st.caption(f"Session: `{st.session_state.session_id[:16]}...`")
    else:
        st.caption("No active session")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "New Chat",
            use_container_width=True,
            type="primary",
            disabled=not is_healthy,
        ):
            start_new_conversation()
            st.rerun()
    with col2:
        if st.button(
            "Clear",
            use_container_width=True,
            disabled=len(st.session_state.chat_history) == 0,
        ):
            st.session_state.chat_history = []
            st.session_state.session_id = None
            st.session_state.conversation_started = False
            st.rerun()

    st.divider()

    # Quick test prompts
    st.subheader("Try these")
    st.caption("Click any prompt to send it instantly")

    quick_prompts = [
        "What is the status of order ORD-002?",
        "Show me orders for amina.bello@email.com",
        "I want to file a complaint about my delivery",
        "What is your return policy?",
        "I need to speak to a human agent",
        "What are your business hours?",
    ]

    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True, key=f"quick_{prompt[:20]}"):
            if not st.session_state.session_id:
                start_new_conversation()

            # Add to history immediately
            st.session_state.chat_history.append({
                "role": "user",
                "content": prompt,
                "tools_used": [],
            })

            with st.spinner("Aria is thinking..."):
                result = send_message(
                    message=prompt,
                    session_id=st.session_state.session_id,
                )

            if result["success"]:
                data = result["data"]
                st.session_state.session_id = data["session_id"]
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": data["response"],
                    "tools_used": data.get("tools_used", []),
                })
            else:
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": f"❌ {result['error']}",
                    "tools_used": [],
                })
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────
st.title("TechMart Nigeria — Customer Support")
st.caption(
    "Ask about your orders, file complaints, or get help with our products and policies. "
    "Powered by Aria, your AI support agent."
)

if not is_healthy:
    st.warning(
        "⚠️ The backend API is not reachable. Start your FastAPI server to begin.",
        icon="⚠️",
    )

st.divider()

# ── Welcome message ───────────────────────────────────────────────────────────
if not st.session_state.conversation_started:
    st.markdown(
        """
        <div style="text-align: center; padding: 40px 20px; color: #888;">
            <h3>👋 Welcome to TechMart Support</h3>
            <p>Click <strong>New Chat</strong> in the sidebar to start a conversation,<br>
            or try one of the quick prompts on the left.</p>
            <br>
            <p style="font-size: 0.85em;">
                You can ask about order status, returns, complaints,<br>
                business hours, and more.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Chat history ──────────────────────────────────────────────────────────────
for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
        st.markdown(message["content"])

        # Show tool activity for assistant messages
        if message["role"] == "assistant" and message.get("tools_used"):
            tool_labels = [format_tool(t) for t in message["tools_used"]]
            with st.expander(f"⚡ Actions taken ({len(tool_labels)})", expanded=False):
                for label in tool_labels:
                    st.caption(label)

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input(
    "Type your message here...",
    disabled=not is_healthy,
):
    # Start session if not started
    if not st.session_state.session_id:
        start_new_conversation()

    # Show user message immediately
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt,
        "tools_used": [],
    })

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Aria is thinking..."):
            result = send_message(
                message=prompt,
                session_id=st.session_state.session_id,
            )

        if result["success"]:
            data = result["data"]
            st.session_state.session_id = data["session_id"]
            response_text = data["response"]
            tools_used = data.get("tools_used", [])

            st.markdown(response_text)

            if tools_used:
                tool_labels = [format_tool(t) for t in tools_used]
                with st.expander(f"⚡ Actions taken ({len(tool_labels)})", expanded=True):
                    for label in tool_labels:
                        st.caption(label)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response_text,
                "tools_used": tools_used,
            })

        else:
            error_msg = f"❌ {result['error']}"
            st.error(error_msg)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": error_msg,
                "tools_used": [],
            })