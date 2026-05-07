from typing import List, Dict, Any, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    next_agent: str
    intermediate_results: Dict[str, Any]
    iteration_count: int
