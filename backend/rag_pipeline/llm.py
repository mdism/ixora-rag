from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_perplexity import ChatPerplexity
from langchain_anthropic import ChatAnthropic
from django.conf import settings
from .PROMPT import QUERY_PROMPT1, QUERY_PROMPT2, SYSTEM_PROMPT1, SYSTEM_PROMPT2
import gc
from project_management.models import QueryLog


llm_instances = {}

def get_llm(
    provider: str,
    temperature: float = settings.DEFAULT_TEMPERATURE,
    top_p: float = settings.DEFAULT_TOP_P,
    max_token: int = settings.DEFAULT_MAX_TOKENS,
    n_ctx: int = settings.DEFAULT_N_CTX,
    n_batch: int = settings.DEFAULT_N_BATCH,
    n_gpu_layers: int = settings.DEFAULT_N_GPU_LAYERS,
    f16_kv: bool = settings.DEFAULT_F16_KV,
    streaming: bool = settings.DEFAULT_STREAMING,
    n_threads: int = settings.DEFAULT_N_THREADS,
):
    """
    Unified LLM loader that supports Ollama (local) and cloud (OpenAI, Gemini, etc.)
    """
    provider = provider.lower()

    USE_FAKE_LLM = settings.USE_FAKE_LLM

    # ✅ NEW: Check fake mode
    if USE_FAKE_LLM:
        print("⚙️ Using FakeChatModel instead of real LLM.")
        from .fake_llm import FakeChatWithMetadata  # if you place it in a separate file
        return FakeChatWithMetadata(responses=["Fake response enabled."])

    if provider in llm_instances:
        print(f"INFO: Reusing cached model for {provider}")
        return llm_instances[provider]

    print(f"INFO: Loading new model for {provider}")

    # Base params used by both Ollama and cloud models
    common_params = dict(
        temperature=temperature,
        top_p=top_p,
    )

    if provider in ("phi3" , "llama", "mistral", 'gemma'):
        # 🧠 Use Ollama local models
        # model_name = "llama3" if provider == "llama" else "mistral-nemo"
        if provider == "phi3":
            model_name = "phi3:latest"  # or "llama3:8b", "llama3:70b" for specific sizes
        elif provider == "llama":
            model_name = "llama3"  # or "llama3:8b", "llama3:70b" for specific sizes
        elif provider == "mistral":
            model_name = "mistral-nemo"
        elif provider == "gemma":
            model_name = "gemma3" # Use the model name you pulled with 'ollama pull'
        else:
            # Handle the case where the provider is unknown, or set a default
            print(f"Warning: Unknown provider '{provider}'. Defaulting to llama3.")
            model_name = "llama3"

        llm_instances[provider] = ChatOllama(
            model=model_name,
            num_ctx=n_ctx,
            num_predict=max_token,
            streaming=streaming,
            **common_params
        )

    elif provider == "openai":
        llm_instances[provider] = ChatOpenAI(
            model="gpt-4o-mini",
            max_tokens=max_token,
            **common_params
        )

    elif provider == "gemini":
        llm_instances[provider] = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            max_output_tokens=max_token,
            **common_params
        )

    elif provider == "perplexity":
        llm_instances[provider] = ChatPerplexity(
            model="sonar-small-chat",
            max_tokens=max_token,
            **common_params
        )

    elif provider == "anthropic":
        llm_instances[provider] = ChatAnthropic(
            model="claude-3-5-sonnet-20240620",
            max_tokens=max_token,
            **common_params
        )

    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    gc.collect()
    return llm_instances[provider]


from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.messages import ChatMessage
from rag_pipeline.utility import generate_no_context_message

def generate_answer(
    query: str,
    context: str,
    sources=[],
    provider: str = settings.DEFAULT_LLM_PROVIDER,
    temperature: float = settings.DEFAULT_TEMPERATURE,
    top_p: float = settings.DEFAULT_TOP_P,
    max_token: int = settings.DEFAULT_MAX_TOKENS,
    n_ctx: int = settings.DEFAULT_N_CTX,
    n_batch: int = settings.DEFAULT_N_BATCH,
    n_gpu_layers: int = settings.DEFAULT_N_GPU_LAYERS,
    f16_kv: bool = settings.DEFAULT_F16_KV,
    streaming: bool = settings.DEFAULT_STREAMING,
    n_threads: int = settings.DEFAULT_N_THREADS,
):
    """
    Generate a response using the selected LLM.
    Works seamlessly for Ollama (local) and cloud models.
    """

    # if not context.strip() or context.strip() == "No relevant document found":
    #     return generate_no_context_message(query=query, fallback=False)

    # Prepare prompt
    final_query_text = QUERY_PROMPT2.replace("||RETRIEVED_CONTEXT||", context)
    final_query_text = final_query_text.replace("||USER_QUESTION||", query)

    messages = [
        SystemMessage(content=SYSTEM_PROMPT2),
        HumanMessage(content=final_query_text)
    ]

    llm = get_llm(
        provider=provider,
        temperature=temperature,
        top_p=top_p,
        f16_kv=f16_kv,
        max_token=max_token,
        n_ctx=n_ctx,
        n_batch=n_batch,
        n_gpu_layers=n_gpu_layers,
        streaming=streaming,
        n_threads=n_threads,
    )

    try:
        res = llm.invoke(messages)
        response_text = res.content if hasattr(res, "content") else str(res)

        # Extract small snippets from context
        context_chunks = context.split("\n\n")
        snippet_data = []
        for chunk in context_chunks:
            snippet_data.append(chunk[:20] + "..." + chunk[-20:])

        # Store to DB
        QueryLog.objects.create(
            user_query=query,
            response=response_text,
            provider=provider,
            context_snippet="\n".join(snippet_data),
            context_match_count=len(context_chunks),
            sources="\n".join(sources) if sources else None
        )        
        return res
    except Exception as e:
        print(f"ERROR: Failed to generate answer: {e}")
        return generate_no_context_message(query=query, fallback=True)
