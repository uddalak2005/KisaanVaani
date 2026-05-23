import os
from livekit.agents import JobContext, WorkerOptions, cli
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.pipeline.runner import PipelineRunner
from pipecat.frames.frames import TextFrame
from pipecat.transports.livekit.transport import LiveKitTransport, LiveKitParams
from dotenv import load_dotenv

from utils.language_enum import Language
from voice.sarvam_stt import create_stt
from voice.sarvam_tts import create_tts
from voice.groq_llm import create_groq_llm
from voice.generate_token import generate_token  # your existing token generator

load_dotenv()

GREETINGS = {
    Language.HI: "राम-राम किसान भाई! मैं किसान-साथी हूँ। कहिए आज क्या मदद करूँ?",
    Language.BN: "নমস্কার চাষীভাই! আমি কিষাণ-সাথী। বলুন আজকে মাঠে কী সমস্যা হচ্ছে?",
    Language.TE: "నమస్తే రైతు సోదరా! నేను కిసాన్-సాథిని. ఈరోజు మీ పొలంలో సమస్య ఏమిటో చెప్పండి?",
    Language.EN: "Hello there! I'm Kisan-Sathi. How can I help you with your crops today?"
}

async def entrypoint(ctx: JobContext):
    selected_language = Language.BN

    print(f"Handshaking incoming job allocation request for room: {ctx.room.name}")

    # Use the room name from JobContext, generate token for it
    await ctx.connect()

    room_name = ctx.room.name
    token = generate_token(room_name)
    url = str(os.getenv("LIVEKIT_URL"))

    transport = LiveKitTransport(
        url,
        token,
        room_name,
        params=LiveKitParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
        )
    )

    stt = create_stt()
    tts = create_tts(lang=selected_language)
    llm_service, aggregators, rag_injector = create_groq_llm(selected_language)

    pipeline = Pipeline([
        transport.input(),
        stt,
        aggregators.user(),
        rag_injector,
        llm_service,
        tts,
        aggregators.assistant(),
        transport.output()
    ])

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            audio_in_sample_rate=8000,
            audio_out_sample_rate=8000,
        )
    )

    @transport.event_handler("on_first_participant_joined")
    async def on_first_join(_transport, _participant_id):
        greeting_text = GREETINGS.get(selected_language, GREETINGS[Language.HI])
        await task.queue_frame(TextFrame(greeting_text))

    runner = PipelineRunner()
    await runner.run(task)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, agent_name="kisan-agent"))