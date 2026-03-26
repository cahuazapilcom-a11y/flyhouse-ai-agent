from typing import List, Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


def build_vectorstore(documents: List[Document], api_key: str) -> Optional[FAISS]:
    if not documents:
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )

    split_docs = splitter.split_documents(documents)

    embeddings = OpenAIEmbeddings(api_key=api_key)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    return vectorstore