"""SCADA WEB INTERACTIVO | Público, solo lectura, demo + Firebase.

Inicia con: py -m streamlit run app.py
Sin FIREBASE_DATABASE_URL los valores son SIMULADOS y los controles NO actúan sobre equipos.
"""
from __future__ import annotations

import math
import os
import random
from datetime import datetime, timezone
from html import escape

import requests
import streamlit as st

st.set_page_config(
    page_title="SCADA Industrial · Centro de monitoreo",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
html, body, [class*="css"], [data-testid="stApp"] {font-family:'DM Sans', sans-serif;}
.stApp {background: radial-gradient(ellipse at 88% 0%, #112c40 0%, #081321 44%, #08111e 100%);}
.block-container {max-width: 1420px; padding-top: 1.6rem; padding-bottom: 3rem;}
h1, h2, h3, h4 {font-family:'Space Grotesk', sans-serif; letter-spacing:-.025em;}
[data-testid="stSidebar"] {background:#0c1b2b; border-right:1px solid #1c3447;}
[data-testid="stSidebar"] h2 {letter-spacing:-.02em;}
[data-testid="stMetric"] {background:#112238;border:1px solid #27445b; padding:14px 17px; border-radius:15px;}
[data-testid="stVerticalBlock"] {gap:.65rem;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.75rem;}
header[data-testid="stHeader"] {background:transparent;}
.stButton button {border-radius:10px;}
.hero {display:flex;justify-content:space-between;gap:18px;align-items:center;
 background:linear-gradient(105deg,rgba(17,58,76,.9),rgba(12,30,47,.9));border:1px solid #285063;
 border-radius:18px;padding:22px 27px;margin-bottom:18px;}
.hero .small {color:#5fdac9; font-weight:800;letter-spacing:2px;font-size:11px;text-transform:uppercase;}
.hero h1 {color:#f4fbff;font-size:clamp(25px,3vw,39px);line-height:1.12;margin:6px 0 9px;}
.hero .sub {color:#abc7d5;font-size:13px;}
.live-pill {border:1px solid #3c756a;border-radius:100px;padding:9px 13px;
 font-weight:800;color:#a0f7d7;font-size:11px;letter-spacing:.8px;white-space:nowrap;
 background:#123b35;display:flex;align-items:center;gap:9px;}
.pulse {width:8px;height:8px;background:#61e0b1;border-radius:50%;display:inline-block;box-shadow:0 0 0 4px #61e0b124;animation:beacon 1.6s infinite;}
.pulse.warn {background:#ffba66;box-shadow:0 0 0 4px #ffba6624;}
@keyframes beacon {0%,100%{opacity:1;box-shadow:0 0 0 3px #61e0b128}50%{opacity:.6;box-shadow:0 0 0 10px #61e0b100}}
.section-tag {font-weight:700; font-size:12px; letter-spacing:1.7px; color:#6acdc5;margin:14px 0 12px;text-transform:uppercase;}
.sensor {background:linear-gradient(165deg,#11273b,#0d1d31);border:1px solid #28455b;
 border-radius:15px;padding:17px 18px 16px;min-height:162px; position:relative;overflow:hidden;}
.sensor:before {content:'';position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--accent,#42cdbb);}
.sensor .cap {font-size:11px;text-transform:uppercase;letter-spacing:1.5px;color:#93adbe;font-weight:700;}
.sensor .value {font-family:'Space Grotesk',sans-serif;font-size:clamp(22px,2.4vw,35px);font-weight:700;color:#edfaff;margin-top:13px;white-space:nowrap;}
.sensor .unit {font-size:14px;font-weight:500;color:#8fb1c2;}
.sensor .foot {display:flex;justify-content:space-between;align-items:center;gap:8px;
 margin-top:15px;color:#91aabd;font-size:11px;}
.gauge {height:6px;border-radius:10px;background:#20364a;overflow:hidden;margin-top:14px;}
.gauge .fill {height:100%;width:var(--fill,50%);border-radius:10px;background:var(--accent,#42cdbb);transition:width .8s ease;}
.circuit {background:linear-gradient(140deg,#11243b,#0c1c2f);border:1px solid #254258;
 border-radius:16px;padding:15px 18px 13px;min-height:205px;}
.circuit-head {display:flex;justify-content:space-between;align-items:center;font-size:12px;
 color:#a9c3d2;letter-spacing:1px;font-weight:700;text-transform:uppercase;margin-bottom:17px;}
.circuit-area {display:flex;align-items:center;justify-content:space-around;gap:2px;padding:9px 0 10px;}
.node {min-width:82px;text-align:center;flex:1;}
.node-box {width:64px;height:64px;border:1px solid #315d6b;border-radius:16px;background:#173748;
 display:flex;align-items:center;justify-content:center;margin:0 auto 10px;position:relative;}
.node-label {font-size:12px;font-weight:800;color:#d1e8ee;}
.node-detail {font-size:10px;color:#88a3b7;margin-top:2px;}
.cable {height:2px;flex:1;min-width:12px;max-width:100px;background:#245164;position:relative;overflow:hidden;align-self:center;margin-bottom:22px;}
.cable:after {content:'';display:block;position:absolute;width:26px;height:3px;top:-1px;left:-30px;
 background:#49edc1;box-shadow:0 0 12px #4af1bb;animation:transmit 2s linear infinite;}
@keyframes transmit {to{left:110%}}
.fan-wrap {width:64px;height:64px;display:flex;align-items:center;justify-content:center;}
.fan {width:42px;height:42px;color:#50e2c1;filter:drop-shadow(0 0 7px #38ba9870);}
.fan.spinning {animation:spin .75s linear infinite;}
.fan.stopped {color:#607f8f;}
@keyframes spin {to{transform:rotate(360deg)}}
.status {background:linear-gradient(140deg,#11283b,#0e1d31);border:1px solid #29445b;
 border-radius:16px;padding:18px;min-height:205px;display:flex;flex-direction:column;justify-content:space-between;}
.status .headline {font-weight:800;font-size:12px;color:#a7c1cf;letter-spacing:1.2px;text-transform:uppercase;}
.status .big {font-size:27px;color:var(--color,#55dfb6);font-weight:800;font-family:'Space Grotesk';margin-top:13px;}
.status .desc {font-size:12px;color:#9bb6c7;line-height:1.5;}
.alert-flash {animation:flash 1.3s infinite;}
@keyframes flash {0%,100%{opacity:1}50%{opacity:.55}}
.mini {font-size:12px;color:#99b6c4;margin:6px 0 14px;}
.footer-note {font-size:11px;color:#8aa1af;line-height:1.7;border-top:1px solid #253b50;margin-top:17px;padding-top:16px;}
@media(max-width:750px){.hero{padding:16px;align-items:flex-start;flex-direction:column;}
 .hero h1{font-size:26px}.sensor{min-height:142px}.circuit-area{gap:0}.node-box{width:50px;height:50px}.node{min-width:58px}
 .fan-wrap{width:50px;height:50px}.fan{width:32px;height:32px}}
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


def firebase_url() -> str:
    try:
        secret = st.secrets.get("FIREBASE_DATABASE_URL", "")
    except (FileNotFoundError, OSError):
        secret = ""
    return str(secret or os.getenv("FIREBASE_DATABASE_URL", "")).strip().rstrip("/")


FIREBASE_URL = firebase_url()
ES_DEMO = not bool(FIREBASE_URL)


def safe_number(value):
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def demo_reset():
    st.session_state.pop("demo_actual", None)
    st.session_state.pop("historial", None)
    st.session_state.pop("last_scenario", None)


with st.sidebar:
    st.markdown("## ⚙️ Panel de pruebas")
    if ES_DEMO:
        st.info("🧪 MODO DEMO: controles solo para simular datos. No operan el PLC ni el ESP32.")
        st.toggle("Simulación en movimiento", value=True, key="demo_moviendose")
        st.selectbox(
            "Escenario de prueba",
            ["Operación normal", "Temperatura elevada", "Gas elevado", "Alarma general"],
            key="escenario",
        )
        st.toggle("Ajustar lecturas manualmente", value=False, key="demo_manual")
        if st.session_state.demo_manual:
            st.slider("Temperatura (°C)", 0, 120, 33, key="temp_manual")
            st.slider("Gas (ADC)", 0, 4095, 1260, key="gas_manual")
            st.slider("Voltaje (V)", 0, 250, 127, key="volt_manual")
            st.slider("Corriente (A)", 0.0, 35.0, 7.3, step=0.1, key="corr_manual")
            st.toggle("Ventilador (simulado)", value=True, key="vent_manual")
            st.toggle("Alarma (simulada)", value=False, key="alarma_manual")
        if st.button("↺ Reiniciar simulación", use_container_width=True):
            demo_reset()
            st.rerun()
        st.caption("Cada visitante tiene su propia simulación independiente.")
    else:
        st.success("Fuente configurada: Firebase Realtime Database")
        st.caption("El tablero es de consulta pública; no ofrece mandos remotos.")
    st.divider()
    st.markdown("**Guía de colores**")
    st.markdown("🟢 Valores informativos\n\n🟠 Advertencia del escenario\n\n🔴 Alarma reportada")
    st.caption("MQ-6: valor ADC sin calibración a ppm. Los colores demo son ilustrativos y NO son límites de seguridad certificados.")
    st.divider()
    st.caption("SCADA Web · Prototipo didáctico\n\nESP32 + Siemens S7-1200 + Python")


TARGETS = {
    "Operación normal": (32.5, 1260, 127.1, 7.3, True, False),
    "Temperatura elevada": (86, 1290, 127.0, 8.1, True, True),
    "Gas elevado": (33, 3250, 126.6, 7.7, True, True),
    "Alarma general": (92, 3380, 119.0, 12.0, True, True),
}


def leer_demo() -> dict:
    escenario = st.session_state.escenario
    objetivo = TARGETS[escenario]
    manual = bool(st.session_state.demo_manual)
    movimiento = bool(st.session_state.demo_moviendose)
    if manual:
        vals = [st.session_state.temp_manual, st.session_state.gas_manual,
                st.session_state.volt_manual, st.session_state.corr_manual]
        ventilador = bool(st.session_state.vent_manual)
        alarma = bool(st.session_state.alarma_manual)
    else:
        if "demo_actual" not in st.session_state:
            st.session_state.demo_actual = list(objetivo[:4])
        vals = st.session_state.demo_actual
        if movimiento:
            for i, destino in enumerate(objetivo[:4]):
                ruido = [0.6, 27, 0.6, 0.18][i]
                vals[i] = vals[i] + .33 * (destino - vals[i]) + random.uniform(-ruido, ruido)
            vals[1] = max(0, min(4095, vals[1]))
        ventilador = objetivo[4]
        alarma = objetivo[5]
    return {
        "temperatura_c": round(float(vals[0]), 1),
        "gas_adc": int(vals[1]),
        "voltaje_v": round(float(vals[2]), 1),
        "corriente_a": round(float(vals[3]), 2),
        "ventilador": ventilador,
        "alarma": alarma,
        "modo_demo": True,
        "actualizado_utc": datetime.now(timezone.utc).isoformat(),
    }


def leer_firebase() -> dict:
    r = requests.get(f"{FIREBASE_URL}/publico.json", timeout=6)
    r.raise_for_status()
    data = r.json()
    return data if isinstance(data, dict) else {}


def dato_fecha(datos: dict) -> tuple[bool, str]:
    raw = datos.get("actualizado_utc")
    if not isinstance(raw, str) or not raw:
        return False, "Sin marca de tiempo"
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return False, "Hora recibida sin zona horaria"
        age = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).total_seconds()
        if age < -30:
            return False, "Reloj de origen desajustado"
        return age <= 30, f"Último dato hace {max(0, int(age))} segundos · {dt.astimezone(timezone.utc):%H:%M:%S} UTC"
    except ValueError:
        return False, "Marca de tiempo inválida"


def tarjeta(etiqueta: str, valor, unidad: str, maximo: float, accent: str, pie: str) -> str:
    v = safe_number(valor)
    v_str = "Sin dato" if v is None else (f"{v:,.0f}" if unidad == "ADC" else f"{v:,.2f}" if unidad == "A" else f"{v:,.1f}")
    pct = 0 if v is None else max(0, min(100, 100 * v / maximo))
    return f'''<div class="sensor" style="--accent:{accent};--fill:{pct:.1f}%">
        <div class="cap">{escape(etiqueta)}</div>
        <div class="value">{v_str} <span class="unit">{escape(unidad)}</span></div>
        <div class="gauge"><div class="fill"></div></div>
        <div class="foot"><span>{escape(pie)}</span><span>{pct:.0f}% escala visual</span></div>
    </div>'''


def ventilador_svg(activo: bool) -> str:
    clase = "spinning" if activo else "stopped"
    return f'''<svg class="fan {clase}" viewBox="0 0 64 64" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-label="Ventilador">
    <path d="M32 30C22 25 18 12 26 7c9-6 16 5 10 23 10-5 23-1 22 9-1 12-15 12-24-1 0 11-8 20-17 15C7 48 12 34 30 34c-11-3-19-13-12-21 7-8 19 0 14 17Z" opacity=".86"/>
    <circle cx="32" cy="32" r="7" fill="#15384a" stroke="currentColor" stroke-width="3"/>
    <circle cx="32" cy="32" r="2.1" fill="currentColor"/>
    </svg>'''


def esquema(ventilador: bool | None) -> str:
    es_activo = ventilador is True
    fan_descr = "GIRANDO" if es_activo else "PARADO" if ventilador is False else "SIN DATO"
    return f'''<div class="circuit">
     <div class="circuit-head"><span>Flujo de datos y equipo</span><span style="color:#69dcca">● VISUALIZACIÓN</span></div>
     <div class="circuit-area">
       <div class="node"><div class="node-box"><span style="font-size:28px">📟</span></div><div class="node-label">Sensores</div><div class="node-detail">MQ-6 · K · SCT</div></div>
       <div class="cable"></div>
       <div class="node"><div class="node-box"><span style="font-size:26px">🧠</span></div><div class="node-label">ESP32</div><div class="node-detail">Adquisición</div></div>
       <div class="cable"></div>
       <div class="node"><div class="node-box"><span style="font-size:28px">☁️</span></div><div class="node-label">Nube</div><div class="node-detail">Firebase*</div></div>
       <div class="cable"></div>
       <div class="node"><div class="node-box"><div class="fan-wrap">{ventilador_svg(es_activo)}</div></div><div class="node-label">Ventilador</div><div class="node-detail">{fan_descr}</div></div>
     </div></div>'''


def caja_estado(alarma: bool | None, activo: bool, demo: bool) -> str:
    if not activo:
        titulo, color, desc = "SIN CONEXIÓN", "#ffb66c", "Datos ausentes o desactualizados. No se confirma el estado actual."
    elif alarma is True:
        titulo, color, desc = "ALARMA SIMULADA" if demo else "ALARMA ACTIVA", "#ff6d79", "Evento de demostración." if demo else "Alarma informada por el control local."
    elif alarma is False:
        titulo, color, desc = "ESCENARIO NORMAL" if demo else "SIN ALARMAS", "#5de4b7", "Valores de prueba. No corresponden a sensores reales." if demo else "El equipo local no reporta alarmas."
    else:
        titulo, color, desc = "SIN ESTADO", "#ffb66c", "No se ha recibido el bit de alarma del equipo local."
    css = " alert-flash" if alarma is True and activo else ""
    return f'''<div class="status" style="--color:{color}">
    <div><div class="headline">Estado del sistema</div><div class="big{css}">● {titulo}</div></div>
    <div class="desc">{desc}</div></div>'''


def guardar_historial(datos: dict) -> None:
    if "historial" not in st.session_state:
        st.session_state.historial = []
    h = st.session_state.historial
    h.append({
        "Temperatura (°C)": safe_number(datos.get("temperatura_c")),
        "Voltaje (V)": safe_number(datos.get("voltaje_v")),
        "Corriente (A)": safe_number(datos.get("corriente_a")),
        "Gas (ADC)": safe_number(datos.get("gas_adc")),
    })
    if len(h) > 70:
        del h[:-70]


st.markdown(
    '<div class="hero"><div><div class="small">Industrial telemetry · v2.0</div>'
    '<h1>Centro de monitoreo SCADA</h1><div class="sub">Panel eléctrico • ESP32 • Siemens S7-1200 • Python</div></div>'
    '<div class="live-pill"><i class="pulse"></i> PANTALLA INTERACTIVA</div></div>',
    unsafe_allow_html=True,
)

INTERVALO = "2s" if ES_DEMO and st.session_state.demo_moviendose else "5s" if not ES_DEMO else None


@st.fragment(run_every=INTERVALO)
def tablero():
    if ES_DEMO:
        datos = leer_demo()
    else:
        try:
            datos = leer_firebase()
        except (requests.RequestException, ValueError) as exc:
            st.error("No se pudieron consultar los datos. Verifica Firebase y la conexión.")
            st.caption(str(exc))
            return
        if not datos:
            st.warning("Todavía no hay datos publicados en Firebase.")
            return

    demo = ES_DEMO or datos.get("modo_demo") is True
    actualizado, leyenda = dato_fecha(datos)
    valido = True if demo else actualizado
    if demo:
        st.warning("🧪 **DEMOSTRACIÓN:** los valores son simulados. Los controles no activan ningún equipo físico.")
    elif not actualizado:
        st.error("🔴 **DATOS DESACTUALIZADOS:** no se confirma el estado actual de los equipos.")
    else:
        st.success("🟢 Datos recibidos del publicador local")
    if not demo:
        st.caption(leyenda)
    else:
        st.caption("Simulación individual en tu navegador · Gráficas actualizadas cada 2 s cuando está en movimiento")

    st.markdown('<div class="section-tag">01 / Variables en línea</div>', unsafe_allow_html=True)
    v = st.columns(4, gap="small")
    specs = [
        ("Temperatura", datos.get("temperatura_c"), "°C", 120, "#58ddc3", "Termopar tipo K"),
        ("Sensor de gas", datos.get("gas_adc"), "ADC", 4095, "#febd69", "MQ-6 · No mide ppm"),
        ("Voltaje AC", datos.get("voltaje_v"), "V", 250, "#65aaf5", "ZMPT101B"),
        ("Corriente AC", datos.get("corriente_a"), "A", 35, "#b294ff", "SCT-013"),
    ]
    for col, spec in zip(v, specs):
        with col:
            st.markdown(tarjeta(*spec), unsafe_allow_html=True)

    st.markdown('<div class="section-tag">02 / Vista animada del proceso</div>', unsafe_allow_html=True)
    izq, der = st.columns([2.2, 1], gap="small")
    ventilador = datos.get("ventilador") if isinstance(datos.get("ventilador"), bool) else None
    alarma = datos.get("alarma") if isinstance(datos.get("alarma"), bool) else None
    with izq:
        st.markdown(esquema(ventilador), unsafe_allow_html=True)
    with der:
        st.markdown(caja_estado(alarma, valido, demo), unsafe_allow_html=True)

    st.markdown('<div class="section-tag">03 / Tendencias actualizándose</div>', unsafe_allow_html=True)
    guardar_historial(datos)
    historico = st.session_state.historial
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🌡️ Temperatura · historial de pantalla**")
        st.line_chart([r["Temperatura (°C)"] for r in historico], height=194, color="#50ddc2")
        st.markdown("**⚡ Voltaje AC · historial de pantalla**")
        st.line_chart([r["Voltaje (V)"] for r in historico], height=194, color="#6daeff")
    with c2:
        st.markdown("**🔥 Gas ADC · historial de pantalla**")
        st.line_chart([r["Gas (ADC)"] for r in historico], height=194, color="#ffbd70")
        st.markdown("**🔌 Corriente AC · historial de pantalla**")
        st.line_chart([r["Corriente (A)"] for r in historico], height=194, color="#b799ff")

    st.markdown(
        '<div class="footer-note">* En modo demostración, el flujo animado es conceptual: no hay conexión real con ESP32, PLC o Firebase.'
        '<br>Las gráficas guardan únicamente muestras desde que abriste esta página, no un historial persistente.'
        '<br>El estado público es informativo y de solo lectura. Nunca sustituye las protecciones eléctricas ni la seguridad local del PLC.'
        '</div>',
        unsafe_allow_html=True,
    )


tablero()
