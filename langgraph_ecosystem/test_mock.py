from app.core.graph import app as graph_app
from langchain_core.messages import HumanMessage
import asyncio
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

async def main():
    import app.agents.supervisor
    import app.agents.workers.math_worker
    import app.agents.workers.file_worker
    
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = AIMessage(content="FINISH")
    
    app.agents.supervisor.llm = mock_llm
    app.agents.workers.math_worker.llm = mock_llm
    app.agents.workers.file_worker.llm = mock_llm
    
    result = graph_app.invoke(
        {"messages": [HumanMessage(content="hola")], "intermediate_results": {}, "iteration_count": 0},
        config={"configurable": {"thread_id": "test3"}}
    )
    print("Test result:", result)

if __name__ == "__main__":
    asyncio.run(main())
