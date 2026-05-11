
# Target Model

Target model: NSR LATAM Cube / NSR LATAM Semantic Model (Power BI).

# Tables and Columns Available

## Channel
- 'Channel'[Trade Channel]
- 'Channel'[Sub Trade Channel]
- 'Channel'[Sub Trade Channel Code]
- 'Channel'[BU Channel Code]
- 'Channel'[Consumer Activity Cluster]
- 'Channel'[LT1.0 - Sub Trade Channel]
- 'Channel'[LT1.1 - Trade Channel]
- 'Channel'[LT1.2 - Channel Group]
- 'Channel'[LT1.3 - Channel Macro Group]

## Product
- 'Product'[Beverage Category]
- 'Product'[Beverage Sub Category]
- 'Product'[Beverage Type]
- 'Product'[Beverage State]
- 'Product'[BPP]
- 'Product'[BPP Code]
- 'Product'[BU Product]
- 'Product'[BU Product Code]
- 'Product'[LT1.1 - Beverage Product]
- 'Product'[LT1.2 - Brand Group]
- 'Product'[LT1.3 - Trademark Category]
- 'Product'[LT1.4 - Sub-Category]
- 'Product'[LT1.5 - Category]
- 'Product'[LT1.6 - Category Group]
- 'Product'[LT1.7 - Segment]
- 'Product'[LT1.8 - Industry]
- 'Product'[Non-KO Product]

## Package
- 'Package'[Package]
- 'Package'[Container Type]
- 'Package'[Primary Container]
- 'Package'[Secondary Package]
- 'Package'[BPP]
- 'Package'[LT1.1 - Package]
- 'Package'[LT1.2 - Package Type]
- 'Package'[LT1.3 - Container]
- 'Package'[LT1.4 - Refillability]
- 'Package'[LT1.5 - MS-SS]
- 'Package'[LT1.6 - RTD-NRTD]

## Ship From (Bottler / Geography)
- 'Ship From'[Country]
- 'Ship From'[Country Code]
- 'Ship From'[Business Unit]
- 'Ship From'[Region]
- 'Ship From'[Operating Group]
- 'Ship From'[BU Ship From]
- 'Ship From'[L1.0 - Bottler Franchise or CEDI]
- 'Ship From'[L1.1 - Bottler SubZone]
- 'Ship From'[L1.2 - Bottler Zone]
- 'Ship From'[L1.3 - Bottler]
- 'Ship From'[L1.4 - Field Unit]
- 'Ship From'[L1.5 - Country]
- 'Ship From'[L1.6 - Franchise Sub Region]
- 'Ship From'[L1.7 - Franchise Region]
- 'Ship From'[L1.8 - Franchise Unit Operations]
- 'Ship From'[L1.9 - Zone Operations]
- 'Ship From'[L1.10 - Operating Unit]

## Ship To (Customer)
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]
- 'Ship To'[LT1.3 - Business Sub Type]
- 'Ship To'[LT1.4 - Business Type]
- 'Ship To'[LT1.5 - Consumption Type]
- 'Ship To'[LT1.6 - Customer Leadership]

