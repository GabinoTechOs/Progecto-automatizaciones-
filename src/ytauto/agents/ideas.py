from __future__ import annotations

from ..models import IdeaBatch
from .base import Agent


class IdeaGenerator(Agent):
    rol = (
        "Eres un estratega de contenido de YouTube obsesionado con el CTR y la retención. "
        "Generas ideas con demanda comprobable (lo que la gente busca o ya ve en masa), un ángulo "
        "propio y un gancho fuerte. Mezclas videos de búsqueda (evergreen, traen tráfico durante años) "
        "con videos de navegación/tendencia (picos de views y suscriptores)."
    )

    def generate(self, cantidad: int = 10, tema: str | None = None, investigar: bool = True) -> IdeaBatch:
        foco = f" centradas en: {tema}" if tema else ""
        tendencias = ""
        if investigar:
            tendencias = self.llm.research(
                self.system,
                f"Busca qué está funcionando AHORA en el nicho '{self.canal.nicho}'{foco}: videos recientes "
                "con muchas views en relación al tamaño del canal (outliers), preguntas frecuentes de la "
                "audiencia, noticias y tendencias. Lista hallazgos concretos con fuentes.",
            )
        return self.llm.structured(
            self.system,
            f"Genera {cantidad} ideas de video largo{foco}.\n\n"
            + (f"Tendencias y outliers detectados:\n{tendencias}\n\n" if tendencias else "")
            + "Para cada idea: título provisional (curiosidad + beneficio claro), gancho de los primeros "
            "5 segundos, intención (busqueda | navegacion | tendencia), pilar, palabra clave principal y "
            "por qué funcionaría. Ordénalas por puntuación viral descendente.",
            IdeaBatch,
        )
