"""
Combined RAG tools (merged from tools.py and calender_tool.py).
"""

import asyncio
from typing import Any, Dict
from livekit.agents import function_tool, RunContext, ToolError

from ..rag.pdf_engine import get_pdf_rag_answer_async, initialize_pdf_rag
from ..rag.json_engine import get_json_rag_answer_async, initialize_json_rag


@function_tool
async def get_rag_answer(context: RunContext, query: str) -> Dict[str, Any]:
    """
    Function tool to retrieve the top-k documents for a query from the PDF RAG engine.
    
    Args:
        query (str): The user's question about the university information.
        
    Returns:
        Dict[str, Any]: A dictionary containing the context about the university information
    """
    async def updating(delay: float = 0.5):
        """Send a temporary 'loading' message."""
        await asyncio.sleep(delay)
        try:
            await context.session.generate_reply("Retrieving information from the knowledge base...")
        except Exception:
            pass

    status_task = asyncio.create_task(updating())

    try:
        result = await get_pdf_rag_answer_async(query)
        context_text = result.get("context", "")
        if not context_text:
            raise ToolError("No relevant information found.")
        return {"query": query, "context": context_text}

    except Exception as e:
        raise ToolError(f"Error retrieving RAG answer: {e}")

    finally:
        if not status_task.done():
            status_task.cancel()
            try:
                await status_task
            except asyncio.CancelledError:
                pass
        # Send final message safely
        try:
            await context.session.generate_reply("Information retrieval complete.")
        except Exception:
            pass


@function_tool
async def get_rag_answer_json(context: RunContext, query: str) -> Dict[str, Any]:
    """
    Function tool to retrieve information from JSON data (calendar, faculty, tech lab schedules).
    Use this for questions about:
    - Calendar events and academic dates
    - Faculty information and staff details
    - Tech lab schedules and timings
    - Holiday dates and semester information
    
    Args:
        query (str): The user's question about calendar, faculty, or tech lab information.
        
    Returns: 
        Dict[str, Any]: A dictionary containing the context about the requested information
    """
    async def updating(delay: float = 0.5):
        """Send a temporary 'loading' message."""
        await asyncio.sleep(delay)
        try:
            await context.session.generate_reply("Searching calendar and faculty information...")
        except Exception:
            pass

    status_task = asyncio.create_task(updating())

    try:
        # Ensure the JSON RAG engine is initialized (safe to call multiple times)
        await initialize_json_rag()

        # Get the JSON RAG result
        result = await get_json_rag_answer_async(query, k=10, top_n=5, include_embeddings=False)

        # Extract the combined context (similar to PDF RAG format)
        context_text = result.get("combined_context", "")
        if not context_text or context_text.strip() == "":
            raise ToolError("No relevant information found in calendar or faculty data.")

        # Return in the same format as PDF RAG tool for consistency
        return {"query": query, "context": context_text}

    except Exception as e:
        raise ToolError(f"Error retrieving calendar/faculty information: {e}")

    finally:
        if not status_task.done():
            status_task.cancel()
            try:
                await status_task
            except asyncio.CancelledError:
                pass
        try:
            await context.session.generate_reply("Information search complete.")
        except Exception:
            pass