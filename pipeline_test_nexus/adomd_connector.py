"""
Conector ADOMD para ejecutar DAX contra Power BI (ground truth)
y helpers de YAML compartidos por el pipeline.
Copiado de src/connections/nsr_latam_queries.py.
"""

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
    """String que se serializa como bloque literal (|) en YAML."""
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
    """Guarda datos en un YAML legible (unicode, sin ordenar llaves)."""
    with open(path_salida, "w", encoding="utf-8") as f:
        yaml.dump(
            datos,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )
