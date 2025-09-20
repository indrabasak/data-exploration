"""
Planning Agent for coordinating tasks between Database and Writer agents.
"""
import os

from autogen_agentchat.agents import AssistantAgent
from dotenv import load_dotenv

from llm_util import LlmUtil
from prompt import PLANNING_AGENT_SYSTEM_MESSAGE

load_dotenv()

planning_agent = AssistantAgent(
    name="PlanningAgent",
    model_client=LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_MODEL_GPT_4_1")),
    description="Planning Agent for promotion analysis. "
                "Analyzes user requests and coordinates tasks between Database and Writer agents.",
    system_message=PLANNING_AGENT_SYSTEM_MESSAGE,
)
