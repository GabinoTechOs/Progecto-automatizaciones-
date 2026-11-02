"""Carga de la configuración del canal (config/canal.yaml)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field


class ChannelConfig(BaseModel):
    nombre: str
    idioma: str = "español"
    pais_objetivo: str = "LATAM"
    nicho: str = ""
    nichos_candidatos: list[str] = Field(default_factory=list)
    audiencia: str = ""
    tono: str = "cercano y directo"
    formato: Literal["faceless", "con_cara", "mixto"] = "faceless"
    duracion_objetivo_min: int = 10
    shorts_por_video: int = 3
    plataformas: list[str] = Field(default_factory=lambda: ["youtube", "youtube_shorts"])
    videos_largos_por_semana: int = 2
    shorts_por_semana: int = 7
    monetizacion: list[str] = Field(default_factory=lambda: ["adsense"])
    reglas: list[str] = Field(default_factory=list)

    def as_context(self) -> str:
        """Resumen del canal que se inyecta en el prompt de cada agente."""
        reglas = "\n".join(f"- {r}" for r in self.reglas) or "- (ninguna)"
        return (
            f"Canal: {self.nombre}\n"
            f"Idioma: {self.idioma} | Mercado: {self.pais_objetivo}\n"
            f"Nicho: {self.nicho or '(por definir)'}\n"
            f"Audiencia: {self.audiencia}\n"
            f"Tono: {self.tono}\n"
            f"Formato: {self.formato} | Duración objetivo: {self.duracion_objetivo_min} min\n"
            f"Plataformas: {', '.join(self.plataformas)}\n"
            f"Monetización: {', '.join(self.monetizacion)}\n"
            f"Reglas del canal:\n{reglas}"
        )


DEFAULT_PATHS = (Path("config/canal.yaml"), Path("config/canal.example.yaml"))


def load_config(path: str | Path | None = None) -> ChannelConfig:
    candidates = [Path(path)] if path else list(DEFAULT_PATHS)
    for p in candidates:
        if p.exists():
            data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
            return ChannelConfig.model_validate(data)
    raise FileNotFoundError(
        f"No se encontró la configuración del canal en: {', '.join(map(str, candidates))}. "
        "Copia config/canal.example.yaml a config/canal.yaml."
    )
