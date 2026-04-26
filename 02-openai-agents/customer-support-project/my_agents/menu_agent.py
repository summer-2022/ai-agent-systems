from agents import Agent
from output_guardrails import restaurant_output_guardrail

menu_agent = Agent(
    name="Menu Agent",
    instructions="""
    Help customers with menu questions.

    You can explain:
    - food items
    - drinks
    - vegetarian / vegan / allergy options
    - recommendations

    Be friendly and concise.
    """,
    output_guardrails=[restaurant_output_guardrail],
)