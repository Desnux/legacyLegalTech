from abc import ABC

from providers.openai import ChatOpenAI, simulation_llm


class BaseSimulator(ABC):
    def get_simulator_model(self) -> ChatOpenAI:
        return simulation_llm