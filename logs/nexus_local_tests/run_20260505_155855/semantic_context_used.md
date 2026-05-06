
# Target model

Target model: NSR LATAM Cube UAT / NSR LATAM semantic model.

# Tables and columns available

## Channel
- 'Channel'[Trade Channel]
- 'Channel'[Sub Trade Channel]

## Ship To
- 'Ship To'[Source Ship To Code]
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]

## Period
- 'Period'[Date]
- 'Period'[Year]
- 'Period'[Month]
- 'Period'[Week]

# Measures available

- [NSR]
- [NSR YTD]

# Local test defaults

For this local test only:
- If the user asks for "by channel", interpret channel as 'Channel'[Trade Channel].
- If the user asks for "YTD" without year, interpret it as latest available YTD.
- If the user asks for Colombia but no valid country/geography column is available in this context, do NOT invent 'Ship To'[Country].
- If Colombia cannot be filtered with the listed objects, generate the DAX without the Colombia filter and make the validator flag the missing geography object, OR ask for a valid geography column.
- For first local smoke test, prioritize executable DAX over perfect business filtering.

# Business Rules

- NSR means Net Sales Revenue.
- NSR is SELL-IN / bottler revenue, not sell-out / retail sales.
- Default scenario is Actuals unless the user explicitly asks for BP or RE.
- Use only tables, columns, and measures listed here.
- Do not invent tables.
- Do not invent columns.
- Do not invent measures.
- For channel breakdown, use 'Channel'[Trade Channel].
- Do not use 'Channel'[Channel].
- Do not use 'Ship To'[Country] unless it appears explicitly in this context.
- Prefer exposed model measures over raw metric columns.
- If a metric exists as a measure, use the measure.
- Return executable DAX only.
