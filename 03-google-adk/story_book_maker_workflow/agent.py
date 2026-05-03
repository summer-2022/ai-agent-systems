import os
import json
from dotenv import load_dotenv

from google.adk.agents import LlmAgent, SequentialAgent

load_dotenv()


# 1. Story Writer Agent
story_writer = LlmAgent(
    name="story_writer",
    model="gemini-2.0-flash",
    instruction="""
You are a children's story writer.

Create a 5-page children's story.

Return JSON only.

Format:
{
  "pages":[
    {
      "page":1,
      "text":"...",
      "visual":"..."
    }
  ]
}
""",
    output_key="story_data"
)


# 2. Illustrator Agent
illustrator = LlmAgent(
    name="illustrator",
    model="gemini-2.0-flash",
    instruction="""
Read the story data below:

{story_data}

For each page, describe the illustration result.

Example:
Page 1 Image Created: rabbit in forest
""",
)


# 3. Root Pipeline
root_agent = SequentialAgent(
    name="storybook_pipeline",
    sub_agents=[
        story_writer,
        illustrator
    ]
)