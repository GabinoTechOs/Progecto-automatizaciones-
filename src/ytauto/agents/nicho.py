from __future__ import annotations

from ..models import NicheReport
from .base import Agent


class NicheAnalyst(Agent):
    rol = (
        "Eres un estratega de crecimiento de YouTube especializado en elegir nichos rentables. "
        "Evalúas nichos por demanda real, saturación, RPM, potencial de afiliados y productos, "
        "viabilidad sin mostrar la cara y longevidad del contenido. Eres honesto: si un nicho está "
        "saturado o tiene RPM bajo, lo dices y propones un subnicho o ángulo que sí pueda ganar."
    )

    def analyze(self, candidatos: list[str] | None = None, investigar: bool = True) -> NicheReport:
        candidatos = candidatos or self.canal.nichos_candidatos or [self.canal.nicho]
        lista = "\n".join(f"- {c}" for c in candidatos)
        hallazgos = ""
        if investigar:
            hallazgos = self.llm.research(
                self.system,
                "Investiga en la web el estado actual (últimos 12 meses) de estos nichos en YouTube y "
                f"redes sociales para el mercado {self.canal.pais_objetivo}: tendencias de búsqueda, "
                "canales líderes y su tamaño, rangos de RPM/CPM reportados, programas de afiliados "
                f"relevantes y huecos de contenido sin cubrir.\n\nNichos:\n{lista}\n\n"
                "Resume los hallazgos con las fuentes.",
            )
        return self.llm.structured(
            self.system,
            "Evalúa y ordena estos nichos de mejor a peor oportunidad para este canal.\n\n"
            f"Nichos:\n{lista}\n\n"
            + (f"Investigación de mercado:\n{hallazgos}\n\n" if hallazgos else "")
            + "Pondera: demanda 25%, competencia (invertida) 20%, RPM 20%, afiliados/productos 15%, "
            "viabilidad faceless 10%, evergreen 10%. Propón el posicionamiento diferenciador y los "
            "pilares de contenido del nicho ganador.",
            NicheReport,
        )
