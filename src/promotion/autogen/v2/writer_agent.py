"""
Writer Agent for promotion analysis. Transforms data into clear
business insights and actionable recommendations.
"""
import os

from autogen_agentchat.agents import AssistantAgent

from llm_util import LlmUtil
from prompt import WRITER_AGENT_SYSTEM_MESSAGE

writer_agent = AssistantAgent(
    name="WriterAgent",
    model_client=LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_MODEL_GPT_4_1")),
    description="Writer Agent for Autodesk promotion analysis. "
                "Transforms data into clear business insights and actionable recommendations.",
    system_message=WRITER_AGENT_SYSTEM_MESSAGE,
)