## Period
- 'Period'[Day 445]
- 'Period'[Day 445 Code]
- 'Period'[Day Cal]
- 'Period'[Day Cal Code]
- 'Period'[Week 445]
- 'Period'[Week 445 Code]
- 'Period'[Week 445 #]
- 'Period'[Week 445 Begin – End]
- 'Period'[Month 445]
- 'Period'[Month 445 Code]
- 'Period'[Month 445 #]
- 'Period'[Month 445 Name]
- 'Period'[Month 445 Begin – End]
- 'Period'[Month Cal]
- 'Period'[Month Cal Code]
- 'Period'[Quarter 445]
- 'Period'[Quarter 445 Code]
- 'Period'[Quarter 445 Name]
- 'Period'[Quarter Cal]
- 'Period'[Quarter Cal Code]
- 'Period'[Half 445]
- 'Period'[Half 445 Code]
- 'Period'[Half 445 Name]
- 'Period'[Half Cal]
- 'Period'[Half Cal Code]
- 'Period'[Year 445]
- 'Period'[Year 445 Code]
- 'Period'[Year Cal]
- 'Period'[Year Cal Code]

## Sales Type
- 'Sales Type'[BU Sales Type]
- 'Sales Type'[BU Sales Type Code]
- 'Sales Type'[Primary Sales Indicator]
- 'Sales Type'[Source Sales Type]

## Reporting View
- 'Reporting View'[Reporting View]

## Record Type
- 'Record Type'[Record Type]

## Discount Dimensions
- 'On Standard Discount'[On Standard Discount Category]
- 'On Standard Discount'[On Standard Discount Code]
- 'On Standard Discount'[On Standard Discount Concept]
- 'On Standard Discount Classification'[Discount Group]
- 'On Standard Discount Classification'[Sales Group]
- 'On Standard Discount Classification'[Discount Applied Flag]
- 'On Bulk Discount'[On Bulk Discount Category]
- 'On Bulk Discount'[On Bulk Discount Code]
- 'Off Discount'[Off Discount Category]
- 'Off Discount'[Off Discount Code]
- 'Other Discount'[Other Discount Category]
- 'Other Discount'[Other Discount Code]

# Raw Metric Columns (use only if no measure exists for the metric)

## Volume (from Metrics-Actuals-Vol)
- 'Metrics-Actuals-Vol'[unit_case_amt]
- 'Metrics-Actuals-Vol'[liter_amt]
- 'Metrics-Actuals-Vol'[phys_case_amt]
- 'Metrics-Actuals-Vol'[indv_unit_amt]
- 'Metrics-Actuals-Vol'[btlr_unit_case_amt]
- 'Metrics-Actuals-Vol'[purch_trx_amt]

## Revenue (from Metrics-Actuals-Rev)
- 'Metrics-Actuals-Rev'[btlr_gross_rev_amt]
- 'Metrics-Actuals-Rev'[btlr_net_sls_rev_amt]
- 'Metrics-Actuals-Rev'[btlr_wholesale_price]

## Plan / Estimate Revenue & Volume (Metrics-BP, Metrics-RE, Metrics-WE)
- 'Metrics-BP'[btlr_gross_rev_amt]
- 'Metrics-BP'[btlr_net_sls_rev_amt]
- 'Metrics-BP'[unit_case_amt]
- 'Metrics-RE'[btlr_gross_rev_amt]
- 'Metrics-RE'[btlr_net_sls_rev_amt]
- 'Metrics-RE'[unit_case_amt]
- 'Metrics-WE'[btlr_gross_rev_amt]
- 'Metrics-WE'[unit_case_amt]

## Discounts (raw)
- 'Metrics-Std-Discount'[dscnt_amt]
- 'Metrics-Bulk-Discount'[dscnt_amt]
- 'Metrics-Inv-Discount'[dscnt_amt]
- 'Metrics-Other-Discount'[dscnt_amt]

## Measures Available
- [Bottler Gross Revenue AC (LC)]
- [Bottler Gross Revenue AC (LC) YTD]
- [Bottler Gross Revenue Current RE (LC)]
- [Bottler Gross Revenue Current RE (LC) YTD]
- [Bottler Gross Revenue Current RE (LC) YTG]
- [Unit Cases AC]
- [Unit Cases AC YTD]
- [Unit Cases Current RE]
- [Unit Cases Current RE YTD]
- [Unit Cases Current RE YTG]
- [Bottler Gross Price per UC AC (LC)]
- [Bottler Gross Price per UC AC (LC) YTD]
- [Bottler Net Revenue AC (LC)_Y]
- [Bottler Net Revenue AC (LC)_N]
- [Bottler Net Revenue AC (LC)]
- [Bottler Net Revenue AC (LC) YTD]
- [Bottler Net Revenue Current RE (LC)]
- [Bottler Net Revenue Current RE (LC) YTD]
- [Bottler Net Revenue Current RE (LC) YTG]



# Business Rules

- NSR means Net Sales Revenue. It is SELL-IN / bottler revenue, not sell-out / retail sales.
- Volume default unit is unit cases (unit_case_amt) unless the user specifies liters or physical cases.
- Default scenario is Actuals (Metrics-Actuals-Vol / Metrics-Actuals-Rev) unless the user explicitly asks for BP (Business Plan), RE (Rolling Estimate), or WE (Weekly Estimate).
- The model uses two calendar systems: 445 calendar and Gregorian calendar. Default to 445 unless the user specifies Gregorian.
- For country/geography filtering, use 'Ship From'[Country] or 'Ship From'[L1.5 - Country]. Do NOT use 'Ship To'[Country] — it does not exist in this model.
- For channel breakdown, prefer 'Channel'[Trade Channel] unless the user specifies a more granular level.
- For product breakdown, prefer 'Product'[Beverage Category] or 'Product'[BPP] unless the user specifies a hierarchy level.
- Use only tables and columns listed in this context.
- Do not invent tables, columns, or measures.
- If a metric already has a measure defined in the model, use that measure instead of summing the raw column.
- Return executable DAX only.

# Local Test Defaults

- If the user asks for "by channel" without further detail, use 'Channel'[Trade Channel].
- If the user asks for "YTD" without specifying a year, interpret it as the latest available YTD in the 445 calendar.
- If a requested filter dimension (e.g., a specific geography level) is not listed in this context, do NOT invent a column. Instead, generate the DAX without that filter and flag the missing object, OR ask the user for the correct column name.
- Prioritize executable DAX over perfect business filtering when columns are ambiguous.
