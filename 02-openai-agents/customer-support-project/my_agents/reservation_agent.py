from agents import Agent
from output_guardrails import restaurant_output_guardrail

reservation_agent = Agent(
    name="Reservation Agent",
    instructions="""
    Help customers make reservations.

    Ask for:
    - date
    - time
    - party size
    - name

    Confirm politely.
    """,
    output_guardrails=[restaurant_output_guardrail],
)