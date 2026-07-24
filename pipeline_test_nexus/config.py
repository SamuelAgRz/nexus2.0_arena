"""
Configuración central del pipeline de testing.
Todas las rutas, URLs, selectores y parámetros viven aquí.
"""

import re
from pathlib import Path

# --- Rutas ---
PIPELINE_DIR = Path(__file__).parent
PROJECT_ROOT = PIPELINE_DIR.parent

GOLDEN_SET_FILE = PIPELINE_DIR / "golden_set.yaml"
CREDENTIALS_DIR = PIPELINE_DIR / "credentials"
AUTH_STATE_FILE = CREDENTIALS_DIR / "auth_state.json"
RESULTS_DIR = PIPELINE_DIR / "results"

# --- Power BI / ADOMD (ground truth) ---
PATH_DLL = str(PROJECT_ROOT / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll")
STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM;"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
)

# --- Plataforma Nexus (Playwright) ---
CHATBOT_URL = "https://stage.nexusai.coke.com/weekly-ou360"

INPUT_SELECTOR = "textarea[placeholder='Ask me anything...']"
# El input existe desde el primer render pero queda disabled mientras la app
# inicializa — hay que esperar a que esté visible Y habilitado.
INPUT_READY_SELECTOR = "textarea[placeholder='Ask me anything...']:not([disabled])"
INPUT_READY_TIMEOUT_MS = 60_000   # espera por intento a que el input se habilite
PAGE_LOAD_ATTEMPTS = 3            # recargas de página si el input nunca se habilita
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
THREAD_ID_RE = re.compile(r"threadId:\s*([0-9a-fA-F-]+)")
SUMMARIZER_RE = re.compile(r"Source: SummarizerAgent.*?Content:\n\n(.*?)\nCopy", re.DOTALL)

# Cuánto esperar a que el textarea se vacíe tras presionar Enter (confirmación
# de envío). Bajo carga concurrente (varias ventanas mandando la misma
# pregunta a la vez) el indicador de "loading" puede tardar más en aparecer.
SEND_CONFIRM_TIMEOUT_MS = 20_000
# Timeout del click al reintentar un envío. Si el input ya no es clickeable
# para entonces, es señal de que el envío anterior sí funcionó y la app está
# ocupada procesándolo — no vale la pena esperar el default de Playwright (30s).
SEND_RETRY_CLICK_TIMEOUT_MS = 10_000

RESPONSE_TIMEOUT_MS = 600_000  # 10 minutos por pregunta
# Doble uso: tamaño del semáforo de ventanas de browser concurrentes Y
# número de corridas repetidas (misma pregunta) que se lanzan por cada
# item del golden set, para medir consistencia de respuestas.
CONCURRENCY = 5
HEADLESS = False
