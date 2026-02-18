import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Visitas · FROCA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado para responsive y mobile
st.markdown("""
<style>
    /* Mobile responsive */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        iframe {
            width: 100% !important;
        }
    }
    
    /* Sidebar en mobile */
    @media (max-width: 768px) {
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
    
    /* Tabs más visibles */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

PERSONS = ["ANGELS","ARANTXA","CRISTINA","Mª JOSÉ","MONTSERRAT","NURIA","SARA","VANESA","EMMA"]
DUR_ORDER  = ["30 m","1 h","1h30","2 h","2h30","3 h","4 h","8 h"]
HORA_ORDER = ["7h","8h","9h","10h","11h","12h","13h","14h","15h","16h","17h"]
PERSON_COLORS = {
    "ANGELS":"#6366f1","ARANTXA":"#f59e0b","CRISTINA":"#10b981","Mª JOSÉ":"#3b82f6",
    "MONTSERRAT":"#ec4899","NURIA":"#8b5cf6","SARA":"#14b8a6","VANESA":"#f97316","EMMA":"#64748b"
}
DUR_COLORS = ["#c7d2fe","#a5b4fc","#818cf8","#6366f1","#4f46e5","#4338ca","#3730a3","#312e81"]
MESES = {"01":"Ene","02":"Feb","03":"Mar","04":"Abr","05":"May","06":"Jun",
         "07":"Jul","08":"Ago","09":"Sep","10":"Oct","11":"Nov","12":"Dic"}

EXCEL_PATH = Path(__file__).parent / "visitas_FROCA.xlsx"

# ── CARGA DE DATOS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="Datos", usecols=[0,2,3,4,6,7], header=0)
        df.columns = ["marca","persona","centro","fecha","hora","duracion"]
        df = df.dropna(subset=["fecha","persona","centro"])
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])
        df["persona"]  = df["persona"].astype(str).str.strip().str.upper()
        df["centro"]   = df["centro"].astype(str).str.strip().str.upper()
        df["hora"]     = df["hora"].astype(str).str.strip()
        df["duracion"] = df["duracion"].astype(str).str.strip()
        df["year"]     = df["fecha"].dt.year.astype(str)
        df["ym"]       = df["fecha"].dt.strftime("%Y-%m")
        df["mes_label"]= df["fecha"].dt.strftime("%m").map(MESES) + " " + df["fecha"].dt.strftime("%y")
        df = df[df["persona"].isin(PERSONS)]
        df = df[df["year"].isin(["2023","2024","2025","2026"])]
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

df_all = load_data()

if df_all.empty:
    st.error("No se pudieron cargar los datos del archivo Excel")
    st.stop()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard Visitas")
    st.markdown("**FROCA** · Seguimiento operativo")
    st.divider()

    year_opts = ["Todos"] + sorted(df_all["year"].unique())
    year_sel = st.selectbox("📅 Año", year_opts, key="year_filter")

    person_opts = ["Todas"] + PERSONS
    person_sel = st.selectbox("👤 Consultora", person_opts, key="person_filter")

    st.divider()
    top_n = st.slider("Top N centros", 10, min(50, len(df_all["centro"].unique())), 20, 5, key="top_n_slider")

    st.divider()
    total_rows = len(df_all)
    max_fecha = df_all["fecha"].max().strftime("%b %Y")
    st.caption(f"🗂 {total_rows:,} registros")
    st.caption(f"📅 Hasta {max_fecha}")

# ── FILTRADO ──────────────────────────────────────────────────────────────────
df = df_all.copy()
if year_sel != "Todos":
    df = df[df["year"] == year_sel]
if person_sel != "Todas":
    df = df[df["persona"] == person_sel]

active_persons = [person_sel] if person_sel != "Todas" else PERSONS
active_years = [year_sel] if year_sel != "Todos" else sorted(df_all["year"].unique())

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Dashboard de Visitas · FROCA")
parts = []
if year_sel != "Todos":
    parts.append(f"Año {year_sel}")
if person_sel != "Todas":
    parts.append(person_sel)
st.caption(" · ".join(parts) if parts else "Histórico completo · 2023–2026")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_vis = len(df)
meses_act = df.groupby("ym").size()
media_mens = round(total_vis / len(meses_act[meses_act > 0])) if len(meses_act) > 0 else 0

col1, col2 = st.columns(2)
with col1:
    st.metric("🔢 Total Visitas", f"{total_vis:,}".replace(",", "."))
with col2:
    st.metric("📈 Media Mensual", f"{media_mens} vis/mes")

st.divider()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Visión General",
    "🏫 Centros",
    "📈 Evolución",
    "⏱ Duración & Hora"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1: VISIÓN GENERAL
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    # Visitas por mes
    st.subheader("📅 Visitas por Mes")
    monthly = df.groupby(["ym","mes_label"]).size().reset_index(name="visitas").sort_values("ym")
    
    if not monthly.empty:
        max_m = monthly["visitas"].max()
        monthly["color"] = monthly["visitas"].apply(lambda v: "#6366f1" if v == max_m else "#c7d2fe")
        
        fig = go.Figure(go.Bar(
            x=monthly["mes_label"],
            y=monthly["visitas"],
            marker_color=monthly["color"],
            text=monthly["visitas"],
            textposition="outside",
            textfont=dict(size=10),
        ))
        fig.update_layout(
            height=300,
            margin=dict(t=30, b=80, l=40, r=20),
            xaxis=dict(tickangle=-45, tickfont=dict(size=10)),
            yaxis=dict(title="Visitas"),
            showlegend=False,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Visitas por consultora - BARRAS HORIZONTALES
    st.subheader("👤 Visitas por Consultora")
    
    person_df = (df.groupby("persona").size()
                   .reindex(active_persons, fill_value=0)
                   .reset_index(name="visitas")
                   .sort_values("visitas", ascending=True))  # True para horizontal
    person_df = person_df[person_df["visitas"] > 0]
    
    if not person_df.empty:
        person_df["color"] = person_df["persona"].map(PERSON_COLORS)
        
        fig = go.Figure(go.Bar(
            x=person_df["visitas"],
            y=person_df["persona"],
            orientation="h",
            marker_color=person_df["color"],
            text=person_df["visitas"],
            textposition="outside",
            textfont=dict(size=12),
        ))
        fig.update_layout(
            height=max(250, len(person_df) * 40),
            margin=dict(t=20, b=20, l=100, r=60),
            xaxis=dict(title="Visitas"),
            yaxis=dict(tickfont=dict(size=12)),
            showlegend=False,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 2: CENTROS
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"🏫 Top {top_n} Centros Educativos")
    
    centro_df = (df.groupby("centro").size()
                   .reset_index(name="visitas")
                   .sort_values("visitas", ascending=False)
                   .head(top_n)
                   .sort_values("visitas", ascending=True))
    
    if not centro_df.empty:
        max_c = centro_df["visitas"].max()
        
        def get_color(v):
            if v >= max_c * 0.75:
                return "#6366f1"
            elif v >= max_c * 0.5:
                return "#818cf8"
            elif v >= max_c * 0.25:
                return "#a5b4fc"
            return "#c7d2fe"
        
        centro_df["color"] = centro_df["visitas"].apply(get_color)
        
        fig = go.Figure(go.Bar(
            x=centro_df["visitas"],
            y=centro_df["centro"],
            orientation="h",
            marker_color=centro_df["color"],
            text=centro_df["visitas"],
            textposition="outside",
            textfont=dict(size=11),
        ))
        fig.update_layout(
            height=max(400, len(centro_df) * 28),
            margin=dict(t=20, b=20, l=200, r=70),
            xaxis=dict(title="Visitas", showgrid=True, gridcolor="#f1f5f9"),
            yaxis=dict(tickfont=dict(size=11)),
            showlegend=False,
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3: EVOLUCIÓN
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    # Evolución mensual
    st.subheader("📈 Evolución Mensual por Consultora")
    
    months_sorted = sorted(df["ym"].unique())
    evol_rows = []
    for ym in months_sorted:
        sub = df[df["ym"] == ym]
        label = MESES[ym[5:7]] + " " + ym[2:4]
        row = {"label": label, "ym": ym}
        for p in active_persons:
            row[p] = int((sub["persona"] == p).sum())
        evol_rows.append(row)
    
    df_evol = pd.DataFrame(evol_rows) if evol_rows else pd.DataFrame()
    
    if not df_evol.empty:
        fig = go.Figure()
        for p in active_persons:
            if p in df_evol.columns:
                fig.add_trace(go.Scatter(
                    x=df_evol["label"],
                    y=df_evol[p],
                    mode="lines+markers",
                    name=p,
                    line=dict(color=PERSON_COLORS[p], width=2),
                    marker=dict(size=4),
                ))
        fig.update_layout(
            height=350,
            margin=dict(t=20, b=80, l=40, r=20),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(title="Visitas"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Distribución apilada
    st.subheader("📊 Distribución Mensual Apilada")
    
    if not df_evol.empty:
        fig = go.Figure()
        for p in active_persons:
            if p in df_evol.columns:
                fig.add_trace(go.Bar(
                    x=df_evol["label"],
                    y=df_evol[p],
                    name=p,
                    marker_color=PERSON_COLORS[p],
                ))
        fig.update_layout(
            barmode="stack",
            height=350,
            margin=dict(t=20, b=80, l=40, r=20),
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(title="Visitas"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Comparativa anual
    st.subheader("📆 Comparativa Anual por Consultora")
    
    year_colors = {"2023":"#e2e8f0","2024":"#a5b4fc","2025":"#6366f1","2026":"#312e81"}
    persons_comp = [person_sel] if person_sel != "Todas" else PERSONS
    
    comp_data = []
    for p in persons_comp:
        row = {"persona": p}
        for y in ["2023","2024","2025","2026"]:
            count = len(df_all[(df_all["year"] == y) & (df_all["persona"] == p)])
            row[y] = count
        comp_data.append(row)
    
    df_comp = pd.DataFrame(comp_data)
    
    if not df_comp.empty:
        fig = go.Figure()
        for yr, color in year_colors.items():
            if yr in df_comp.columns:
                fig.add_trace(go.Bar(
                    x=df_comp["persona"],
                    y=df_comp[yr],
                    name=yr,
                    marker_color=color,
                    text=df_comp[yr],
                    textposition="outside",
                    textfont=dict(size=9),
                ))
        fig.update_layout(
            barmode="group",
            height=350,
            margin=dict(t=30, b=40, l=40, r=20),
            xaxis=dict(tickfont=dict(size=11)),
            yaxis=dict(title="Visitas"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white",
        )
        st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 4: DURACIÓN & HORA
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    col_dur, col_hora = st.columns(2)
    
    # Duración - Pie Chart
    with col_dur:
        st.subheader("⏱ Duración de las Visitas")
        
        dur_df = (df["duracion"].dropna()
                    .loc[df["duracion"].isin(DUR_ORDER)]
                    .value_counts()
                    .reindex(DUR_ORDER, fill_value=0)
                    .reset_index())
        dur_df.columns = ["duracion", "visitas"]
        dur_df = dur_df[dur_df["visitas"] > 0]
        
        if not dur_df.empty:
            dur_df["color"] = [DUR_COLORS[i] for i in range(len(dur_df))]
            
            fig = go.Figure(go.Pie(
                labels=dur_df["duracion"],
                values=dur_df["visitas"],
                marker_colors=dur_df["color"],
                textinfo="percent+label",
                textfont=dict(size=11),
                hovertemplate="<b>%{label}</b><br>%{value} visitas<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(
                height=400,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Hora - Barras horizontales
    with col_hora:
        st.subheader("🕐 Hora de Inicio")
        
        hora_df = (df["hora"].dropna()
                     .loc[df["hora"].isin(HORA_ORDER)]
                     .value_counts()
                     .reindex(HORA_ORDER, fill_value=0)
                     .reset_index())
        hora_df.columns = ["hora", "visitas"]
        hora_df = hora_df[hora_df["visitas"] > 0]
        
        if not hora_df.empty:
            max_h = hora_df["visitas"].max()
            
            def get_hora_color(v):
                if v == max_h:
                    return "#6366f1"
                elif v >= max_h * 0.7:
                    return "#818cf8"
                elif v >= max_h * 0.4:
                    return "#a5b4fc"
                return "#c7d2fe"
            
            hora_df["color"] = hora_df["visitas"].apply(get_hora_color)
            
            fig = go.Figure(go.Bar(
                x=hora_df["visitas"],
                y=hora_df["hora"],
                orientation="h",
                marker_color=hora_df["color"],
                text=hora_df["visitas"],
                textposition="outside",
                textfont=dict(size=11),
            ))
            fig.update_layout(
                height=400,
                margin=dict(t=20, b=20, l=50, r=60),
                xaxis=dict(title="Visitas", showgrid=True, gridcolor="#f1f5f9"),
                yaxis=dict(
                    categoryorder="array",
                    categoryarray=HORA_ORDER,
                    tickfont=dict(size=12),
                ),
                showlegend=False,
                plot_bgcolor="white",
            )
            st.plotly_chart(fig, use_container_width=True)

# ── PIE DE PÁGINA ─────────────────────────────────────────────────────────────
st.divider()
st.caption("FROCA · Dashboard de Visitas · visitas_FROCA.xlsx")
