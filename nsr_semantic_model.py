"""
Nexus-ready exporter for NSR LATAM Cube semantic model metadata.

What this script does:
1. Connects to the Power BI / SSAS semantic model through your existing AdomdConnector.
2. Extracts raw INFO.* metadata without assuming fixed column names.
3. Falls back safely when a DMV/INFO query is not supported.
4. Saves raw CSV files for auditability.
5. Normalizes metadata into stable Nexus-friendly JSON files:
   - nexus_semantic_model_context.json
   - nexus_intent_clarifier_context.json
   - nexus_dax_agent_context.json
6. Generates Markdown documentation for sharing with the team.

Run:
    pip install pandas tabulate
    python export_nsr_semantic_model_nexus_ready.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import traceback
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

# -----------------------------------------------------------------------------
# USER CONFIG
# -----------------------------------------------------------------------------

BASE_DIR = Path(r"C:\Users\SamuelAguilarRamirez\nexus2.0")
PROJECT_SRC_DIR = BASE_DIR

PATH_DLL = BASE_DIR / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll"

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
    "Persist Security Info=True;"
)

OUTPUT_BASE_DIR = BASE_DIR / "docs" / "semantic_model"
MODEL_NAME = "NSR LATAM Cube"
DATA_SOURCE_NAME = "NSR LATAM Cube UAT semantic model Power BI"

# Optional: names that are especially important for NSR Nexus agents.
IMPORTANT_TABLE_PATTERNS = [
    "Metrics",
    "Actuals",
    "Rev",
    "Vol",
    "BP",
    "RE",
    "Calendar",
    "Date",
    "Country",
    "Channel",
    "Customer",
    "Product",
    "Bottler",
    "Geography",
    "Package",
]

IMPORTANT_MEASURE_PATTERNS = [
    "NSR",
    "Net Sales",
    "Revenue",
    "Unit Case",
    "UC",
    "Volume",
    "Liter",
    "Discount",
    "BP",
    "RE",
    "Actual",
    "YTD",
    "MTD",
    "QTD",
    "WTD",
    "DTD",
    "YoY",
]

# -----------------------------------------------------------------------------
# IMPORT PROJECT CONNECTOR
# -----------------------------------------------------------------------------

sys.path.insert(0, str(PROJECT_SRC_DIR))

try:
    from src.connections.nsr_conn import AdomdConnector
except Exception as exc:
    raise ImportError(
        "Could not import AdomdConnector. Check BASE_DIR and src.connections.nsr_conn."
    ) from exc


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

@dataclass
class QueryResult:
    name: str
    status: str
    row_count: int = 0
    column_count: int = 0
    columns: Optional[List[str]] = None
    error: Optional[str] = None
    query: Optional[str] = None


def now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_filename(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_\-]+", "_", name).strip("_").lower()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def clean_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def df_to_records(df: Optional[pd.DataFrame], limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    work = df.copy()
    if limit is not None:
        work = work.head(limit)
    work = work.where(pd.notnull(work), None)
    return [{k: clean_value(v) for k, v in row.items()} for row in work.to_dict(orient="records")]


def first_existing_col(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    if df is None or df.empty:
        return None
    cols_lower = {str(c).lower(): c for c in df.columns}
    for candidate in candidates:
        if candidate.lower() in cols_lower:
            return cols_lower[candidate.lower()]
    return None


def contains_any(text: Any, patterns: List[str]) -> bool:
    if text is None:
        return False
    t = str(text).lower()
    return any(p.lower() in t for p in patterns)


def markdown_table(df: Optional[pd.DataFrame], max_rows: int = 80) -> str:
    if df is None or df.empty:
        return "No data available."
    try:
        preview = df.head(max_rows).copy()
        return preview.to_markdown(index=False)
    except Exception:
        return df.head(max_rows).to_string(index=False)


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, default=str)


def save_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(text)


# -----------------------------------------------------------------------------
# DAX / INFO QUERIES
# Keep these RAW. Do not SELECTCOLUMNS because INFO schemas vary by endpoint.
# -----------------------------------------------------------------------------

INFO_QUERIES: Dict[str, str] = {
    "tables": "EVALUATE INFO.TABLES()",
    "columns": "EVALUATE INFO.COLUMNS()",
    "measures": "EVALUATE INFO.MEASURES()",
    "relationships": "EVALUATE INFO.RELATIONSHIPS()",
    "hierarchies": "EVALUATE INFO.HIERARCHIES()",
    "hierarchy_levels": "EVALUATE INFO.HIERARCHYLEVELS()",
    "partitions": "EVALUATE INFO.PARTITIONS()",
    "calculation_groups": "EVALUATE INFO.CALCULATIONGROUPS()",
    "calculation_items": "EVALUATE INFO.CALCULATIONITEMS()",
    "cultures": "EVALUATE INFO.CULTURES()",
    "perspectives": "EVALUATE INFO.PERSPECTIVES()",
    "annotations": "EVALUATE INFO.ANNOTATIONS()",
}

# Some environments support DMVs better than INFO.*. These are optional fallbacks.
DMV_FALLBACK_QUERIES: Dict[str, str] = {
    "tables_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_TABLES",
    "columns_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_COLUMNS",
    "measures_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_MEASURES",
    "relationships_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_RELATIONSHIPS",
    "hierarchies_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_HIERARCHIES",
    "partitions_dmv": "SELECT * FROM $SYSTEM.TMSCHEMA_PARTITIONS",
}


# -----------------------------------------------------------------------------
# EXTRACTION
# -----------------------------------------------------------------------------

def run_query(conn: Any, name: str, query: str) -> Tuple[Optional[pd.DataFrame], QueryResult]:
    print(f"\nRunning query: {name}")
    try:
        df = conn.ejecutar_query(query)
        if df is None:
            result = QueryResult(name=name, status="empty_or_none", query=query)
            print(f"Warning: {name} returned None")
            return None, result

        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        result = QueryResult(
            name=name,
            status="success",
            row_count=len(df),
            column_count=len(df.columns),
            columns=[str(c) for c in df.columns],
            query=query,
        )
        print(f"Success: {name} | rows={len(df)} | columns={len(df.columns)}")
        return df, result
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
        print(f"Error: {name} failed: {err}")
        result = QueryResult(name=name, status="error", error=err, query=query)
        return None, result


def extract_metadata(conn: Any) -> Tuple[Dict[str, pd.DataFrame], List[QueryResult]]:
    frames: Dict[str, pd.DataFrame] = {}
    results: List[QueryResult] = []

    for name, query in INFO_QUERIES.items():
        df, result = run_query(conn, name, query)
        results.append(result)
        if df is not None:
            frames[name] = df

    # DMV fallbacks are saved separately to avoid mixing schemas.
    for name, query in DMV_FALLBACK_QUERIES.items():
        df, result = run_query(conn, name, query)
        results.append(result)
        if df is not None:
            frames[name] = df

    return frames, results


# -----------------------------------------------------------------------------
# NORMALIZATION LAYER
# -----------------------------------------------------------------------------

def normalize_tables(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    df = frames.get("tables") or frames.get("tables_dmv")
    if df is None or df.empty:
        return []

    name_col = first_existing_col(df, ["Name", "Table", "TableName", "ExplicitName"])
    id_col = first_existing_col(df, ["ID", "Id", "TableID", "TableId"])
    hidden_col = first_existing_col(df, ["IsHidden", "Hidden"])
    desc_col = first_existing_col(df, ["Description"])

    records = []
    for _, row in df.iterrows():
        name = clean_value(row.get(name_col)) if name_col else None
        records.append({
            "table_id": clean_value(row.get(id_col)) if id_col else None,
            "table_name": name,
            "is_hidden": clean_value(row.get(hidden_col)) if hidden_col else None,
            "description": clean_value(row.get(desc_col)) if desc_col else None,
            "is_important_candidate": contains_any(name, IMPORTANT_TABLE_PATTERNS),
            "raw": {str(k): clean_value(v) for k, v in row.items()},
        })
    return records


def normalize_columns(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    df = frames.get("columns") or frames.get("columns_dmv")
    if df is None or df.empty:
        return []

    table_col = first_existing_col(df, ["Table", "TableName", "ExplicitTableName", "TableID", "TableId"])
    name_col = first_existing_col(df, ["Name", "Column", "ColumnName", "ExplicitName"])
    data_type_col = first_existing_col(df, ["DataType", "ExplicitDataType", "Type", "DataTypeName"])
    hidden_col = first_existing_col(df, ["IsHidden", "Hidden"])
    desc_col = first_existing_col(df, ["Description"])
    display_folder_col = first_existing_col(df, ["DisplayFolder", "Folder"])
    sort_by_col = first_existing_col(df, ["SortByColumn", "SortByColumnID", "SortByColumnId"])

    records = []
    for _, row in df.iterrows():
        table_name = clean_value(row.get(table_col)) if table_col else None
        col_name = clean_value(row.get(name_col)) if name_col else None
        records.append({
            "table_name_or_id": table_name,
            "column_name": col_name,
            "data_type": clean_value(row.get(data_type_col)) if data_type_col else None,
            "is_hidden": clean_value(row.get(hidden_col)) if hidden_col else None,
            "description": clean_value(row.get(desc_col)) if desc_col else None,
            "display_folder": clean_value(row.get(display_folder_col)) if display_folder_col else None,
            "sort_by_column": clean_value(row.get(sort_by_col)) if sort_by_col else None,
            "dax_reference_guess": f"'{table_name}'[{col_name}]" if table_name and col_name else None,
            "is_important_candidate": contains_any(table_name, IMPORTANT_TABLE_PATTERNS) or contains_any(col_name, IMPORTANT_TABLE_PATTERNS),
            "raw": {str(k): clean_value(v) for k, v in row.items()},
        })
    return records


def normalize_measures(frames: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
    df = frames.get("measures") or frames.get("measures_dmv")
    if df is None or df.empty:
        return []

    table_col = first_existing_col(df, ["Table", "TableName", "ExplicitTableName", "TableID", "TableId"])
    name_col = first_existing_col(df, ["Name", "Measure", "MeasureName", "ExplicitName"])
    expr_col = first_existing_col(df, ["Expression"])
    format_col = first_existing_col(df, ["FormatString", "FormatStringExpression"])
    hidden_col = first_existing_col(df, ["IsHidden", "Hidden"])
    desc_col = first_existing_col(df, ["Description"])
    display_folder_col = first_existing_col(df, ["DisplayFolder", "Folder"])

    records = []
    for _, row in df.iterrows():
        table_name = clean_value(row.get(table_col)) if table_col else None
        measure_name = clean_value(row.get(name_col)) if name_col else None
        expression = clean_value(row.get(expr_col)) if expr_col else None
        records.append({
            "table_name_or_id": table_name,
            "measure_name": measure_name,
            "expression": expression,
            "format_string": clean_value(row.get(format_col)) if format_col else None,
            "is_hidden": clean_value(row.get(hidden_col)) if hidden_col else None,
            "description": clean_value(row.get(desc_col)) if desc_col else None,
            "display_folder": clean_value(row.get(display_folder_col)) if display_folder_col else None,
            "dax_reference": f"[{measure_name}]" if measure_name else None,
            "is_metrics_candidate": contains_any(table_name, ["Metrics"]) or contains_any(measure_name, IMPORTANT_MEASURE_PATTERNS),
            "is_important_candidate": contains_any(table_name, IMPORTANT_TABLE_PATTERNS) or contains_any(measure_name, IMPORTANT_MEASURE_PATTERNS),
            "raw": {str(k): clean_value(v) for k, v in row.items()},
        })
    return records


def build_nexus_context(frames: Dict[str, pd.DataFrame], query_results: List[QueryResult]) -> Dict[str, Any]:
    tables = normalize_tables(frames)
    columns = normalize_columns(frames)
    measures = normalize_measures(frames)

    visible_columns = [c for c in columns if c.get("is_hidden") in [False, "False", "false", 0, None]]
    visible_measures = [m for m in measures if m.get("is_hidden") in [False, "False", "false", 0, None]]
    important_measures = [m for m in visible_measures if m.get("is_important_candidate")]
    important_columns = [c for c in visible_columns if c.get("is_important_candidate")]

    table_to_columns: Dict[str, List[Dict[str, Any]]] = {}
    for col in visible_columns:
        key = str(col.get("table_name_or_id") or "UNKNOWN")
        table_to_columns.setdefault(key, []).append({
            "column_name": col.get("column_name"),
            "data_type": col.get("data_type"),
            "dax_reference_guess": col.get("dax_reference_guess"),
            "description": col.get("description"),
        })

    measure_groups: Dict[str, List[Dict[str, Any]]] = {}
    for measure in visible_measures:
        key = str(measure.get("table_name_or_id") or measure.get("display_folder") or "UNKNOWN")
        measure_groups.setdefault(key, []).append({
            "measure_name": measure.get("measure_name"),
            "dax_reference": measure.get("dax_reference"),
            "format_string": measure.get("format_string"),
            "description": measure.get("description"),
            "display_folder": measure.get("display_folder"),
        })

    payload = {
        "metadata": {
            "model_name": MODEL_NAME,
            "data_source_name": DATA_SOURCE_NAME,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "purpose": "Nexus-ready semantic model metadata context for Intent Clarifier and DAX agents.",
            "note": "Raw INFO/DMV schemas vary by Power BI XMLA endpoint. This file is normalized in Python and should be preferred over hardcoded INFO.SELECTCOLUMNS queries.",
        },
        "extraction_status": [asdict(r) for r in query_results],
        "raw_available_frames": {
            name: {"rows": len(df), "columns": [str(c) for c in df.columns]}
            for name, df in frames.items()
        },
        "business_context": {
            "nsr_definition": "NSR refers to Net Sales Revenue SELL-IN.",
            "source_type": "Power BI semantic model / XMLA endpoint.",
            "important_measure_tables_expected": [
                "Metrics-Actuals-Rev",
                "Metrics-Actuals-Vol",
                "Metrics-BP",
                "Metrics-RE",
            ],
            "agent_usage": [
                "Intent Clarifier should map user terms to canonical table/column/measure names.",
                "DAX Developer should only use measures and dimensions that exist in this exported context.",
                "DAX Validator should reject hallucinated tables, columns, and measures.",
                "Result Summarizer should explain results using business terminology and avoid exposing internal metadata unless needed.",
            ],
        },
        "normalized": {
            "tables": tables,
            "columns": columns,
            "measures": measures,
            "visible_columns": visible_columns,
            "visible_measures": visible_measures,
            "important_columns_candidates": important_columns,
            "important_measures_candidates": important_measures,
            "table_to_columns": table_to_columns,
            "measure_groups": measure_groups,
            "relationships_raw": df_to_records(frames.get("relationships") or frames.get("relationships_dmv"), limit=1000),
            "hierarchies_raw": df_to_records(frames.get("hierarchies"), limit=1000),
            "hierarchy_levels_raw": df_to_records(frames.get("hierarchy_levels"), limit=1000),
        },
        "nexus_guardrails": {
            "do_not_hardcode_info_schema": True,
            "do_not_use_select_star": True,
            "use_existing_measures_first": True,
            "avoid_recomputing_governed_metrics": True,
            "clarify_ambiguous_terms_before_dax": True,
            "ask_all_missing_dimensions_in_one_message": True,
            "validate_dax_identifiers_against_context": True,
            "prefer_summarizecolumns_for_analytical_queries": True,
        },
    }

    return payload


def build_intent_clarifier_context(nexus_context: Dict[str, Any]) -> Dict[str, Any]:
    norm = nexus_context["normalized"]
    return {
        "metadata": nexus_context["metadata"],
        "business_context": nexus_context["business_context"],
        "available_visible_measures": [
            {
                "measure_name": m.get("measure_name"),
                "dax_reference": m.get("dax_reference"),
                "table_or_folder": m.get("table_name_or_id") or m.get("display_folder"),
                "description": m.get("description"),
                "format_string": m.get("format_string"),
            }
            for m in norm["visible_measures"]
            if m.get("measure_name")
        ],
        "important_measure_candidates": [
            {
                "measure_name": m.get("measure_name"),
                "dax_reference": m.get("dax_reference"),
                "table_or_folder": m.get("table_name_or_id") or m.get("display_folder"),
                "description": m.get("description"),
            }
            for m in norm["important_measures_candidates"]
            if m.get("measure_name")
        ],
        "available_dimensions": norm["table_to_columns"],
        "clarification_policy": {
            "collect_all_missing_dimensions_first": True,
            "ask_once_not_dimension_by_dimension": True,
            "ambiguous_term_behavior": "If user term cannot be mapped to an available measure/dimension, ask for clarification before DAX generation.",
            "period_behavior": "If period is missing, ask for the required time grain or use the default agreed by the NSR product owner.",
        },
    }


def build_dax_agent_context(nexus_context: Dict[str, Any]) -> Dict[str, Any]:
    norm = nexus_context["normalized"]
    valid_measure_names = sorted({m.get("measure_name") for m in norm["visible_measures"] if m.get("measure_name")})
    valid_column_refs = sorted({c.get("dax_reference_guess") for c in norm["visible_columns"] if c.get("dax_reference_guess")})

    return {
        "metadata": nexus_context["metadata"],
        "valid_measure_names": valid_measure_names,
        "valid_column_references_guess": valid_column_refs,
        "measure_groups": norm["measure_groups"],
        "table_to_columns": norm["table_to_columns"],
        "dax_generation_rules": [
            "Use EVALUATE for tabular queries.",
            "Prefer SUMMARIZECOLUMNS for grouped analytical output.",
            "Use existing semantic model measures instead of recomputing governed metrics.",
            "Do not use SELECT *.",
            "Never reference a table, column, or measure that is not present in this context.",
            "For previews use TOPN or keep outputs small.",
            "When sorting by a measure, include it in SUMMARIZECOLUMNS output or use an explicit variable table.",
        ],
        "example_templates": {
            "measure_by_dimension": "EVALUATE TOPN(50, SUMMARIZECOLUMNS('<DimensionTable>'[<Column>], \"Metric\", [<Measure>]), [Metric], DESC)",
            "single_measure": "EVALUATE ROW(\"Metric\", [<Measure>])",
            "distinct_dimension_values": "EVALUATE DISTINCT('<DimensionTable>'[<Column>]) ORDER BY '<DimensionTable>'[<Column>]",
        },
    }


# -----------------------------------------------------------------------------
# OUTPUTS
# -----------------------------------------------------------------------------

def save_outputs(frames: Dict[str, pd.DataFrame], query_results: List[QueryResult]) -> Tuple[Path, Path]:
    run_dir = OUTPUT_BASE_DIR / f"nsr_latam_cube_nexus_ready_{now_ts()}"
    ensure_dir(run_dir)

    print(f"\nExport run directory: {run_dir}")

    # Raw CSVs
    for name, df in frames.items():
        path = run_dir / f"{safe_filename(name)}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Saved CSV: {path}")

    status_df = pd.DataFrame([asdict(r) for r in query_results])
    status_path = run_dir / "extraction_status.csv"
    status_df.to_csv(status_path, index=False, encoding="utf-8-sig")
    print(f"Saved status: {status_path}")

    nexus_context = build_nexus_context(frames, query_results)
    intent_context = build_intent_clarifier_context(nexus_context)
    dax_context = build_dax_agent_context(nexus_context)

    save_json(run_dir / "nexus_semantic_model_context.json", nexus_context)
    save_json(run_dir / "nexus_intent_clarifier_context.json", intent_context)
    save_json(run_dir / "nexus_dax_agent_context.json", dax_context)

    # Also save latest copies for stable agent loading.
    save_json(OUTPUT_BASE_DIR / "nexus_semantic_model_context_latest.json", nexus_context)
    save_json(OUTPUT_BASE_DIR / "nexus_intent_clarifier_context_latest.json", intent_context)
    save_json(OUTPUT_BASE_DIR / "nexus_dax_agent_context_latest.json", dax_context)

    md = build_markdown(frames, query_results, nexus_context)
    md_path = run_dir / "nsr_latam_cube_nexus_ready_catalog.md"
    latest_md_path = OUTPUT_BASE_DIR / "nsr_latam_cube_nexus_ready_catalog_latest.md"
    save_text(md_path, md)
    save_text(latest_md_path, md)
    print(f"Saved Markdown: {md_path}")
    print(f"Saved latest Markdown: {latest_md_path}")

    prompt_pack = build_prompt_pack(intent_context, dax_context)
    prompt_path = run_dir / "nexus_agent_prompt_context.md"
    latest_prompt_path = OUTPUT_BASE_DIR / "nexus_agent_prompt_context_latest.md"
    save_text(prompt_path, prompt_pack)
    save_text(latest_prompt_path, prompt_pack)
    print(f"Saved prompt context: {prompt_path}")
    print(f"Saved latest prompt context: {latest_prompt_path}")

    return run_dir, latest_md_path


def build_markdown(frames: Dict[str, pd.DataFrame], query_results: List[QueryResult], context: Dict[str, Any]) -> str:
    norm = context["normalized"]
    lines: List[str] = []
    lines.append(f"# {MODEL_NAME} — Nexus-ready Semantic Model Catalog")
    lines.append("")
    lines.append(f"Generated at: {context['metadata']['generated_at']}")
    lines.append(f"Data source: **{DATA_SOURCE_NAME}**")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This catalog is designed to support Nexus agents with semantic model context without hardcoding unstable INFO() schemas.")
    lines.append("")
    lines.append("## Key Counts")
    lines.append("")
    lines.append(f"- Tables normalized: {len(norm['tables'])}")
    lines.append(f"- Columns normalized: {len(norm['columns'])}")
    lines.append(f"- Visible columns: {len(norm['visible_columns'])}")
    lines.append(f"- Measures normalized: {len(norm['measures'])}")
    lines.append(f"- Visible measures: {len(norm['visible_measures'])}")
    lines.append(f"- Important measure candidates: {len(norm['important_measures_candidates'])}")
    lines.append("")

    lines.append("## Extraction Status")
    lines.append("")
    lines.append(markdown_table(pd.DataFrame([asdict(r) for r in query_results]), max_rows=100))
    lines.append("")

    important_measures_df = pd.DataFrame([
        {
            "Measure": m.get("measure_name"),
            "DAX Ref": m.get("dax_reference"),
            "Table/Folder": m.get("table_name_or_id") or m.get("display_folder"),
            "Description": m.get("description"),
            "Format": m.get("format_string"),
        }
        for m in norm["important_measures_candidates"]
    ])
    lines.append("## Important Measure Candidates for Intent Clarifier")
    lines.append("")
    lines.append(markdown_table(important_measures_df, max_rows=150))
    lines.append("")

    important_columns_df = pd.DataFrame([
        {
            "Table": c.get("table_name_or_id"),
            "Column": c.get("column_name"),
            "DAX Ref Guess": c.get("dax_reference_guess"),
            "Data Type": c.get("data_type"),
            "Description": c.get("description"),
        }
        for c in norm["important_columns_candidates"]
    ])
    lines.append("## Important Dimension Candidates for Intent Clarifier")
    lines.append("")
    lines.append(markdown_table(important_columns_df, max_rows=200))
    lines.append("")

    for name in ["tables", "columns", "measures", "relationships", "hierarchies", "hierarchy_levels", "partitions"]:
        lines.append(f"## Raw Preview: {name}")
        lines.append("")
        lines.append(markdown_table(frames.get(name), max_rows=50))
        lines.append("")

    lines.append("## Nexus Guardrails")
    lines.append("")
    for key, value in context["nexus_guardrails"].items():
        lines.append(f"- **{key}**: {value}")
    lines.append("")

    return "\n".join(lines)


def build_prompt_pack(intent_context: Dict[str, Any], dax_context: Dict[str, Any]) -> str:
    important_measures = intent_context.get("important_measure_candidates", [])[:80]
    measure_lines = []
    for m in important_measures:
        measure_lines.append(
            f"- {m.get('dax_reference')} | table/folder: {m.get('table_or_folder')} | desc: {m.get('description')}"
        )

    dimension_lines = []
    dims = intent_context.get("available_dimensions", {})
    for table, cols in list(dims.items())[:80]:
        col_names = [c.get("column_name") for c in cols[:25] if c.get("column_name")]
        dimension_lines.append(f"- {table}: {', '.join(map(str, col_names))}")

    return f"""# Nexus Agent Prompt Context — NSR LATAM Cube

