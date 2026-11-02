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


class PendingResponse(Exception):
    """En modo manual: falta la respuesta a un prompt. `prompt_path` dice dónde está."""

    def __init__(self, prompt_path, response_path):
        self.prompt_path, self.response_path = prompt_path, response_path
        super().__init__(f"Falta la respuesta: {response_path}")


class ManualLLM:
    """Backend sin clave de API: copia/pega con claude.ai (o cualquier chat).

    Cada llamada escribe `<carpeta>/<id>-prompt.md`. Pega ese texto en claude.ai, guarda la respuesta
    en `<id>-respuesta.json` (o `.md` en investigación) y vuelve a ejecutar el mismo comando: los pasos
    ya respondidos se reutilizan y el pipeline avanza hasta el siguiente prompt pendiente.
    """

    model = "manual (claude.ai)"

    def __init__(self, carpeta: str | os.PathLike = "output/_manual"):
        from pathlib import Path

        self.dir = Path(carpeta)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _paths(self, *partes: str, ext: str):
        import hashlib

        h = hashlib.sha256("\x00".join(partes).encode()).hexdigest()[:10]
        return self.dir / f"{h}-prompt.md", self.dir / f"{h}-respuesta.{ext}"

    def structured(self, system: str, prompt: str, schema: type[T], effort: str = "high") -> T:
        import json

        p, r = self._paths(system, prompt, schema.__name__, ext="json")
        if r.exists():
            texto = r.read_text(encoding="utf-8").strip()
            if texto.startswith("```"):  # tolera respuestas pegadas dentro de ```json ... ```
                texto = texto.split("\n", 1)[1].rsplit("```", 1)[0]
            return schema.model_validate_json(texto)
        esquema = json.dumps(schema.model_json_schema(), ensure_ascii=False, indent=2)
        p.write_text(
            f"{system}\n\n---\n\n{prompt}\n\n---\n\nResponde ÚNICAMENTE con un objeto JSON válido que "
            f"cumpla este JSON Schema (sin texto antes ni después):\n\n```json\n{esquema}\n```\n",
            encoding="utf-8",
        )
        raise PendingResponse(p, r)

    def research(self, system: str, prompt: str) -> str:
        p, r = self._paths(system, prompt, "research", ext="md")
        if r.exists():
            return r.read_text(encoding="utf-8")
        p.write_text(f"{system}\n\n---\n\n{prompt}\n\n(Usa la búsqueda web si tu chat la tiene.)\n",
                     encoding="utf-8")
        raise PendingResponse(p, r)


def make_llm():
    """`YTAUTO_BACKEND=manual` usa ManualLLM; si no, la API de Claude."""
    if os.getenv("YTAUTO_BACKEND", "").lower() == "manual":
        return ManualLLM()
    return ClaudeLLM()


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
