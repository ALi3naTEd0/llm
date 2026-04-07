"""
Tutor Virtual Inteligente — Interfaz de línea de comandos
Basado en Groq API (free tier)

Uso:
    python tutor_virtual.py
    GROQ_API_KEY=<clave> python tutor_virtual.py

Comandos disponibles dentro del chat:
    /ayuda      Muestra esta lista de comandos
    /materia    Cambia la materia (reinicia el historial)
    /modelo     Cambia el modelo LLM
    /nuevo      Reinicia el historial de la sesión actual
    /historial  Imprime el historial de la sesión
    /guardar    Exporta el historial a historial_sesion.json
    /salir      Termina el programa
"""

import os
import sys
import json

# ── Verificar dependencias ───────────────────────────────────────────────────
try:
    from groq import Groq
except ImportError:
    print("Error: la librería 'groq' no está instalada.")
    print("Ejecuta:  pip install -r requirements.txt")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    # Busca .env en el mismo directorio que este script
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv es opcional; se puede usar variable de entorno directamente


# ── Colores ANSI ─────────────────────────────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    YELLOW = "\033[93m"
    RED    = "\033[91m"
    BLUE   = "\033[94m"
    GRAY   = "\033[90m"
    WHITE  = "\033[97m"

def bold(text):    return f"{C.BOLD}{text}{C.RESET}"
def cyan(text):    return f"{C.CYAN}{text}{C.RESET}"
def green(text):   return f"{C.GREEN}{text}{C.RESET}"
def yellow(text):  return f"{C.YELLOW}{text}{C.RESET}"
def red(text):     return f"{C.RED}{text}{C.RESET}"
def gray(text):    return f"{C.GRAY}{text}{C.RESET}"


