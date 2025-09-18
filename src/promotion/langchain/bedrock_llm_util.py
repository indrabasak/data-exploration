"""
Utility to get a Bedrock LLM instance.
"""
import os

import logging
from dotenv import load_dotenv

from custom_langchain_bedrock import BedrockClient, CustomBedrockAnthropicChat

logger = logging.getLogger(__name__)

load_dotenv()


class BedrockLlmUtil:
    """
    Utility class to get a Bedrock LLM instance.
    """

    @staticmethod
    def get_llm():
        bedrock_client = BedrockClient(
            auth_url=os.environ.get("APS_HOST"),
            client_id=os.environ.get("APS_CLIENT_ID"),
            client_secret=os.environ.get("APS_CLIENT_SECRET"),
        )

        return CustomBedrockAnthropicChat(
            client=bedrock_client,
            llm_type=os.environ.get("APS_LLM_TYPE"),
            model_endpoint=os.environ.get("APS_MODEL_ENDPOINT"),
            temperature=0.3,
            anthropic_version=os.environ.get("APS_ANTHROPIC_VERSION"))


def main():
    llm = BedrockLlmUtil.get_llm()
    response = llm.invoke("Tell me a joke")
    print(response.content)


if __name__ == "__main__":
    main()
