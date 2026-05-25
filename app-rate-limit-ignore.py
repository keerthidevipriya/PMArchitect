import os
import time
import streamlit as st
from crewai import Agent, Crew, Process, Task

api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is not set. Please check your Replit Secrets.")
    st.stop()

os.environ["GEMINI_API_KEY"] = api_key

# gemini-2.0-flash-lite: best free-tier limits (30 RPM, 1500 RPD)
GEMINI_MODEL = "gemini/gemini-2.0-flash-lite"


def run_with_retry(crew, max_retries=5):
    for attempt in range(max_retries):
        try:
            return crew.kickoff()
        except Exception as e:
            msg = str(e)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                wait = 30 * (attempt + 1)
                st.warning(f"⏳ Rate limit hit — waiting {wait}s before retry {attempt + 1}/{max_retries}…")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded. Please wait a minute and try again.")


def run_agentic_workflow(prd_text):
    pm_analyst = Agent(
        role="Product Management Analyst",
        goal="Extract high-level features and write perfect user stories from a PRD.",
        backstory=(
            "You are an expert TPM. You take messy feature descriptions and turn them "
            "into structured user stories using the standard 'As a... I want to... So that...' format."
        ),
        verbose=False,
        llm=GEMINI_MODEL,
    )

    tech_lead = Agent(
        role="Technical Lead",
        goal="Break down user stories into granular engineering tasks and identify technical blockers.",
        backstory=(
            "You are a seasoned Software Architect. You look at user stories and outline the specific "
            "backend, frontend, and database tasks required, flagging dependencies."
        ),
        verbose=False,
        llm=GEMINI_MODEL,
    )

    tpm_critic = Agent(
        role="TPM Quality Assurance Critic",
        goal="Review the generated tasks to ensure they meet strict acceptance criteria standards.",
        backstory=(
            "You are a meticulous Senior Program Manager. If any engineering task lacks clear "
            "Acceptance Criteria or formatting, you reject it and demand a rewrite."
        ),
        verbose=False,
        llm=GEMINI_MODEL,
    )

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
        description=(
            "Review the output. Ensure every story has clear 'Acceptance Criteria' "
            "and is formatted in clean Markdown tables ready for Jira."
        ),
        expected_output="Final polished markdown output with Epics, Stories, Technical Tasks, and Acceptance Criteria.",
        agent=tpm_critic,
    )

    crew = Crew(
        agents=[pm_analyst, tech_lead, tpm_critic],
        tasks=[task1, task2, task3],
        process=Process.sequential,
    )

    return run_with_retry(crew)


# --- Streamlit UI ---
st.set_page_config(page_title="AI Co-TPM Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI Co-TPM: PRD to Jira Ticket Generator")
st.markdown(
    "Multi-agent workflow powered by **Google Gemini** (PM Analyst → Tech Lead → TPM Critic)."
)
st.info(
    "ℹ️ Using **gemini-2.0-flash-lite** (free tier: 30 req/min). "
    "If rate-limited, the app will automatically retry with a short wait.",
    icon="💡",
)
st.divider()

dummy_prd = """
# PRD: User Authentication Upgrade
We need to add Multi-Factor Authentication (MFA) to our user login flow.
Users should be able to opt-in via their settings page. We will support TOTP (Google Authenticator).
If a user has MFA enabled, intercept the login route to require the 6-digit token before issuing a JWT.
""".strip()

if st.button("✨ Load Demo PRD"):
    st.session_state["prd_input"] = dummy_prd

prd_input = st.text_area(
    "Paste your Product Requirement Document (PRD) here:",
    value=st.session_state.get("prd_input", ""),
    height=250,
    placeholder="Describe the feature or product requirement…",
)

if st.button("🚀 Generate Jira Backlog", type="primary"):
    if not prd_input.strip():
        st.warning("Please paste a PRD first.")
    else:
        with st.spinner("Agents are collaborating… (this may take 30–60 seconds on the free tier)"):
            try:
                result = run_agentic_workflow(prd_input.strip())
                st.success("✅ Backlog generation complete!")
                st.subheader("📋 Generated Jira Tickets")
                st.markdown(str(result))
            except Exception as e:
                st.error(f"❌ Error: {e}")
                st.info("If you see a quota error, wait 1 minute and try again — free tier resets every minute.")
