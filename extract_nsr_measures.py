"""
Nexus-ready extractor for exposed measures from NSR LATAM Cube semantic model.

Goal:
- Extract measures from INFO.MEASURES()
- Join measures to INFO.TABLES() to recover table names
- Handle Power BI XMLA INFO() schemas where column names are bracketed, e.g. [Name], [ExplicitName]
- Save raw and curated outputs as CSV and Markdown
- Generate a compact Nexus prompt context for DAX Developer / DAX Validator

Run from repo root:
    python extract_nsr_measures.py

Requirements:
    pip install pandas tabulate

Notes:
- This script assumes your local Nexus connector exposes nsr_conn.ejecutar_query(query)
- It does NOT rewrite or validate DAX queries; it only extracts semantic model metadata.
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

# -----------------------------------------------------------------------------
# USER CONFIG
# -----------------------------------------------------------------------------

BASE_DIR = Path(r"C:\Users\SamuelAguilarRamirez\nexus2.0")

PATH_DLL = BASE_DIR / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll"

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
    "Persist Security Info=True;"
)

OUTPUT_ROOT = BASE_DIR / "docs" / "semantic_model_measures"

# Optional filter. Keep broad by default, because measures often live in Metrics-* tables.
IMPORTANT_MEASURE_TABLE_PATTERNS = (
    "Metrics|Actuals|BP|RE|WE|Revenue|Rev|Volume|Vol|NSR|Financial|Finance|KPI"
)

# -----------------------------------------------------------------------------
# IMPORT PROJECT CONNECTOR
# -----------------------------------------------------------------------------

sys.path.insert(0, str(BASE_DIR))

try:
    from src.connections.nsr_conn import AdomdConnector
except Exception as exc:
    raise ImportError(
        "Could not import AdomdConnector from src.connections.nsr_conn. "
        f"Check BASE_DIR: {BASE_DIR}"
    ) from exc


# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------

def ensure_output_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = OUTPUT_ROOT / f"measures_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved CSV: {path}")


def save_md(title: str, description: str, df: pd.DataFrame, path: Path, max_rows: int = 1000) -> None:
    preview = df.head(max_rows).copy()
    content = f"# {title}\n\n{description}\n\n"
    content += f"Total rows: {len(df)}\n\n"

    if df.empty:
        content += "No data available.\n"
    else:
        content += preview.to_markdown(index=False)
        if len(df) > max_rows:
            content += f"\n\n> Showing first {max_rows} rows only. See CSV for full output.\n"

    path.write_text(content, encoding="utf-8")
    print(f"Saved Markdown: {path}")


def first_existing_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    for col in candidates:
        if col in df.columns:
            return col
    return None


def require_columns(df: pd.DataFrame, required_cols: Iterable[str], context: str) -> None:
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise KeyError(
            f"Missing required columns for {context}: {missing}\n"
            f"Available columns: {list(df.columns)}"
        )


def clean_text_series(series: pd.Series) -> pd.Series:
    return series.astype(str).replace({"nan": ""}).str.strip()


def is_false_like(series: pd.Series) -> pd.Series:
    return (
        series.astype(str).str.lower().isin(["false", "0", "none", "nan", ""])
        | (series == False)  # noqa: E712
    )


def run_dax(nsr_conn: AdomdConnector, query: str, label: str) -> pd.DataFrame:
    print(f"\nRunning {label}...")
    df = nsr_conn.ejecutar_query(query)

    if df is None or df.empty:
        raise RuntimeError(f"{label} returned no data.")

    print(f"{label} extracted: rows={len(df)}, columns={len(df.columns)}")
    print(f"{label} columns:")
    print(list(df.columns))
    return df


# -----------------------------------------------------------------------------
# EXTRACTION LOGIC
# -----------------------------------------------------------------------------

def extract_tables(nsr_conn: AdomdConnector, run_dir: Path) -> pd.DataFrame:
    tables = run_dax(
        nsr_conn,
        """
