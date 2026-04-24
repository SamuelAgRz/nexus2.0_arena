# NSR LATAM Cube UAT - Semantic Context Example

## Model
- Name: NSR LATAM Cube UAT
- Source: Power BI semantic model

## Business Rules
- NSR means sell-in revenue only.
- Prefer YTD when the user does not specify another time aggregation.
- Avoid mixing measures with incompatible business logic unless explicitly asked.
- Never invent measures or columns.

## Example Dimensions
- 'Date'[Year]
- 'Date'[Month]
- 'Date'[MonthNumber]
- 'Geography'[Country]
- 'Geography'[Zone]
- 'Channel'[Channel]
- 'Product'[Category]
- 'Product'[Brand]

## Example Measures
- [NSR]
- [NSR YTD]
- [Volume]
- [Volume YTD]

## Query Guidance
- When the user asks for a breakdown, prefer SUMMARIZECOLUMNS.
- When the user asks for ranking, use TOPN only if explicitly needed.
- Keep the query readable.
