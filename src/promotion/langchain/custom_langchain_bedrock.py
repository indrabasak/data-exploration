"""
Custom Bedrock Chat model for LangChain integration.
"""
import base64
import os
from typing import Optional, Any, List

import logging
import requests
from dotenv import load_dotenv
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult

logger = logging.getLogger(__name__)

load_dotenv()


class BedrockClient:
    """
    Client to interact with Bedrock API for authentication and message posting.
    """

    def __init__(self, auth_url, client_id: str, client_secret: str):
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self) -> str:
        """
        Obtain a bearer token using client credentials.
        :return:
        """
        # Concatenate the client ID and secret with a colon
        credentials = f"{self.client_id}:{self.client_secret}"

        # Encode the credentials in Base64
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("ascii")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"Basic {encoded_credentials}",
        }

        # Define the payload
        payload = {"grant_type": "client_credentials", "scope": "data:read"}

        # Make the POST request to get the token
        response = requests.post(self.auth_url, headers=headers, data=payload, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]

        raise Exception(f"Failed to obtain token: {response.status_code} {response.text}")

    def post_message(self, endpoint: str, payload: dict) -> dict:
        """
        Post a message to the specified Bedrock endpoint.
        :param endpoint:
        :param payload:
        :return:
        """
        token = self.get_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # Make the POST request to get the token
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        # Check if the request was successful
        if response.status_code == 200:
            return response.json()

        raise Exception(f"Failed to obtain response: {response.status_code} {response.text}")


class CustomBedrockAnthropicChat(BaseChatModel):
    """
    Custom Bedrock Chat model for LangChain integration.
    """

    client: BedrockClient
    model_endpoint: str
    anthropic_version: str = "bedrock-2023-05-31"
    max_tokens: int = 1000
    temperature: float = 0.7
    llm_type: str

    @property
    def _llm_type(self) -> str:
        """Get the type of language model used by this chat model.
        Used for logging purposes only."""
        return self.llm_type

    def _generate(
            self,
            messages: list[BaseMessage],
            stop: Optional[list[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            **kwargs: Any,
    ) -> ChatResult:
        """Generate a response from the model."""
        system_prompt: str = ""
        input_messages: List[dict[str, Any]] = []
        for message in messages:
            if isinstance(message, SystemMessage):
                if isinstance(message.content, str):
                    system_prompt = message.content
                continue
            msg = CustomBedrockAnthropicChat._convert_message(message)
            input_messages.append(msg)

        payload = {
            "anthropic_version": self.anthropic_version,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": input_messages,
        }

        if system_prompt is not None and system_prompt != "":
            payload["system"] = system_prompt
        payload.update(kwargs)

        response = self.client.post_message(self.model_endpoint, payload)
        logger.debug("Original response: %r", response)
        output = CustomBedrockAnthropicChat._covert_to_ai_message(response)
        generation = ChatGeneration(message=output)
        return ChatResult(generations=[generation])

    @staticmethod
    def _convert_message(message: BaseMessage) -> dict[str, Any]:
        if isinstance(message, HumanMessage):
            return CustomBedrockAnthropicChat._convert_human_message(message)

        if isinstance(message, AIMessage):
            return CustomBedrockAnthropicChat._convert_ai_message(message)

        raise ValueError(f"Unsupported message type: {type(message)}")

    @staticmethod
    def _convert_human_message(message: HumanMessage) -> dict[str, Any]:
        return {
            "role": "user",
            "content": [{"type": "text", "text": message.content}]
        }

    @staticmethod
    def _convert_ai_message(message: AIMessage) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": [{"type": "text", "text": message.content}]
        }

    @staticmethod
    def _covert_to_ai_message(response: dict[str, Any]) -> AIMessage:
        text_contents = []
        for content in response["content"]:
            if content["type"] == "text":
                text_contents.append(content)

        return AIMessage(
            content=text_contents,
            id=response.get("id"),
            response_metadata={"model_name": response["model"]},
            usage_metadata={
                "input_tokens": response["usage"]["input_tokens"],
                "output_tokens": response["usage"]["output_tokens"],
                "total_tokens": response["usage"]["input_tokens"] +
                                response["usage"]["output_tokens"],
            },
            stop_reason=response.get("stop_reason"),
            stop_sequence=response.get("stop_sequence"),
        )


def main():
    """
    Main function to demonstrate the usage of CustomBedrockAnthropicChat.
    :return:
    """
    bedrock_client = BedrockClient(
        auth_url=os.environ.get("APS_HOST"),
        client_id=os.environ.get("APS_CLIENT_ID"),
        client_secret=os.environ.get("APS_CLIENT_SECRET"),
    )

    llm = CustomBedrockAnthropicChat(
        client=bedrock_client,
        llm_type=os.environ.get("APS_LLM_TYPE"),
        model_endpoint=os.environ.get("APS_MODEL_ENDPOINT"),
        temperature=0.3,
        anthropic_version=os.environ.get("APS_ANTHROPIC_VERSION"))

    response = llm.invoke("Tell me a joke")
    print("==============================")
    print(response.content)

    msg = HumanMessage(content="Tell me a joke")
    response = llm.invoke([msg])
    print(response.content)

    system_msg = SystemMessage("You are a helpful coding assistant.")
    messages = [system_msg, HumanMessage("How do I create a REST API?")]
    response = llm.invoke(messages)
    print(response.content)

    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is the capital of France?"),
        AIMessage(content="The capital of France is Paris.")  # This is an example of AIMessage
    ]
    response = llm.invoke(messages)
    print("++++++++++++++++++++++++++++++++")
    print(response.content)


if __name__ == "__main__":
    main()
