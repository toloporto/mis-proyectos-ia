from app.core.graph import app
from langchain_core.messages import HumanMessage
import asyncio

async def main():
    result = app.invoke(
        {"messages": [HumanMessage(content="hola")], "intermediate_results": {}, "iteration_count": 0},
        config={"configurable": {"thread_id": "test"}}
    )
    print("Test result:", result)

if __name__ == "__main__":
    asyncio.run(main())
