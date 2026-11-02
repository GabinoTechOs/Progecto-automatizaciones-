from __future__ import annotations

from ..models import SEOPackage, VideoScript
from .base import Agent


class SEOOptimizer(Agent):
    rol = (
        "Eres especialista en SEO de YouTube. Los títulos priorizan CTR sin engañar (máx. ~60-70 "
        "caracteres, palabra clave al inicio cuando sea natural). Las descripciones abren con 2 líneas "
        "que venden el video, incluyen la palabra clave, capítulos, enlaces de afiliado/producto como "
        "marcadores [ENLACE] y una divulgación de afiliados si aplica."
    )

    def optimize(self, guion: VideoScript, palabra_clave: str = "") -> SEOPackage:
        secciones = "\n".join(f"{s.inicio_seg}s - {s.nombre}: {s.narracion[:200]}" for s in guion.secciones)
        return self.llm.structured(
            self.system,
            f"Crea el paquete SEO para este video.\nTítulo de trabajo: {guion.titulo}\n"
            f"Palabra clave principal: {palabra_clave or '(elígela tú)'}\n"
            f"Duración: {guion.duracion_estimada_seg // 60} min\n\nResumen por secciones:\n{secciones}\n\n"
            "Incluye 3-5 títulos para test A/B, descripción, capítulos con marcas de tiempo, "
            "10-15 etiquetas, 3 hashtags, comentario fijado que provoque respuestas y playlist sugerida.",
            SEOPackage,
            effort="medium",
        )
