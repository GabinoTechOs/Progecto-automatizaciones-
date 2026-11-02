"""Capa fina sobre la API de Claude.

Todos los agentes hablan con Claude a través de `ClaudeLLM`, que ofrece dos operaciones:

* `structured(...)`  -> devuelve un objeto Pydantic validado (salidas estructuradas).
* `research(...)`    -> investiga en la web (herramienta web_search) y devuelve texto.

Se puede sustituir por cualquier objeto con la misma interfaz (p. ej. un falso en los tests).
"""

from __future__ import annotations

import os
from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

DEFAULT_MODEL = "claude-opus-5-5"
# Si el clasificador de seguridad rechaza una petición, la API la reintenta en otro modelo.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
WEB_SEARCH_TOOL = {"type": "web_search_20260209", "name": "web_search", "max_uses": 8}


class LLMError(RuntimeError):
    pass


class LLM(Protocol):
    def structured(self, system: str, prompt: str, schema: type[T], effort: str = "high") -> T: ...

    def research(self, system: str, prompt: str) -> str: ...


class ClaudeLLM:
    def __init__(self, model: str | None = None, client=None):
        import anthropic

        self.model = model or os.getenv("YTAUTO_MODEL", DEFAULT_MODEL)
        # Sin argumentos el SDK toma ANTHROPIC_API_KEY (o un perfil de `ant auth login`).
        self.client = client or anthropic.Anthropic()

    # ------------------------------------------------------------------ #
    def structured(self, system: str, prompt: str, schema: type[T], effort: str = "high") -> T:
        response = self.client.beta.messages.parse(
            model=self.model,
            max_tokens=16000,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            output_format=schema,
            betas=[FALLBACK_BETA],
            fallbacks="default",
        )
        self._check(response)
        if response.parsed_output is None:
            raise LLMError("Claude no devolvió una salida válida para el esquema " + schema.__name__)
        return response.parsed_output

    # ------------------------------------------------------------------ #
    def research(self, system: str, prompt: str) -> str:
        """Investigación con búsqueda web. Gestiona `pause_turn` (turnos largos del servidor)."""
        messages: list = [{"role": "user", "content": prompt}]
        for _ in range(5):
            with self.client.beta.messages.stream(
                model=self.model,
                max_tokens=32000,
                system=system,
                messages=messages,
                tools=[WEB_SEARCH_TOOL],
                thinking={"type": "adaptive"},
                output_config={"effort": "high"},
                betas=[FALLBACK_BETA],
                fallbacks="default",
            ) as stream:
                response = stream.get_final_message()
            self._check(response)
            if response.stop_reason != "pause_turn":
                return "\n".join(b.text for b in response.content if b.type == "text").strip()
            messages = [*messages, {"role": "assistant", "content": response.content}]
        raise LLMError("La investigación no terminó tras varios intentos.")

    # ------------------------------------------------------------------ #
    @staticmethod
    def _check(response) -> None:
        if response.stop_reason == "refusal":
            detail = getattr(response, "stop_details", None)
            raise LLMError(f"Claude rechazó la petición: {getattr(detail, 'explanation', '') or 'sin detalle'}")
        if response.stop_reason == "max_tokens":
            raise LLMError("La respuesta se cortó por max_tokens; acorta la petición o súbelo.")
