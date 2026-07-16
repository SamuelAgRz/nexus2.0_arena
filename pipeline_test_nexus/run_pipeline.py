"""
Pipeline de testing end-to-end del golden set contra la plataforma Nexus.

Para cada pregunta del golden set:
  1. Ground truth : ejecuta el dax_query contra el cubo de Power BI (ADOMD).
  2. Plataforma   : hace la pregunta al chatbot Nexus vía Playwright.
  3. Merge        : guarda un YAML con question + ground_truth + platform_answer.

Uso:
    .venv\\Scripts\\python.exe pipeline_test_nexus/run_pipeline.py
    .venv\\Scripts\\python.exe pipeline_test_nexus/run_pipeline.py --limit 2
    .venv\\Scripts\\python.exe pipeline_test_nexus/run_pipeline.py --only-ground-truth
    .venv\\Scripts\\python.exe pipeline_test_nexus/run_pipeline.py --only-platform

Requisitos:
  - credentials/auth_state.json (correr auth.py una vez para generarlo)
  - golden_set.yaml con items {id, question, dax_query}
"""

import argparse
import asyncio
import sys
from datetime import datetime

# La consola de Windows (cp1252) no soporta emojis/flechas de los prints
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from adomd_connector import LiteralString, queries_yaml, save_yaml
from config import AUTH_STATE_FILE, GOLDEN_SET_FILE, RESULTS_DIR
from ground_truth import run_ground_truth
from platform_runner import run_platform


def parse_args():
    parser = argparse.ArgumentParser(description="Pipeline de testing golden set vs plataforma Nexus")
    parser.add_argument("--limit", type=int, default=None,
                        help="Correr solo las primeras N preguntas (smoke test)")
    parser.add_argument("--only-ground-truth", action="store_true",
                        help="Solo ejecutar el DAX (sin Playwright)")
    parser.add_argument("--only-platform", action="store_true",
                        help="Solo preguntar a la plataforma (sin DAX)")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.only_ground_truth and args.only_platform:
        sys.exit("❌ --only-ground-truth y --only-platform son excluyentes.")

    run_platform_step = not args.only_ground_truth
    run_ground_truth_step = not args.only_platform

    if run_platform_step and not AUTH_STATE_FILE.exists():
        sys.exit(f"❌ No hay sesión guardada en {AUTH_STATE_FILE}. Corre auth.py primero.")

    if not GOLDEN_SET_FILE.exists():
        sys.exit(f"❌ No se encontró el golden set en {GOLDEN_SET_FILE}.")

    items = queries_yaml(GOLDEN_SET_FILE)
    if args.limit:
        items = items[:args.limit]

    run_dir = RESULTS_DIR / f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"Pipeline: {len(items)} pregunta(s) del golden set")
    print(f"Resultados → {run_dir}\n")

    # --- Paso 1: ground truth (DAX) ---
    if run_ground_truth_step:
        print("=== Paso 1/2: Ground truth (DAX contra Power BI) ===")
        items = run_ground_truth(items)
    else:
        print("=== Paso 1/2: Ground truth OMITIDO (--only-platform) ===\n")

    # --- Paso 2: plataforma (Playwright) ---
    if run_platform_step:
        print("=== Paso 2/2: Plataforma Nexus (Playwright) ===")
        items = asyncio.run(run_platform(items, run_dir))
    else:
        print("=== Paso 2/2: Plataforma OMITIDA (--only-ground-truth) ===\n")

    # --- Merge y guardado final ---
    resultados = []
    for item in items:
        resultados.append({
            "id": item["id"],
            "question": item["question"],
            "dax_query": LiteralString(item["dax_query"]),
            "ground_truth": item.get("ground_truth"),
            "platform_answer": item.get("platform_answer"),
        })

    results_file = run_dir / "results.yaml"
    save_yaml(results_file, resultados)

    print("=== Resumen ===")
    if run_ground_truth_step:
        gt_ok = sum(1 for r in resultados if (r["ground_truth"] or {}).get("status") == "ok")
        print(f"Ground truth OK : {gt_ok}/{len(resultados)}")
    if run_platform_step:
        pf_ok = sum(1 for r in resultados if (r["platform_answer"] or {}).get("status") == "ok")
        print(f"Plataforma OK   : {pf_ok}/{len(resultados)}")
    print(f"Resultados guardados en {results_file}")


if __name__ == "__main__":
    main()
