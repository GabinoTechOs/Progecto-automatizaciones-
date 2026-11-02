from __future__ import annotations

from ..models import ShortsPack, VideoScript
from .base import Agent


class ShortsRepurposer(Agent):
    rol = (
        "Eres editor de formato corto (YouTube Shorts, TikTok, Reels). Conviertes un video largo en "
        "clips que funcionan solos: gancho en el primer segundo, una sola idea, ritmo rápido y un final "
        "que invita a ver el video completo o a seguir la cuenta. Adaptas hashtags y CTA a cada plataforma."
    )

    def repurpose(self, guion: VideoScript, cantidad: int | None = None) -> ShortsPack:
        cantidad = cantidad or self.canal.shorts_por_video
        cuerpo = "\n\n".join(f"[{s.nombre}] {s.narracion}" for s in guion.secciones)
        plataformas = [p for p in self.canal.plataformas if p != "youtube"] or ["youtube_shorts"]
        return self.llm.structured(
            self.system,
            f"Extrae {cantidad} shorts del guion '{guion.titulo}' para: {', '.join(plataformas)}.\n\n"
            f"Guion:\n{cuerpo}\n\n"
            "Cada short debe aportar valor por sí mismo (no un simple recorte) y durar 30-55 s.",
            ShortsPack,
            effort="medium",
        )
