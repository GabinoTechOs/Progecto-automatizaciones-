from __future__ import annotations

from ..models import ThumbnailPack
from .base import Agent


class ThumbnailDesigner(Agent):
    rol = (
        "Eres director de arte de miniaturas de YouTube. Una buena miniatura se entiende en 1 segundo "
        "en móvil: un solo foco, alto contraste, máximo 3-4 palabras que complementan (no repiten) el "
        "título, y una emoción o tensión clara."
    )

    def design(self, titulo: str, cantidad: int = 3) -> ThumbnailPack:
        return self.llm.structured(
            self.system,
            f"Diseña {cantidad} conceptos de miniatura distintos para el video: '{titulo}'. "
            "Cada uno con un prompt de imagen en inglés listo para un generador (16:9, 1280x720, "
            "sin texto en la imagen: el texto se añade después en el editor).",
            ThumbnailPack,
            effort="medium",
        )
