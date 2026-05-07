import os
import sys
import pandas as pd

from src.connections.nsr_conn import AdomdConnector


# ============================================================
# 1. Paths
# ============================================================

BASE_DIR =  r"c:\\Users\\AdrianLandaverde\\Documents\\nexus2.0_arena"

PATH_DLL = os.path.join(
    BASE_DIR,
    "lib",
    "Microsoft.AnalysisServices.AdomdClient.dll"
)

if not os.path.exists(PATH_DLL):
    raise FileNotFoundError(f"❌ DLL no encontrada: {PATH_DLL}")

print(f"✔ DLL encontrada en: {PATH_DLL}")


# ============================================================
# 2. Connection
# ============================================================

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
)

nsr_conn = AdomdConnector(PATH_DLL, STR_CONN)


# ============================================================
# 3. Helper (ESTA ES LA QUE TE FALTABA)
# ============================================================

def run_query(name: str, query: str):
    print("\n" + "=" * 80)
    print(f"🚀 {name}")
    print("=" * 80)
    print(query)

    df = nsr_conn.ejecutar_query(query)

    if df is None:
        print(f"❌ Error en la consulta: {name}")
        return None

    print(f"✅ OK - {name}")
    print(f"Shape: {df.shape}")
    print(df.head(20))

    return df


# ============================================================
# 4. Smoke test
# ============================================================

test_query = """
EVALUATE
ROW("Test", 1)
"""

df_test = run_query("Smoke test", test_query)

if df_test is None:
    print("❌ No hay conexión. Revisa token/autenticación.")
    sys.exit(1)


cols = nsr_conn.ejecutar_query("""
EVALUATE
SUMMARIZECOLUMNS(
    'Channel'[Trade Channel]
)
ORDER BY
    'Channel'[Trade Channel] ASC
""")

print(cols)