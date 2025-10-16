from langchain_core.language_models.fake_chat_models import FakeChatModel
from langchain_core.messages import AIMessage
import time

class FakeChatWithMetadata(FakeChatModel):
    """
    A FakeChatModel that returns a structured response
    resembling ChatOllama or ChatOpenAI outputs.
    """

    def invoke(self, messages, *args, **kwargs):
        start = time.time()

        # Get the user query (last human message)
        query_text = ""
        for msg in messages:
            if msg.type == "human":
                query_text = msg.content

        # Build fake content
        fake_answer = f"This is a FAKE answer for query: '{query_text}' (no real LLM used)."

        # Mimic realistic metadata
        metadata = {
            "model_name": "fake-chat-model",
            "provider": "FakeChatModel",
            "total_duration": int((time.time() - start) * 1e9),  # ns
            "eval_count": 30,
            "prompt_eval_count": 15
        }

        usage_metadata = {
            "input_tokens": 15,
            "output_tokens": 30,
            "total_tokens": 45
        }

        return AIMessage(
            content=fake_answer,
            response_metadata=metadata,
            usage_metadata=usage_metadata
        )
