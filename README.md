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

## Project Flow

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
