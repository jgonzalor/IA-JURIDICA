import base64
import random
import textwrap
import time
from datetime import date
from pathlib import Path

import streamlit as st

from data.knowledge_base import (
    CNPP_ENTRIES,
    CRIME_CARDS,
    LEGAL_WARNINGS,
    OFFICIAL_SOURCES,
    STAGE_GUIDES,
    SUGGESTION_RULES,
)
from utils.search_engine import build_missing_data_checklist, detect_suggestions, search_records
from utils.templates import TEMPLATE_BUILDERS

st.set_page_config(
    page_title="Sentinel Penal IA",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSS = """
<style>
:root {
  --card-bg: rgba(255,255,255,.78);
  --border: rgba(120,120,120,.18);
}
.block-container {padding-top: 1.5rem; padding-bottom: 2.5rem;}
.sentinel-hero {
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 1.4rem 1.6rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, rgba(38, 99, 235, .10), rgba(20, 184, 166, .08));
}
.sentinel-title {font-size: 2.05rem; font-weight: 800; margin: 0;}
.sentinel-subtitle {font-size: 1rem; opacity: .78; margin-top: .4rem; max-width: 980px;}
.card {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1rem 1.1rem;
  margin-bottom: .8rem;
  background: var(--card-bg);
  box-shadow: 0 1px 9px rgba(0,0,0,.035);
}
.card h4 {margin-top: 0; margin-bottom: .45rem;}
.badge {
  display: inline-block;
  padding: .16rem .48rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  margin-right: .35rem;
  font-size: .78rem;
  opacity: .82;
}
.small-muted {font-size: .88rem; opacity: .72;}
.warning-box {
  border-left: 4px solid #f59e0b;
  padding: .85rem 1rem;
  background: rgba(245, 158, 11, .08);
  border-radius: 10px;
  margin-bottom: .8rem;
}
.result-score {float:right; opacity: .55; font-size: .8rem;}
textarea {font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI";}
.sentinel-nav-overlay {
  position: fixed;
  inset: 0;
  z-index: 999999;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, rgba(15,23,42,.78), rgba(2,6,23,.92));
  backdrop-filter: blur(8px);
  pointer-events: none;
  animation: sentinelOverlayFade 7s ease-in-out forwards;
}
.sentinel-loader-card {
  min-width: 290px;
  max-width: 420px;
  padding: 1.3rem 1.45rem;
  text-align: center;
  border: 1px solid rgba(255,255,255,.20);
  border-radius: 28px;
  color: white;
  background: linear-gradient(145deg, rgba(255,255,255,.14), rgba(255,255,255,.06));
  box-shadow: 0 24px 80px rgba(0,0,0,.35);
}
.sentinel-loader-img {
  width: 148px;
  height: 148px;
  object-fit: cover;
  border-radius: 999px;
  background: white;
  padding: 6px;
  margin-bottom: .65rem;
  box-shadow: 0 14px 38px rgba(0,0,0,.32);
  animation: sentinelPulse 1.05s ease-in-out infinite;
}
.sentinel-loader-title {font-size: 1.05rem; font-weight: 800; margin-top: .3rem;}
.sentinel-loader-subtitle {font-size: .86rem; opacity: .82; margin-top: .25rem;}
.sentinel-progress {
  height: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(255,255,255,.18);
  margin-top: .9rem;
}
.sentinel-progress span {
  display:block; height:100%; width:44%; border-radius:999px;
  background: linear-gradient(90deg, rgba(255,255,255,.25), rgba(255,255,255,.95), rgba(255,255,255,.25));
  animation: sentinelBar 1.05s ease-in-out infinite;
}
.sentinel-click-pop {
  position: fixed;
  right: 24px;
  bottom: 24px;
  z-index: 999998;
  width: min(250px, 34vw);
  padding: .8rem .8rem .7rem;
  border: 1px solid rgba(15,23,42,.10);
  border-radius: 26px;
  background: rgba(255,255,255,.92);
  box-shadow: 0 18px 60px rgba(0,0,0,.22);
  text-align: center;
  pointer-events: none;
  animation: sentinelStickerPop .95s ease-in-out forwards;
}
.sentinel-click-pop img {width: 100%; border-radius: 20px; display:block;}
.sentinel-click-text {font-size:.83rem; font-weight:800; margin-top:.35rem; color:#0f172a;}
@keyframes sentinelOverlayFade {
  0% {opacity:0; transform: scale(1.02);}
  12% {opacity:1; transform: scale(1);}
  72% {opacity:1; transform: scale(1);}
  100% {opacity:0; transform: scale(.985); visibility:hidden;}
}
@keyframes sentinelPulse {
  0%, 100% {transform: scale(1) rotate(-1deg);}
  50% {transform: scale(1.045) rotate(1deg);}
}
@keyframes sentinelBar {
  0% {transform: translateX(-120%);}
  100% {transform: translateX(260%);}
}
@keyframes sentinelStickerPop {
  0% {opacity:0; transform: translateY(32px) scale(.75) rotate(-6deg);}
  18% {opacity:1; transform: translateY(0) scale(1.04) rotate(2deg);}
  72% {opacity:1; transform: translateY(0) scale(1) rotate(0deg);}
  100% {opacity:0; transform: translateY(18px) scale(.92) rotate(4deg); visibility:hidden;}
}
@media (max-width: 640px) {
  .sentinel-click-pop {right: 12px; bottom: 12px; width: 170px;}
  .sentinel-loader-card {min-width: 245px; margin: 0 18px;}
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

BASE_DIR = Path(__file__).resolve().parent
ASSET_DIR = BASE_DIR / "assets"
SHOW_ACTION_STICKER_EVERY_CLICK = True


@st.cache_data(show_spinner=False)
def asset_data_uri(filename: str, mime: str) -> str:
    """Carga un asset local como data URI para poder usarlo dentro de HTML/CSS."""
    path = ASSET_DIR / filename
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def show_navigation_overlay(module_name: str):
    """Animación breve al cargar la app o cambiar de módulo."""
    head_gif = asset_data_uri("sentinel_head_turn.gif", "image/gif")
    if not head_gif:
        return
    st.markdown(
        f'''
        <div class="sentinel-nav-overlay">
            <div class="sentinel-loader-card">
                <img class="sentinel-loader-img" src="{head_gif}" alt="Sentinel cargando">
                <div class="sentinel-loader-title">Sentinel Penal IA trabajando...</div>
                <div class="sentinel-loader-subtitle">Cargando módulo: <b>{module_name}</b></div>
                <div class="sentinel-progress"><span></span></div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def show_action_sticker(message: str = "Procesando solicitud..."):
    """Sticker emergente para acciones de análisis/generación."""
    if not SHOW_ACTION_STICKER_EVERY_CLICK and random.random() > 0.45:
        return
    sticker = asset_data_uri("sentinel_click_sticker.png", "image/png")
    if not sticker:
        return
    placeholder = st.empty()
    placeholder.markdown(
        f'''
        <div class="sentinel-click-pop">
            <img src="{sticker}" alt="Sentinel acción">
            <div class="sentinel-click-text">{message}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
    time.sleep(0.75)
    placeholder.empty()


def mark_navigation_change():
    st.session_state["nav_animation_pending"] = True


def hero(title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="sentinel-hero">
            <p class="sentinel-title">{title}</p>
            <div class="sentinel-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_warning_panel():
    with st.expander("⚠️ Avisos de uso responsable", expanded=False):
        for warning in LEGAL_WARNINGS:
            st.markdown(f"- {warning}")


def card(title: str, body: str, tags=None):
    tags = tags or []
    tag_html = "".join(f'<span class="badge">{t}</span>' for t in tags)
    st.markdown(
        f"""
        <div class="card">
            <h4>{title}</h4>
            <div>{body}</div>
            <div style="margin-top:.7rem">{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def article_card(entry):
    score = entry.get("_score")
    score_html = f'<span class="result-score">score {score}</span>' if score else ""
    st.markdown(
        f"""
        <div class="card">
            <h4>{entry['tema']} {score_html}</h4>
            <p><span class="badge">{entry['ley']} art. {entry['articulo']}</span><span class="badge">{entry['etapa']}</span></p>
            <p>{entry['resumen']}</p>
            <p><b>Uso práctico:</b> {entry['uso_practico']}</p>
            <p class="small-muted">Fuente: <a href="{entry['fuente']}" target="_blank">texto oficial</a></p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def crime_card(delito):
    st.markdown(
        f"""
        <div class="card">
            <h4>{delito['delito']}</h4>
            <p><span class="badge">{delito['articulos']}</span></p>
            <p><b>Referencia:</b> {delito['ley_referencia']}</p>
            <p><b>Tipo base:</b> {delito['tipo_base']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Elementos a revisar**")
        for x in delito["elementos"]:
            st.markdown(f"- {x}")
    with c2:
        st.markdown("**Datos útiles / evidencia**")
        for x in delito["datos_utiles"]:
            st.markdown(f"- {x}")
    if delito.get("alertas"):
        st.markdown("**Alertas**")
        for x in delito["alertas"]:
            st.warning(x)


def combined_search(text: str, limit: int = 8):
    cnpp = search_records(
        text,
        CNPP_ENTRIES,
        fields=("tema", "ley", "articulo", "etapa", "resumen", "keywords", "uso_practico"),
        limit=limit,
    )
    crimes = search_records(
        text,
        CRIME_CARDS,
        fields=("delito", "tipo_base", "keywords", "ley_referencia", "articulos"),
        limit=limit,
    )
    return cnpp, crimes


def page_inicio():
    hero(
        "⚖️ Sentinel Penal IA",
        "MVP de consulta interna para derecho penal mexicano, CNPP, evidencia digital, cadena de custodia y análisis preliminar de hechos. Diseñado para Streamlit Cloud.",
    )
    render_warning_panel()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Entradas CNPP", len(CNPP_ENTRIES))
    m2.metric("Fichas penales", len(CRIME_CARDS))
    m3.metric("Guías por etapa", len(STAGE_GUIDES))
    m4.metric("Plantillas", len(TEMPLATE_BUILDERS))

    st.markdown("### Qué hace esta versión")
    c1, c2, c3 = st.columns(3)
    with c1:
        card("Consulta por hechos", "Pega una narración y el sistema sugiere temas CNPP, delitos relacionados, datos faltantes y alertas procesales.", ["CNPP", "hechos"])
    with c2:
        card("Fichas y etapas", "Consulta etapas del procedimiento, cadena de custodia, actos con/sin control judicial, prueba y evidencia digital.", ["proceso", "prueba"])
    with c3:
        card("Borradores", "Genera bases editables de denuncia, solicitud de acto de investigación, preservación digital, cadena de custodia y teoría del caso.", ["formatos", "markdown"])

    st.markdown("### Recomendación de operación")
    st.info(
        "Úsala como apoyo interno: cada salida debe revisarse contra el CNPP, Código Penal Federal, código penal local, leyes especiales y criterios judiciales vigentes."
    )


def page_consulta():
    hero("🔎 Consulta inteligente penal", "Describe los hechos y recibe una guía inicial con referencias del CNPP, posibles delitos y alertas de evidencia.")
    render_warning_panel()

    ejemplo = """Ejemplo: La víctima recibió mensajes de WhatsApp desde un número desconocido. Le exigieron depositar dinero a una cuenta bancaria y amenazaron con hacerle daño a su familia. La víctima hizo una transferencia y conserva capturas, audios y comprobantes."""
    hechos = st.text_area("Narración de hechos", height=220, placeholder=ejemplo)
    enfoque = st.selectbox(
        "Enfoque principal",
        ["General", "Evidencia digital / metadatos", "CDR / telefonía", "Cadena de custodia", "Audiencia inicial", "Actos de investigación"],
    )

    if st.button("Analizar", type="primary", use_container_width=True):
        if not hechos.strip():
            st.warning("Escribe una narración de hechos para analizar.")
            return
        show_action_sticker("Analizando hechos...")
        query = f"{hechos} {enfoque}"
        cnpp, crimes = combined_search(query)
        suggestions = detect_suggestions(query, SUGGESTION_RULES)
        checklist = build_missing_data_checklist(query)

        st.markdown("## Resultado preliminar")
        c1, c2 = st.columns([1.15, .85])
        with c1:
            st.markdown("### Temas CNPP relacionados")
            if not cnpp:
                st.info("No se detectaron temas CNPP con la búsqueda textual. Intenta agregar palabras como cadena de custodia, cateo, prueba, audiencia, dato de prueba, etc.")
            for entry in cnpp[:6]:
                article_card(entry)
        with c2:
            st.markdown("### Posibles fichas penales")
            if not crimes:
                st.info("No se detectó una ficha penal clara. Revisa manualmente el tipo penal aplicable.")
            for delito in crimes[:4]:
                st.markdown(f"**{delito['delito']}** · {delito.get('_score')}  ")
                st.caption(delito["tipo_base"])
                for alert in delito.get("alertas", []):
                    st.warning(alert)

            st.markdown("### Alertas y próximos pasos")
            if suggestions:
                for s in suggestions:
                    st.markdown(f"- {s}")
            else:
                st.markdown("- Verificar competencia, requisito de procedibilidad y legislación aplicable.")
                st.markdown("- Identificar datos de prueba disponibles y actos pendientes.")

        st.markdown("### Datos que conviene completar")
        for item in checklist:
            st.checkbox(item, value=False)

        st.markdown("### Borrador breve de análisis")
        resumen = f"""
        Con base en la narración proporcionada, se recomienda tratar el análisis como una valoración preliminar de hechos probablemente constitutivos de delito, evitando afirmar responsabilidad penal antes de resolución jurisdiccional. Deben identificarse con precisión modo, tiempo, lugar, víctima, conducta atribuida, datos de prueba disponibles, origen lícito de la evidencia y necesidad de actos de investigación con o sin control judicial. En caso de evidencia digital, debe preservarse su integridad mediante cadena de custodia, hash, bitácora de obtención y metodología verificable.
        """
        st.write(textwrap.dedent(resumen).strip())


def page_cnpp():
    hero("📚 CNPP por etapas y temas", "Consulta guías rápidas del procedimiento penal y entradas fundamentales del CNPP.")
    render_warning_panel()

    tab1, tab2 = st.tabs(["Guías por etapa", "Buscador CNPP"])
    with tab1:
        etapa = st.selectbox("Selecciona una etapa o enfoque", list(STAGE_GUIDES.keys()))
        guide = STAGE_GUIDES[etapa]
        st.markdown(f"### {etapa}")
        st.write(guide["objetivo"])
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("**Puntos clave**")
            for p in guide["puntos_clave"]:
                st.markdown(f"- {p}")
        with c2:
            st.markdown("**Artículos relacionados**")
            for a in guide["articulos_relacionados"]:
                st.markdown(f"- {a}")
        st.markdown("---")
        st.markdown("**Entradas relacionadas en la base local**")
        related_query = etapa + " " + " ".join(guide["articulos_relacionados"])
        for entry in search_records(related_query, CNPP_ENTRIES, ("tema", "articulo", "etapa", "resumen", "keywords"), limit=6):
            article_card(entry)

    with tab2:
        q = st.text_input("Buscar en entradas CNPP", placeholder="Ej. cadena de custodia, prueba ilícita, cateo, vinculación...")
        if q:
            results = search_records(q, CNPP_ENTRIES, ("tema", "articulo", "etapa", "resumen", "keywords", "uso_practico"), limit=10)
        else:
            results = CNPP_ENTRIES[:10]
        for entry in results:
            article_card(entry)


def page_delitos():
    hero("🧩 Fichas penales", "Fichas de orientación con elementos a revisar y evidencia útil. Verifica siempre el código local aplicable.")
    render_warning_panel()

    q = st.text_input("Buscar delito o palabra clave", placeholder="fraude, robo, lesiones, extorsión, evidencia digital...")
    if q:
        cards = search_records(q, CRIME_CARDS, ("delito", "tipo_base", "keywords", "ley_referencia", "articulos"), limit=10)
    else:
        cards = CRIME_CARDS

    names = [c["delito"] for c in cards]
    if not names:
        st.warning("No encontré fichas con ese término.")
        return
    selected = st.selectbox("Selecciona ficha", names)
    delito = next(c for c in cards if c["delito"] == selected)
    crime_card(delito)


def page_generador():
    hero("📝 Generador de borradores", "Crea documentos base editables para investigación penal, evidencia digital y teoría del caso.")
    render_warning_panel()

    tipo = st.selectbox("Tipo de documento", list(TEMPLATE_BUILDERS.keys()))
    st.markdown("### Datos base")
    c1, c2 = st.columns(2)
    with c1:
        carpeta = st.text_input("Carpeta / expediente")
        victima = st.text_input("Víctima u ofendido")
        probable = st.text_input("Probable interviniente / imputado")
        lugar = st.text_input("Lugar")
    with c2:
        fecha_hecho = st.text_input("Fecha/hora del hecho")
        acto = st.text_input("Acto solicitado / diligencia")
        destinatario = st.text_input("Destinatario / institución / proveedor")
        identificador = st.text_input("Identificador digital: teléfono, cuenta, URL, ID, etc.")

    hechos = st.text_area("Hechos o antecedentes", height=160)

    with st.expander("Campos opcionales para cadena de custodia / evidencia digital"):
        c3, c4 = st.columns(2)
        with c3:
            indicio = st.text_input("Indicio")
            descripcion_indicio = st.text_input("Descripción del indicio")
            tipo_indicio = st.text_input("Tipo de indicio")
            serie = st.text_input("Marca/modelo/serie")
            estado = st.text_input("Estado observado")
            embalaje = st.text_input("Embalaje")
        with c4:
            fecha_recepcion = st.text_input("Fecha/hora de recepción")
            entrega = st.text_input("Entrega/localiza")
            recibe = st.text_input("Recibe")
            herramienta = st.text_input("Herramienta/método")
            md5 = st.text_input("Hash MD5")
            sha = st.text_input("Hash SHA-1/SHA-256")
            ruta = st.text_input("Ruta/nombre de imagen/respaldo")
            observaciones = st.text_input("Observaciones")

    with st.expander("Campos opcionales para preservación / teoría del caso"):
        periodo_inicio = st.text_input("Periodo inicio")
        periodo_fin = st.text_input("Periodo fin")
        dato_1 = st.text_input("Dato/medio 1")
        fuente_1 = st.text_input("Fuente 1")
        dato_2 = st.text_input("Dato/medio 2")
        fuente_2 = st.text_input("Fuente 2")
        dato_3 = st.text_input("Dato/medio 3")
        fuente_3 = st.text_input("Fuente 3")

    data = dict(
        carpeta=carpeta,
        victima=victima,
        probable=probable,
        lugar=lugar,
        fecha_hecho=fecha_hecho,
        acto=acto,
        destinatario=destinatario,
        identificador=identificador,
        hechos=hechos,
        indicio=indicio,
        descripcion_indicio=descripcion_indicio,
        tipo_indicio=tipo_indicio,
        serie=serie,
        estado=estado,
        embalaje=embalaje,
        fecha_recepcion=fecha_recepcion,
        entrega=entrega,
        recibe=recibe,
        herramienta=herramienta,
        md5=md5,
        sha=sha,
        ruta=ruta,
        observaciones=observaciones,
        periodo_inicio=periodo_inicio,
        periodo_fin=periodo_fin,
        dato_1=dato_1,
        fuente_1=fuente_1,
        dato_2=dato_2,
        fuente_2=fuente_2,
        dato_3=dato_3,
        fuente_3=fuente_3,
    )

    if st.button("Generar borrador", type="primary", use_container_width=True):
        show_action_sticker("Generando borrador...")
        q = f"{hechos} {acto} {identificador} {tipo}"
        cnpp, crimes = combined_search(q, limit=5)
        temas = cnpp[:4] + crimes[:3]
        draft = TEMPLATE_BUILDERS[tipo](data, temas)
        st.markdown("## Borrador generado")
        st.markdown(draft)
        filename = f"{tipo.lower().replace(' ', '_').replace('/', '_')}_{date.today().isoformat()}.md"
        st.download_button("Descargar borrador .md", draft.encode("utf-8"), file_name=filename, mime="text/markdown")


def page_fuentes():
    hero("🔗 Fuentes oficiales y actualización", "Control de fuentes para mantener la app viva y evitar referencias desactualizadas.")
    st.markdown("### Fuentes incorporadas")
    for source in OFFICIAL_SOURCES:
        st.markdown(
            f"""
            <div class="card">
                <h4>{source['nombre']}</h4>
                <p>{source['descripcion']}</p>
                <p><a href="{source['url']}" target="_blank">Abrir fuente oficial</a></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Cómo actualizar la base local")
    st.code(
        """# 1) Abrir data/knowledge_base.py
# 2) Agregar o editar entradas en CNPP_ENTRIES, CRIME_CARDS y STAGE_GUIDES
# 3) Verificar contra fuentes oficiales
# 4) Subir cambios a GitHub y redeploy en Streamlit Cloud""",
        language="bash",
    )
    st.info("Siguiente mejora recomendada: agregar un módulo de carga de PDFs oficiales y búsqueda por texto completo con embeddings o pgvector/Supabase.")


PAGES = {
    "Inicio": page_inicio,
    "Consulta inteligente": page_consulta,
    "CNPP por etapas": page_cnpp,
    "Fichas penales": page_delitos,
    "Generador de borradores": page_generador,
    "Fuentes oficiales": page_fuentes,
}

with st.sidebar:
    st.markdown("# ⚖️ Sentinel Penal IA")
    st.caption("Derecho penal México · CNPP · Evidencia digital")
    page = st.radio("Módulo", list(PAGES.keys()), key="selected_page", on_change=mark_navigation_change)
    st.markdown("---")
    st.caption("Base local inicial. Verificar siempre legislación vigente y criterios judiciales.")

if "first_load_animation_done" not in st.session_state:
    st.session_state["first_load_animation_done"] = True
    st.session_state["nav_animation_pending"] = True

if st.session_state.get("nav_animation_pending", False):
    show_navigation_overlay(page)
    st.session_state["nav_animation_pending"] = False

PAGES[page]()
