import sys
import os
import clr
import pandas as pd
import yaml

class AdomdConnector:
    """
    Clase para gestionar la conexión a Power BI.
    El entorno debera estar listo antes de cargar pyadomd.
    """
    
    def __init__(self, dll_path, connection_string):
        self.dll_path = dll_path
        self.connection_string = connection_string
        self._driver_loaded = False
        self.pyadomd = None 
        
        # Configurar el entorno ANTES de importar pyadomd
        if self._setup_environment():
            # Importar pyadomd solo cuando el PATH y la DLL están listos
            import pyadomd
            self.pyadomd = pyadomd
            self._driver_loaded = True

    def _setup_environment(self):
        """Configura el PATH de Windows y carga la referencia de .NET."""
        if not os.path.exists(self.dll_path):
            print(f"❌ Error: No se encontró la DLL en {self.dll_path}")
            return False

        try:
            dll_dir = os.path.dirname(self.dll_path)
            
            # Agregar al PATH para que Windows encuentre las dependencias de la DLL
            if dll_dir not in os.environ['PATH']:
                os.environ['PATH'] = dll_dir + os.pathsep + os.environ['PATH']

            # Cargar la referencia en el Global Assembly Cache de PythonNet 
            clr.AddReference(self.dll_path)
            
            # Forzar el reconocimiento del namespace de Microsoft 
            import Microsoft.AnalysisServices.AdomdClient
            
            print("✅ Entorno .NET y DLL preparados.")
            return True
        except Exception as e:
            print(f"❌ Error configurando el entorno .NET: {e}")
            return False

    def ejecutar_query(self, dax_query):
        """Ejecuta DAX y devuelve un DataFrame"""
        if not self._driver_loaded or self.pyadomd is None:
            print("❌ El driver no está cargado correctamente.")
            return None

        try:
            # Usamos la instancia de pyadomd cargada dinámicamente 
            with self.pyadomd.Pyadomd(self.connection_string) as conn:
                with conn.cursor().execute(dax_query) as cur:
                    data = cur.fetchall()
                    
                    if not data:
                        return pd.DataFrame()
                    
                    columnas = [d[0] for d in cur.description]
                    return pd.DataFrame(data, columns=columnas)
                    
        except Exception as e:
            print(f"❌ Error en la consulta: {e}")
            return None


# --- YAML ---
class LiteralString(str):
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar(
        'tag:yaml.org,2002:str',
        data,
        style='|'
    )

yaml.add_representer(LiteralString, literal_presenter)

def queries_yaml(path_yaml):
    """Lee el archivo YAML y devuelve la lista de consultas."""
    with open(path_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path_salida, datos):
    """Guarda preguntas, DAX y resultados en un YAML."""
    with open(path_salida, "w", encoding="utf-8") as f:
        yaml.dump(
            datos,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )

# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    # 1. Obtener la ruta de la carpeta actual (src/connections)
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Subir dos niveles para llegar a la raíz del proyecto (nexus2.0_arena)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
    
    # 3. Construir la ruta a la DLL buscando en la carpeta lib de la raíz
    PATH_DLL = os.path.join(PROJECT_ROOT, 'lib', 'Microsoft.AnalysisServices.AdomdClient.dll')
    
    STR_CONN = (
        "Provider=MSOLAP;"
        "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM;"
        "Initial Catalog=NSR LATAM Cube;"
        "Integrated Security=ClaimsToken;"
    )

    # Instanciar clase
    nsr_conn = AdomdConnector(PATH_DLL, STR_CONN)

    # Consulta DAX
    #query = "EVALUATE VALUES('Reporting View')"
    PATH_YAML = os.path.join(PROJECT_ROOT, 'playwright_test', "queries.yaml") 
    PATH_OUTPUT = os.path.join(PROJECT_ROOT, 'playwright_test', "queries_answered.yaml")

    consultas = queries_yaml(PATH_YAML)

    for i, consulta in enumerate(consultas, start=1):

        print(f"Ejecutando {i}/{len(consultas)} - ID {consulta['id']}")

        df = nsr_conn.ejecutar_query(consulta["dax_query"])

        if df is None:
            consulta["dax_answer"] = {
                "status": "error",
                "data": None
            }

        elif df.empty:
            consulta["dax_answer"] = {
                "status": "ok",
                "data": []
            }

        else:
            consulta["dax_answer"] = {
                "status": "ok",
                "data": df.to_dict(orient="records")
            }

    for consulta in consultas:
        consulta["dax_query"] = LiteralString(consulta["dax_query"])
        
    save_yaml(PATH_OUTPUT, consultas)

    print(f"Resultados guardados en {PATH_OUTPUT}")