# 📊 Dashboard de Visitas · FROCA

Dashboard interactivo para el seguimiento de visitas a centros educativos.
Desplegado en Streamlit Cloud, accesible por URL para cualquier persona del equipo.

---

## 🗂 Estructura del proyecto

```
froca_dashboard/
├── app.py                  ← Código principal del dashboard
├── visitas_FROCA.xlsx      ← Fuente de datos (hoja "Datos", columnas A-H)
├── requirements.txt        ← Dependencias Python (Streamlit Cloud las instala solo)
└── README.md               ← Este fichero
```

---

## 🚀 Despliegue inicial en Streamlit Cloud (solo la primera vez)

### Paso 1 — Subir el proyecto a GitHub

1. Abre [github.com](https://github.com) e inicia sesión
2. Crea un nuevo repositorio: boton **"New"** → nombre `froca-dashboard` → **Create repository**
3. Sube los 4 ficheros del proyecto:
   - Boton **"Add file" → "Upload files"**
   - Arrastra o selecciona: `app.py`, `visitas_FROCA.xlsx`, `requirements.txt`, `README.md`
   - Boton **"Commit changes"**

### Paso 2 — Conectar con Streamlit Cloud

1. Abre [share.streamlit.io](https://share.streamlit.io) e inicia sesión con tu cuenta GitHub
2. Boton **"New app"**
3. Selecciona:
   - **Repository:** `tu-usuario/froca-dashboard`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Boton **"Deploy!"**
5. En 2-3 minutos tendras una URL publica del tipo:
   `https://tu-usuario-froca-dashboard-app-xxxx.streamlit.app`

Comparte esa URL con todo el equipo — no necesitan cuenta ni instalar nada.

---

## 🔄 Actualizar los datos (cada semana o 10 dias)

Cuando tengas un Excel nuevo con mas visitas:

1. Abre tu repositorio en [github.com](https://github.com)
2. Haz clic en el fichero `visitas_FROCA.xlsx`
3. Boton **"..." (tres puntos) → "Replace file"**
4. Selecciona el nuevo Excel → **"Commit changes"**
5. **Listo.** Streamlit Cloud detecta el cambio automaticamente y recarga la app.

> El Excel nuevo debe mantener la misma estructura:
> hoja llamada **"Datos"**, columnas A-H con las mismas cabeceras.

---

## 🎛 Uso del dashboard

| Elemento | Descripcion |
|----------|-------------|
| **Filtro Anyo** | Filtra todos los graficos al anyo seleccionado |
| **Filtro Consultora** | Filtra todos los graficos a una consultora concreta |
| **Top N centros** | Ajusta cuantos centros se muestran en el ranking |
| **KPIs** | Total de visitas y media mensual segun filtros activos |

---

## 📦 Dependencias

| Libreria | Para que se usa |
|----------|-----------------|
| `streamlit` | Interfaz y despliegue web |
| `pandas` | Carga y procesado del Excel |
| `plotly` | Todos los graficos interactivos |
| `openpyxl` | Lectura de ficheros .xlsx |

Streamlit Cloud instala estas dependencias automaticamente desde `requirements.txt`.
