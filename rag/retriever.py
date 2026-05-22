from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.documents import Document
from typing import List
from vector_store import VectorStore

class Retriever:
    _vector_store : Chroma
    _retriever : VectorStoreRetriever

    def __init__(self):

        self._vector_store = VectorStore().get_vector_store()

        self._retriever = self._vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 4,
                "filter": {"type": "farming_qa"},
                "fetch_k" : 10
            }
        )

    def retrieve(self, query : str) -> List[str]:

        docs : List[Document] = self._retriever.invoke(query)

        context = []

        for doc in docs:
            context.append(doc.page_content)

        return context

if __name__ == "__main__":
    retriever = Retriever()
    result = retriever.retrieve("What is Potato Blight")
    print(result)
