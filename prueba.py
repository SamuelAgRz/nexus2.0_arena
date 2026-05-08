from nsr_conn import AdomdConnector
import os
#from agents.dax_executor import DaxExecutorAgent# Obtener la ruta absoluta de la carpeta donde está este script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(os.getcwd())
 
# Construir la ruta a la DLL dentro de la carpeta /lib
PATH_DLL = os.path.join(BASE_DIR, 'lib', 'Microsoft.AnalysisServices.AdomdClient.dll')
 
STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
)
 
# Instanciar clase
nsr_conn = AdomdConnector(PATH_DLL, STR_CONN)
print(f"Buscando DLL en: {PATH_DLL}")
print("Ejecutando consulta...")
df = nsr_conn.ejecutar_query("""
EVALUATE
ROW("Test", 1)
""")
 
print(df)