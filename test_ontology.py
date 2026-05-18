import os
import sys
import pandas as pd

from src.connections.ontology import AdomdConnector


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
        "Data Source=powerbi://api.powerbi.com/v1.0/myorg/mf-pocai-eastus2-dev-01;"
        "Initial Catalog=ontology_nsr;"
        "Integrated Security=ClaimsToken;"
)

nsr_conn = AdomdConnector(PATH_DLL, STR_CONN)

# Consulta DAX
query = "EVALUATE VALUES('kpi_documentation 1')"


print(f"Buscando DLL en: {PATH_DLL}")
print("Ejecutando consulta...")
df = nsr_conn.ejecutar_query(query)
df.to_csv("docs/ontology/ontology_table.csv", index=False)

if df is not None:
    print("\n--- Resultado Obtenido ---")
    print(df.head())