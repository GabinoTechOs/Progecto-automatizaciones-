from __future__ import annotations

from ..models import VideoScript
from .base import Agent


class ScriptWriter(Agent):
    rol = (
        "Eres guionista senior de YouTube. Escribes guiones que retienen: gancho que cumple la promesa "
        "del título en los primeros 5-15 s, loops abiertos, cambios de ritmo cada 30-60 s, ejemplos "
        "concretos y un CTA natural (no al principio). Escribes para el oído: frases cortas, segunda "
        "persona, sin relleno."
    )

    def write(self, idea: str, notas: str = "", investigar: bool = True) -> VideoScript:
        datos = ""
        if investigar:
            datos = self.llm.research(
                self.system,
                f"Reúne datos, cifras, ejemplos y casos reales verificables para un video sobre: {idea}. "
                "Incluye la fuente de cada dato.",
            )
        minutos = self.canal.duracion_objetivo_min
        return self.llm.structured(
            self.system,
            f"Escribe el guion completo de un video de ~{minutos} minutos sobre: {idea}\n\n"
            + (f"Notas del creador: {notas}\n\n" if notas else "")
            + (f"Investigación (usa solo datos de aquí y cita las fuentes):\n{datos}\n\n" if datos else "")
            + "Estructura: gancho, intro breve con la promesa, 3-6 bloques de valor, CTA a mitad o al "
            "final, cierre que enlace a otro video del canal. Indica visuales y técnica de retención "
            "en cada sección.",
            VideoScript,
        )
