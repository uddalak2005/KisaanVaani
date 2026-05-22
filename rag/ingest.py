from datasets import load_dataset, DatasetDict
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

class Ingest:
    _dataset : DatasetDict
    _BATCH_SIZE : int = 5000
    embedder : HuggingFaceEmbeddings
    vector_store : Chroma

    def __init__(self):
        load_dotenv()

        self.dataset = load_dataset("KisanVaani/agriculture-qa-english-only")

        self.embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

        self.vector_store = Chroma(
            collection_name="farming_qa",
            embedding_function=self.embedder,
            persist_directory="./chroma_langchain_db",
        )

    def prepare(self) -> List[Document]:
        docs : List[Document] = []

        for doc in self.dataset["train"]:
            text = f"""
        Question: {doc["question"]}
        Answer: {doc["answers"]}
        """

            docs.append(Document(page_content=text, metadata={"type": "farming_qa"}))

        return docs

    def ingest(self) -> None:

        count : int = len(self.vector_store.get()["ids"])

        if count > 0:
            print("Data Already Ingested")
            return

        documents : List[Document] = self.prepare()

        for i in range(0, len(documents), self._BATCH_SIZE):

            batch : List[Document] = documents[i : i + self._BATCH_SIZE]

            self.vector_store.add_documents(batch)

            print(f"Inserted batch {i // self._BATCH_SIZE + 1}")

        print("Ingestion completed")
        return


if __name__ == "__main__":
    ingestion = Ingest()
    ingestion.ingest()



