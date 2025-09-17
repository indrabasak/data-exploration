"""
Planning Agent for coordinating tasks between Database and Writer agents.
"""
from autogen_agentchat.agents import AssistantAgent

from llm_util import LlmUtil
from prompt import PLANNING_AGENT_SYSTEM_MESSAGE

planning_agent = AssistantAgent(
    name="PlanningAgent",
    model_client=LlmUtil.get_llm(),
    description="Planning Agent for Autodesk's EDH promotion analysis. "
                "Analyzes user requests and coordinates tasks between Database and Writer agents.",
    system_message=PLANNING_AGENT_SYSTEM_MESSAGE,
)
