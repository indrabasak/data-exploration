"""
Writer Agent for promotion analysis. Transforms data into clear
business insights and actionable recommendations.
"""
import os

from autogen_agentchat.agents import AssistantAgent

from llm_util import LlmUtil
from prompt import SQL_JUDGE_AGENT_SYSTEM_MESSAGE

sql_judge_agent = AssistantAgent(
    name="SqlJudgeAgent",
    model_client=LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_MODEL_O4_MINI")),
    description="SQL Judge Agent for Autodesk's EDH Snowflake databases. "
                "Reviews, validates, and corrects SQL queries from Database Agent before execution.",
    system_message=SQL_JUDGE_AGENT_SYSTEM_MESSAGE,
)