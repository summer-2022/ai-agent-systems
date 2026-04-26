from agents import Agent
from output_guardrails import restaurant_output_guardrail

order_agent = Agent(
    name="Order Agent",
    instructions="""
    Help customers place or modify food orders.

    Assist with:
    - takeout
    - delivery
    - order changes
    - item quantities

    Be clear and helpful.
    """,
    output_guardrails=[restaurant_output_guardrail],
)