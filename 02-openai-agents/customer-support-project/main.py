import dotenv
dotenv.load_dotenv()

import asyncio
import streamlit as st
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)
from models import UserAccountContext
from my_agents.triage_agent import triage_agent


user_account_ctx = UserAccountContext(
    customer_id=1,
    name="summer",
    tier="basic",
)

st.set_page_config(page_title="Restaurant Bot", page_icon="🍽️")

st.title("🍽️ Restaurant Bot")
st.caption("Ask about menus, reservations, orders, or complaints.")


if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "restaurant-chat-history",
        "restaurant-memory.db",
    )

if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent

if "messages" not in st.session_state:
    st.session_state["messages"] = []


session = st.session_state["session"]


for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])


async def run_agent(user_input: str):
    try:
        result = await Runner.run(
            st.session_state["agent"],
            user_input,
            session=session,
            context=user_account_ctx,
        )

        responding_agent_name = result.last_agent.name
        st.session_state["agent"] = triage_agent
        return result.final_output, responding_agent_name

    except InputGuardrailTripwireTriggered:
        return (
            "저는 레스토랑 관련 질문에 대해서만 도와드리고 있어요. "
            "메뉴 확인, 예약, 주문, 불만 접수를 도와드릴 수 있습니다.",
            "Input Guardrail",
        )

    except OutputGuardrailTripwireTriggered:
        return (
            "죄송합니다. 해당 응답은 안전 기준에 맞지 않아 표시할 수 없습니다.",
            "Output Guardrail",
        )


user_input = st.chat_input("메뉴, 예약, 주문, 불만 사항을 입력하세요...")

if user_input:
    st.session_state["messages"].append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, agent_name = asyncio.run(run_agent(user_input))

        st.caption(f"Responding agent: {agent_name}")
        st.write(response)

    st.session_state["messages"].append(
        {"role": "assistant", "content": response}
    )


with st.sidebar:
    st.header("Session")
    st.write(f"Current agent: `{st.session_state['agent'].name}`")

    if st.button("Reset memory"):
        asyncio.run(session.clear_session())
        st.session_state["agent"] = triage_agent
        st.session_state["messages"] = []
        st.rerun()

    with st.expander("Memory items"):
        st.write(asyncio.run(session.get_items()))


# import dotenv

# dotenv.load_dotenv()
# from openai import OpenAI
# import asyncio
# import streamlit as st
# from agents import (
#     Runner,
#     SQLiteSession,
#     InputGuardrailTripwireTriggered,
#     OutputGuardrailTripwireTriggered,
# )
# from agents.voice import AudioInput, VoicePipeline
# from models import UserAccountContext
# from my_agents.triage_agent import triage_agent
# import numpy as np
# import wave, io
# from workflow import CustomWorkflow
# import sounddevice as sd

# client = OpenAI()

# user_account_ctx = UserAccountContext(
#     customer_id=1,
#     name="summer",
#     tier="basic",
# )


# if "session" not in st.session_state:
#     st.session_state["session"] = SQLiteSession(
#         "chat-history",
#         "customer-support-memory.db",
#     )
# session = st.session_state["session"]

# if "agent" not in st.session_state:
#     st.session_state["agent"] = triage_agent


# def convert_audio(audio_input):

#     audio_data = audio_input.getvalue()

#     with wave.open(io.BytesIO(audio_data), "rb") as wav_file:
#         audio_frames = wav_file.readframes(-1)

#     return np.frombuffer(
#         audio_frames,
#         dtype=np.int16,
#     )


# async def run_agent(audio_input):

#     with st.chat_message("ai"):
#         status_container = st.status("⏳ Processing voice message...")
#         try:

#             audio_array = convert_audio(audio_input)

#             audio = AudioInput(buffer=audio_array)

#             workflow = CustomWorkflow(context=user_account_ctx)

#             pipeline = VoicePipeline(workflow=workflow)

#             status_container.update(label="Running workflow", state="running")

#             result = await pipeline.run(audio)

#             player = sd.OutputStream(
#                 samplerate=24000,
#                 channels=1,
#                 dtype=np.int16,
#             )
#             player.start()

#             status_container.update(state="complete")

#             async for event in result.stream():
#                 if event.type == "voice_stream_event_audio":
#                     player.write(event.data)

#         except InputGuardrailTripwireTriggered:
#             st.write("I can't help you with that.")

#         except OutputGuardrailTripwireTriggered:
#             st.write("Cant show you that answer.")


# audio_input = st.audio_input(
#     "Record your message",
# )

# if audio_input:

#     with st.chat_message("human"):
#         st.audio(audio_input)
#     asyncio.run(run_agent(audio_input))


# with st.sidebar:
#     reset = st.button("Reset memory")
#     if reset:
#         asyncio.run(session.clear_session())
#     st.write(asyncio.run(session.get_items()))
