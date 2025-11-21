from typing import Optional

from pydantic import BaseModel, Field

from .enum import ChatMessageSource


class ChatMessage(BaseModel):
    source: Optional[ChatMessageSource] = Field(..., description="Source of the message")
    content: Optional[str] = Field(..., description="Content the message")


class ChatSimulation(BaseModel):
    messages: Optional[list[ChatMessage]] = Field(..., description="Messages in the chat")
    simulated_information: Optional[dict] = Field(..., description="Information created for the simulation")
    seed: Optional[int] = Field(..., description="Seed used by the randomizer")


class ChatAnswer(BaseModel):
    answer: Optional[str] = Field(..., description="Answer to the query")