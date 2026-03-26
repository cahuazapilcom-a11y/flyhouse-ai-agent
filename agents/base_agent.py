from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from tools.document_loader import load_area_documents
from tools.vector_store import build_vectorstore
from app.settings import OPENAI_MODEL


class BaseDocumentAgent:
    def __init__(
        self,
        api_key: str,
        area_name: str,
        docs_folder: str,
        system_prompt: str,
        temperature: float = 0.2,
    ):
        self.area_name = area_name
        self.docs_folder = docs_folder
        self.system_prompt = system_prompt.strip()

        self.llm = ChatOpenAI(
            model=OPENAI_MODEL,
            temperature=temperature,
            api_key=api_key
        )

        docs = load_area_documents(docs_folder)
        self.vectorstore = build_vectorstore(docs, api_key) if docs else None

    def _build_context(self, user_input: str, k: int = 4) -> str:
        if not self.vectorstore:
            return "No hay documentos cargados para esta área."

        results = self.vectorstore.similarity_search(user_input, k=k)

        chunks = []
        for i, doc in enumerate(results, start=1):
            source = doc.metadata.get("source_file", "desconocido")
            content = doc.page_content.strip()
            chunks.append(f"[Fragmento {i} | Fuente: {source}]\n{content}")

        return "\n\n".join(chunks) if chunks else "No se encontró contexto relevante."

    def run(self, user_input: str) -> str:
        context = self._build_context(user_input)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""
Pregunta del usuario:
{user_input}

Contexto documental:
{context}

Instrucciones:
- Responde principalmente con base en el contexto documental.
- Si falta información en los documentos, dilo claramente.
- No inventes datos.
- Si corresponde, resume primero y luego detalla.
""".strip()
            ),
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()