import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Visitas · FROCA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PERSONS = ["ANGELS","ARANTXA","CRISTINA","Mª JOSÉ","MONTSERRAT","NURIA","SARA","VANESA","EMMA"]
DUR_ORDER  = ["30 m","1 h","1h30","2 h","2h30","3 h","4 h","8 h"]
HORA_ORDER = ["7h","8h","9h","10h","11h","12h","13h","14h","15h","16h","17h"]
PERSON_COLORS = {
    "ANGELS":    "#6366f1",
    "ARANTXA":   "#f59e0b",
    "CRISTINA":  "#10b981",
    "Mª JOSÉ":   "#3b82f6",
    "MONTSERRAT":"#ec4899",
    "NURIA":     "#8b5cf6",
    "SARA":      "#14b8a6",
    "VANESA":    "#f97316",
    "EMMA":      "#64748b",
}
DUR_COLORS = ["#c7d2fe","#a5b4fc","#818cf8","#6366f1",
              "#4f46e5","#4338ca","#3730a3","#312e81"]
MESES = {
    "01":"Ene","02":"Feb","03":"Mar","04":"Abr","05":"May","06":"Jun",
    "07":"Jul","08":"Ago","09":"Sep","10":"Oct","11":"Nov","12":"Dic"
}

EXCEL_PATH = Path(__file__).parent / "visitas_FROCA.xlsx"

# ── CARGA DE DATOS (cacheada, se refresca sola al detectar cambio en el Excel)
@st.cache_data(ttl=300)
def load_data():
    df = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Datos",
        usecols=[0, 2, 3, 4, 6, 7],
        header=0,
    )
    df.columns = ["marca","persona","centro","fecha","hora","duracion"]
    df = df.dropna(subset=["fecha","persona","centro"])
    df["fecha"]    = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])
    df["persona"]  = df["persona"].str.strip().str.upper()
    df["centro"]   = df["centro"].str.strip().str.upper()
    df["hora"]     = df["hora"].astype(str).str.strip()
    df["duracion"] = df["duracion"].astype(str).str.strip()
    df["year"]     = df["fecha"].dt.year.astype(str)
    df["ym"]       = df["fecha"].dt.strftime("%Y-%m")
    df["mes_label"]= df["fecha"].dt.strftime("%m").map(MESES) + " " + df["fecha"].dt.strftime("%y")
    df = df[df["persona"].isin(PERSONS)]
    df = df[df["year"].isin(["2023","2024","2025","2026"])]
    return df

df_all = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Dashboard Visitas")
    st.markdown("**FROCA** · Seguimiento operativo")
    st.divider()

    year_opts = ["Todos"] + sorted(df_all["year"].unique())
    year_sel  = st.selectbox("📅 Año", year_opts)

    person_opts = ["Todas"] + PERSONS
    person_sel  = st.selectbox("👤 Consultora", person_opts)

    st.divider()
    top_n = st.slider("Top N centros", 10, len(df_all["centro"].unique()), 20, 5)

    st.divider()
    total_rows = len(df_all)
    max_fecha  = df_all["fecha"].max().strftime("%b %Y")
    st.caption(f"🗂 {total_rows:,} registros · hasta {max_fecha}")
    st.caption("📁 Fuente: `visitas_FROCA.xlsx`")

# ── FILTRADO ──────────────────────────────────────────────────────────────────
df = df_all.copy()
if year_sel   != "Todos": df = df[df["year"]    == year_sel]
if person_sel != "Todas": df = df[df["persona"] == person_sel]
active_persons = [person_sel] if person_sel != "Todas" else PERSONS

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 📊 Dashboard de Visitas · FROCA")
parts = []
if year_sel   != "Todos": parts.append(f"Año {year_sel}")
if person_sel != "Todas": parts.append(person_sel)
st.caption(" · ".join(parts) if parts else "Histórico completo · 2023–2026")
st.divider()

# ── KPIs ──────────────────────────────────────────────────────────────────────
total_vis    = len(df)
meses_act    = df.groupby("ym").size()
media_mens   = round(total_vis / len(meses_act[meses_act > 0])) if len(meses_act) > 0 else 0

