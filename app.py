import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(
    page_title="CrewAI + Gemini Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 CrewAI + Gemini Assistant")
st.markdown("Build and run AI agent crews powered by Google Gemini.")

api_key = os.environ.get("GOOGLE_API_KEY", "")
if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is not set. Please add it to your Secrets.")
    st.stop()


@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.7,
    )


with st.sidebar:
    st.header("⚙️ Crew Configuration")

    st.subheader("Agent 1 — Researcher")
    researcher_role = st.text_input("Role", value="Senior Research Analyst")
    researcher_goal = st.text_area(
        "Goal",
        value="Uncover cutting-edge developments and gather comprehensive information on the given topic.",
        height=80,
    )
    researcher_backstory = st.text_area(
        "Backstory",
        value="You are an expert researcher with years of experience finding accurate, relevant information.",
        height=80,
    )

    st.divider()

    st.subheader("Agent 2 — Writer")
    writer_role = st.text_input("Role ", value="Content Strategist")
    writer_goal = st.text_area(
        "Goal ",
        value="Craft compelling, clear, and insightful content based on research findings.",
        height=80,
    )
    writer_backstory = st.text_area(
        "Backstory ",
        value="You are a skilled writer who turns complex research into engaging, well-structured content.",
        height=80,
    )

    st.divider()
    process_type = st.selectbox(
        "Process Type",
        ["Sequential", "Hierarchical"],
        help="Sequential runs agents one after another. Hierarchical uses a manager agent.",
    )

st.subheader("📋 Define Your Task")
topic = st.text_input(
    "Topic / Task",
    placeholder="e.g. The future of AI in healthcare",
)
task_description = st.text_area(
    "Task Description",
    value="Research the topic thoroughly and then produce a well-written summary report.",
    height=100,
)
expected_output = st.text_input(
    "Expected Output",
    value="A detailed, well-structured report with key findings and insights.",
)

run_btn = st.button("🚀 Run Crew", type="primary", disabled=not topic.strip())

if run_btn and topic.strip():
    llm = get_llm()

    researcher = Agent(
        role=researcher_role,
        goal=researcher_goal,
        backstory=researcher_backstory,
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    writer = Agent(
        role=writer_role,
        goal=writer_goal,
        backstory=writer_backstory,
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    research_task = Task(
        description=f"Research the following topic in depth: {topic}\n\n{task_description}",
        expected_output=f"Comprehensive research notes on: {topic}",
        agent=researcher,
    )

    writing_task = Task(
        description=f"Using the research provided, write a polished report on: {topic}",
        expected_output=expected_output,
        agent=writer,
        context=[research_task],
    )

    process = Process.sequential if process_type == "Sequential" else Process.hierarchical

    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, writing_task],
        process=process,
        verbose=False,
    )

    with st.spinner("🔄 Crew is working... this may take a moment."):
        try:
            result = crew.kickoff()
            st.success("✅ Crew finished!")
            st.subheader("📄 Result")
            st.markdown(str(result))
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

elif not topic.strip() and run_btn:
    st.warning("Please enter a topic before running the crew.")
