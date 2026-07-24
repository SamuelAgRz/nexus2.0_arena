"""
Paso 1 del pipeline: obtener el ground truth ejecutando el DAX
de cada pregunta del golden set contra el cubo de Power BI.
"""

from adomd_connector import AdomdConnector
from config import PATH_DLL, STR_CONN


def run_ground_truth(items: list[dict]) -> list[dict]:
    """
    Ejecuta el dax_query de cada item y le agrega la llave 'ground_truth':
        {status: ok|error, data: [...] | None}
    Los errores se registran por pregunta, nunca abortan el batch.
    """
    connector = AdomdConnector(PATH_DLL, STR_CONN)

    for i, item in enumerate(items, start=1):
        print(f"[GT {i}/{len(items)}] Ejecutando DAX - ID {item['id']}")

        df = connector.ejecutar_query(item["dax_query"])

        if df is None:
            item["ground_truth"] = {"status": "error", "data": None}
        elif df.empty:
            item["ground_truth"] = {"status": "ok", "data": []}
        else:
            item["ground_truth"] = {"status": "ok", "data": df.to_dict(orient="records")}

    ok = sum(1 for it in items if it["ground_truth"]["status"] == "ok")
    print(f"Ground truth listo: {ok}/{len(items)} consultas OK.\n")
    return items
