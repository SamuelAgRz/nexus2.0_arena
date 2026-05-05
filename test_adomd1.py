import os
import sys
import pandas as pd

from src.connections.nsr_conn import AdomdConnector


# ============================================================
# 1. Project paths
# ============================================================

BASE_DIR = r"C:\Users\SamuelAguilarRamirez\nexus2.0"

PATH_DLL = os.path.join(
    BASE_DIR,
    "lib",
    "Microsoft.AnalysisServices.AdomdClient.dll"
)

print("=" * 80)
print("NEXUS LOCAL - ADOMD DAX TEST")
print("=" * 80)
print(f"Current working directory: {os.getcwd()}")
print(f"BASE_DIR: {BASE_DIR}")
print(f"Buscando DLL en: {PATH_DLL}")

if not os.path.exists(PATH_DLL):
    raise FileNotFoundError(f"No se encontró la DLL en: {PATH_DLL}")


# ============================================================
# 2. Power BI / XMLA connection string
# ============================================================

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
)


# ============================================================
# 3. Instantiate connector
# ============================================================

nsr_conn = AdomdConnector(PATH_DLL, STR_CONN)


# ============================================================
# 4. Helper function
# ============================================================

def run_query(query_name: str, query: str) -> pd.DataFrame | None:
    print("\n" + "=" * 80)
    print(f"Ejecutando: {query_name}")
    print("=" * 80)
    print(query)

    df = nsr_conn.ejecutar_query(query)

    if df is None:
        print(f"❌ La consulta falló: {query_name}")
        return None

    print(f"✅ Consulta exitosa: {query_name}")
    print(f"Shape: {df.shape}")
    print(df.head(20))

    return df


# ============================================================
# 5. Smoke test
# ============================================================

smoke_test_query = """
EVALUATE
ROW("Test", 1)
"""

df_test = run_query("Smoke test", smoke_test_query)

if df_test is None:
    print("❌ No se pudo validar la conexión. Deteniendo ejecución.")
    sys.exit(1)


# ============================================================
# 6. Main NSR query
# ============================================================
# Nota:
# No usamos DATESYTD('Period'[Date]) porque en tu semantic model
# no existe 'Period'[Date]. La metadata muestra columnas como:
# day_dt, c445_week_start_dt, c445_month_start_dt y Year 445.
# Además, este modelo usa calendario 445. 
# Por eso probamos primero con filtro directo por Year 445.

nsr_query = """
EVALUATE
SUMMARIZECOLUMNS(
    'Channel'[LT1.2 - Channel Group],
    "NSR YTD (M)",
    CALCULATE(
        ROUND([NSR] / 1000000, 1),
        'Period'[Year 445] = "2025",
        'Scenario'[Scenario] = "Actuals"
    )
)
ORDER BY [NSR YTD (M)] DESC
"""

df_nsr = run_query("NSR YTD by Channel Group - no country filter", nsr_query)


# ============================================================
# 7. Optional: save result
# ============================================================

if df_nsr is not None:
    output_path = os.path.join(BASE_DIR, "outputs", "nsr_ytd_by_channel_group.csv")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df_nsr.to_csv(output_path, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 80)
    print("Resultado guardado")
    print("=" * 80)
    print(output_path)
else:
    print("\n❌ No se generó archivo porque la query principal falló.")