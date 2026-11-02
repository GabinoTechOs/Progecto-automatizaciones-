from __future__ import annotations

from ..models import AnalyticsReport
from .base import Agent


class AnalyticsCoach(Agent):
    rol = (
        "Eres analista de canales de YouTube. Lees métricas (views, CTR de impresiones, duración media, "
        "% de retención, suscriptores ganados, RPM) y conviertes los datos en acciones concretas: qué "
        "repetir, qué dejar de hacer y qué probar. Comparas cada video con la mediana del canal, no con "
        "otros canales."
    )

    def analyze(self, datos: str) -> AnalyticsReport:
        return self.llm.structured(
            self.system,
            "Analiza estas métricas del canal (CSV o JSON exportado de YouTube Studio o de la API):\n\n"
            f"{datos}\n\n"
            "Detecta outliers (positivos y negativos), patrones de títulos/temas/duraciones que funcionan, "
            "y estima el progreso hacia el Programa de Partners (1.000 suscriptores + 4.000 horas de "
            "visualización pública en 12 meses, o 10 M de vistas de Shorts en 90 días; verifica los umbrales "
            "vigentes en tu país).",
            AnalyticsReport,
        )
