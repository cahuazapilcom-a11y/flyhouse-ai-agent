import re
from typing import Tuple

from agents import (
    RRHHAgent,
    LogisticoAgent,
    FinanzasAgent,
    ProyectosAgent,
    ComercialAgent,
    SupervisorAgent,
)
from app.settings import OPENAI_API_KEY
from tools.tavily_search_tool import search_web, format_search_result
from tools.tavily_extract_tool import extract_urls, format_extract_result


class AgentRouter:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("Falta OPENAI_API_KEY en el archivo .env")

        self.rrhh = RRHHAgent(OPENAI_API_KEY)
        self.logistica = LogisticoAgent(OPENAI_API_KEY)
        self.finanzas = FinanzasAgent(OPENAI_API_KEY)
        self.proyectos = ProyectosAgent(OPENAI_API_KEY)
        self.comercial = ComercialAgent(OPENAI_API_KEY)
        self.supervisor = SupervisorAgent(OPENAI_API_KEY)

    def detect_area(self, user_input: str) -> str:
        text = user_input.lower().strip()

        rrhh_keywords = [
            "rrhh", "recursos humanos", "personal", "trabajador", "empleado",
            "asistencia", "planilla", "planillas", "vacaciones", "contrato",
            "contratos", "capacitacion", "capacitaciones", "reglamento",
            "boleta", "boletas", "descanso", "licencia laboral"
        ]

        logistica_keywords = [
            "logistica", "compra", "compras", "proveedor", "proveedores",
            "inventario", "almacen", "despacho", "despachos", "entrega",
            "entregas", "abastecimiento", "kardex", "materiales", "stock"
        ]

        finanzas_keywords = [
            "finanzas", "pago", "pagos", "egreso", "egresos", "ingreso",
            "ingresos", "impuesto", "impuestos", "cuentas por pagar",
            "cuentas por cobrar", "flujo de caja", "factura", "facturas",
            "desembolso", "desembolsos", "tributo", "sunat", "cobranza"
        ]

        proyectos_keywords = [
            "proyecto", "proyectos", "cronograma", "cronogramas", "avance",
            "avances", "licencia", "licencias", "plano", "planos",
            "presupuesto", "presupuestos", "obra", "expediente", "expedientes",
            "replanteo", "conformidad", "construcción", "constructivo"
        ]

        comercial_keywords = [
            "comercial", "venta", "ventas", "cliente", "clientes",
            "beneficiario", "beneficiarios", "captacion", "captación",
            "prospecto", "prospectos", "seguimiento", "elegibilidad",
            "cierre comercial", "promotora", "campaña comercial"
        ]

        supervisor_keywords = [
            "supervisor", "supervisión", "operacion", "operaciones",
            "resumen general", "resumen operativo", "vision general",
            "visión general", "coordinacion", "coordinación",
            "gerencia", "gerencial", "ejecutivo", "ejecutiva", "estratégico",
            "estrategico", "impacto general", "panorama general"
        ]

        if any(keyword in text for keyword in rrhh_keywords):
            return "rrhh"
        if any(keyword in text for keyword in logistica_keywords):
            return "logistica"
        if any(keyword in text for keyword in finanzas_keywords):
            return "finanzas"
        if any(keyword in text for keyword in proyectos_keywords):
            return "proyectos"
        if any(keyword in text for keyword in comercial_keywords):
            return "comercial"
        if any(keyword in text for keyword in supervisor_keywords):
            return "supervisor"

        return "supervisor"

    def needs_web_search(self, user_input: str) -> bool:
        text = user_input.lower()

        web_terms = [
            "actual",
            "vigente",
            "último",
            "ultimo",
            "hoy",
            "reciente",
            "noticia",
            "noticias",
            "gobierno",
            "ministerio",
            "sunat",
            "ley",
            "norma",
            "normativa",
            "reglamento nacional",
            "subsidio",
            "bono",
            "programa estatal",
            "decreto",
            "resolución",
            "resolucion",
            "2025",
            "2026",
        ]

        return any(term in text for term in web_terms)

    def is_management_query(self, user_input: str) -> bool:
        text = user_input.lower()

        management_terms = [
            "resumen ejecutivo",
            "resumen gerencial",
            "para gerencia",
            "para dirección",
            "para direccion",
            "impacto operativo",
            "riesgos",
            "recomendación",
            "recomendacion",
            "toma de decisiones",
            "panorama general",
            "situación actual",
            "situacion actual",
        ]

        return any(term in text for term in management_terms)

    def contains_url(self, user_input: str) -> bool:
        url_pattern = r"https?://[^\s]+"
        return bool(re.search(url_pattern, user_input))

    def extract_first_url(self, user_input: str) -> str | None:
        url_pattern = r"https?://[^\s]+"
        match = re.search(url_pattern, user_input)
        return match.group(0) if match else None

    def route_internal(self, area: str, user_input: str) -> Tuple[str, str]:
        if area == "rrhh":
            return "RRHH", self.rrhh.run(user_input)

        if area == "logistica":
            return "Logística", self.logistica.run(user_input)

        if area == "finanzas":
            return "Finanzas", self.finanzas.run(user_input)

        if area == "proyectos":
            return "Proyectos", self.proyectos.run(user_input)

        if area == "comercial":
            return "Comercial", self.comercial.run(user_input)

        return "Supervisor", self.supervisor.run(user_input)

    def route(self, user_input: str) -> Tuple[str, str]:
        area = self.detect_area(user_input)

        # CASO 1: Si el usuario pega una URL, usamos extracción web
        if self.contains_url(user_input):
            url = self.extract_first_url(user_input)

            extract_result = extract_urls(
                urls=[url],
                extract_depth="basic",
                include_images=False,
            )
            web_text = format_extract_result(extract_result)

            # Si además parece gerencial, el supervisor lo resume
            if self.is_management_query(user_input):
                final_response = self.supervisor.summarize_for_management(
                    topic=user_input,
                    internal_context="No se proporcionó contexto interno adicional para esta consulta basada en URL.",
                    web_context=web_text,
                )
                return "Supervisor + Web Extract", final_response

            return "Web Extract", web_text

        # CASO 2: Si necesita búsqueda web, combinamos interno + web + supervisor
        if self.needs_web_search(user_input):
            internal_area, internal_response = self.route_internal(area, user_input)

            web_result = search_web(
                query=user_input,
                topic="general",
                max_results=5,
                search_depth="basic",
            )
            web_response = format_search_result(web_result)

            if self.is_management_query(user_input):
                final_response = self.supervisor.summarize_for_management(
                    topic=user_input,
                    internal_context=f"Área interna detectada: {internal_area}\n\n{internal_response}",
                    web_context=web_response,
                )
                return f"{internal_area} + Web + Supervisor Gerencial", final_response

            final_response = self.supervisor.run_with_combined_context(
                user_input=user_input,
                internal_context=f"Área interna detectada: {internal_area}\n\n{internal_response}",
                web_context=web_response,
            )
            return f"{internal_area} + Web + Supervisor", final_response

        # CASO 3: Si no necesita web y parece gerencial, el supervisor resume la respuesta interna
        if self.is_management_query(user_input):
            internal_area, internal_response = self.route_internal(area, user_input)

            final_response = self.supervisor.summarize_for_management(
                topic=user_input,
                internal_context=f"Área interna detectada: {internal_area}\n\n{internal_response}",
                web_context="No se realizó búsqueda web porque la consulta no parecía requerir información externa actualizada.",
            )
            return f"{internal_area} + Supervisor Gerencial", final_response

        # CASO 4: Consulta interna normal
        return self.route_internal(area, user_input)