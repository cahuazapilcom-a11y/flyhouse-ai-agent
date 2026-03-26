from typing import Any, Dict, Optional

from langchain_tavily import TavilySearch

from app.settings import TAVILY_API_KEY


def get_tavily_search_tool(
    max_results: int = 5,
    topic: str = "general",
    include_answer: bool = True,
    include_raw_content: bool = False,
    search_depth: str = "basic",
) -> TavilySearch:
    """
    Crea y devuelve la herramienta oficial de Tavily Search para LangChain.
    """
    if not TAVILY_API_KEY:
        raise ValueError("Falta TAVILY_API_KEY en el archivo .env")

    return TavilySearch(
        max_results=max_results,
        topic=topic,
        include_answer=include_answer,
        include_raw_content=include_raw_content,
        search_depth=search_depth,
    )


def search_web(
    query: str,
    topic: str = "general",
    max_results: int = 5,
    search_depth: str = "basic",
    time_range: Optional[str] = None,
    include_domains: Optional[list[str]] = None,
    exclude_domains: Optional[list[str]] = None,
) -> Dict[str, Any]:
    """
    Ejecuta una búsqueda web con Tavily y devuelve el resultado crudo.
    """
    tool = get_tavily_search_tool(
        max_results=max_results,
        topic=topic,
        include_answer=True,
        include_raw_content=False,
        search_depth=search_depth,
    )

    payload: Dict[str, Any] = {
        "query": query,
    }

    if time_range:
        payload["time_range"] = time_range
    if include_domains:
        payload["include_domains"] = include_domains
    if exclude_domains:
        payload["exclude_domains"] = exclude_domains

    return tool.invoke(payload)


def format_search_result(result: Dict[str, Any]) -> str:
    """
    Convierte la respuesta de Tavily Search en texto legible.
    """
    if not result:
        return "No se obtuvo respuesta de Tavily."

    query = result.get("query", "")
    answer = result.get("answer", "")
    results = result.get("results", [])

    lines = []

    if query:
        lines.append(f"Consulta web: {query}")

    if answer:
        lines.append(f"Respuesta breve de Tavily:\n{answer}")

    if results:
        lines.append("Fuentes encontradas:")
        for idx, item in enumerate(results[:5], start=1):
            title = item.get("title", "Sin título")
            url = item.get("url", "Sin URL")
            content = item.get("content", "Sin contenido")
            lines.append(
                f"{idx}. {title}\n"
                f"   URL: {url}\n"
                f"   Resumen: {content}"
            )

    if not lines:
        return "No se encontraron resultados útiles en la web."

    return "\n\n".join(lines)