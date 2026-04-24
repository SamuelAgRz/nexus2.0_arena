# Nexus 2.0 Notebook Replica for Foundry + Power BI

Repositorio base para replicar una arquitectura tipo Nexus 2.0 dentro de un notebook de Python.

## Qué incluye
- Cliente LLM para endpoint OpenAI-compatible de Foundry/Azure OpenAI
- Cliente Power BI para ejecutar DAX vía REST API
- Orquestador multiagente
- Agentes separados por responsabilidad:
  - Intent Clarifier
  - DAX Query Developer
  - DAX Validator
  - DAX Executor
  - DAX Result Summarizer
  - Visualization Agent
  - Final Summarizer
- Logging estructurado
- Configuración por variables de entorno
- Notebook listo para pruebas
- Ejemplo de contexto semántico para `NSR LATAM Cube UAT`

## Estructura
```text
nexus_notebook_repo_v2/
├─ notebooks/
│  └─ 01_nexus_replica.ipynb
├─ src/
│  ├─ agents/
│  ├─ config/
│  ├─ prompts/
│  ├─ utils/
│  ├─ llm_client.py
│  ├─ powerbi_client.py
│  └─ orchestrator.py
├─ examples/
│  └─ semantic_context_nsr_latam_cube_uat.md
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Instalación
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Configuración
Copia `.env.example` a `.env` y llena los valores:

- `FOUNDRY_BASE_URL`
- `FOUNDRY_API_KEY`
- `FOUNDRY_MODEL`
- `PBI_TENANT_ID`
- `PBI_CLIENT_ID`
- `PBI_CLIENT_SECRET`
- `PBI_GROUP_ID`
- `PBI_DATASET_ID`

## Ejecución rápida
1. Abre `notebooks/01_nexus_replica.ipynb`
2. Ajusta `semantic_context_path`
3. Corre las celdas
4. Prueba con una pregunta como:
   - `What is NSR YTD by channel for Colombia?`

## Notas
- El semantic context es crítico. Si no aterrizas tablas, medidas, dimensiones y reglas, el agente puede inventar columnas o medidas.
- Este repo usa un patrón simple y depurable para notebook. Luego se puede mover a contenedores, APIM y evaluación automática.
