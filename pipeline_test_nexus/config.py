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
AGENT_BTN_SELECTOR = "button:has-text('Agent Interaction')"
THREAD_ID_RE = re.compile(r"threadId:\s*([0-9a-fA-F-]+)")
SUMMARIZER_RE = re.compile(r"Source: SummarizerAgent.*?Content:\n\n(.*?)\nCopy", re.DOTALL)

RESPONSE_TIMEOUT_MS = 600_000  # 10 minutos por pregunta
CONCURRENCY = 5
HEADLESS = False
