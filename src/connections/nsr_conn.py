import os
import sys
import logging
from pathlib import Path

import clr
import pandas as pd
from dotenv import load_dotenv


class Config:
    BASE_DIR = Path(__file__).resolve().parent
    DLL_PATH = BASE_DIR / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll"

    PBI_TENANT_ID = os.getenv("PBI_TENANT_ID")
    PBI_CLIENT_ID = os.getenv("PBI_CLIENT_ID")
    PBI_CLIENT_SECRET = os.getenv("PBI_CLIENT_SECRET")

    PBI_WORKSPACE_NAME = os.getenv("PBI_WORKSPACE_NAME", "NSR LATAM [Test]")
    PBI_DATASET_NAME = os.getenv("PBI_DATASET_NAME", "NSR LATAM Cube")

    APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "INFO")


class AdomdConnector:
    def __init__(self, dll_path: str, connection_string: str):
        self.dll_path = str(dll_path)
        self.connection_string = connection_string
        self.pyadomd = None
        self._driver_loaded = False

        self._setup_logging()

        if self._setup_environment():
            import pyadomd
            self.pyadomd = pyadomd
            self._driver_loaded = True

    def _setup_logging(self):
        logging.basicConfig(
            level=getattr(logging, Config.APP_LOG_LEVEL.upper(), logging.INFO),
            format="%(asctime)s | %(levelname)s | %(message)s",
        )

    def _setup_environment(self) -> bool:
        if not os.path.exists(self.dll_path):
            logging.error(f"No se encontró la DLL en: {self.dll_path}")
            return False

        try:
            dll_dir = os.path.dirname(self.dll_path)

            if dll_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = dll_dir + os.pathsep + os.environ.get("PATH", "")

            clr.AddReference(self.dll_path)
            import Microsoft.AnalysisServices.AdomdClient  # noqa: F401

            logging.info("Entorno .NET y DLL preparados correctamente.")
            return True

        except Exception as e:
            logging.exception(f"Error configurando el entorno .NET: {e}")
            return False

    def ejecutar_query(self, dax_query: str) -> pd.DataFrame | None:
        if not self._driver_loaded or self.pyadomd is None:
            logging.error("El driver ADOMD no está cargado correctamente.")
            return None

        try:
            logging.info("Ejecutando consulta DAX...")

            with self.pyadomd.Pyadomd(self.connection_string) as conn:
                with conn.cursor().execute(dax_query) as cur:
                    rows = cur.fetchall()

                    if not rows:
                        logging.info("La consulta no devolvió registros.")
                        return pd.DataFrame()

                    columns = [col[0] for col in cur.description]
                    return pd.DataFrame(rows, columns=columns)

        except Exception as e:
            logging.exception(f"Error ejecutando consulta DAX: {e}")
            return None


def validate_env_vars():
    required_vars = [
        "PBI_TENANT_ID",
        "PBI_CLIENT_ID",
        "PBI_CLIENT_SECRET",
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(
            "Faltan variables en .env: "
            + ", ".join(missing)
        )


def build_connection_string() -> str:
    workspace = Config.PBI_WORKSPACE_NAME
    dataset = Config.PBI_DATASET_NAME

    tenant_id = Config.PBI_TENANT_ID
    client_id = Config.PBI_CLIENT_ID
    client_secret = Config.PBI_CLIENT_SECRET

    return (
        "Provider=MSOLAP;"
        f"Data Source=powerbi://api.powerbi.com/v1.0/myorg/{workspace};"
        f"Initial Catalog={dataset};"
        f"User ID=app:{client_id}@{tenant_id};"
        f"Password={client_secret};"
    )


def main():
    load_dotenv()

    validate_env_vars()

    logging.info(f"Buscando DLL en: {Config.DLL_PATH}")

    conn_string = build_connection_string()

    nsr_conn = AdomdConnector(
        dll_path=Config.DLL_PATH,
        connection_string=conn_string,
    )

    query = """
    EVALUATE
    TOPN(
        10,
        VALUES('Reporting View')
    )
    """

    df = nsr_conn.ejecutar_query(query)

    if df is not None:
        print("\n--- Resultado obtenido ---")
        print(df.head())


if __name__ == "__main__":
    main()