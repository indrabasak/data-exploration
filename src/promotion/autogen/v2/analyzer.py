"""
EDH Promotion Analysis System
"""
import asyncio
import os

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from database_agent import database_agent
from llm_util import LlmUtil
from planning_agent import planning_agent
from prompt import SELECTOR_GROUP_CHAT_PROMPT
from sql_judge_agent import sql_judge_agent
from writer_agent import writer_agent

# Setup termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=12)
termination = max_messages_termination | text_mention_termination

# Create the team
team = SelectorGroupChat(
    [planning_agent, database_agent, sql_judge_agent, writer_agent],
    model_client=LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_MODEL_GPT_4_1")),
    termination_condition=termination,
    selector_prompt=SELECTOR_GROUP_CHAT_PROMPT,
    allow_repeated_speaker=True,
)


async def main():
    """Main function to run the EDH promotion analysis system"""

    print("🚀 Starting EDH Promotion Analysis System...")
    print("💡 For interactive UI, run: streamlit run streamlit_app.py")
    print("📋 This console version is for testing purposes.")

    # Example question for testing -
    # Name all the promotions that resulted in sales in the US in the last quarter?
    # Example task for console testing
    task = input("Enter your question about promotions: ")

    if task.strip():
        print(f"📋 Processing: {task}")
        # Run the team with streaming console output
        await Console(team.run_stream(task=task))
    else:
        print("No question provided. Exiting.")


if __name__ == "__main__":
    # Use asyncio.run() when running as a script
    asyncio.run(main())
