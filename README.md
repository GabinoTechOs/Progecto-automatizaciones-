# Proyecto Automatizaciones – Agentes de IA para YouTube y redes sociales

Sistema de agentes (con Claude) para **elegir nicho, crear contenido que genere views y monetizar**
canales de YouTube, Shorts, TikTok e Instagram Reels.

```
          ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
 nicho ─► │ NicheAnalyst │─► │IdeaGenerator │─► │ContentPlanner│ ─► calendario semanal
          └──────────────┘   └──────┬───────┘   └──────────────┘
                                    │ idea
          ┌──────────────┐   ┌──────▼───────┐   ┌──────────────┐   ┌────────────────┐
          │ ScriptWriter │─► │ SEOOptimizer │─► │ThumbnailDesig│─► │ShortsRepurposer│ ─► output/<video>/
          └──────────────┘   └──────────────┘   └──────────────┘   └────────────────┘
                                                                          │
                                       YouTube Data API (subida programada) ◄─┘
                                       AnalyticsCoach ◄── métricas del canal (bucle de mejora)
```

| Agente | Qué hace |
|---|---|
| `NicheAnalyst` | Investiga en la web y puntúa nichos (demanda, competencia, RPM, afiliados, faceless, evergreen). Propone posicionamiento y pilares. |
| `IdeaGenerator` | Detecta tendencias y videos *outlier* del nicho y genera ideas con gancho y palabra clave. |
| `ScriptWriter` | Guion completo con estructura de retención, visuales sugeridos y fuentes. |
| `SEOOptimizer` | Títulos A/B, descripción, capítulos, etiquetas, hashtags y comentario fijado. |
| `ThumbnailDesigner` | Conceptos de miniatura + prompts de imagen listos para un generador. |
| `ShortsRepurposer` | 3+ shorts por video largo, adaptados a cada plataforma. |
| `ContentPlanner` | Calendario semanal multiplataforma. |
| `AnalyticsCoach` | Lee tus métricas y te dice qué repetir, qué cortar y qué probar. |

La estrategia completa (nicho, sistema de contenido, monetización, plan de 90 días y cómo automatizar
**sin** que YouTube te desmonetice) está en **[docs/ESTRATEGIA.md](docs/ESTRATEGIA.md)**.

## Instalación

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[youtube,dev]"
cp .env.example .env                       # pon tu ANTHROPIC_API_KEY
cp config/canal.example.yaml config/canal.yaml   # describe tu canal
```

## Uso

```bash
ytauto nicho                               # ¿qué nicho conviene? (usa nichos_candidatos de canal.yaml)
ytauto nicho "IA para abogados" "recetas keto"   # o evalúa los que quieras
ytauto ideas -n 20 --tema "ahorro"         # ideas basadas en tendencias actuales
ytauto video "Cómo ahorrar 1.000 USD en 3 meses ganando el mínimo"
#   -> output/como-ahorrar-1-000-usd.../README.md  (guion, SEO, miniaturas, shorts, checklist)
ytauto semana                              # ideas + calendario de la semana
ytauto analizar --csv export_studio.csv    # o: ytauto analizar --youtube
ytauto subir final.mp4 output/<carpeta> --miniatura mini.png --publicar 2026-11-10T18:00:00-05:00
```

`--sin-web` desactiva la búsqueda web (más rápido y barato, pero sin datos actuales).

### Subir a YouTube (opcional)
1. En Google Cloud: crea un proyecto, habilita **YouTube Data API v3** y crea credenciales OAuth de tipo *App de escritorio*.
2. Guarda el JSON en `config/client_secret.json`. La primera vez se abrirá el navegador para autorizar.

## Desarrollo

```bash
pytest          # los tests usan un LLM falso: no gastan créditos ni necesitan red
```

Estructura:
```
config/canal.example.yaml   configuración del canal (nicho, audiencia, tono, cadencia, reglas)
docs/ESTRATEGIA.md          manual de nicho, contenido y monetización
src/ytauto/llm.py           cliente de Claude (salidas estructuradas + búsqueda web)
src/ytauto/agents/          un archivo por agente
src/ytauto/pipeline.py      idea -> paquete de video completo
src/ytauto/youtube/         subida programada y estadísticas (YouTube Data API)
src/ytauto/cli.py           comando `ytauto`
```

## Próximos pasos sugeridos
- Voz en off automática (TTS) y montaje con plantillas de edición.
- Generación de las miniaturas a partir de los prompts.
- Publicación automática en TikTok / Instagram.
- Ejecución programada (p. ej. `ytauto semana` cada lunes) y panel de métricas.
