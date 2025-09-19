Data Exploration with Python and Generative AI
===============================================

This project is aimed at data exploration and analysis using Python and generative AI techniques. There are multiple
subprojects within this repository, each focusing on different ways of analyzing data.

## 📦 Projects

✅ Promotion Analysis
------------------
The promotion has a few different projects for analyzing promotion data:
- 🗂 Analysis using AutoGen library
  - 📝 Version 1: Use 3 different agents to analyze data.
      - **Planning Agent:** Analyzes user requests and coordinates tasks between Database and Writer agents.
      - **Database Agent:** Creates SQL queries, executes them using tools, and returns structured data.
      - **Writer Agent:** Transforms data into clear business insights and actionable recommendations.
      - The communication between the agents takes place through **Selector Group Chat**.
      - The main script is `src/promotion/autogen/v1/analyzer.py`.
  - 📝 Version 2: It's similar to version 1, except it introduces a new SQL Judge Agent.
      - **SQL Judge Agent:** Reviews, validates, and corrects SQL queries from Database Agent before execution.
      - The main script is `src/promotion/autogen/v2/analyzer.py`.

- 🗂️ Analysis using LangChain/LangGraph library
  - 📝 Version 1: It analyzes data using LangGraph.
      - The main script is `src/promotion/langgraph/analyzer.py`.


## Technologies

- Python
- Snowflake SQL
- UV (Python package and project manager)

## Installation
- Clone the repository.
- Create a new `.env` file in the root directory and add your OpenAI APIs key as shown below:

```aiignore
AZURE_OPENAI_API_INSTANCE_NAME=<AZURE ENDPOINT>
AZURE_OPENAI_API_DEPLOYMENT_NAME=<MODEL DEPLOYMENT NAME>
AZURE_OPENAI_API_VERSION=<OPENAI API VERSION>

AZURE_OPENAI_API_MODEL_GPT_4_1=gpt-4.1
AZURE_OPENAI_API_MODEL_O4_MINI=o4-mini

AZURE_AUTHORITY_HOST=<AUTHORITY HOST>
AZURE_FEDERATED_TOKEN_FILE=<PATH TO FEDERATED TOKEN FILE>
AZURE_TENANT_ID=<TENANT ID>
AZURE_CLIENT_ID=<CLIENT ID>
AZURE_CLIENT_SECRET=<CLIENT SECRET>

SNOWFLAKE_ACCOUNT=<DATABASE ACCOUNT>
SNOWFLAKE_DATABASE=<DATABASE NAME>
SNOWFLAKE_SCHEMA=<DATABASE SCHEMA>
SNOWFLAKE_WAREHOUSE=<DATABASE WAREHOUSE>
SNOWFLAKE_USER=<DATABASE USER>
SNOWFLAKE_PASSWORD=<DATABASE PASSWORD>
SNOWFLAKE_ROLE=<DATABASE ROLE>
```
- This project uses `uv`, a Python package and project manager, to manage dependencies and run scripts.
  Make sure you have `uv` installed.

## Usage
To run a Python script, use the following command:
```bash
uv run src/promotion/autogen/v1/analyzer.py
```
