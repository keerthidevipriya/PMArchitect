import os
import streamlit as st
import google.generativeai as genai

# 1. Authenticate using the key saved in Replit Secrets
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is not set. Please check your Replit Secrets tool.")
    st.stop()

genai.configure(api_key=api_key)


# 2. Multi-Agent Emulation Workflow (Single-request architecture)
def run_agentic_workflow(prd_text):
    # We instruct the premier 2.0-flash model to run the multi-agent chain internally
    prompt = f"""
    You are an elite AI Technical Program Management Crew consisting of three distinct agents. 
    You must process the following Product Requirement Document (PRD) sequentially and output the collaboration logs along with the final Jira tickets.

    PRD TEXT:
    {prd_text}

    ----------------------------------------------------------------------
    STEP 1: [Product Management Analyst]
    Goal: Extract high-level features and write perfect user stories using the 'As a... I want to... So that...' format.

    STEP 2: [Technical Lead]
    Goal: Take the user stories from Step 1 and break them down into granular engineering tasks (Frontend, Backend, Database) and note any technical blockers.

    STEP 3: [TPM Quality Assurance Critic]
    Goal: Review the output of Step 1 and Step 2. Format everything into neat, clean Markdown tables ready to copy-paste straight into Jira, ensuring explicit 'Acceptance Criteria' are defined for every ticket.
    ----------------------------------------------------------------------

    Provide your response in two clear sections:
    1. 🤝 **Agent Collaboration Logs**: A brief summary of what each agent contributed during the process loop.
    2. 📋 **Final Jira Backlog**: The polished markdown tables with Epics, Stories, Technical Tasks, and Acceptance Criteria.
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Co-TPM Agent", layout="wide")
st.title("🤖 AI Co-TPM: PRD to Jira Ticket Generator")
st.markdown(
    "**Architecture:** Multi-Agent Pipeline (PM Analyst ➔ Tech Lead ➔ TPM Critic) optimized for Free-Tier performance."
)
st.markdown("---")

# Preloaded Dummy Data
dummy_prd = """
# PRD: User Authentication Upgrade
We need to add Multi-Factor Authentication (MFA) to our user login flow.
Users should be able to opt-in via their settings page. We will support TOTP (Google Authenticator).
If a user has MFA enabled, intercept the login route to require the 6-digit token before issuing a JWT.
"""

if st.button("✨ Load Demo Dummy PRD"):
    st.session_state["prd_input"] = dummy_prd.strip()

prd_input = st.text_area(
    "Paste Product Requirement Document (PRD) here:",
    value=st.session_state.get("prd_input", ""),
    height=250,
)

if st.button("🚀 Generate Jira Backlog", type="primary"):
    if not prd_input:
        st.warning("Please paste a PRD first.")
    else:
        with st.spinner("🤖 TPM Crew is collaborating on your backlog..."):
            try:
                final_output = run_agentic_workflow(prd_input)
                st.success("✅ Backlog Generation Complete!")
                st.markdown(final_output)
            except Exception as e:
                st.error(f"Error running agents: {e}")
