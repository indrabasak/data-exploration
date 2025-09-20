"""
Utility for managing Azure OpenAI credentials and client.
"""
import asyncio
import os

from autogen_core.models import UserMessage
from autogen_ext.auth.azure import AzureTokenProvider
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()


class LlmUtil:
    """
    Utility class for managing Azure OpenAI credentials and client.
    """

    @staticmethod
    def get_azure_credential() -> AzureTokenProvider:
        """
        Get Azure credential using DefaultAzureCredential and create a token provider.
        :return:
        """
        return AzureTokenProvider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default",
        )

    @staticmethod
    def get_llm(model: str) -> AzureOpenAIChatCompletionClient:
        """
        Get Azure OpenAI Chat Completion client with the necessary credentials.
        :return:
        """
        return AzureOpenAIChatCompletionClient(
            azure_deployment=os.environ.get("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
            model=model,
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.environ.get("AZURE_OPENAI_API_INSTANCE_NAME"),
            azure_ad_token_provider=LlmUtil.get_azure_credential())


async def main():
    """
    Main function to demonstrate the usage of LlmUtil.
    """
    llm = LlmUtil.get_llm(os.environ.get("AZURE_OPENAI_API_DEPLOYMENT_NAME"))
    result = await llm.create(
        [UserMessage(content="What is the capital of France?", source="user")]
    )
    print(result)
    await llm.close()


if __name__ == "__main__":
    asyncio.run(main())
