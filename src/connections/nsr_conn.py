import sys
import os
import clr
import pandas as pd

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


# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    # Obtener la ruta absoluta de la carpeta donde está este script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
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

    # Consulta DAX
    query = "EVALUATE VALUES('Reporting View')"
    
    print(f"Buscando DLL en: {PATH_DLL}")
    print("Ejecutando consulta...")
    df = nsr_conn.ejecutar_query(query)

    if df is not None:
        print("\n--- Resultado Obtenido ---")
        print(df.head())