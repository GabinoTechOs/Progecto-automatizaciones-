"""Tests sin red: un LLM falso devuelve objetos mínimos válidos para cada esquema."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from ytauto import models
from ytauto.agents import ContentPlanner, IdeaGenerator, NicheAnalyst
from ytauto.config import ChannelConfig, load_config
from ytauto.pipeline import VideoPipeline, slugify
from ytauto.youtube.client import build_upload_body

SCRIPT = models.VideoScript(
    titulo="Cómo ahorrar 1.000 USD en 3 meses",
    duracion_estimada_seg=600,
    secciones=[models.ScriptSection(nombre="gancho", inicio_seg=0, narracion="¿Y si...?",
                                    visuales="texto", retencion="loop abierto")],
    fuentes=["https://ejemplo.org"],
    notas_para_editor="cortes rápidos",
)
FIXTURES = {
    models.VideoScript: SCRIPT,
    models.SEOPackage: models.SEOPackage(titulos=["Ahorra 1.000 USD"], descripcion="d", capitulos=["00:00 Intro"],
                                         etiquetas=["ahorro"], hashtags=["#ahorro"], comentario_fijado="c",
                                         playlist_sugerida="p"),
    models.ThumbnailPack: models.ThumbnailPack(conceptos=[models.ThumbnailConcept(
        concepto="c", texto_en_miniatura="1.000 USD", composicion="x", colores=["amarillo"], emocion="sorpresa",
        prompt_imagen="piggy bank")]),
    models.ShortsPack: models.ShortsPack(shorts=[models.ShortClip(
        titulo="t", gancho="g", guion="s", texto_en_pantalla=["a"], cta="c", plataformas=["tiktok"],
        hashtags=["#x"])]),
    models.IdeaBatch: models.IdeaBatch(ideas=[models.VideoIdea(
        titulo_provisional="i", gancho="g", intencion="busqueda", pilar="ahorro", palabra_clave_principal="k",
        por_que_funciona="p", puntuacion_viral=8, dificultad_produccion=3)]),
    models.ContentCalendar: models.ContentCalendar(semana=[], notas="n"),
    models.NicheReport: models.NicheReport(ranking=[], recomendacion="r", posicionamiento="p",
                                           pilares_de_contenido=["a"]),
}


class FakeLLM:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def structured(self, system, prompt, schema, effort="high"):
        self.calls.append(("structured", schema.__name__))
        assert "Contexto del canal" in system and "inauténtico" in system
        return FIXTURES[schema]

    def research(self, system, prompt):
        self.calls.append(("research", prompt[:30]))
        return "hallazgos con fuentes"


def canal() -> ChannelConfig:
    return ChannelConfig(nombre="Test", nicho="finanzas", plataformas=["youtube", "tiktok"])


def test_example_config_loads():
    cfg = load_config("config/canal.example.yaml")
    assert cfg.nicho and cfg.nichos_candidatos
    assert "Nicho:" in cfg.as_context()


def test_pipeline_saves_package(tmp_path):
    llm = FakeLLM()
    paquete, carpeta = VideoPipeline(llm, canal(), salida=tmp_path).run("ahorrar", log=lambda m: None)
    assert carpeta == tmp_path / "como-ahorrar-1-000-usd-en-3-meses"
    for f in ("guion.json", "seo.json", "miniaturas.json", "shorts.json", "README.md"):
        assert (carpeta / f).exists()
    assert json.loads((carpeta / "seo.json").read_text())["titulos"] == ["Ahorra 1.000 USD"]
    assert "Checklist" in (carpeta / "README.md").read_text()
    assert [c[1] for c in llm.calls if c[0] == "structured"] == [
        "VideoScript", "SEOPackage", "ThumbnailPack", "ShortsPack"]


def test_no_web_skips_research():
    llm = FakeLLM()
    NicheAnalyst(llm, canal()).analyze(["a", "b"], investigar=False)
    IdeaGenerator(llm, canal()).generate(3, investigar=False)
    assert all(kind == "structured" for kind, _ in llm.calls)


def test_week_plan():
    llm = FakeLLM()
    ideas = IdeaGenerator(llm, canal()).generate(3)
    cal = ContentPlanner(llm, canal()).plan_week(ideas)
    assert cal.notas == "n" and llm.calls[0][0] == "research"


def test_slugify():
    assert slugify("¡Cómo GANAR dinero con IA! (2026)") == "como-ganar-dinero-con-ia-2026"
    assert slugify("???") == "video"


def test_upload_body_scheduled():
    fecha = datetime(2026, 11, 10, 23, 0, tzinfo=timezone.utc)
    body = build_upload_body("t" * 150, "d", [f"tag{i}" for i in range(40)], fecha, True)
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["publishAt"].startswith("2026-11-10T23:00")
    assert body["status"]["containsSyntheticMedia"] is True
    assert len(body["snippet"]["title"]) == 100 and len(body["snippet"]["tags"]) == 30
    assert build_upload_body("t", "d", [], None, False)["status"]["privacyStatus"] == "public"
