"""
Writer Agent for promotion analysis. Transforms data into clear
business insights and actionable recommendations.
"""
from autogen_agentchat.agents import AssistantAgent

from llm_util import LlmUtil
from prompt import WRITER_AGENT_SYSTEM_MESSAGE

writer_agent = AssistantAgent(
    name="WriterAgent",
    model_client=LlmUtil.get_llm(),
    description="Writer for promotion analysis. "
                "Transforms data into clear business insights and actionable recommendations.",
    system_message=WRITER_AGENT_SYSTEM_MESSAGE,
)
