# Estrategia: nicho, contenido y monetización

Esta guía es el "manual de juego" que siguen los agentes de `ytauto`. Úsala para tomar las decisiones que
la IA no debe tomar sola.

> ⚠️ Los umbrales y las políticas de YouTube cambian. Verifica los requisitos vigentes en
> [YouTube Partner Program](https://support.google.com/youtube/answer/72851) antes de planificar.

---

## 1. Elegir (y afinar) el nicho

Un buen nicho para monetizar cumple **tres de estas cuatro** condiciones:

| Criterio | Pregunta clave | Señal positiva |
|---|---|---|
| **Demanda** | ¿La gente busca y ve esto todos los meses? | Canales pequeños con videos de 100k+ views (outliers) |
| **RPM** | ¿Los anunciantes pagan bien por esta audiencia? | Finanzas, software, IA, negocios, educación, tecnología |
| **Monetización extra** | ¿Hay productos/afiliados que recomendar? | Programas de afiliados con comisión recurrente, cursos, plantillas |
| **Sostenibilidad** | ¿Puedes hacer 100 videos sin quemarte? | Al menos 3-5 pilares de contenido con decenas de temas cada uno |

**Regla de oro:** no compitas en el nicho amplio ("finanzas"); gana en un **subnicho + ángulo**
("finanzas para freelancers latinos que cobran en dólares"). El agente `ytauto nicho` propone el
posicionamiento y los pilares.

RPM orientativo para audiencia hispana (muy variable según país; EE.UU. y España pagan más que LATAM):
- Alto: finanzas, inversión, software/SaaS, IA para negocios, bienes raíces.
- Medio: tecnología, educación, salud, productividad, autos.
- Bajo: entretenimiento, curiosidades, gaming, humor, compilaciones (compensan con volumen).

## 2. Sistema de contenido

**Mezcla 70/20/10**
- **70 % búsqueda (evergreen):** responden preguntas concretas ("cómo...", "mejor X para...", "X vs Y").
  Traen views durante años y convierten bien en afiliados.
- **20 % navegación/tendencia:** historias, listas, polémicas del nicho, noticias. Traen picos y suscriptores.
- **10 % experimentos:** formatos nuevos. Si uno se dispara, se convierte en serie.

**Embudo multiplataforma**
```
Shorts / TikTok / Reels  ──►  Video largo de YouTube  ──►  Lista de correo / comunidad  ──►  Producto o afiliado
   (descubrimiento)            (confianza + AdSense)          (activo propio)               (ingresos altos)
```
Cada video largo genera 3+ shorts (`ytauto video` ya los crea) que enlazan al video completo.

**Fórmula de un video que retiene**
1. **0-5 s:** gancho que confirma la promesa del título y la miniatura.
2. **5-30 s:** por qué importa y qué va a obtener quien se quede.
3. **Bloques de valor** con un loop abierto ("en un momento te enseño el error que...") y un cambio visual cada 30-60 s.
4. **CTA** después de entregar valor, nunca al principio.
5. **Cierre** que manda a otro video (sesión más larga = más recomendaciones).

**Métricas que importan (en orden)**
1. CTR de impresiones (objetivo inicial 4-10 %).
2. Retención a los 30 s (>65-70 %) y duración media.
3. Views en las primeras 24-48 h vs la mediana del canal.
4. Suscriptores por cada 1.000 views.

`ytauto analizar` compara cada video con la mediana de TU canal y te dice qué repetir.

## 3. Rutas de monetización (de más rápida a más rentable)

| Fuente | Cuándo | Notas |
|---|---|---|
| **Afiliados** | Desde el video 1 | Enlaces en descripción y comentario fijado. Divulga siempre que son afiliados. |
| **YouTube Partner Program – nivel inicial** | ~500 suscriptores + actividad reciente | Membresías, Super Thanks, compras. |
| **YouTube Partner Program – anuncios** | 1.000 suscriptores + 4.000 h de visualización (12 meses) **o** 10 M de vistas de Shorts (90 días) | Ingresos por AdSense. |
| **Producto digital propio** | Desde ~1.000-5.000 suscriptores fieles | Plantillas, guías, mini-cursos. El margen más alto. |
| **Patrocinios** | Desde ~5.000-10.000 suscriptores en nicho de RPM alto | Cobra por video o por CPM; ten un media kit. |
| **Servicios / consultoría** | Cualquier momento | Si tu nicho es B2B, un solo cliente puede valer más que el AdSense de un año. |

## 4. Automatización responsable (para NO perder la monetización)

YouTube desmonetiza el **contenido inauténtico**: videos producidos en masa, repetitivos o hechos con
plantillas con cambios mínimos. Automatizar está bien; **publicar sin aportar nada propio, no**.

Lo que se automatiza con `ytauto`:
- Investigación de nicho y tendencias, ideas, guiones base, SEO, conceptos de miniatura, shorts, calendario, analítica, subida programada.

Lo que debe tener tu toque humano:
- **Revisión y edición del guion** con tu opinión, experiencia o investigación propia.
- **Verificación de datos** (los guiones incluyen fuentes: revísalas).
- **Voz y edición**: voz propia o clonada con permiso, edición con ritmo, visuales originales o de stock con licencia.
- **Divulgación de IA**: si muestras personas, lugares o hechos realistas generados/alterados con IA, marca la casilla al subir (`ytauto subir --ia-realista`).

## 5. Plan de 90 días

| Semana | Objetivo |
|---|---|
| 1 | `ytauto nicho` → elegir subnicho, posicionamiento y 3-5 pilares. Crear canal, banner, trailer. |
| 2 | `ytauto ideas -n 30` → elegir las 12 mejores. Producir los 2 primeros videos con `ytauto video`. |
| 3-6 | 2 videos largos + 7 shorts por semana (`ytauto semana`). Afiliados activos desde el día 1. |
| 7 | Primer `ytauto analizar`: doblar lo que funciona, cortar lo que no. Probar 2 formatos nuevos. |
| 8-12 | Convertir los formatos ganadores en series. Lanzar lead magnet (guía gratis) para capturar correos. |
| 13 | Revisar progreso hacia YPP; si hay audiencia fiel, validar un producto digital con preventa. |
