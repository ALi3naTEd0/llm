# 🎓 Tutor Virtual Inteligente

Un tutor virtual basado en modelos de lenguaje de gran escala (LLM) que responde preguntas, explica conceptos y guía a estudiantes a través de tareas difíciles. Soporta múltiples materias (Matemáticas, Programación, Ciencias, Historia, Idiomas) con tres modos de uso: interfaz gráfica, chat en terminal y notebook de JupyterLab.

**API utilizada:** [Groq](https://groq.com/) — acceso gratuito a modelos como `llama-3.1-8b-instant`, `llama-3.3-70b-versatile` y `gemma2-9b-it`.

---

## Requisitos previos

- Python 3.9 o superior
- Una API Key gratuita de Groq: obtenerla en [https://console.groq.com/keys](https://console.groq.com/keys)

---

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd llm
```

### 2. Crear el entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual:

- **Linux / macOS:**
  ```bash
  source venv/bin/activate
  ```
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la API Key de Groq

Edita el archivo **`.env`** (ya incluido en el repositorio) y reemplaza el valor:

```
GROQ_API_KEY=tu_clave_aqui
```

Obtén tu clave gratuita en [https://console.groq.com/keys](https://console.groq.com/keys).

> El archivo `.env` está listado en `.gitignore` y **nunca se sube a Git**.

Alternativamente, puedes exportar la variable de entorno directamente:

```bash
# Linux / macOS
export GROQ_API_KEY="gsk_..."

# Windows (PowerShell)
$env:GROQ_API_KEY="gsk_..."
```

### 5. Iniciar JupyterLab

```bash
jupyter lab
```

Se abrirá el navegador automáticamente. Abre el archivo **`tutor_virtual.ipynb`**.

### 6. Ejecutar el notebook

Ejecuta las celdas en orden (`Shift + Enter` en cada celda o _Run All_):

1. **Celda de importaciones** — carga las librerías.
2. **Configuración de API Key** — carga la clave desde la variable de entorno o muestra un campo para ingresarla.
3. **Motor del tutor** — define la clase `TutorVirtual`.
4. **Inicialización** — crea la instancia del tutor.
5. **Interfaz interactiva** — muestra la UI completa con chat, selector de materia y modelo.

---

## Uso

### Opción A — Interfaz gráfica (recomendado)

```bash
python tutor_virtual_ui.py
```

Abre una ventana de escritorio con:
- **Selector de materia** y **selector de modelo** en el header
- **Chat con burbujas** — tus mensajes a la derecha, el tutor a la izquierda
- **Indicador de carga** mientras el modelo responde
- **Botón de reset** (🔄) — nueva sesión limpia
- **Botón de guardar** (💾) — exporta el historial a `historial_sesion.json`
- Si no hay `GROQ_API_KEY` en `.env`, aparece un diálogo para introducirla

### Opción B — Chat interactivo en terminal

```bash
python tutor_virtual.py
```

Al iniciar, el programa pedirá que selecciones la **materia** y el **modelo LLM**.  
Una vez en el chat, puedes usar estos comandos:

| Comando | Acción |
|---|---|
| `/ayuda` | Lista de comandos |
| `/materia` | Cambia la materia (reinicia historial) |
| `/modelo` | Cambia el modelo |
| `/nuevo` | Reinicia el historial |
| `/historial` | Imprime la sesión actual |
| `/guardar` | Exporta historial a `historial_sesion.json` |
| `/salir` | Termina el programa |

### Opción C — Notebook explicativo (JupyterLab)

El archivo `tutor_virtual.ipynb` contiene:
- Explicación de la arquitectura del sistema
- Código documentado de la clase `TutorVirtual`
- Demostraciones programáticas de conversaciones multi-turno
- Exportación del historial a JSON

Ejecuta las celdas en orden (`Shift + Enter`) o usa _Run All_.

### Exportar historial

Tanto la UI gráfica (botón 💾) como el script de terminal (`/guardar`) y el notebook guardan el historial en `historial_sesion.json`.

---

## Estructura del proyecto

```
llm/
├── tutor_virtual_ui.py   # Interfaz gráfica con Flet (recomendado)
├── tutor_virtual.py      # Script de chat interactivo en terminal
├── tutor_virtual.ipynb   # Notebook explicativo con demos programáticas
├── .env                  # API Key (NO se sube a Git — editar antes de usar)
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Este archivo
```

---

## Modelos disponibles (Groq free tier)

| Modelo | Descripción |
|---|---|
| `llama-3.1-8b-instant` | Rápido y eficiente, ideal para uso general |
| `llama-3.3-70b-versatile` | Más potente, mejores razonamientos complejos |
| `llama-3.1-70b-versatile` | Alternativa estable al 70B |
| `gemma2-9b-it` | Modelo Google, buen rendimiento general |

