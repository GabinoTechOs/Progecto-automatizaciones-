"""Orquestación: de una idea a un paquete de publicación completo listo para producir."""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from .agents import ScriptWriter, SEOOptimizer, ShortsRepurposer, ThumbnailDesigner
from .config import ChannelConfig
from .llm import LLM
from .models import SEOPackage, ShortsPack, ThumbnailPack, VideoScript


def slugify(texto: str, max_len: int = 60) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = re.sub(r"[^a-zA-Z0-9]+", "-", texto).strip("-").lower()
    return texto[:max_len].rstrip("-") or "video"


@dataclass
class VideoPackage:
    guion: VideoScript
    seo: SEOPackage
    miniaturas: ThumbnailPack
    shorts: ShortsPack

    def save(self, carpeta: Path) -> Path:
        carpeta.mkdir(parents=True, exist_ok=True)
        for nombre, obj in vars(self).items():
            _dump(carpeta / f"{nombre}.json", obj)
        (carpeta / "README.md").write_text(self.to_markdown(), encoding="utf-8")
        return carpeta

    def to_markdown(self) -> str:
        g, s = self.guion, self.seo
        partes = [f"# {g.titulo}", "", "## Títulos (A/B)", *[f"- {t}" for t in s.titulos], "",
                  "## Guion"]
        for sec in g.secciones:
            partes += [f"### {sec.nombre} ({sec.inicio_seg}s)", sec.narracion, "",
                       f"*Visuales:* {sec.visuales}  ", f"*Retención:* {sec.retencion}", ""]
        partes += ["## Descripción", s.descripcion, "", *s.capitulos, "",
                   "## Etiquetas", ", ".join(s.etiquetas), "", "## Comentario fijado", s.comentario_fijado, "",
                   "## Miniaturas"]
        for i, m in enumerate(self.miniaturas.conceptos, 1):
            partes += [f"{i}. **{m.texto_en_miniatura}** — {m.concepto}", f"   - Prompt: `{m.prompt_imagen}`"]
        partes += ["", "## Shorts"]
        for sh in self.shorts.shorts:
            partes += [f"### {sh.titulo}", f"**Gancho:** {sh.gancho}", sh.guion, f"**CTA:** {sh.cta}", ""]
        partes += ["## Fuentes", *[f"- {f}" for f in g.fuentes], "",
                   "## Checklist antes de publicar",
                   "- [ ] Revisé y edité el guion con mi voz/opinión (evita contenido 'inauténtico').",
                   "- [ ] Verifiqué cada dato con su fuente.",
                   "- [ ] Si hay escenas realistas generadas con IA, activé la divulgación de contenido alterado.",
                   "- [ ] La miniatura y el título se cumplen en el video.",
                   "- [ ] Enlaces de afiliado con divulgación en la descripción."]
        return "\n".join(partes) + "\n"


def _dump(path: Path, obj: BaseModel) -> None:
    path.write_text(json.dumps(obj.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


class VideoPipeline:
    """idea -> guion -> SEO -> miniaturas -> shorts."""

    def __init__(self, llm: LLM, canal: ChannelConfig, salida: Path = Path("output")):
        self.canal = canal
        self.salida = salida
        self.guionista = ScriptWriter(llm, canal)
        self.seo = SEOOptimizer(llm, canal)
        self.disenador = ThumbnailDesigner(llm, canal)
        self.shorts = ShortsRepurposer(llm, canal)

    def run(self, idea: str, notas: str = "", palabra_clave: str = "", investigar: bool = True,
            log=print) -> tuple[VideoPackage, Path]:
        log("✍️  Escribiendo guion...")
        guion = self.guionista.write(idea, notas=notas, investigar=investigar)
        log("🔎 Optimizando SEO...")
        seo = self.seo.optimize(guion, palabra_clave=palabra_clave)
        log("🖼️  Diseñando miniaturas...")
        miniaturas = self.disenador.design(seo.titulos[0] if seo.titulos else guion.titulo)
        log("📱 Creando shorts...")
        shorts = self.shorts.repurpose(guion)
        paquete = VideoPackage(guion=guion, seo=seo, miniaturas=miniaturas, shorts=shorts)
        carpeta = paquete.save(self.salida / slugify(guion.titulo))
        return paquete, carpeta