EVALUATE
INFO.TABLES()
""",
        "INFO.TABLES()",
    )

    save_csv(tables, run_dir / "tables_raw.csv")
    require_columns(tables, ["[ID]", "[Name]"], "INFO.TABLES()")

    useful_cols = [
        "[ID]",
        "[Name]",
        "[Description]",
        "[IsHidden]",
        "[SystemManaged]",
        "[ModifiedTime]",
        "[StructureModifiedTime]",
        "[RefreshedTime]",
    ]
    useful_cols = [c for c in useful_cols if c in tables.columns]

    tables_clean = tables[useful_cols].copy().sort_values("[Name]", kind="stable")
    save_csv(tables_clean, run_dir / "tables_clean.csv")

    return tables_clean


def extract_measures(nsr_conn: AdomdConnector, tables: pd.DataFrame, run_dir: Path) -> pd.DataFrame:
    measures = run_dax(
        nsr_conn,
        """
EVALUATE
INFO.MEASURES()
""",
        "INFO.MEASURES()",
    )

    save_csv(measures, run_dir / "measures_raw.csv")

    # Common INFO.MEASURES fields in Power BI / Tabular.
    # We do not hardcode all of them as required because schemas vary by engine/version.
    measure_name_col = first_existing_column(measures, ["[Name]", "[ExplicitName]", "[InferredName]"])
    table_id_col = first_existing_column(measures, ["[TableID]", "[TableId]"])
    expression_col = first_existing_column(measures, ["[Expression]"])

    if measure_name_col is None:
        raise KeyError(
            "Could not find a measure name field in INFO.MEASURES(). "
            f"Available columns: {list(measures.columns)}"
        )

    if table_id_col is None:
        raise KeyError(
            "Could not find [TableID] in INFO.MEASURES(). "
            f"Available columns: {list(measures.columns)}"
        )

    measures = measures.copy()
    measures["[MeasureName]"] = clean_text_series(measures[measure_name_col])
    measures["[TableID]"] = measures[table_id_col].astype("Int64")

    # Join table name.
    require_columns(tables, ["[ID]", "[Name]"], "tables")
    table_lookup = tables[["[ID]", "[Name]"]].copy()
    table_lookup["[ID]"] = table_lookup["[ID]"].astype("Int64")
    table_lookup = table_lookup.rename(columns={"[ID]": "[TableID]", "[Name]": "[TableName]"})

    measures = measures.merge(table_lookup, on="[TableID]", how="left")

    # Normalize expression if exposed.
    if expression_col:
        measures["[MeasureExpression]"] = measures[expression_col].fillna("").astype(str)
    else:
        measures["[MeasureExpression]"] = ""

    # Helpful classification flags for prompt context.
    if "[IsHidden]" in measures.columns:
        measures["[IsVisible]"] = is_false_like(measures["[IsHidden]"])
    else:
        measures["[IsVisible]"] = True

    measures["[MetricFamilyGuess]"] = measures.apply(classify_measure_family, axis=1)

    useful_cols = [
        "[TableName]",
        "[TableID]",
        "[MeasureName]",
        "[MetricFamilyGuess]",
        "[Description]",
        "[DisplayFolder]",
        "[FormatString]",
        "[DataType]",
        "[IsHidden]",
        "[IsVisible]",
        "[MeasureExpression]",
        "[ModifiedTime]",
        "[StructureModifiedTime]",
    ]
    useful_cols = [c for c in useful_cols if c in measures.columns]

    measures_clean = measures[useful_cols].copy()
    measures_clean = measures_clean.sort_values(
        by=["[TableName]", "[DisplayFolder]", "[MeasureName]"]
        if "[DisplayFolder]" in measures_clean.columns
        else ["[TableName]", "[MeasureName]"],
        kind="stable",
    )

    visible_measures = measures_clean[measures_clean["[IsVisible]"] == True].copy()  # noqa: E712

    important_visible_measures = visible_measures[
        visible_measures["[TableName]"].astype(str).str.contains(
            IMPORTANT_MEASURE_TABLE_PATTERNS,
            case=False,
            na=False,
            regex=True,
        )
        | visible_measures["[MeasureName]"].astype(str).str.contains(
            IMPORTANT_MEASURE_TABLE_PATTERNS,
            case=False,
            na=False,
            regex=True,
        )
    ].copy()

    save_csv(measures_clean, run_dir / "measures_clean.csv")
    save_csv(visible_measures, run_dir / "visible_measures.csv")
    save_csv(important_visible_measures, run_dir / "important_visible_measures.csv")

    save_md(
        title="NSR LATAM Cube - Measures Clean",
        description="All measures extracted from INFO.MEASURES(), joined to table names where possible.",
        df=measures_clean,
        path=run_dir / "measures_clean.md",
    )

    save_md(
        title="NSR LATAM Cube - Visible Measures",
        description="Visible exposed measures only. This is the safest source for DAX Developer and DAX Validator prompts.",
        df=visible_measures,
        path=run_dir / "visible_measures.md",
    )

    save_md(
        title="NSR LATAM Cube - Important Visible Measures",
        description="Visible measures filtered by likely business/metric tables and KPI names.",
        df=important_visible_measures,
        path=run_dir / "important_visible_measures.md",
    )

    return measures_clean


def classify_measure_family(row: pd.Series) -> str:
    table = str(row.get("[TableName]", "")).lower()
    name = str(row.get("[MeasureName]", "")).lower()
    text = f"{table} {name}"

    if any(token in text for token in ["bp", "business plan", "plan"]):
        return "BP / Plan"
    if any(token in text for token in [" re", "rolling estimate", "estimate"]):
        return "RE / Estimate"
    if any(token in text for token in ["vol", "volume", "unit case", "uc"]):
        return "Volume"
    if any(token in text for token in ["nsr", "net sales", "revenue", "rev"]):
        return "NSR / Revenue"
    if any(token in text for token in ["discount", "deduction"]):
        return "Discount / Deduction"
    if any(token in text for token in ["yoy", "growth", "chg", "change", "%"]):
        return "Growth / Comparison"
    return "Other"


def generate_measures_nexus_context(measures: pd.DataFrame, run_dir: Path) -> None:
    print("\nGenerating Nexus measures context...")

    if "[IsVisible]" in measures.columns:
        context_measures = measures[measures["[IsVisible]"] == True].copy()  # noqa: E712
    else:
        context_measures = measures.copy()

    lines = []
    lines.append("# Nexus Measures Context - NSR LATAM Cube")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file contains exposed semantic model measures extracted from `INFO.MEASURES()`. "
        "Use this as controlled context for Nexus 2.0 DAX Developer and DAX Validator agents."
    )
    lines.append("")
    lines.append("## Critical Guardrails")
    lines.append("")
    lines.append("- Use exact measure names from this file.")
    lines.append("- Do not invent measures.")
    lines.append("- Prefer existing semantic model measures over raw columns.")
    lines.append("- If a requested KPI does not map to one of these exposed measures, return a validation failure or ask for clarification upstream.")
    lines.append("- Validate scenario-specific measure families: Actuals, BP, RE, Volume, Revenue/NSR.")
    lines.append("- Do not aggregate precomputed percentage measures unless the measure is explicitly designed for that use in the model.")
    lines.append("")
    lines.append("## Exposed Measures by Table")
    lines.append("")

    required = {"[TableName]", "[MeasureName]"}
    if not required.issubset(set(context_measures.columns)):
        lines.append("Measure metadata unavailable.")
    else:
        for table_name, group in context_measures.groupby("[TableName]", dropna=False):
            lines.append(f"### {table_name}")
            lines.append("")
            for _, row in group.iterrows():
                measure = row.get("[MeasureName]", "")
                family = row.get("[MetricFamilyGuess]", "")
                folder = row.get("[DisplayFolder]", "")
                fmt = row.get("[FormatString]", "")
                desc = row.get("[Description]", "")
                lines.append(
                    f"- `[{measure}]` | Family: `{family}` | Folder: `{folder}` | Format: `{fmt}` | Description: {desc}"
                )
            lines.append("")

    path = run_dir / "measures_nexus_context.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Markdown: {path}")

    latest_path = OUTPUT_ROOT / "measures_nexus_context_latest.md"
    latest_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved latest Markdown: {latest_path}")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main() -> None:
    print("cwd:", os.getcwd())
    print("BASE_DIR:", BASE_DIR)
    print("dll exists:", PATH_DLL.exists(), "|", PATH_DLL)

    if not PATH_DLL.exists():
        raise FileNotFoundError(f"ADOMD DLL not found: {PATH_DLL}")

    run_dir = ensure_output_dir()
    print("Output run directory:", run_dir)

    print("\nCreating ADOMD connector...")
    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)

    tables = extract_tables(nsr_conn, run_dir)
    measures = extract_measures(nsr_conn, tables, run_dir)
    generate_measures_nexus_context(measures, run_dir)

    print("\nDone.")
    print("Run folder:", run_dir)
    print("Latest Nexus measures context:", OUTPUT_ROOT / "measures_nexus_context_latest.md")


if __name__ == "__main__":
    main()
