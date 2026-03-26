from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader


def load_area_documents(folder_path: str) -> List[Document]:
    docs: List[Document] = []
    folder = Path(folder_path)

    if not folder.exists():
        print(f"[WARN] La carpeta no existe: {folder_path}")
        return docs

    for file in folder.rglob("*"):
        if not file.is_file():
            continue

        suffix = file.suffix.lower()

        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(file))
                loaded = loader.load()
                for doc in loaded:
                    doc.metadata["source_file"] = file.name
                    doc.metadata["source_path"] = str(file)
                docs.extend(loaded)

            elif suffix in [".docx", ".doc"]:
                loader = Docx2txtLoader(str(file))
                loaded = loader.load()
                for doc in loaded:
                    doc.metadata["source_file"] = file.name
                    doc.metadata["source_path"] = str(file)
                docs.extend(loaded)

        except Exception as e:
            print(f"[ERROR] No se pudo cargar {file.name}: {e}")

    print(f"[INFO] Documentos cargados desde {folder_path}: {len(docs)}")
    return docs