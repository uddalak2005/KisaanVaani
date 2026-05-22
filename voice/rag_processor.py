import asyncio
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import TextFrame, TranscriptionFrame
from rag.main import Rag
from utils.language_enum import Language


class RagProcessor(FrameProcessor):

    def __init__(self, lang: Language = Language.HI):
        super().__init__()
        self._rag = Rag()
        self._lang = lang

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            query = frame.text.strip()

            if not query:
                await self.push_frame(frame, direction)
                return

            # Run blocking RAG call in a thread so asyncio event loop doesn't freeze
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, self._rag.main, query, self._lang, False
            )

            await self.push_frame(TextFrame(text=response))

        else:
            await self.push_frame(frame, direction)