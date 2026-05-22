import os
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.services.sarvam.tts import SarvamTTSService
from utils.language_enum import Language, LANGUAGE_MAP
from pipecat.transcriptions.language import Language as PipecatLanguage
from dotenv import load_dotenv

load_dotenv()

def create_tts(lang: Language) -> SarvamTTSService:
    pipecat_lang: PipecatLanguage = LANGUAGE_MAP.get(lang, PipecatLanguage.HI_IN)

    return SarvamTTSService(
        api_key=str(os.getenv("SARVAM_API_KEY")),
        sample_rate=8000,  # for Telephonic Conversations
        settings=SarvamTTSService.Settings(
            voice="shubh",
            model="bulbul:v3",  # Explicit model selection
            language=pipecat_lang,  # Enum, not raw string "hi-IN"
        ),
        vad_analyzer=SileroVADAnalyzer(
            sample_rate=8000,
            params=VADParams(stop_secs=0.5)  # wait 0.5s silence before end-of-turn
        )
    )
