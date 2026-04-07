"""
Tutor Virtual Inteligente — Interfaz gráfica con Flet
Basado en Groq API (free tier)

Uso:
    python tutor_virtual_ui.py
    GROQ_API_KEY=<clave> python tutor_virtual_ui.py
"""

import os
import sys
import json
import threading

# ── Verificar dependencias ───────────────────────────────────────────────────
try:
    import flet as ft
except ImportError:
    print("Error: la librería 'flet' no está instalada.")
    print("Ejecuta:  pip install flet")
    sys.exit(1)

try:
    from groq import Groq
except ImportError:
    print("Error: la librería 'groq' no está instalada.")
    print("Ejecuta:  pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass


# ── Configuración ────────────────────────────────────────────────────────────
SYSTEM_PROMPTS = {
    "General": (
        "Eres un tutor virtual amigable y paciente. Tu objetivo es ayudar al estudiante "
        "a comprender conceptos de cualquier área del conocimiento. Explica de forma clara, "
        "usa ejemplos prácticos, y si el estudiante comete un error, corrígelo con amabilidad. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
    "Matemáticas": (
        "Eres un tutor experto en matemáticas. Explica conceptos paso a paso, muestra "
        "el procedimiento completo para resolver problemas, y usa notación clara. "
        "Cuando el estudiante se equivoque, identifica exactamente dónde está el error. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
    "Programación": (
        "Eres un tutor experto en programación y ciencias de la computación. "
        "Explica conceptos con ejemplos de código comentados, sugiere buenas prácticas "
        "y ayuda a depurar errores. Usa bloques de código cuando sea apropiado. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
    "Ciencias": (
        "Eres un tutor experto en ciencias naturales (física, química, biología). "
        "Explica fenómenos con analogías del mundo real, conecta la teoría con la práctica, "
        "y fomenta el pensamiento crítico. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
    "Historia": (
        "Eres un tutor experto en historia, filosofía, literatura y humanidades. "
        "Contextualiza los hechos históricos, analiza textos con profundidad "
        "y ayuda al estudiante a desarrollar argumentos sólidos. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
    "Idiomas": (
        "Eres un tutor de idiomas. Corriges gramática y ortografía con explicaciones, "
        "enseñas vocabulario en contexto, y adaptas las lecciones al nivel del estudiante. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    ),
}

MODELOS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "gemma2-9b-it",
]

MATERIA_EMOJIS = {
    "General": "📚",
    "Matemáticas": "🔢",
    "Programación": "💻",
    "Ciencias": "🔬",
    "Historia": "🏛️",
    "Idiomas": "🌐",
}


# ── Clase TutorVirtual ───────────────────────────────────────────────────────
class TutorVirtual:
    def __init__(self, api_key: str, materia: str = "General", modelo: str = "llama-3.1-8b-instant"):
        if not api_key:
            raise ValueError("Se requiere una API Key de Groq.")
        self.client = Groq(api_key=api_key)
        self.materia = materia
        self.modelo = modelo
        self.historial: list[dict] = []
        self.reset_historial()

    def reset_historial(self):
        self.historial = [
            {"role": "system", "content": SYSTEM_PROMPTS.get(self.materia, SYSTEM_PROMPTS["General"])}
        ]

    def cambiar_materia(self, materia: str):
        self.materia = materia
        self.reset_historial()

    def cambiar_modelo(self, modelo: str):
        self.modelo = modelo

    def preguntar(self, pregunta: str, temperatura: float = 0.7, max_tokens: int = 1024) -> str:
        self.historial.append({"role": "user", "content": pregunta})
        response = self.client.chat.completions.create(
            model=self.modelo,
            messages=self.historial,
            temperature=temperatura,
            max_tokens=max_tokens,
        )
        respuesta = response.choices[0].message.content
        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta

    def historial_legible(self) -> list[dict]:
        return [m for m in self.historial if m["role"] != "system"]

    def guardar_historial(self, ruta: str = "historial_sesion.json") -> str:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.historial_legible(), f, ensure_ascii=False, indent=2)
        return ruta


# ── App Flet ─────────────────────────────────────────────────────────────────
def main(page: ft.Page):
    page.title = "Tutor Virtual Inteligente"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#1a1f2e"
    page.padding = 0
    try:
        page.window.width = 960
        page.window.height = 720
        page.window.min_width = 640
        page.window.min_height = 480
    except Exception:
        pass

    # ── State ─────────────────────────────────────────────────────────────────
    state: dict = {"tutor": None, "thinking": False}
    THINKING_KEY = "__thinking__"

    # ── Chat list ─────────────────────────────────────────────────────────────
    chat_list = ft.ListView(
        expand=True,
        spacing=10,
        padding=ft.padding.symmetric(horizontal=24, vertical=16),
        auto_scroll=True,
    )

    # ── Dropdowns ─────────────────────────────────────────────────────────────
    def on_materia_change(e):
        if state["tutor"] and not state["thinking"]:
            state["tutor"].cambiar_materia(dd_materia.value)
            chat_list.controls.clear()
            _add_welcome()

    def on_modelo_change(e):
        if state["tutor"]:
            state["tutor"].cambiar_modelo(dd_modelo.value)

    dd_materia = ft.Dropdown(
        width=170,
        options=[
            ft.dropdown.Option(key=m, text=f"{MATERIA_EMOJIS.get(m, '')} {m}")
            for m in SYSTEM_PROMPTS
        ],
        value="General",
        bgcolor="#252d3d",
        color="white",
        border_color="#3d4a63",
        focused_border_color="#4299e1",
        content_padding=ft.padding.symmetric(horizontal=10, vertical=6),
        text_size=13,
        on_select=on_materia_change,
    )

    dd_modelo = ft.Dropdown(
        width=215,
        options=[ft.dropdown.Option(m) for m in MODELOS],
        value=MODELOS[0],
        bgcolor="#252d3d",
        color="white",
        border_color="#3d4a63",
        focused_border_color="#4299e1",
        content_padding=ft.padding.symmetric(horizontal=10, vertical=6),
        text_size=13,
        on_select=on_modelo_change,
    )

    # ── Helpers: burbujas de chat ─────────────────────────────────────────────
    def _make_bubble(text: str, is_user: bool, is_error: bool = False) -> ft.Row:
        if is_user:
            return ft.Row(
                [
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Text(text, color="white", selectable=True, size=14),
                        bgcolor="#2563eb",
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        border_radius=ft.BorderRadius.only(
                            top_left=16, top_right=4, bottom_left=16, bottom_right=16
                        ),
                    ),
                ],
            )
        else:
            bg = "#3d1f1f" if is_error else "#252d3d"
            return ft.Row(
                [
                    ft.Container(
                        content=ft.Text("🤖", size=18),
                        width=34,
                        height=34,
                        bgcolor="#1e2c45",
                        border_radius=17,
                        alignment=ft.Alignment(0, 0),
                        margin=ft.margin.only(right=10, top=2),
                    ),
                    ft.Container(
                        content=ft.Text(text, color="#e2e8f0", selectable=True, size=14),
                        bgcolor=bg,
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
border_radius=ft.BorderRadius.only(
                            top_left=4, top_right=16, bottom_left=16, bottom_right=16
                        ),
                        expand=True,
                    ),
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )

    def _add_bubble(text: str, is_user: bool, is_error: bool = False):
        chat_list.controls.append(_make_bubble(text, is_user, is_error))
        page.update()

    def _add_thinking_bubble():
        bubble = ft.Row(
            [
                ft.Container(
                    content=ft.Text("🤖", size=18),
                    width=34,
                    height=34,
                    bgcolor="#1e2c45",
                    border_radius=17,
                    alignment=ft.Alignment(0, 0),
                    margin=ft.margin.only(right=10, top=2),
                ),
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ProgressRing(width=14, height=14, stroke_width=2, color="#4299e1"),
                            ft.Text(" Pensando...", color="#718096", size=13, italic=True),
                        ],
                        tight=True,
                        spacing=8,
                    ),
                    bgcolor="#252d3d",
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    border_radius=ft.BorderRadius.only(
                        top_left=4, top_right=16, bottom_left=16, bottom_right=16
                    ),
                ),
                ft.Container(expand=True),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            key=THINKING_KEY,
        )
        chat_list.controls.append(bubble)
        page.update()

    def _remove_thinking_bubble():
        chat_list.controls = [
            c for c in chat_list.controls if getattr(c, "key", None) != THINKING_KEY
        ]

    def _set_thinking(active: bool):
        state["thinking"] = active
        btn_send.bgcolor = "#4a5568" if active else "#4299e1"
        if active:
            _add_thinking_bubble()
        page.update()

    def _add_welcome():
        materia = dd_materia.value
        emoji = MATERIA_EMOJIS.get(materia, "📚")
        _add_bubble(
            f"{emoji} ¡Hola! Soy tu tutor de {materia}. ¿En qué puedo ayudarte hoy?",
            is_user=False,
        )

    def _snack(msg: str, ok: bool = True):
        page.open(ft.SnackBar(
            content=ft.Text(msg, color="white"),
            bgcolor="#276227" if ok else "#622727",
        ))

    # ── Input ─────────────────────────────────────────────────────────────────
    def on_send(e):
        if state["thinking"] or not state["tutor"]:
            return
        text = txt_input.value.strip()
        if not text:
            return
        txt_input.value = ""
        page.update()
        _add_bubble(text, is_user=True)

        def call_api():
            _set_thinking(True)
            try:
                respuesta = state["tutor"].preguntar(text)
                _remove_thinking_bubble()
                _add_bubble(respuesta, is_user=False)
            except Exception as ex:
                _remove_thinking_bubble()
                _add_bubble(f"❌ Error al consultar la API:\n{ex}", is_user=False, is_error=True)
            finally:
                _set_thinking(False)

        threading.Thread(target=call_api, daemon=True).start()

    txt_input = ft.TextField(
        hint_text="Escribe tu pregunta... (Enter para enviar, Shift+Enter nueva línea)",
        hint_style=ft.TextStyle(color="#4a5568"),
        text_style=ft.TextStyle(color="white", size=14),
        bgcolor="#252d3d",
        border_color="#3d4a63",
        focused_border_color="#4299e1",
        border_radius=14,
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=5,
        shift_enter=True,
        content_padding=ft.padding.symmetric(horizontal=16, vertical=12),
        on_submit=on_send,
        cursor_color="#4299e1",
    )

    btn_send = ft.Container(
        content=ft.Icon(ft.Icons.SEND_ROUNDED, color="white", size=20),
        bgcolor="#4299e1",
        border_radius=12,
        padding=ft.padding.all(10),
        on_click=on_send,
        tooltip="Enviar",
        ink=True,
    )

    # ── Botones de header ──────────────────────────────────────────────────────
    def on_reset(e):
        if state["tutor"] and not state["thinking"]:
            state["tutor"].reset_historial()
            chat_list.controls.clear()
            _add_welcome()

    def on_save(e):
        if not state["tutor"]:
            return
        if not state["tutor"].historial_legible():
            _snack("El historial está vacío.", ok=False)
            return
        try:
            ruta = state["tutor"].guardar_historial()
            _snack(f"✓ Guardado en '{ruta}'")
        except Exception as ex:
            _snack(f"Error al guardar: {ex}", ok=False)

    btn_reset = ft.IconButton(
        icon=ft.Icons.RESTART_ALT_ROUNDED,
        icon_color="#a0aec0",
        icon_size=20,
        tooltip="Nueva sesión",
        on_click=on_reset,
    )

    btn_save = ft.IconButton(
        icon=ft.Icons.SAVE_ALT_ROUNDED,
        icon_color="#a0aec0",
        icon_size=20,
        tooltip="Guardar historial JSON",
        on_click=on_save,
    )

    # ── Inicialización con API Key ─────────────────────────────────────────────
    def init_tutor(api_key: str):
        try:
            state["tutor"] = TutorVirtual(
                api_key=api_key,
                materia=dd_materia.value,
                modelo=dd_modelo.value,
            )
            _add_welcome()
        except Exception as ex:
            _add_bubble(f"❌ Error al inicializar: {ex}", is_user=False, is_error=True)

    api_key_env = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key_env:
        def on_key_confirm(e):
            key = txt_api_key.value.strip()
            if not key:
                txt_api_key.error_text = "La clave no puede estar vacía"
                page.update()
                return
            page.close(dlg_apikey)
            init_tutor(key)

        txt_api_key = ft.TextField(
            label="GROQ_API_KEY",
            hint_text="gsk_...",
            password=True,
            can_reveal_password=True,
            bgcolor="#2d3748",
            color="white",
            border_color="#4a5568",
            focused_border_color="#4299e1",
            width=380,
            on_submit=on_key_confirm,
            autofocus=True,
        )

        dlg_apikey = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔑 Configura tu API Key de Groq", size=16, weight=ft.FontWeight.BOLD),
            content=ft.Column(
                [
                    ft.Text(
                        "Necesitas una clave gratuita de Groq para usar el tutor.",
                        color="#a0aec0",
                        size=13,
                    ),
                    ft.TextButton(
                        "→ Obtener clave en console.groq.com/keys",
                        url="https://console.groq.com/keys",
                        style=ft.ButtonStyle(color="#4299e1"),
                    ),
                    txt_api_key,
                    ft.Text(
                        "O crea un archivo .env con: GROQ_API_KEY=gsk_...",
                        color="#4a5568",
                        size=11,
                        italic=True,
                    ),
                ],
                tight=True,
                spacing=10,
                width=400,
            ),
            actions=[
                ft.ElevatedButton(
                    "Conectar",
                    bgcolor="#4299e1",
                    color="white",
                    on_click=on_key_confirm,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_apikey)
    else:
        init_tutor(api_key_env)

    # ── Layout ─────────────────────────────────────────────────────────────────
    header = ft.Container(
        content=ft.Row(
            [
                ft.Row(
                    [
                        ft.Text("🎓", size=22),
                        ft.Text("Tutor Virtual", color="white", size=16, weight=ft.FontWeight.BOLD),
                    ],
                    spacing=8,
                ),
                ft.Container(width=20),
                ft.Row(
                    [ft.Text("Materia", color="#718096", size=12), dd_materia],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(width=6),
                ft.Row(
                    [ft.Text("Modelo", color="#718096", size=12), dd_modelo],
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Container(expand=True),
                btn_reset,
                btn_save,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        bgcolor="#161c2a",
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        border=ft.border.only(bottom=ft.BorderSide(1, "#252d3d")),
    )

    input_bar = ft.Container(
        content=ft.Row(
            [txt_input, ft.Container(width=8), btn_send],
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
        bgcolor="#161c2a",
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        border=ft.border.only(top=ft.BorderSide(1, "#252d3d")),
    )

    page.add(
        ft.Column(
            [
                header,
                ft.Container(content=chat_list, expand=True, bgcolor="#1a1f2e"),
                input_bar,
            ],
            expand=True,
            spacing=0,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
