from __future__ import annotations

from ..models import ContentCalendar, IdeaBatch
from .base import Agent


class ContentPlanner(Agent):
    rol = (
        "Eres planificador de contenido multiplataforma. Organizas la semana para maximizar alcance "
        "sin quemar al creador: los videos largos en los días/horas de más actividad de la audiencia, "
        "shorts diarios que alimentan a los largos y publicaciones de comunidad para mantener el engagement."
    )

    def plan_week(self, ideas: IdeaBatch) -> ContentCalendar:
        lista = "\n".join(f"- {i.titulo_provisional} ({i.intencion}, pilar: {i.pilar})" for i in ideas.ideas)
        return self.llm.structured(
            self.system,
            f"Arma el calendario de la próxima semana con {self.canal.videos_largos_por_semana} videos "
            f"largos y {self.canal.shorts_por_semana} shorts repartidos entre {', '.join(self.canal.plataformas)}.\n"
            f"Ideas disponibles:\n{lista}\n\n"
            f"Usa horarios en la zona horaria principal de {self.canal.pais_objetivo} e indícala.",
            ContentCalendar,
            effort="medium",
        )
