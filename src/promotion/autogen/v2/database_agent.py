"""
Database Agent for Snowflake databases.
"""
import os

from autogen_agentchat.agents import AssistantAgent

from llm_util import LlmUtil
from prompt import DATABASE_AGENT_SYSTEM_MESSAGE
from snowflake_util import SnowflakeUtil

database_agent = AssistantAgent(
    name="DatabaseAgent",
    model_client=LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_MODEL_GPT_4_1")),
    description="Database Agent for Snowflake databases. "
                "Creates SQL queries, executes them using tools, and returns structured data.",
    system_message=DATABASE_AGENT_SYSTEM_MESSAGE,
    tools=[SnowflakeUtil.execute_query],
)