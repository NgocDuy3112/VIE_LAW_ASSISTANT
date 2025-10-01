from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import ChatHuggingFace



def get_llm(model_name: str, **kwargs) -> BaseChatModel:
    provider = model_name.split("/")[0]
    model = model_name.split("/")[-1]
    if provider == 'openai':
        return ChatOpenAI(model=model, **kwargs)
    elif provider in ['lmstudio', 'lm-studio', 'lm_studio']:
        return ChatOpenAI(model=model, api_key="no-api-key", **kwargs)
    elif provider == 'ollama':
        return ChatOllama(model=model, **kwargs)
    elif provider == 'anthropic':
        return ChatAnthropic(model=model, **kwargs)
    elif provider == 'groq':
        return ChatGroq(model=model, **kwargs)
    elif provider in ['hf', 'huggingface', 'hugging-face', 'hugging_face']:
        return ChatHuggingFace(model=model, **kwargs)
    else:
        raise ValueError(f"No support for model with provider: {provider}")