import streamlit as st
from app.interviewer import answer_turn, InterviewerFactory
from app.auth import check_password
from app.security import validate_input, wrap_user_input
from app.cost_tracker import count_tokens, calculate_cost, format_cost

# ==================== PASSWORD PROTECTION ====================
if not check_password():
    st.stop()

# ==================== STREAMLIT CONFIG ====================
st.set_page_config(
    page_title="Interview Application",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("🤖 Interview Practice bot")

# ==================== INITIALIZE SESSION STATE ====================
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0
if "total_input_tokens" not in st.session_state:
    st.session_state.total_input_tokens = 0
if "total_output_tokens" not in st.session_state:
    st.session_state.total_output_tokens = 0
if "session_messages" not in st.session_state:
    st.session_state.session_messages = 0

if "interviewer_settings" not in st.session_state:
    st.session_state.interviewer_settings = {
        "job_role": "",
        "skills": "",
        "difficulty": "Medium",
        "technique": "Zero-shot"
    }

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I am your interviewer. Ready to go?"}
    ]

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Setup for the interview bot")

    job_role = st.text_input(
        "Job role (e.g., 'Python Backend Engineer at Google')",
        value=st.session_state.interviewer_settings["job_role"]
    )
    skills = st.text_input(
        "Skills to focus on (e.g., 'Django, REST, SQL')",
        value=st.session_state.interviewer_settings["skills"]
    )
    difficulty = st.selectbox(
        "Difficulty level",
        ["Easy", "Medium", "Hard"],
        index=["Easy", "Medium", "Hard"].index(
            st.session_state.interviewer_settings["difficulty"]
        )
    )

    prompt_technique = st.selectbox(
        "Prompt Technique",
        ["Zero-shot", "Few-shot", "Chain-of-Thought", "Dynamic", "Least-to-Most"],
        index=["Zero-shot", "Few-shot", "Chain-of-Thought", "Dynamic", "Least-to-Most"].index(
            st.session_state.interviewer_settings["technique"]
        )
    )

    st.divider()
    st.subheader("AI Model Settings")
    temperature = st.slider(
        "Temperature (Creativity of responses)",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative/varied"
    )

    # Settings change detection
    current_settings = {
        "job_role": job_role,
        "skills": skills,
        "difficulty": difficulty,
        "technique": prompt_technique
    }
    
    if current_settings != st.session_state.interviewer_settings:
        st.warning("⚠️ Settings changed! Click 'Reset Interview' to apply.")
        if st.button("🔄 Reset Interview"):
            st.session_state.interviewer_settings = current_settings
            InterviewerFactory.reset(st.session_state, "interviewer")
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi, I am your interviewer. Ready to go?"}
            ]
            st.rerun()

    # Cost tracking display
    st.divider()
    st.subheader("💰 Cost Tracking")

    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Total Cost",
            format_cost(st.session_state.total_cost),
            help="Estimated API cost for this session"
        )
    
    with col2:
        st.metric(
            "Messages",
            st.session_state.session_messages,
            help="Number of messages sent"
        )
    
    with st.expander("📊 Token Details"):
        st.write(f"**Input tokens:** {st.session_state.total_input_tokens:,}")
        st.write(f"**Output tokens:** {st.session_state.total_output_tokens:,}")
        st.write(f"**Total tokens:** {st.session_state.total_input_tokens + st.session_state.total_output_tokens:,}")
        
        st.divider()
        model = "gpt-4o-mini"
        st.caption(f"**Pricing ({model}):**")
        st.caption("• Input: $0.150/1M tokens")
        st.caption("• Output: $0.600/1M tokens")
    
    if st.button("🔄 Reset Usage Stats"):
        st.session_state.total_cost = 0.0
        st.session_state.total_input_tokens = 0
        st.session_state.total_output_tokens = 0
        st.session_state.session_messages = 0
        st.success("Usage stats reset!")
        st.rerun()

# ==================== CHAT INTERFACE ====================
# Render chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Type your message here...")

if prompt:
    # Validate input
    is_valid, error_msg = validate_input(prompt)
    if not is_valid:
        st.error(f"Input validation error: {error_msg}")
        st.stop()

    # Wrap for security
    wrapped_prompt = wrap_user_input(prompt)
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Count input tokens
    input_tokens = count_tokens(wrapped_prompt, model="gpt-4o-mini")
    
    # Get AI response
    bot_reply = answer_turn(
        storage=st.session_state,
        user_message=wrapped_prompt,
        job_role=job_role,
        skills=skills,
        difficulty=difficulty,
        technique=prompt_technique,
        temperature=temperature
    )

    # Calculate output tokens and cost
    output_tokens = count_tokens(bot_reply, model="gpt-4o-mini")
    turn_cost = calculate_cost(input_tokens, output_tokens, model="gpt-4o-mini")
    
    # Update tracking
    st.session_state.total_input_tokens += input_tokens
    st.session_state.total_output_tokens += output_tokens
    st.session_state.total_cost += turn_cost
    st.session_state.session_messages += 1

    # Display AI response
    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)
