
import streamlit as st
from app.interviewer import answer_turn, InterviewerFactory
import uuid

import hmac

# Access to interviewer app (low level security but better than nothing)

def check_password():
    """Returns `True` if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(
            st.session_state["password"],
            st.secrets["app_password"]  # Store password in secrets!
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password in session
        else:
            st.session_state["password_correct"] = False

    # First run or password not correct
    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "🔐 Enter Password to Access",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.write("*Please contact the developer for access*")
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "🔐 Enter Password to Access",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    
    else:
        # Password correct
        return True

# Check password before showing app
if not check_password():
    st.stop()  # Don't continue if password is wrong


# Security validation

def validate_input(text: str) -> tuple[bool, str]:
    '''
    Prevents prompt injection and abuse
    Returns (is_valid, error_message)
    '''
    # Preventing token abuse
    MAX_LENGTH = 1200
    if len(text) > MAX_LENGTH:
        return (False, f"Input too long! Max {MAX_LENGTH} characters. You used {len(text)}.")
    
    # Preventing prompt injection
    forbidden_phrases = [
        "ignore previous instructions","disregard all prior messages",
        "you are no longer","forget you are",
        "bypass your restrictions","break your programming",
        "act as a different AI","malicious","harmful",
        "illegal","unethical","pretend to be","jailbreak",
        "pretend","imagine","disregard","bypass",
        "override","disable","break","you are now",
        "you are","forget"
    ]

    text_lower = text.lower()
    for phrase in forbidden_phrases:
        if phrase in text_lower:
            return (False, "Input contains forbidden phrases. Please revise your input.")
        
    return True, ""

def wrap_user_input(user_text: str) -> str:
    """
    Wraps user input with unique identifiers to prevent prompt injection.
    AI treats anything in boundaries as NOT instructions to itself.
    """ 
    boundary = str(uuid.uuid4())
    return f"""<USER_INPUT id="{boundary}">
{user_text}
</USER_INPUT>"""

st.set_page_config(
    page_title="Interview Application",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("🤖 Interview Practice bot")

# Initialize settings tracking
if "interviewer_settings" not in st.session_state:
    st.session_state.interviewer_settings = {
        "job_role": "",
        "skills": "",
        "difficulty": "Medium",
        "technique": "Zero-shot"
    }

with st.sidebar:
    st.header("Setup for the interview bot")

    job_role = st.text_input(
        "Job role (e.g., 'Python Backend Engineer at Google')",
        value=st.session_state.interviewer_settings["job_role"])
    skills = st.text_input("Skills to focus on (e.g., 'Django, REST, SQL')",
                           value=st.session_state.interviewer_settings["skills"])
    difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard"],
                              index=["Easy", "Medium", "Hard"].index(
                                 st.session_state.interviewer_settings["difficulty"]))

    prompt_technique = st.selectbox(
        "Prompt Technique",
        ["Zero-shot", "Few-shot", "Chain-of-Thought", "Role-Play"],
        index=["Zero-shot", "Few-shot", "Chain-of-Thought", "Role-Play"].index(
            st.session_state.interviewer_settings["technique"])
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
            # Update settings
            st.session_state.interviewer_settings = current_settings
            
            # Use factory to reset
            InterviewerFactory.reset(st.session_state, "interviewer")
            
            # Reset UI messages
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi, I am your interviewer. Ready to go?"}
            ]
            st.rerun()
#Initialise chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi, I am your interviewer. Ready to go?"}
    ]

# Render chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input for user
prompt = st.chat_input("Type your message here...")

if prompt:
    # Add user message to chat history
    is_valid, error_msg = validate_input(prompt)

    if not is_valid:
        st.error(f"Input validation error: {error_msg}")
        st.stop()

    wrapped_prompt = wrap_user_input(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
 # Use factory-based answer_turn
    bot_reply = answer_turn(
        storage=st.session_state,  # Pass session state as storage
        user_message=wrapped_prompt,
        job_role=st.session_state.interviewer_settings["job_role"],
        skills=st.session_state.interviewer_settings["skills"],
        difficulty=st.session_state.interviewer_settings["difficulty"],
        technique=st.session_state.interviewer_settings["technique"],
        temperature=temperature
    )

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.markdown(bot_reply)    