# ── Configuración del tutor ──────────────────────────────────────────────────
MATERIAS = {
    "1": ("General", (
        "Eres un tutor virtual amigable y paciente. Tu objetivo es ayudar al estudiante "
        "a comprender conceptos de cualquier área del conocimiento. Explica de forma clara, "
        "usa ejemplos prácticos, y si el estudiante comete un error, corrígelo con amabilidad. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
    "2": ("Matemáticas", (
        "Eres un tutor experto en matemáticas. Explica conceptos paso a paso, muestra "
        "el procedimiento completo para resolver problemas, y usa notación clara. "
        "Cuando el estudiante se equivoque, identifica exactamente dónde está el error. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
    "3": ("Programación", (
        "Eres un tutor experto en programación y ciencias de la computación. "
        "Explica conceptos con ejemplos de código comentados, sugiere buenas prácticas "
        "y ayuda a depurar errores. Usa bloques de código cuando sea apropiado. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
    "4": ("Ciencias", (
        "Eres un tutor experto en ciencias naturales (física, química, biología). "
        "Explica fenómenos con analogías del mundo real, conecta la teoría con la práctica, "
        "y fomenta el pensamiento crítico. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
    "5": ("Historia y Humanidades", (
        "Eres un tutor experto en historia, filosofía, literatura y humanidades. "
        "Contextualiza los hechos históricos, analiza textos con profundidad "
        "y ayuda al estudiante a desarrollar argumentos sólidos. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
    "6": ("Idiomas", (
        "Eres un tutor de idiomas. Corriges gramática y ortografía con explicaciones, "
        "enseñas vocabulario en contexto, y adaptas las lecciones al nivel del estudiante. "
        "Responde siempre en el idioma en que el estudiante te escriba."
    )),
}

MODELOS = {
    "1": ("llama-3.1-8b-instant",      "Llama 3.1 8B  — rápido, ideal para uso general"),
    "2": ("llama-3.3-70b-versatile",    "Llama 3.3 70B — más potente, razonamiento complejo"),
    "3": ("llama-3.1-70b-versatile",    "Llama 3.1 70B — alternativa estable"),
    "4": ("gemma2-9b-it",               "Gemma 2 9B    — modelo Google, buen rendimiento"),
}

TEMPERATURA_DEFAULT = 0.7
MAX_TOKENS_DEFAULT  = 1024


# ── Clase TutorVirtual ───────────────────────────────────────────────────────
class TutorVirtual:
    def __init__(self, api_key: str, materia_key: str = "1", modelo_key: str = "1"):
        self.client = Groq(api_key=api_key)
        self.materia_key = materia_key
        self.modelo_key  = modelo_key
        self.historial: list[dict] = []
        self._reset_historial()

    @property
    def materia_nombre(self) -> str:
        return MATERIAS[self.materia_key][0]

    @property
    def modelo_nombre(self) -> str:
        return MODELOS[self.modelo_key][0]

    def _reset_historial(self):
        system_prompt = MATERIAS[self.materia_key][1]
        self.historial = [{"role": "system", "content": system_prompt}]

    def cambiar_materia(self, key: str):
        self.materia_key = key
        self._reset_historial()

    def cambiar_modelo(self, key: str):
        self.modelo_key = key

    def preguntar(self, pregunta: str, temperatura: float = TEMPERATURA_DEFAULT,
                  max_tokens: int = MAX_TOKENS_DEFAULT) -> str:
        self.historial.append({"role": "user", "content": pregunta})
        response = self.client.chat.completions.create(
            model=self.modelo_nombre,
            messages=self.historial,
            temperature=temperatura,
            max_tokens=max_tokens,
        )
        respuesta = response.choices[0].message.content
        self.historial.append({"role": "assistant", "content": respuesta})
        return respuesta

    def historial_legible(self) -> list[dict]:
        return [m for m in self.historial if m["role"] != "system"]

    def guardar_historial(self, ruta: str = "historial_sesion.json"):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self.historial_legible(), f, ensure_ascii=False, indent=2)
        return ruta


# ── Menús de selección ───────────────────────────────────────────────────────
def seleccionar_materia(actual: str = None) -> str:
    print(f"\n{bold('Selecciona la materia:')}")
    for k, (nombre, _) in MATERIAS.items():
        marca = green(" ◄ actual") if k == actual else ""
        print(f"  {cyan(k)}) {nombre}{marca}")
    while True:
        opcion = input(f"\n{gray('Opción')} [{actual or '1'}]: ").strip() or (actual or "1")
        if opcion in MATERIAS:
            return opcion
        print(red("Opción inválida."))


def seleccionar_modelo(actual: str = None) -> str:
    print(f"\n{bold('Selecciona el modelo LLM:')}")
    for k, (nombre, desc) in MODELOS.items():
        marca = green(" ◄ actual") if k == actual else ""
        print(f"  {cyan(k)}) {bold(nombre)}{marca}")
        print(f"     {gray(desc)}")
    while True:
        opcion = input(f"\n{gray('Opción')} [{actual or '1'}]: ").strip() or (actual or "1")
        if opcion in MODELOS:
            return opcion
        print(red("Opción inválida."))


# ── Ayuda ────────────────────────────────────────────────────────────────────
AYUDA = f"""
{bold('Comandos disponibles:')}
  {cyan('/ayuda')}      Muestra este mensaje
  {cyan('/materia')}    Cambia la materia (reinicia el historial)
  {cyan('/modelo')}     Cambia el modelo LLM
  {cyan('/nuevo')}      Reinicia el historial sin cambiar materia/modelo
  {cyan('/historial')}  Imprime los mensajes de la sesión actual
  {cyan('/guardar')}    Exporta el historial a historial_sesion.json
  {cyan('/salir')}      Termina el programa
"""


# ── Función principal ────────────────────────────────────────────────────────
def main():
    # Banner
    print(f"""
{C.CYAN}{C.BOLD}╔══════════════════════════════════════════════╗
║        🎓  TUTOR VIRTUAL INTELIGENTE         ║
║            Powered by Groq LLM               ║
╚══════════════════════════════════════════════╝{C.RESET}
""")

    # ── API Key ──────────────────────────────────────────────────────────────
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        print(f"{yellow('ℹ')} No se encontró la variable de entorno GROQ_API_KEY.")
        print(f"  Puedes obtener una clave gratuita en: {cyan('https://console.groq.com/keys')}\n")
        api_key = input(bold("Ingresa tu GROQ API Key: ")).strip()
        if not api_key:
            print(red("Error: se requiere una API Key para continuar."))
            sys.exit(1)

    # ── Selección inicial ────────────────────────────────────────────────────
    materia_key = seleccionar_materia()
    modelo_key  = seleccionar_modelo()

    # ── Inicializar tutor ────────────────────────────────────────────────────
    try:
        tutor = TutorVirtual(api_key, materia_key, modelo_key)
    except Exception as e:
        print(red(f"Error al inicializar el tutor: {e}"))
        sys.exit(1)

    print(f"""
{green('✓')} Tutor listo.  Materia: {bold(tutor.materia_nombre)}  |  Modelo: {bold(tutor.modelo_nombre)}
{gray('Escribe tu pregunta o usa /ayuda para ver los comandos disponibles.')}
{gray('─' * 60)}""")

    # ── Bucle de conversación ────────────────────────────────────────────────
    while True:
        try:
            entrada = input(f"\n{C.CYAN}{C.BOLD}Tú:{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n{yellow('Hasta pronto 👋')}")
            break

        if not entrada:
            continue

        # ── Comandos ─────────────────────────────────────────────────────────
        if entrada.lower() == "/salir":
            print(f"\n{yellow('Hasta pronto 👋')}")
            break

        elif entrada.lower() == "/ayuda":
            print(AYUDA)

        elif entrada.lower() == "/nuevo":
            tutor._reset_historial()
            print(green("✓ Historial reiniciado."))

        elif entrada.lower() == "/materia":
            nuevo_key = seleccionar_materia(tutor.materia_key)
            tutor.cambiar_materia(nuevo_key)
            print(green(f"✓ Materia cambiada a '{tutor.materia_nombre}'. Historial reiniciado."))

        elif entrada.lower() == "/modelo":
            nuevo_key = seleccionar_modelo(tutor.modelo_key)
            tutor.cambiar_modelo(nuevo_key)
            print(green(f"✓ Modelo cambiado a '{tutor.modelo_nombre}'."))

        elif entrada.lower() == "/historial":
            msgs = tutor.historial_legible()
            if not msgs:
                print(gray("El historial está vacío."))
            else:
                print(f"\n{bold('── Historial de la sesión ──')}")
                for m in msgs:
                    rol = bold(cyan("Tú:")) if m["role"] == "user" else bold(green("Tutor:"))
                    print(f"\n{rol}")
                    print(m["content"])
                print(gray("─" * 40))

        elif entrada.lower() == "/guardar":
            try:
                ruta = tutor.guardar_historial()
                print(green(f"✓ Historial guardado en '{ruta}'."))
            except Exception as e:
                print(red(f"Error al guardar: {e}"))

        # ── Pregunta al tutor ─────────────────────────────────────────────────
        else:
            print(f"\n{C.GREEN}{C.BOLD}Tutor{C.RESET} {gray(f'({tutor.modelo_nombre})')}:")
            print(gray("Pensando..."), end="\r")
            try:
                respuesta = tutor.preguntar(entrada)
                # Limpiar línea "Pensando..."
                print(" " * 20, end="\r")
                print(respuesta)
            except Exception as e:
                print(" " * 20, end="\r")
                print(red(f"Error al consultar la API: {e}"))

    # ── Al salir, ofrecer guardar ─────────────────────────────────────────────
    if tutor.historial_legible():
        try:
            guardar = input(f"\n{yellow('¿Guardar el historial antes de salir? [s/N]: ')}").strip().lower()
            if guardar == "s":
                ruta = tutor.guardar_historial()
                print(green(f"✓ Historial guardado en '{ruta}'."))
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    main()
