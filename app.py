import os
import streamlit as st
from crewai import Agent, Crew, Process, Task

# 1. Grab the key from the environment (Replit used GOOGLE_API_KEY)
api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ API Key is not set. Please check your Replit Secrets tool.")
    st.stop()

# CrewAI's native engine looks specifically for GEMINI_API_KEY,
# so we sync the two variables right here in the code.
os.environ["GEMINI_API_KEY"] = api_key

# 2. Define the model as a simple string.
# This completely bypasses LangChain and avoids the Pydantic type error!
gemini_model = "gemini/gemini-2.0-flash"


def run_agentic_workflow(prd_text):
    # 3. Define the TPM Agents using the native model string
    pm_analyst = Agent(
        role="Product Management Analyst",
        goal="Extract high-level features and write perfect user stories from a PRD.",
        backstory="You are an expert TPM. You take messy feature descriptions and turn them into structured user stories using the standard 'As a... I want to... So that...' format.",
        verbose=True,
        llm=gemini_model,
    )

    tech_lead = Agent(
        role="Technical Lead",
        goal="Break down user stories into granular engineering tasks and identify technical blockers.",
        backstory="You are a seasoned Software Architect. You look at user stories and outline the specific backend, frontend, and database tasks required, flagging dependencies.",
        verbose=True,
        llm=gemini_model,
    )

    tpm_critic = Agent(
        role="TPM Quality Assurance Critic",
        goal="Review the generated tasks to ensure they meet strict acceptance criteria standards.",
        backstory="You are a meticulous Senior Program Manager. If any engineering task lacks clear Acceptance Criteria or formatting, you reject it and demand a rewrite.",
        verbose=True,
        llm=gemini_model,
    )

    # 4. Define Tasks
    task1 = Task(
        description=f"Analyze this PRD text and extract the core User Stories:\n\n{prd_text}",
        expected_output="A list of clearly formatted User Stories.",
        agent=pm_analyst,
    )

    task2 = Task(
        description="Take the User Stories and break them down into technical sub-tasks (API, Database, Frontend) with technical notes.",
        expected_output="Technical implementation breakdown per user story.",
        agent=tech_lead,
    )

    task3 = Task(
        description="Review the output. Ensure every story has clear 'Acceptance Criteria' and is formatted in clean Markdown tables ready for Jira.",
        expected_output="The final polished markdown output containing Epics, Stories, Technical Tasks, and Acceptance Criteria.",
        agent=tpm_critic,
    )

    # 5. Assemble the Crew
    crew = Crew(
        agents=[pm_analyst, tech_lead, tpm_critic],
        tasks=[task1, task2, task3],
        process=Process.sequential,
    )

    return crew.kickoff()


# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Co-TPM Agent", layout="wide")
st.title("🤖 AI Co-TPM: PRD to Jira Ticket Generator")
st.markdown(
    "**Architecture:** Multi-Agent workflow powered by Google Gemini (PM Analyst -> Tech Lead -> TPM Critic loop)."
)
st.markdown("---")

# Preloaded Dummy Data for presentation speed
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

if st.button("Generate Jira Backlog", type="primary"):
    if not prd_input:
        st.warning("Please paste a PRD first.")
    else:
        with st.spinner("Gemini Agents are collaborating... (Running Critic Loops)"):
            try:
                final_output = run_agentic_workflow(prd_input)
                st.success("✅ Backlog Generation Complete!")
                st.markdown("### 📋 Generated Jira Tickets")
                st.markdown(str(final_output))
            except Exception as e:
                st.error(f"Error running agents: {e}")
