"""Esquemas de salida estructurada de cada agente."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------- Nicho ----------
class NicheScore(BaseModel):
    nicho: str
    demanda: int = Field(description="1-10: volumen de búsqueda e interés sostenido")
    competencia: int = Field(description="1-10: 10 = muy saturado")
    rpm_estimado_usd: str = Field(description="Rango estimado de RPM en USD, p. ej. '3-8'")
    potencial_afiliados: int = Field(description="1-10")
    viabilidad_faceless: int = Field(description="1-10")
    evergreen: int = Field(description="1-10: cuánto dura vigente el contenido")
    puntuacion_total: int = Field(description="0-100, ponderada")
    subnichos_recomendados: list[str]
    riesgos: list[str]
    justificacion: str


class NicheReport(BaseModel):
    ranking: list[NicheScore]
    recomendacion: str
    posicionamiento: str = Field(description="Ángulo diferenciador: por qué alguien elige ESTE canal")
    pilares_de_contenido: list[str] = Field(description="3-5 temas fijos del canal")


# ---------- Ideas ----------
class VideoIdea(BaseModel):
    titulo_provisional: str
    gancho: str = Field(description="Primera frase del video (0-5 s)")
    intencion: str = Field(description="busqueda | navegacion | tendencia")
    pilar: str
    palabra_clave_principal: str
    por_que_funciona: str
    puntuacion_viral: int = Field(description="1-10")
    dificultad_produccion: int = Field(description="1-10")


class IdeaBatch(BaseModel):
    ideas: list[VideoIdea]


# ---------- Guion ----------
class ScriptSection(BaseModel):
    nombre: str = Field(description="gancho, intro, bloque_1, ..., cta, cierre")
    inicio_seg: int
    narracion: str
    visuales: str = Field(description="B-roll, gráficos o texto en pantalla sugeridos")
    retencion: str = Field(description="Técnica de retención usada (loop abierto, pattern interrupt...)")


class VideoScript(BaseModel):
    titulo: str
    duracion_estimada_seg: int
    secciones: list[ScriptSection]
    fuentes: list[str] = Field(description="Fuentes de los datos citados")
    notas_para_editor: str


# ---------- SEO ----------
class SEOPackage(BaseModel):
    titulos: list[str] = Field(description="3-5 variantes para test A/B, máx. 70 caracteres")
    descripcion: str
    capitulos: list[str] = Field(description="Formato '00:00 Título'")
    etiquetas: list[str]
    hashtags: list[str]
    comentario_fijado: str
    playlist_sugerida: str


# ---------- Miniatura ----------
class ThumbnailConcept(BaseModel):
    concepto: str
    texto_en_miniatura: str = Field(description="Máximo 4 palabras")
    composicion: str
    colores: list[str]
    emocion: str
    prompt_imagen: str = Field(description="Prompt en inglés para un generador de imágenes")


class ThumbnailPack(BaseModel):
    conceptos: list[ThumbnailConcept]


# ---------- Shorts ----------
class ShortClip(BaseModel):
    titulo: str
    gancho: str
    guion: str = Field(description="Narración completa, 30-55 s")
    texto_en_pantalla: list[str]
    cta: str
    plataformas: list[str]
    hashtags: list[str]


class ShortsPack(BaseModel):
    shorts: list[ShortClip]


# ---------- Calendario ----------
class CalendarSlot(BaseModel):
    dia: str
    hora: str
    plataforma: str
    tipo: str = Field(description="video_largo | short | comunidad | live")
    tema: str
    objetivo: str


class ContentCalendar(BaseModel):
    semana: list[CalendarSlot]
    notas: str


# ---------- Analítica ----------
class AnalyticsInsight(BaseModel):
    hallazgo: str
    evidencia: str
    accion: str
    impacto_esperado: str


class AnalyticsReport(BaseModel):
    resumen: str
    insights: list[AnalyticsInsight]
    proximos_videos_sugeridos: list[str]
    progreso_monetizacion: str
