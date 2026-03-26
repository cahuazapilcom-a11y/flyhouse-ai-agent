from agents.base_agent import BaseDocumentAgent
from langchain_core.messages import SystemMessage, HumanMessage


class SupervisorAgent(BaseDocumentAgent):
    def __init__(self, api_key: str):
        system_prompt = """
Eres Flyhouse Supervisor, agente supervisor general de Corporación Flyhouse SAC.

Tu función es ayudar con:
- operaciones
- visión general de procesos
- coordinación entre áreas
- resúmenes ejecutivos
- validación de información operativa
- integración de información interna y externa

Reglas:
1. Prioriza siempre la información documental interna de la empresa.
2. Si también se entrega contexto web, úsalo solo como complemento.
3. Si hay diferencias entre documentos internos y web, acláralo explícitamente.
4. No inventes procesos, estados, normas ni conclusiones no sustentadas.
5. Responde en tono ejecutivo, claro, profesional y útil para toma de decisiones.
6. Cuando la pregunta sea amplia, estructura la respuesta así:
   - Resumen ejecutivo
   - Hallazgos clave
   - Riesgos o vacíos
   - Recomendación
7. Si falta información suficiente, dilo claramente.
"""
        super().__init__(
            api_key=api_key,
            area_name="Supervisor",
            docs_folder="company_docs/operaciones",
            system_prompt=system_prompt,
            temperature=0.1,
        )

    def run(self, user_input: str) -> str:
        """
        Respuesta normal basada solo en contexto interno documental.
        """
        context = self._build_context(user_input)

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""
Pregunta del usuario:
{user_input}

Contexto documental interno:
{context}

Instrucciones:
- Responde como supervisor general.
- Usa principalmente el contexto documental interno.
- Si falta información, indícalo.
- No inventes datos.
- Da una respuesta ejecutiva y clara.
""".strip()
            ),
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def run_with_combined_context(
        self,
        user_input: str,
        internal_context: str = "",
        web_context: str = "",
    ) -> str:
        """
        Responde combinando contexto interno + contexto web.
        Ideal para preguntas mixtas:
        - normativa vigente + proceso interno
        - noticias/actualidad + impacto interno
        - validación externa + operación interna
        """
        if not internal_context:
            internal_context = self._build_context(user_input)

        if not web_context:
            web_context = "No se proporcionó contexto web adicional."

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""
Pregunta del usuario:
{user_input}

Contexto interno de la empresa:
{internal_context}

Contexto web o externo:
{web_context}

Instrucciones:
- Prioriza el contexto interno de la empresa.
- Usa el contexto web solo como complemento o contraste.
- Si hay diferencias entre ambas fuentes, explícalas claramente.
- No inventes información.
- Estructura la respuesta así:
  1. Resumen ejecutivo
  2. Hallazgos clave
  3. Riesgos, diferencias o vacíos detectados
  4. Recomendación práctica
""".strip()
            ),
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()

    def summarize_for_management(
        self,
        topic: str,
        internal_context: str = "",
        web_context: str = "",
    ) -> str:
        """
        Genera un resumen tipo gerencial para toma de decisiones.
        """
        if not internal_context:
            internal_context = self._build_context(topic)

        if not web_context:
            web_context = "No se proporcionó contexto web adicional."

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""
Tema a resumir para gerencia:
{topic}

Contexto interno:
{internal_context}

Contexto externo/web:
{web_context}

Genera una salida breve y ejecutiva con esta estructura:
- Situación actual
- Puntos críticos
- Impacto operativo
- Acción recomendada

Reglas:
- Usa lenguaje claro para gerencia.
- No inventes.
- Si algo no está documentado, indícalo.
""".strip()
            ),
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()