## Business Context
- NSR means Net Sales Revenue SELL-IN.
- Data source is a Power BI semantic model: {DATA_SOURCE_NAME}.
- Use governed semantic model measures first. Do not recompute metrics when a measure exists.

## Intent Clarifier Context
The Intent Clarifier must map user wording to canonical semantic model measures and dimensions.
If ambiguity remains, ask one consolidated clarification message with all missing dimensions.

### Important Measures Detected
{chr(10).join(measure_lines) if measure_lines else 'No important measures detected automatically. Review nexus_semantic_model_context.json.'}

### Available Dimension Candidates
{chr(10).join(dimension_lines) if dimension_lines else 'No dimensions detected automatically. Review nexus_semantic_model_context.json.'}

## DAX Developer Rules
{chr(10).join('- ' + rule for rule in dax_context.get('dax_generation_rules', []))}

## DAX Templates

### Single Measure
```DAX
EVALUATE
ROW("Metric", [<Measure>])
```

### Measure by Dimension
```DAX
EVALUATE
TOPN(
    50,
    SUMMARIZECOLUMNS(
        '<DimensionTable>'[<Column>],
        "Metric", [<Measure>]
    ),
    [Metric],
    DESC
)
```

### Distinct Dimension Values
```DAX
EVALUATE
DISTINCT('<DimensionTable>'[<Column>])
ORDER BY '<DimensionTable>'[<Column>]
```

