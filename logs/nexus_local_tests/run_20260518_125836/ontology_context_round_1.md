RELEVANT ONTOLOGY CONTEXT

Measures:
- [Unit Cases AC] : Volumen de ventas actual en Unidades de Caja (UC). Total de unit cases vendidos en el período activo según contexto de filtro.

Business Rules:
- Suma directa de unit_case_amt en la tabla de hechos Metrics-Actuals-Vol. Medida base de volumen sin inteligencia de tiempo.
- Aditiva solo sobre dimensiones conectadas a Metrics-Actuals-Vol. No combinar con slicers exclusivos de otras tablas de hechos (CurrencyRate, Off Discount) sin medida puente.
- Rol KO (SEC-IDM-NSR-RPT-LATAM-VR-PS-LMQY-TCRON): filtra Product[Non-KO Product] distinto de Y – solo productos Coca-Cola. Rol NONKO (SEC-IDM-NSR-RPT-LATAM-VR-PS-LMQY-TCRON-NONKO): sin filtro de producto, acceso completo.