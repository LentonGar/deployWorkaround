# Authentication and access control for the Streamlit app
import streamlit as st
import hmac


def check_password() -> bool:
    """Returns `True` if the user has entered the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(
            st.session_state["password"],
            st.secrets["app_password"]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input(
            "🔐 Enter Password to Access",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.write("*Please contact the developer for access*")
        return False
    
    elif not st.session_state["password_correct"]:
        st.text_input(
            "🔐 Enter Password to Access",
            type="password",
            on_change=password_entered,
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    
    else:
        return True
