from datasets import load_dataset, DatasetDict
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from vector_store import VectorStore


class Ingest:

    def __init__(self):
        load_dotenv()

        self._dataset: DatasetDict = load_dataset(
            "KisanVaani/agriculture-qa-english-only"
        )

        self._embedder: HuggingFaceEmbeddings = VectorStore().get_embedder()

        self._vector_store: Chroma = VectorStore().get_vector_store()

    def prepare(self) -> List[Document]:
        docs: List[Document] = []

        for doc in self._dataset["train"]:
            text = f"""
Question: {doc["question"]}
Answer: {doc["answers"]}
""".strip()

            docs.append(Document(page_content=text, metadata={"type": "farming_qa"}))

        return docs

    def ingest(self) -> None:

        count: int = len(self._vector_store.get()["ids"])

        if count > 0:
            print("Data Already Ingested")
            return

        documents: List[Document] = self.prepare()

        for i in range(0, len(documents), self._BATCH_SIZE):

            batch: List[Document] = documents[i : i + self._BATCH_SIZE]

            self._vector_store.add_documents(batch)

            print(f"Inserted batch {i // self._BATCH_SIZE + 1}")

        print("Ingestion completed")
        return


if __name__ == "__main__":
    ingestion = Ingest()
    ingestion.ingest()
