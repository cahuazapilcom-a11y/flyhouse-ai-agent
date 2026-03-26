from typing import Any, Dict, List

from langchain_tavily import TavilyExtract

from app.settings import TAVILY_API_KEY


def get_tavily_extract_tool(
    extract_depth: str = "basic",
    include_images: bool = False,
) -> TavilyExtract:
    """
    Crea y devuelve la herramienta oficial de Tavily Extract.
    """
    if not TAVILY_API_KEY:
        raise ValueError("Falta TAVILY_API_KEY en el archivo .env")

    return TavilyExtract(
        extract_depth=extract_depth,
        include_images=include_images,
    )


def extract_urls(
    urls: List[str],
    extract_depth: str = "basic",
    include_images: bool = False,
) -> Dict[str, Any]:
    """
    Extrae contenido de una o varias URLs usando Tavily Extract.
    """
    if not urls:
        return {"results": [], "failed_results": [], "response_time": 0}

    tool = get_tavily_extract_tool(
        extract_depth=extract_depth,
        include_images=include_images,
    )

    return tool.invoke(
        {
            "urls": urls,
            "extract_depth": extract_depth,
            "include_images": include_images,
        }
    )


def format_extract_result(result: Dict[str, Any]) -> str:
    """
    Convierte la respuesta de Tavily Extract en texto legible.
    """
    if not result:
        return "No se obtuvo contenido extraído."

    extracted = result.get("results", [])
    failed = result.get("failed_results", [])

    lines = []

    if extracted:
        lines.append("Contenido extraído:")
        for idx, item in enumerate(extracted, start=1):
            url = item.get("url", "Sin URL")
            raw_content = item.get("raw_content", "Sin contenido")
            snippet = raw_content[:2500] if raw_content else "Sin contenido"
            lines.append(f"{idx}. URL: {url}\n{snippet}")

    if failed:
        lines.append("URLs con fallo de extracción:")
        for idx, item in enumerate(failed, start=1):
            lines.append(f"{idx}. {item}")

    if not lines:
        return "No se pudo extraer contenido útil de las URLs."

    return "\n\n".join(lines)