## Validator Policy
Reject any DAX that uses tables, columns, or measures not present in `nexus_dax_agent_context_latest.json`.
"""


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main() -> None:
    print("Nexus-ready NSR semantic model exporter")
    print(f"cwd: {os.getcwd()}")
    print(f"BASE_DIR exists: {BASE_DIR.exists()} | {BASE_DIR}")
    print(f"DLL exists: {PATH_DLL.exists()} | {PATH_DLL}")

    if not PATH_DLL.exists():
        raise FileNotFoundError(f"ADOMD DLL not found: {PATH_DLL}")

    ensure_dir(OUTPUT_BASE_DIR)

    print("\nCreating ADOMD connector...")
    conn = AdomdConnector(str(PATH_DLL), STR_CONN)

    frames, query_results = extract_metadata(conn)
    run_dir, latest_md_path = save_outputs(frames, query_results)

    print("\nExport completed.")
    print(f"Run folder: {run_dir}")
    print(f"Latest Markdown: {latest_md_path}")
    print(f"Latest Nexus context JSON: {OUTPUT_BASE_DIR / 'nexus_semantic_model_context_latest.json'}")
    print(f"Latest Intent Clarifier JSON: {OUTPUT_BASE_DIR / 'nexus_intent_clarifier_context_latest.json'}")
    print(f"Latest DAX Agent JSON: {OUTPUT_BASE_DIR / 'nexus_dax_agent_context_latest.json'}")
    print(f"Latest Prompt Context: {OUTPUT_BASE_DIR / 'nexus_agent_prompt_context_latest.md'}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("\nFatal error:")
        traceback.print_exc()
        raise
