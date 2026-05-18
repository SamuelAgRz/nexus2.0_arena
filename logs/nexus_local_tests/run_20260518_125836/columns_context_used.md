
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

# Business Rules

- For country/geography filtering, use 'Ship From'[Country] or 'Ship From'[L1.5 - Country]. Do NOT use 'Ship To'[Country] — it does not exist in this model.
- For channel breakdown, prefer 'Channel'[Trade Channel] unless the user specifies a more granular level.
- For product breakdown, prefer 'Product'[Beverage Category] or 'Product'[BPP] unless the user specifies a hierarchy level.
- The model uses two calendar systems: 445 calendar and Gregorian calendar. Default to 445 unless the user specifies Gregorian.
- Use only tables and columns listed in this context.
- Do not invent tables or columns.
