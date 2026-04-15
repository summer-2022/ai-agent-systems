import dotenv
dotenv.load_dotenv()

from openai import OpenAI
import asyncio
import streamlit as st
from agents import Agent, Runner, SQLiteSession, WebSearchTool, FileSearchTool

client = OpenAI()

# 네가 이미 만든 Vector Store ID 사용
VECTOR_STORE_ID =   "vs_69e00674834c8191accb94cb44b78f69"



# -----------------------------
# Agent
# -----------------------------
if "agent" not in st.session_state:
    st.session_state["agent"] = Agent(
        name="Life Coach",
        instructions="""
You are a supportive and practical life coach.

Your role:
- Help the user reflect on personal goals, habits, journals, and progress over time.
- Personalize advice using the user's uploaded files first.
- Use web search when current tips, research, or practical recommendations would improve the answer.

Tool usage rules:
1. If the user asks about their goals, habits, routines, progress, past reflections, journals, or personal plans,
   use the File Search Tool first.
2. If the user asks for advice that would benefit from current best practices, recent recommendations, or research,
   also use the Web Search Tool.
3. If both personal context and current advice matter, combine both tools.

How to answer:
- First refer to the user's uploaded goals/journal if relevant.
- Be specific: mention their stated goals or patterns when found.
- Give practical, kind, personalized coaching advice.
- If the files do not contain enough information, say so clearly.
- Do not pretend to know personal facts that are not found in the uploaded files or chat history.

Examples of what you should do:
- "Am I doing well with my exercise goals?" -> search uploaded files first.
- "Give me advice based on my journal and current health tips." -> search files, then web.
- "What habit should I focus on this week?" -> search personal files first, then answer.
""",
        tools=[
            WebSearchTool(),
            FileSearchTool(
                vector_store_ids=[VECTOR_STORE_ID],
                max_num_results=5,
            ),
        ],
    )

agent = st.session_state["agent"]


# -----------------------------
# Session memory
# -----------------------------
if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "life-coach-history",
        "life-coach-memory.db",
    )

session = st.session_state["session"]


# -----------------------------
# Helpers
# -----------------------------
def render_message_content(message):
    """
    Safely render stored assistant/user message content.
    The session message structure may vary slightly, so handle defensively.
    """
    if message.get("role") == "user":
        content = message.get("content", "")
        if isinstance(content, str):
            st.write(content)
        else:
            st.write(str(content))
        return

    if message.get("role") == "assistant":
        if message.get("type") == "message":
            content = message.get("content", [])
            if isinstance(content, list) and len(content) > 0:
                first_item = content[0]
                if isinstance(first_item, dict) and "text" in first_item:
                    st.write(first_item["text"].replace("$", "\\$"))
                    return

        st.write(str(message))


async def paint_history():
    messages = await session.get_items()

    for message in messages:
        if "role" in message:
            with st.chat_message(message["role"]):
                render_message_content(message)

        if "type" in message:
            if message["type"] == "web_search_call":
                with st.chat_message("assistant"):
                    st.write("🔍 Web search used")
            elif message["type"] == "file_search_call":
                with st.chat_message("assistant"):
                    st.write("🗂️ Personal files searched")


asyncio.run(paint_history())


def update_status(status_container, event_type):
    status_messages = {
        "response.web_search_call.completed": ("✅ Web search completed.", "complete"),
        "response.web_search_call.in_progress": ("🔍 Starting web search...", "running"),
        "response.web_search_call.searching": ("🔍 Web search in progress...", "running"),
        "response.file_search_call.completed": ("✅ File search completed.", "complete"),
        "response.file_search_call.in_progress": ("🗂️ Searching your uploaded goals/journal...", "running"),
        "response.file_search_call.searching": ("🗂️ Looking through your files...", "running"),
        "response.completed": ("✅ Done", "complete"),
    }

    if event_type in status_messages:
        label, state = status_messages[event_type]
        status_container.update(label=label, state=state)


async def run_agent(message):
    with st.chat_message("assistant"):
        status_container = st.status("⏳ Thinking...", expanded=False)
        text_placeholder = st.empty()
        response = ""

        try:
            stream = Runner.run_streamed(
                agent,
                message,
                session=session,
            )

            async for event in stream.stream_events():
                if event.type == "raw_response_event":
                    update_status(status_container, event.data.type)

                    if event.data.type == "response.output_text.delta":
                        response += event.data.delta
                        text_placeholder.write(response.replace("$", "\\$"))

        except Exception as e:
            status_container.update(label="❌ Error", state="error")
            st.error(f"Agent run failed: {e}")


# -----------------------------
# UI
# -----------------------------
st.title("💛 Life Coach")
st.caption("Upload your goals or journal files, then ask for personalized coaching.")

prompt = st.chat_input(
    "Ask your life coach anything...",
    accept_file=True,
    file_type=["txt", "pdf"],
)

if prompt:
    # 1) Upload attached files to OpenAI Files + Vector Store
    if hasattr(prompt, "files") and prompt.files:
        for file in prompt.files:
            with st.chat_message("assistant"):
                with st.status(f"⏳ Uploading {file.name}...", expanded=False) as status:
                    try:
                        uploaded_file = client.files.create(
                            file=(file.name, file.getvalue()),
                            purpose="user_data",
                        )

                        status.update(label=f"⏳ Adding {file.name} to vector store...")

                        client.vector_stores.files.create(
                            vector_store_id=VECTOR_STORE_ID,
                            file_id=uploaded_file.id,
                        )

                        status.update(
                            label=f"✅ {file.name} uploaded and ready for search",
                            state="complete",
                        )

                    except Exception as e:
                        status.update(label=f"❌ Upload failed: {file.name}", state="error")
                        st.error(str(e))

    # 2) Run agent on user text
    if prompt.text:
        with st.chat_message("user"):
            st.write(prompt.text)

        asyncio.run(run_agent(prompt.text))


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.subheader("Memory")
    reset = st.button("Reset memory")

    if reset:
        asyncio.run(session.clear_session())
        st.success("Conversation memory cleared.")

    with st.expander("Debug: session items"):
        st.write(asyncio.run(session.get_items()))