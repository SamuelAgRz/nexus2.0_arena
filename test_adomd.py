"""
Minimal Nexus-ready extractor for NSR LATAM Cube semantic model.

Goal:
- Extract important tables from INFO.TABLES()
- Extract columns only for those important tables from INFO.COLUMNS()
- Handle Power BI XMLA INFO() schemas where column names are bracketed, e.g. [Name], [ExplicitName]
- Save raw and curated outputs as CSV and Markdown

Run from repo root:
    python extract_nsr_important_tables_columns.py

Requirements:
    pip install pandas tabulate
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

OUTPUT_ROOT = BASE_DIR / "docs" / "semantic_model_minimal"

IMPORTANT_TABLE_PATTERNS = (
    "Metrics|Actuals|BP|RE|WE|"
    "Channel|Package|Product|Period|"
    "Sales Type|Ship From|Ship To|"
    "CurrencyRate|Discount|Concept"
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
    run_dir = OUTPUT_ROOT / f"important_tables_columns_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"Saved CSV: {path}")


def save_md(title: str, description: str, df: pd.DataFrame, path: Path, max_rows: int = 500) -> None:
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
    return series.astype(str).str.strip()


# -----------------------------------------------------------------------------
# EXTRACTION LOGIC
# -----------------------------------------------------------------------------

def extract_tables(nsr_conn: AdomdConnector, run_dir: Path) -> pd.DataFrame:
    print("\nRunning INFO.TABLES()...")
    tables = nsr_conn.ejecutar_query("""
EVALUATE
INFO.TABLES()
""")

    if tables is None or tables.empty:
        raise RuntimeError("INFO.TABLES() returned no data.")

    print(f"Tables extracted: rows={len(tables)}, columns={len(tables.columns)}")
    print("INFO.TABLES columns:")
    print(list(tables.columns))

    save_csv(tables, run_dir / "tables_raw.csv")

    require_columns(tables, ["[ID]", "[Name]"], "INFO.TABLES()")

    important_tables = tables[
        tables["[Name]"].astype(str).str.contains(
            IMPORTANT_TABLE_PATTERNS,
            case=False,
            na=False,
            regex=True,
        )
    ].copy()

    preferred_cols = [
        "[ID]",
        "[Name]",
        "[Description]",
        "[IsHidden]",
        "[ModifiedTime]",
        "[StructureModifiedTime]",
        "[SystemManaged]",
    ]
    selected_cols = [c for c in preferred_cols if c in important_tables.columns]
    important_tables = important_tables[selected_cols].copy()
    important_tables = important_tables.sort_values("[Name]")

    save_csv(important_tables, run_dir / "important_tables.csv")
    save_md(
        title="NSR LATAM Cube - Important Tables",
        description="Important tables extracted from INFO.TABLES(). This is the first minimal metadata layer for Nexus.",
        df=important_tables,
        path=run_dir / "important_tables.md",
    )

    return important_tables


def extract_columns(nsr_conn: AdomdConnector, important_tables: pd.DataFrame, run_dir: Path) -> pd.DataFrame:
    print("\nRunning INFO.COLUMNS()...")
    columns = nsr_conn.ejecutar_query("""
