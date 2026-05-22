from enum import Enum
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_groq import ChatGroq

from rag.prompt_factory import PromptFactory
from retriever import Retriever
from typing import List
from dotenv import load_dotenv
from intent_router import IntentRouter


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

        self._history: List[AIMessage | HumanMessage | SystemMessage] = []

        self._retriever = Retriever(k=4)

        self._intent_router = IntentRouter()

    def rag_query(self, query_string: str, lang: Language) -> str:

        rag_context: str = self._retriever.retrieve(query_string)

        system_prompt: str = PromptFactory().get_rag_prompt(lang, rag_context)

        messages = [
            SystemMessage(content=system_prompt),
            ## Because * “unpacks” the list elements into another list.
            ## Without *, you insert the whole list as ONE element.
            *self._history,
            HumanMessage(content=query_string),
        ]

        response: AIMessage = self._model.invoke(messages)

        self._history.append(HumanMessage(content=query_string))

        self._history.append(AIMessage(content=response.content))

        return str(response.content)

    def general_query(self, query_string: str, lang: Language) -> str:

        system_prompt: str = PromptFactory().get_general_prompt(lang)

        messages = [
            SystemMessage(content=system_prompt),
            *self._history,
            HumanMessage(content=query_string),
        ]

        response: AIMessage = self._model.invoke(messages)

        self._history.append(HumanMessage(content=query_string))

        self._history.append(AIMessage(content=response.content))

        return str(response.content)

    def main(self, query_string: str, lang: Language) -> str:

        intent: IntentRouter.Intent = self._intent_router.get_intent(query_string)

        if intent.intent in ["disease", "farming"]:
            return self.rag_query(query_string, lang)  ## Call RAG

        return self.general_query(query_string, lang)  ## General Questions


if __name__ == "__main__":

    init_query = "Greet Me!"
    language: Language = Language.HI
    rag = Rag(language)
    ans = rag.main(init_query, language)
    print("KisanSaathi : ", ans)

    while True:
        query: str = input("User : ")

        if query == "0":
            break

        ans = rag.main(query, language)

        print("KisanSaathi : ", ans)
