"""
EDH Promotion Analysis System
"""
import asyncio

from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console

from database_agent import database_agent
from llm_util import LlmUtil
from planning_agent import planning_agent
from prompt import SELECTOR_GROUP_CHAT_PROMPT
from writer_agent import writer_agent

# Setup termination conditions
text_mention_termination = TextMentionTermination("TERMINATE")
max_messages_termination = MaxMessageTermination(max_messages=5)
termination = max_messages_termination | text_mention_termination

# Create the team
team = SelectorGroupChat(
    [planning_agent, database_agent, writer_agent],
    model_client=LlmUtil.get_llm(),
    termination_condition=termination,
    selector_prompt=SELECTOR_GROUP_CHAT_PROMPT,
    allow_repeated_speaker=True,
)


async def main():
    """Main function to run the EDH promotion analysis system"""

    task = "How many promotions resulted in sales in the last quarter? Name all promotions."

    print("🚀 Starting EDH Promotion Analysis System...")
    print(f"📋 Task: {task}")

    # Run the team with streaming console output
    await Console(team.run_stream(task=task))


if __name__ == "__main__":
    # Use asyncio.run() when running as a script
    asyncio.run(main())
