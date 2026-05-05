Target model: NSR LATAM semantic model

Tables and columns available:

Channel:
- 'Channel'[RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61]
- 'Channel'[chnl_id]
- 'Channel'[src_sys_id]
- 'Channel'[Sub Trade Channel]
- 'Channel'[Trade Channel]
- 'Channel'[Consumer Activity Cluster]
- 'Channel'[BU Channel Code]
- 'Channel'[Sub Trade Channel Code]
- 'Channel'[Source Channel Code]
- 'Channel'[src_sub_chnl_cd]
- 'Channel'[LT1.0 - Sub Trade Channel]
- 'Channel'[LT1.1 - Trade Channel]
- 'Channel'[LT1.2 - Channel Group]
- 'Channel'[LT1.3 - Channel Macro Group]

Ship To:
- 'Ship To'[RowNumber-2662979B-1795-4F74-8F37-6A1BA8059B61]
- 'Ship To'[ship_to_loc_id]
- 'Ship To'[Source Ship To Code]
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]
- 'Ship To'[LT1.3 - Business Sub Type]
- 'Ship To'[LT1.4 - Business Type]
- 'Ship To'[LT1.5 - Consumption Type]
- 'Ship To'[LT1.6 - Customer Leadership]


Measures:
- [NSR]
- [NSR YTD]

Business Rules:
- NSR is Net Sales Revenue (SELL-IN).
- Use only tables and columns listed above.
- Do not invent columns or measures.
- For channel breakdown, prefer 'Channel'[Trade Channel] unless the user asks for a more granular channel level.
- Do not use 'Channel'[Channel] because that column does not exist.
- Do not use 'Ship To'[Country] unless it appears explicitly in the metadata.
