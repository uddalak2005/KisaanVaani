from enum import Enum
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from retriever import Retriever
from typing import List
from dotenv import load_dotenv
# from sarvamai import SarvamAI
# import os


class Language(Enum):
    EN = "english"
    HI = "hindi"
    BN = "bengali"
    TE = "telugu"


class Rag:

    def __init__(self, lang: Language) -> None:

        load_dotenv()

        self._language = lang

        self._model = ChatGroq(
            model="llama-3.3-70b-versatile",
        )

        #         self._client = SarvamAI(
        #     api_subscription_key=os.getenv("SARVAM_API_KEY"),
        #
        # )

        # self._history: List[dict] = []

        self._history: List[AIMessage | HumanMessage | SystemMessage] = []

        self._retriever = Retriever()

    def query(self, query_string: str, lang: Language) -> str:

        rag_context: str = self._retriever.retrieve(query_string)

        system_prompt: str = f"""
You are Kisaan-Sathi, AgroSure's farming assistant for Indian farmers.

## LANGUAGE
Respond ONLY in {lang.value} using its native script.

Examples:
- Bengali → বাংলা script
- Hindi → देवनागरी script
- Telugu → తెలుగు script

Never write Bengali, Hindi, or Telugu using English letters.
Never transliterate.

Use very simple village-level spoken language.
Speak exactly like one farmer talking to another farmer in a village.

Speak warmly like an experienced local farmer helping another farmer.
Use natural Indian rural conversational tone.

Do NOT use:
- formal language
- textbook language
- scientific language
- government office language
- news channel language
- Do not think step-by-step.
- Do not explain your reasoning.
- Never generate analysis.
- Reply only with the final answer for the farmer.

## SPEAKING STYLE
Phone call with a farmer working in the field.

- Maximum 2-3 short sentences
- Natural spoken tone only
- No bullet points
- No lists
- No headings
- No markdown
- No English words if a simple local word exists
- Never use scientific or Latin disease names
- If mentioning medicine or fertilizer, say the common shop name farmers use
- Always explain the disease simply before giving symptoms or advice.

## CONVERSATION
- First acknowledge the farmer's concern naturally
- Then give practical advice
- Ask only one question at a time if needed
- If farmer mentions crop loss or money problems, respond with empathy first
- End naturally so the farmer can continue talking

## GOOD EXAMPLE (BENGALI)
"হ্যাঁ দাদা, আলুর পাতায় যে কালো দাগ ধরেছে সেটা রোগের জন্য হতে পারে। একটা ভালো ছত্রাকের ওষুধ স্প্রে করুন আর জমিতে জল বেশি জমতে দেবেন না।"

## CONTEXT
{rag_context}
"""

        messages = [
            SystemMessage(content=system_prompt),
            ## Because * “unpacks” the list elements into another list.
            ## Without *, you insert the whole list as ONE element.
            *self._history,
            HumanMessage(content=query),
            # {
            #     "role": "system",
            #     "content": system_prompt,
            # },
            #
            # ## Because * “unpacks” the list elements into another list.
            # ## Without *, you insert the whole list as ONE element.
            # *self._history,
            #
            # {
            #     "role": "user",
            #     "content": query_string,
            # }
        ]

        response: AIMessage = self._model.invoke(messages)

        self._history.append(HumanMessage(content=query))

        self._history.append(AIMessage(content=response.content))

        return str(response.content)

        # # #Sarvam 30-B LLM
        # response = self._client.chat.completions(
        #     model="sarvam-30b",
        #     messages=messages,
        # )
        #
        # answer = response.choices[0].message.content
        #
        # print(response.usage.total_tokens)
        #
        # self._history.append({
        #     "role": "user",
        #     "content": query_string,
        # })
        #
        # self._history.append({
        #     "role": "assistant",
        #     "content": answer,
        # })
        #
        # return answer


if __name__ == "__main__":

    query: str = "What is potato blight"
    language: Language = Language.HI
    rag = Rag(language)
    ans = rag.query(query, language)
    print(ans)
