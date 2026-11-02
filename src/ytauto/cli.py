"""Línea de comandos: `ytauto <comando>`.

    ytauto nicho                      # analiza y ordena los nichos candidatos
    ytauto ideas -n 15                # ideas de video con tendencias actuales
    ytauto video "idea del video"     # guion + SEO + miniaturas + shorts en output/<slug>/
    ytauto semana                     # ideas + calendario semanal
    ytauto analizar --csv datos.csv   # informe de analítica (o --youtube para leer tu canal)
    ytauto subir video.mp4 output/<slug> --publicar 2026-11-10T18:00:00-05:00
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from .config import load_config


def _print(obj: BaseModel) -> None:
    print(json.dumps(obj.model_dump(), ensure_ascii=False, indent=2))


def _save(obj: BaseModel, nombre: str) -> Path:
    out = Path("output")
    out.mkdir(exist_ok=True)
    path = out / f"{nombre}-{datetime.now():%Y%m%d-%H%M}.json"
    path.write_text(json.dumps(obj.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def diagnostico(llm, canal) -> int:
    """Prueba real y barata: 1 llamada a Claude que debe devolver ideas válidas para el canal."""
    import time

    from .agents import IdeaGenerator

    print(f"✔ Configuración cargada: canal '{canal.nombre}', nicho '{canal.nicho}'")
    print(f"… Llamando a Claude ({llm.model}) sin búsqueda web...")
    t0 = time.monotonic()
    try:
        ideas = IdeaGenerator(llm, canal).generate(3, investigar=False)
    except Exception as e:  # mostramos el error tal cual para poder corregirlo
        print(f"✘ Falló la llamada: {type(e).__name__}: {e}")
        return 1
    print(f"✔ Claude respondió en {time.monotonic() - t0:.1f}s con {len(ideas.ideas)} ideas válidas:")
    for i in ideas.ideas:
        print(f"   - {i.titulo_provisional}  (viral {i.puntuacion_viral}/10)")
    print("Todo listo. Prueba ahora: ytauto video \"<tu idea>\" --sin-web")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ytauto", description="Agentes de IA para canales de YouTube y redes.")
    p.add_argument("--config", help="Ruta a canal.yaml (por defecto config/canal.yaml)")
    p.add_argument("--sin-web", action="store_true", help="No usar búsqueda web (más rápido y barato)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("diagnostico", help="Comprueba configuración, clave y conexión real con Claude")

    s = sub.add_parser("nicho", help="Evalúa nichos y recomienda posicionamiento")
    s.add_argument("candidatos", nargs="*", help="Nichos a evaluar (por defecto los de canal.yaml)")

    s = sub.add_parser("ideas", help="Genera ideas de video")
    s.add_argument("-n", type=int, default=10)
    s.add_argument("--tema")

    s = sub.add_parser("video", help="Paquete completo para un video")
    s.add_argument("idea")
    s.add_argument("--notas", default="")
    s.add_argument("--keyword", default="")

    s = sub.add_parser("semana", help="Ideas + calendario de la semana")
    s.add_argument("-n", type=int, default=8)

    s = sub.add_parser("analizar", help="Analiza métricas del canal")
    g = s.add_mutually_exclusive_group(required=True)
    g.add_argument("--csv", type=Path, help="Exportación de YouTube Studio (CSV/JSON)")
    g.add_argument("--youtube", action="store_true", help="Leer estadísticas vía API")

    s = sub.add_parser("subir", help="Sube un video usando el paquete SEO generado")
    s.add_argument("video", type=Path)
    s.add_argument("paquete", type=Path, help="Carpeta output/<slug> creada por `ytauto video`")
    s.add_argument("--publicar", help="Fecha ISO 8601 con zona horaria para programar")
    s.add_argument("--miniatura", type=Path)
    s.add_argument("--titulo", type=int, default=0, help="Índice del título A/B a usar")
    s.add_argument("--ia-realista", action="store_true",
                   help="Declara contenido alterado/sintético realista (obligatorio si aplica)")
    return p


def main(argv: list[str] | None = None) -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    args = build_parser().parse_args(argv)
    canal = load_config(args.config)
    web = not args.sin_web

    if args.cmd == "subir":
        from .youtube.client import upload_video
        fecha = datetime.fromisoformat(args.publicar) if args.publicar else None
        vid = upload_video(args.video, args.paquete, fecha, args.miniatura, args.titulo, args.ia_realista)
        print(f"✅ Subido: https://youtu.be/{vid}")
        return 0

    from . import agents
    from .llm import ClaudeLLM
    llm = ClaudeLLM()

    if args.cmd == "diagnostico":
        return diagnostico(llm, canal)
    if args.cmd == "nicho":
        r = agents.NicheAnalyst(llm, canal).analyze(args.candidatos or None, investigar=web)
        _print(r); print(f"\nGuardado en {_save(r, 'nicho')}", file=sys.stderr)
    elif args.cmd == "ideas":
        r = agents.IdeaGenerator(llm, canal).generate(args.n, args.tema, investigar=web)
        _print(r); print(f"\nGuardado en {_save(r, 'ideas')}", file=sys.stderr)
    elif args.cmd == "video":
        from .pipeline import VideoPipeline
        _, carpeta = VideoPipeline(llm, canal).run(args.idea, args.notas, args.keyword, investigar=web,
                                                    log=lambda m: print(m, file=sys.stderr))
        print(f"✅ Paquete listo en {carpeta}/ (abre README.md)")
    elif args.cmd == "semana":
        ideas = agents.IdeaGenerator(llm, canal).generate(args.n, investigar=web)
        cal = agents.ContentPlanner(llm, canal).plan_week(ideas)
        _print(cal); print(f"\nGuardado en {_save(ideas, 'ideas')} y {_save(cal, 'calendario')}", file=sys.stderr)
    elif args.cmd == "analizar":
        if args.youtube:
            from .youtube.client import channel_stats
            datos = json.dumps(channel_stats(), ensure_ascii=False)
        else:
            datos = args.csv.read_text(encoding="utf-8")
        r = agents.AnalyticsCoach(llm, canal).analyze(datos)
        _print(r); print(f"\nGuardado en {_save(r, 'analitica')}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