EVALUATE
INFO.COLUMNS()
""")

    if columns is None or columns.empty:
        raise RuntimeError("INFO.COLUMNS() returned no data.")

    print(f"Columns extracted: rows={len(columns)}, columns={len(columns.columns)}")
    print("INFO.COLUMNS columns:")
    print(list(columns.columns))

    save_csv(columns, run_dir / "columns_raw.csv")

    require_columns(columns, ["[TableID]"], "INFO.COLUMNS()")
    require_columns(important_tables, ["[ID]", "[Name]"], "important_tables")

    important_table_ids = important_tables["[ID]"].astype(int).tolist()

    important_columns = columns[
        columns["[TableID]"].astype(int).isin(important_table_ids)
    ].copy()

    table_lookup = important_tables[["[ID]", "[Name]"]].rename(
        columns={"[ID]": "[TableID]", "[Name]": "[TableName]"}
    )
    table_lookup["[TableID]"] = table_lookup["[TableID]"].astype(int)
    important_columns["[TableID]"] = important_columns["[TableID]"].astype(int)

    important_columns = important_columns.merge(
        table_lookup,
        on="[TableID]",
        how="left",
    )

    # Your model uses [ExplicitName] / [InferredName], not [Name], for INFO.COLUMNS().
    explicit_name_col = first_existing_column(important_columns, ["[ExplicitName]", "[Name]"])
    inferred_name_col = first_existing_column(important_columns, ["[InferredName]"])

    if explicit_name_col and inferred_name_col:
        important_columns["[ColumnName]"] = important_columns[explicit_name_col].fillna(
            important_columns[inferred_name_col]
        )
    elif explicit_name_col:
        important_columns["[ColumnName]"] = important_columns[explicit_name_col]
    elif inferred_name_col:
        important_columns["[ColumnName]"] = important_columns[inferred_name_col]
    else:
        raise KeyError(
            "Could not find a column name field in INFO.COLUMNS(). "
            f"Available columns: {list(important_columns.columns)}"
        )

    explicit_dtype_col = first_existing_column(important_columns, ["[ExplicitDataType]", "[DataType]"])
    inferred_dtype_col = first_existing_column(important_columns, ["[InferredDataType]"])

    if explicit_dtype_col and inferred_dtype_col:
        important_columns["[DataType]"] = important_columns[explicit_dtype_col].fillna(
            important_columns[inferred_dtype_col]
        )
    elif explicit_dtype_col:
        important_columns["[DataType]"] = important_columns[explicit_dtype_col]
    elif inferred_dtype_col:
        important_columns["[DataType]"] = important_columns[inferred_dtype_col]
    else:
        important_columns["[DataType]"] = None

    important_columns["[ColumnName]"] = clean_text_series(important_columns["[ColumnName]"])

    # Remove internal row-number columns unless you want to keep them.
    important_columns["[IsInternalRowNumber]"] = important_columns["[ColumnName]"].str.contains(
        "RowNumber-",
        case=False,
        na=False,
    )

    useful_cols = [
        "[TableName]",
        "[TableID]",
        "[ColumnName]",
        "[Description]",
        "[DataType]",
        "[IsHidden]",
        "[IsKey]",
        "[IsUnique]",
        "[IsNullable]",
        "[SummarizeBy]",
        "[SourceColumn]",
        "[DisplayFolder]",
        "[IsInternalRowNumber]",
        "[ModifiedTime]",
        "[RefreshedTime]",
    ]

    useful_cols = [c for c in useful_cols if c in important_columns.columns]
    important_columns_clean = important_columns[useful_cols].copy()

    important_columns_clean = important_columns_clean.sort_values(
        by=["[TableName]", "[ColumnName]"],
        kind="stable",
    )

    # Visible business columns only: useful for Nexus prompt context.
    visible_business_columns = important_columns_clean.copy()
    if "[IsHidden]" in visible_business_columns.columns:
        visible_business_columns = visible_business_columns[
            visible_business_columns["[IsHidden]"].astype(str).str.lower().isin(["false", "0", "nan"])
            | (visible_business_columns["[IsHidden]"] == False)  # noqa: E712
        ].copy()

    if "[IsInternalRowNumber]" in visible_business_columns.columns:
        visible_business_columns = visible_business_columns[
            visible_business_columns["[IsInternalRowNumber]"] == False  # noqa: E712
        ].copy()

    save_csv(important_columns_clean, run_dir / "important_columns.csv")
    save_csv(visible_business_columns, run_dir / "visible_business_columns.csv")

    save_md(
        title="NSR LATAM Cube - Important Columns",
        description="Columns extracted only from important semantic model tables.",
        df=important_columns_clean,
        path=run_dir / "important_columns.md",
    )

    save_md(
        title="NSR LATAM Cube - Visible Business Columns",
        description="Visible, non-internal columns from important tables. This is the safest initial context for Nexus Intent Clarifier.",
        df=visible_business_columns,
        path=run_dir / "visible_business_columns.md",
    )

    return important_columns_clean


def generate_minimal_nexus_context(
    important_tables: pd.DataFrame,
    important_columns: pd.DataFrame,
    run_dir: Path,
) -> None:
    print("\nGenerating minimal Nexus context...")

    lines = []
    lines.append("# Minimal Nexus Context - NSR LATAM Cube")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "This file contains the first minimal semantic context for Nexus agents. "
        "It only includes important tables and their columns extracted from the Power BI semantic model."
    )
    lines.append("")
    lines.append("## Important Tables")
    lines.append("")

    for _, row in important_tables.iterrows():
        table_name = row.get("[Name]", "")
        desc = row.get("[Description]", "")
        hidden = row.get("[IsHidden]", "")
        lines.append(f"- `{table_name}` | Hidden: `{hidden}` | Description: {desc}")

    lines.append("")
    lines.append("## Table Columns")
    lines.append("")

    if "[TableName]" not in important_columns.columns or "[ColumnName]" not in important_columns.columns:
        lines.append("Column metadata unavailable.")
    else:
        for table_name, group in important_columns.groupby("[TableName]", dropna=False):
            lines.append(f"### {table_name}")
            lines.append("")
            for _, row in group.iterrows():
                col = row.get("[ColumnName]", "")
                dtype = row.get("[DataType]", "")
                hidden = row.get("[IsHidden]", "")
                desc = row.get("[Description]", "")
                internal = row.get("[IsInternalRowNumber]", "")
                if str(internal).lower() == "true":
                    continue
                lines.append(f"- `{col}` | Type: `{dtype}` | Hidden: `{hidden}` | Description: {desc}")
            lines.append("")

    lines.append("## Initial Nexus Guidance")
    lines.append("")
    lines.append("- Use exact table and column names from this file.")
    lines.append("- Do not invent dimensions or measures.")
    lines.append("- Treat `Metrics-*` tables as measure/metric-related tables.")
    lines.append("- Treat `Channel`, `Product`, `Package`, `Period`, `Ship From`, and `Ship To` as core dimensions unless later metadata proves otherwise.")
    lines.append("- This is not yet the final semantic dictionary; it is the first stable extraction layer.")
    lines.append("")

    path = run_dir / "minimal_nexus_context.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved Markdown: {path}")

    # Also save a latest copy for easy reference.
    latest_path = OUTPUT_ROOT / "minimal_nexus_context_latest.md"
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

    important_tables = extract_tables(nsr_conn, run_dir)
    important_columns = extract_columns(nsr_conn, important_tables, run_dir)
    generate_minimal_nexus_context(important_tables, important_columns, run_dir)

    print("\nDone.")
    print("Run folder:", run_dir)
    print("Latest Nexus context:", OUTPUT_ROOT / "minimal_nexus_context_latest.md")


if __name__ == "__main__":
    main()