k1, k2 = st.columns(2)
k1.metric("🔢 Total Visitas",  f"{total_vis:,}".replace(",","."))
k2.metric("📈 Media Mensual",  f"{media_mens} vis/mes")
st.divider()

# ── HELPER: layout plotly ─────────────────────────────────────────────────────
def clean_layout(fig, height=320, **kwargs):
    fig.update_layout(
        height=height,
        margin=dict(t=20, b=10, l=0, r=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        **kwargs,
    )
    return fig

# ── VISITAS POR MES ───────────────────────────────────────────────────────────
st.subheader("📅 Visitas por Mes")

monthly = (df.groupby(["ym","mes_label"])
             .size().reset_index(name="visitas")
             .sort_values("ym"))
max_m = monthly["visitas"].max() if len(monthly) else 1
monthly["color"] = monthly["visitas"].apply(
    lambda v: "#6366f1" if v == max_m else "#c7d2fe")

fig = go.Figure(go.Bar(
    x=monthly["mes_label"], y=monthly["visitas"],
    marker_color=monthly["color"],
    text=monthly["visitas"], textposition="outside",
    textfont=dict(size=10, color="#475569"),
))
clean_layout(fig, xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=10)),
             yaxis=dict(showgrid=True, gridcolor="#f1f5f9"), showlegend=False)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── VISITAS POR CONSULTORA ────────────────────────────────────────────────────
st.subheader("👤 Visitas por Consultora")

person_df = (df.groupby("persona").size()
               .reindex(active_persons, fill_value=0)
               .reset_index(name="visitas")
               .sort_values("visitas", ascending=False))
person_df = person_df[person_df["visitas"] > 0]

ncols = min(len(person_df), 5)
if ncols > 0:
    cols = st.columns(ncols)
    for i, (_, row) in enumerate(person_df.iterrows()):
        cols[i % ncols].metric(row["persona"], int(row["visitas"]))
st.divider()

# ── VISITAS POR CENTRO ────────────────────────────────────────────────────────
st.subheader(f"🏫 Visitas por Centro Educativo — Top {top_n}")

centro_df = (df.groupby("centro").size()
               .reset_index(name="visitas")
               .sort_values("visitas", ascending=False)
               .head(top_n)
               .sort_values("visitas", ascending=True))
max_c = centro_df["visitas"].max() if len(centro_df) else 1
centro_df["color"] = centro_df["visitas"].apply(
    lambda v: "#6366f1" if v >= max_c*0.75 else
              "#818cf8" if v >= max_c*0.5  else
              "#a5b4fc" if v >= max_c*0.25 else "#c7d2fe")

fig = go.Figure(go.Bar(
    x=centro_df["visitas"], y=centro_df["centro"],
    orientation="h", marker_color=centro_df["color"],
    text=centro_df["visitas"], textposition="outside",
    textfont=dict(size=11, color="#475569"),
))
clean_layout(fig, height=max(350, top_n * 26),
             margin=dict(t=10, b=10, l=10, r=60),
             xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
             yaxis=dict(showgrid=False, tickfont=dict(size=11)),
             showlegend=False)
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── EVOLUCIÓN MENSUAL ─────────────────────────────────────────────────────────
st.subheader("📈 Evolución Mensual por Consultora")

months_sorted = sorted(df["ym"].unique())
evol_rows = []
for ym in months_sorted:
    sub = df[df["ym"] == ym]
    label = MESES[ym[5:7]] + " " + ym[2:4]
    row = {"label": label}
    for p in active_persons:
        row[p] = int((sub["persona"] == p).sum())
    evol_rows.append(row)
df_evol = pd.DataFrame(evol_rows) if evol_rows else pd.DataFrame()

fig = go.Figure()
for p in active_persons:
    if not df_evol.empty and p in df_evol.columns:
        fig.add_trace(go.Scatter(
            x=df_evol["label"], y=df_evol[p],
            mode="lines", name=p,
            line=dict(color=PERSON_COLORS[p], width=2),
        ))
