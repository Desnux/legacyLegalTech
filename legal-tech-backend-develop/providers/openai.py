from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from config import Config


llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=Config.OPENAI_API_KEY)
llm_template_filler = ChatOpenAI(model="gpt-4o", temperature=0.2, api_key=Config.OPENAI_API_KEY)
simulation_llm = ChatOpenAI(model="gpt-4o", temperature=0.8, api_key=Config.OPENAI_API_KEY)


def get_structured_generator(schema: dict | BaseModel) -> Runnable:
    return llm.with_structured_output(schema=schema, method="function_calling", strict=False)
