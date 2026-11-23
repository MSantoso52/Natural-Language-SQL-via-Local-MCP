# Natural-Language-SQL-via-Local-MCP
SQL querying using natural language through local MCP and  ollama

https://github.com/user-attachments/assets/f8470f42-efa5-4c94-9976-c048f515c3e7

## Project Overview
A local, privacy-first data exploration workspace that lets you query a **PostgreSQL** database using natural language via the **Model Context Protocol (MCP)**, powered by local **Ollama** models and a **Streamlit** interface. It exposes live database schema inspection and read-only SQL execution as MCP tools so an LLM can translate questions into SQL, run queries locally without sending data to external APIs, and surface results interactively.

## The Problems To Be Solved
* Data Privacy & Security Risks: Sending proprietary database schemas and query data to cloud-based LLM APIs exposes sensitive business information to external servers.

* High API & Infrastructure Costs: Relying on commercial LLM APIs for frequent ad-hoc SQL generation incurs recurring token costs and requires internet connectivity.

* Manual Schema Lookup Friction: Analysts and engineers waste time manually inspecting tables, column names, and relationships before writing basic exploratory queries.

* Non-Technical Access Bottlenecks: Business users without SQL expertise depend heavily on data engineers for routine ad-hoc data pulls.

* Hallucinated SQL Queries: Standalone LLMs often generate invalid queries with wrong column or table names when they lack live, structured access to actual database metadata.

## Prerequisites And Requirement
* Python 3.10+ — Runtime for the MCP server, client, and Streamlit app.
  ```bash
  sudo pacman -S python

  python3 --version
  Python 3.14.10
  ```

* PostgreSQL 14+ — Running local or containerized database instance with target data.
  ```bash
  docker run -d \
  --name pgduckdb \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=duckdb \
  pgduckdb/pgduckdb:16-main

  psql -h localhost -U postgres -d postgres

  docker ps
  CONTAINER ID   IMAGE                       COMMAND                  CREATED        STATUS        PORTS      NAMES
  c1b2fc5d017e   pgduckdb/pgduckdb:16-main   "docker-entrypoint.s…"   2 months ago   Up 15 hours   5432/tcp   hardcore_boyd
  ```

* Ollama — Installed and running locally with a pulled chat/SQL-capable model (e.g., gemma2:2b or qwen2.5-coder).
  ```bash
  sudo pacman -S ollama

  ollama --version
  ollama version is 0.33.3

  ollama pull gemma2:2b

  ollama ls | grep gemma2
  gemma2:2b                  8ccf136fdd52    1.6 GB    2 months ago
  ```

* Python Libraries — mcp, streamlit, psycopg2-binary (or psycopg), ollama, and pandas.
  ```bash
  python3 -m pip install psycopg2-binary mpc streamlit --break-system-packages

  streamlit version
  Streamlit, version 1.66.0
  ```

* System Resources — At least 8 GB RAM (16 GB recommended) to run the local LLM alongside PostgreSQL.
  ```bash
  lscpu
  Architecture:                x86_64
    CPU op-mode(s):            32-bit, 64-bit
    Address sizes:             39 bits physical, 48 bits virtual
    Byte Order:                Little Endian
  CPU(s):                      4
    On-line CPU(s) list:       0-3
  Vendor ID:                   GenuineIntel
    Model name:                Intel(R) Core(TM) i5-6300U CPU @ 2.40GHz
  ...

  cat /proc/meminfo
  MemTotal:       16088100 kB
  MemFree:         8056312 kB
  MemAvailable:   11801652 kB
  ```

## Project Flow
* Expose the postgreql database to be accessibled
  ```bash
  docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' hardcore_boyd
  172.17.0.2

  ...
  # Database confiiguration
  DB_HOST = os.getenv("DB_HIST", "172.17.0.2")
  ... 
  ```
* Build the MCP server
  ```bash
  nvim mcp_server.py
  ```
* Build Web App with Streamlit for MCP chat to PostgreSQL
  ```bash
  nvim app.py
  ```

## Pros And Cons
### Pros

* 100% Data Privacy: Database schemas and query results never leave your local machine.

* Zero API Costs: Runs completely free on local hardware via Ollama without token fees.

* Standardized Tooling: Uses MCP to cleanly decouple the LLM from PostgreSQL schema inspection and query execution.

* Fast Prototyping: Streamlit provides an immediate, interactive UI for testing prompts and viewing tables.

## Cons

* Hardware Dependent: Query generation speed and model reasoning are limited by local CPU/RAM/GPU resources.

* SQL Accuracy Limits: Smaller local models struggle with complex joins, window functions, or ambiguous schemas compared to frontier cloud models.

* Limited Concurrency: Built for single-user local exploration rather than multi-user production workloads.

* Guardrail Overhead: Requires strict read-only database permissions and query validation to prevent accidental mutations or heavy table scans.
