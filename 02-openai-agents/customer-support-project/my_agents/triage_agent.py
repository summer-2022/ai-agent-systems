import streamlit as st
from agents import (
    Agent,
    RunContextWrapper,
    input_guardrail,
    Runner,
    GuardrailFunctionOutput,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agents.extensions import handoff_filters
from models import UserAccountContext, InputGuardRailOutput, HandoffData

from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent
from my_agents.complaints_agent import complaints_agent


input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
        Ensure the user's request is related to a restaurant.

        Allow:
        - menu
        - reservation
        - order
        - complaints

        Reject:
        - off-topic questions (e.g., philosophy, life meaning)
        - inappropriate language

        Return reason if rejected.
        """,
    output_type=InputGuardRailOutput,
)


@input_guardrail
async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str,
):
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )

    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )

def dynamic_triage_agent_instructions(wrapper, agent):
    return f"""
    You are a restaurant triage assistant.

    The customer's name is {wrapper.context.name}.

    Your main job is to route the user to the correct specialist agent.

    Route based on the user's request:

    1. Menu Agent
    - menu questions
    - food recommendations
    - ingredients, drinks, vegetarian/vegan/allergy options

    2. Order Agent
    - placing food orders
    - takeout or delivery
    - changing or checking an order

    3. Reservation Agent
    - booking a table
    - changing a reservation
    - party size, date, and time

    4. Complaints Agent
    - bad food
    - rude staff
    - refund requests
    - dissatisfaction or serious restaurant issues

    If the user asks a restaurant-related question, route them to the best specialist.
    If the request is unclear, ask one short clarifying question.

    Always be polite and professional.
    """


# def dynamic_triage_agent_instructions(wrapper, agent):
#     return f"""
#     You are a restaurant assistant.

#     The customer's name is {wrapper.context.name}.

#     Your job:
#     - Help with menu, reservations, orders
#     - Detect complaints

#     If the user complains:
#     - Route to Complaints Agent

#     Complaint examples:
#     - "food was bad"
#     - "staff was rude"
#     - "I'm not satisfied"
#     - "I want a refund"

#     If it's not a complaint:
#     - Answer normally as a restaurant assistant

#     Always be polite.
#     """

def handle_handoff(
    wrapper: RunContextWrapper[UserAccountContext],
    input_data: HandoffData,
):

    with st.sidebar:
        st.write(
            f"""
            Handing off to {input_data.to_agent_name}
            Reason: {input_data.reason}
            Issue Type: {input_data.issue_type}
            Description: {input_data.issue_description}
        """
        )


def make_handoff(agent):

    return handoff(
        agent=agent,
        on_handoff=handle_handoff,
        input_type=HandoffData,
        input_filter=handoff_filters.remove_all_tools,
    )


triage_agent = Agent(
    name="Triage Agent",
    instructions=dynamic_triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    # tools=[
    #     technical_agent.as_tool(
    #         tool_name="Technical Help Tool",
    #         tool_description="Use this when the user needs tech support."
    #     )
    # ]
    handoffs=[
    make_handoff(menu_agent),
    make_handoff(order_agent),
    make_handoff(reservation_agent),
    make_handoff(complaints_agent),
    ],
)
