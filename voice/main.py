from voice.livekit_transport import create_transport
from voice.generate_token import generate_token
import os
from utils.language_enum import Language
from voice.sarvam_stt import create_stt
from voice.sarvam_tts import create_tts
from voice.rag_processor import RagProcessor
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.frames.frames import TextFrame
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    room_name = str(os.getenv("LIVEKIT_ROOM"))
    token = generate_token(room_name)  # fresh token each run

    transport = create_transport(token)

    stt = create_stt()
    tts = create_tts(lang=Language.HI)
    rag_processor = RagProcessor(lang=Language.HI)

    pipeline = Pipeline(
        [transport.input(), stt, rag_processor, tts, transport.output()]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
        )
    )


    @transport.event_handler(
        "on_participant_connected"
    )  # SIP uses this, not on_client_connected
    async def on_call_connected(transport, participant):
        await task.queue_frame(TextFrame("नमस्ते! मैं किसान साथी हूँ। आप कैसे हैं?"))

    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    asyncio.run(main())
