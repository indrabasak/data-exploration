import os

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()


class LlmUtil:

    @staticmethod
    def get_azure_credential():
        credential = DefaultAzureCredential()

        # Set the API_KEY to the token from the Azure credential
        os.environ["OPENAI_API_KEY"] \
            = credential.get_token("https://cognitiveservices.azure.com/.default").token

    @staticmethod
    def get_llm() -> AzureChatOpenAI:
        LlmUtil.get_azure_credential()
        return AzureChatOpenAI(
            azure_endpoint=os.environ.get("AZURE_OPENAI_API_INSTANCE_NAME"),
            azure_deployment=os.environ.get("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
            openai_api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
            temperature=0
        )

def main():
    llm = LlmUtil.get_llm()
    response = llm.invoke("Tell me a joke")
    print(response.content)

if __name__ == "__main__":
    main()