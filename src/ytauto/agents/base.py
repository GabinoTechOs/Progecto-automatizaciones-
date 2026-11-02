from __future__ import annotations

from ..config import ChannelConfig
from ..llm import LLM

POLITICAS = """Políticas que SIEMPRE debes respetar (son lo que mantiene el canal monetizado):
- YouTube desmonetiza el contenido "inauténtico": producido en masa, repetitivo o plantillas con cambios
  mínimos. Cada pieza debe aportar valor propio: análisis, opinión, investigación, narrativa o edición original.
- Si un video muestra personas, lugares o hechos realistas generados o alterados con IA, hay que activar la
  divulgación de "contenido alterado o sintético" al subirlo.
- Nada de clickbait engañoso: título y miniatura deben cumplirse en el video.
- No uses material con copyright ajeno salvo uso legítimo claro; sugiere material de stock o propio.
- Los datos y cifras deben ser verificables; si no estás seguro de un dato, dilo."""


class Agent:
    """Agente base: combina su rol, el contexto del canal y las políticas en el prompt de sistema."""

    rol: str = ""

    def __init__(self, llm: LLM, canal: ChannelConfig):
        self.llm = llm
        self.canal = canal

    @property
    def system(self) -> str:
        return (
            f"{self.rol}\n\n"
            f"## Contexto del canal\n{self.canal.as_context()}\n\n"
            f"## {POLITICAS}\n\n"
            f"Responde siempre en {self.canal.idioma}."
        )
