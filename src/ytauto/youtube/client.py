"""Cliente de la YouTube Data API v3: subida programada y estadísticas.

Requisitos (una sola vez):
1. Crea un proyecto en Google Cloud y habilita "YouTube Data API v3".
2. Crea credenciales OAuth tipo "App de escritorio" y descarga el JSON a config/client_secret.json.
3. La primera ejecución abre el navegador para autorizar; el token se guarda en config/token.json.

Nota: los proyectos de Google Cloud no verificados suben los videos como privados hasta que
Google audita la app. Programar la publicación funciona igual una vez verificada.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
TOKEN_PATH = Path("config/token.json")


def _service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:  # pragma: no cover
        raise SystemExit("Instala las dependencias de YouTube: pip install -e '.[youtube]'") from e

    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            secrets = os.getenv("YOUTUBE_CLIENT_SECRETS", "config/client_secret.json")
            flow = InstalledAppFlow.from_client_secrets_file(secrets, SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def build_upload_body(titulo: str, descripcion: str, etiquetas: list[str], publicar_en: datetime | None,
                      contenido_sintetico: bool, categoria: str = "22", idioma: str = "es") -> dict:
    """Cuerpo de videos.insert. Si `publicar_en` se indica, el video queda privado y programado."""
    status: dict = {
        "privacyStatus": "private" if publicar_en else "public",
        "selfDeclaredMadeForKids": False,
        "containsSyntheticMedia": contenido_sintetico,
    }
    if publicar_en:
        status["publishAt"] = publicar_en.isoformat()
    return {
        "snippet": {
            "title": titulo[:100],
            "description": descripcion[:5000],
            "tags": etiquetas[:30],
            "categoryId": categoria,
            "defaultLanguage": idioma,
            "defaultAudioLanguage": idioma,
        },
        "status": status,
    }


def upload_video(video: Path, paquete: Path, publicar_en: datetime | None = None,
                 miniatura: Path | None = None, titulo_idx: int = 0,
                 contenido_sintetico: bool = False) -> str:
    """Sube `video` usando el seo.json de una carpeta generada por `ytauto video`. Devuelve el ID."""
    from googleapiclient.http import MediaFileUpload

    seo = json.loads((paquete / "seo.json").read_text(encoding="utf-8"))
    descripcion = seo["descripcion"] + "\n\n" + "\n".join(seo.get("capitulos", [])) + "\n\n" + " ".join(seo.get("hashtags", []))
    body = build_upload_body(seo["titulos"][titulo_idx], descripcion, seo.get("etiquetas", []),
                             publicar_en, contenido_sintetico)
    yt = _service()
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    video_id = resp["id"]
    if miniatura:
        yt.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(miniatura))).execute()
    return video_id


def channel_stats(max_videos: int = 50) -> list[dict]:
    """Estadísticas públicas de los últimos videos del canal autenticado (para `ytauto analizar`)."""
    yt = _service()
    canal = yt.channels().list(part="contentDetails", mine=True).execute()["items"][0]
    uploads = canal["contentDetails"]["relatedPlaylists"]["uploads"]
    ids: list[str] = []
    token = None
    while len(ids) < max_videos:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50,
                                    pageToken=token).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
    filas = []
    for i in range(0, len(ids[:max_videos]), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50])).execute()
        for v in r["items"]:
            filas.append({
                "titulo": v["snippet"]["title"],
                "publicado": v["snippet"]["publishedAt"],
                "duracion": v["contentDetails"]["duration"],
                **{k: int(x) for k, x in v["statistics"].items() if x.isdigit()},
            })
    return filas