clean_layout(fig,
    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)))
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── DISTRIBUCIÓN APILADA ──────────────────────────────────────────────────────
st.subheader("📊 Distribución Mensual Apilada por Consultora")

fig = go.Figure()
for p in active_persons:
    if not df_evol.empty and p in df_evol.columns:
        fig.add_trace(go.Bar(
            x=df_evol["label"], y=df_evol[p],
            name=p, marker_color=PERSON_COLORS[p],
        ))
clean_layout(fig, barmode="stack",
    xaxis=dict(showgrid=False, tickangle=-45, tickfont=dict(size=9)),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=10)))
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── COMPARATIVA ANUAL ─────────────────────────────────────────────────────────
st.subheader("📆 Comparativa Anual por Consultora")

year_colors = {"2023":"#e2e8f0","2024":"#a5b4fc","2025":"#6366f1","2026":"#312e81"}
persons_comp = [person_sel] if person_sel != "Todas" else PERSONS

fig = go.Figure()
for yr, col in year_colors.items():
    vals = []
    for p in persons_comp:
        sub = df_all[(df_all["year"] == yr) & (df_all["persona"] == p)]
        vals.append(len(sub))
    fig.add_trace(go.Bar(
        x=persons_comp, y=vals, name=yr,
        marker_color=col,
        text=[v if v > 0 else "" for v in vals],
        textposition="outside",
        textfont=dict(size=9),
    ))
clean_layout(fig, barmode="group", height=320,
    xaxis=dict(showgrid=False, tickfont=dict(size=11)),
    yaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)))
st.plotly_chart(fig, use_container_width=True)
st.divider()

# ── DURACIÓN + HORA ───────────────────────────────────────────────────────────
col_dur, col_hora = st.columns(2)

with col_dur:
    st.subheader("⏱ Duración de las Visitas")
    dur_df = (df["duracion"].dropna()
                .loc[df["duracion"].isin(DUR_ORDER)]
                .value_counts()
                .reindex(DUR_ORDER, fill_value=0)
                .reset_index())
    dur_df.columns = ["duracion","visitas"]
    dur_df = dur_df[dur_df["visitas"] > 0]

    fig = go.Figure(go.Pie(
        labels=dur_df["duracion"],
        values=dur_df["visitas"],
        marker_colors=DUR_COLORS[:len(dur_df)],
        textinfo="percent",
        textfont=dict(size=12, color="white"),
        hovertemplate="<b>%{label}</b><br>%{value} visitas · %{percent}<extra></extra>",
    ))
    fig.update_layout(
        height=340, margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor="white",
        legend=dict(font=dict(size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_hora:
    st.subheader("🕐 Hora de Inicio de la Visita")
    hora_df = (df["hora"].dropna()
                 .loc[df["hora"].isin(HORA_ORDER)]
                 .value_counts()
                 .reindex(HORA_ORDER, fill_value=0)
                 .reset_index())
    hora_df.columns = ["hora","visitas"]
    hora_df = hora_df[hora_df["visitas"] > 0]

    max_h = hora_df["visitas"].max() if len(hora_df) else 1
    hora_df["color"] = hora_df["visitas"].apply(
        lambda v: "#6366f1" if v == max_h else
                  "#818cf8" if v >= max_h*0.7 else
                  "#a5b4fc" if v >= max_h*0.4 else "#c7d2fe")

    fig = go.Figure(go.Bar(
        x=hora_df["visitas"], y=hora_df["hora"],
        orientation="h", marker_color=hora_df["color"],
        text=hora_df["visitas"], textposition="outside",
        textfont=dict(size=11, color="#475569"),
    ))
    fig.update_layout(
        height=340, margin=dict(t=10, b=10, l=10, r=50),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f1f5f9"),
        yaxis=dict(
            showgrid=False,
            categoryorder="array",
            categoryarray=HORA_ORDER,
            tickfont=dict(size=12, color="#475569"),
        ),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

# ── PIE DE PÁGINA ─────────────────────────────────────────────────────────────
st.divider()
st.caption("FROCA · Dashboard de Visitas · Hoja 'Datos' · Columnas A–H · FECHA DE VISITA")
