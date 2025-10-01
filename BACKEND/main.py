"""
Nexi - SRM AP University Voice AI Assistant

Main entry point for the LiveKit agent.
Refactored and cleaned up from clean.py with better structure.
"""

import os
import logging
import asyncio
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, RoomInputOptions
from livekit.plugins import (
    cartesia,
    deepgram,
    noise_cancellation,
    silero,
    google
)

from BACKEND.core.agent import NexiAssistant
from BACKEND.rag.pdf_engine import initialize_pdf_rag
from BACKEND.rag.json_engine import initialize_json_rag
from BACKEND.config.settings import LIVEKIT_CONFIG, API_KEYS
from BACKEND.config.prompts import INITIAL_GREETING

logging.basicConfig(level=logging.INFO)
load_dotenv(".env.local")
logger = logging.getLogger(__name__)


async def entrypoint(ctx: agents.JobContext):
    """Main entrypoint for the Nexi LiveKit agent."""
    try:
        logger.info("🚀 Starting Nexi Agent...")
        
        # Initialize RAG engines
        logger.info("📚 Initializing PDF RAG engine...")
        await initialize_pdf_rag()
        logger.info("✅ PDF RAG engine initialized successfully!")
        
        logger.info("📅 Initializing JSON RAG engine...")
        await initialize_json_rag()
        logger.info("✅ JSON RAG engine initialized successfully!")

        # Initialize STT
        stt = deepgram.STT(
            model=LIVEKIT_CONFIG["deepgram_model"], 
            language=LIVEKIT_CONFIG["deepgram_language"]
        )
        logger.info("🎤 STT initialized with Deepgram")

        # Initialize LLM
        llm = google.LLM(
            model=LIVEKIT_CONFIG["gemini_model"],
            api_key=API_KEYS["google"]
        )
        logger.info("🧠 LLM initialized with Gemini")

        # Initialize TTS
        tts = cartesia.TTS(
            model=LIVEKIT_CONFIG["cartesia_model"],
            voice=LIVEKIT_CONFIG["cartesia_voice"],
            api_key=API_KEYS["cartesia"]
        )
        logger.info("🔊 TTS initialized with Cartesia")

        # Initialize VAD
        vad = silero.VAD.load()
        logger.info("👂 VAD initialized with Silero")

        # Create session
        session = AgentSession(
            stt=stt,
            llm=llm,
            tts=tts,
            vad=vad,
        )

        # Create assistant
        assistant = NexiAssistant()

        # Connect with retry logic
        max_retries = 5
        for attempt in range(max_retries):
            try:
                await ctx.connect()
                logger.info("🌐 Connected to LiveKit room")
                break
            except Exception as e:
                logger.warning(f"Connection attempt {attempt+1}/{max_retries} failed: {e}")
                await asyncio.sleep(min(2 ** attempt, 30))
        else:
            raise RuntimeError("Failed to connect to LiveKit after retries")

        # Start the session
        await session.start(
            room=ctx.room,
            agent=assistant,
            room_input_options=RoomInputOptions(
                noise_cancellation=noise_cancellation.BVC(),
            ),
        )
        logger.info("🎯 Session started successfully")

        # Handle transcriptions
        @session.on("transcription")
        def on_transcription(event):
            if not event.text or not event.text.strip():
                return

            user_text = event.text.strip()
            participant_identity = str(event.participant.identity if event.participant else "anonymous")

            logger.info(f"👤 Received from {participant_identity}: {user_text}")

            # Process all messages through the assistant
            async def handle_query():
                try:
                    await assistant.process_query(participant_identity, user_text, session)
                except Exception as e:
                    logger.error(f"❌ Error in handle_query: {e}")

            # Create and run async task
            task = asyncio.create_task(handle_query())
            task.add_done_callback(
                lambda t: logger.error(f"❌ Task error: {t.exception()}") if t.exception() else None
            )

        # Send initial greeting
        logger.info("👋 Sending initial greeting...")
        await session.generate_reply(
            instructions=f"Say: {INITIAL_GREETING} Keep it simple and friendly, no symbols."
        )

        logger.info("✅ Agent started successfully!")
        logger.info("🎤 Listening for user input...")
        logger.info("⏰ Session timeout: 30 seconds")
        logger.info("👋 Automatic goodbye detection enabled")

    except Exception as e:
        logger.error(f"💥 Agent startup error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))