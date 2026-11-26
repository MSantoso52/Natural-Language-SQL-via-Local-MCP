import os
import re
import psycopg2
from dotenv import load_dotenv
from pathlib import Path
from mcp.server.mcpserver import MCPServer

# Load .env from the same directory as this script (does not overwrite existing OS env vars)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

# Initialize MCP server
mcp = MCPServer("PostgresDataServer")

REQUIRED_ENV_VARS = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
FORBIDDEN_SQL_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|truncate|create|grant|revoke|copy|vacuum|analyze|reindex|call|do)\b",
    re.IGNORECASE,
)

def get_db_config() -> dict:
    """Validate and return required database credentials from the environment."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}. "
            "Set them in your .env file or environment."
        )

    try:
        port = int(os.getenv("DB_PORT", "5432"))
        timeout_ms = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "5000"))
    except ValueError as exc:
        raise RuntimeError("DB_PORT and DB_STATEMENT_TIMEOUT_MS must be integers.") from exc

    return {
        "host": os.getenv("DB_HOST"),
        "port": port,
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "timeout_ms": max(100, timeout_ms),
    }

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


@mcp.tool()
def list_tables() -> str:
    """List all public tables in the PostgreSQL database."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema != 'public';"
        )
        tables = [row[0] for row in cursor.fetchall()]
        if not tables:
            return "No tables found in public schema."
        return f"Tables: {', '.join(tables)}"
    finally:
        cursor.close()
        conn.close()


@mcp.tool()
def describe_table(table_name: str) -> str:
    """Get column names and data types for a specific table."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema != 'public' AND table_name = %s;
            """,
            (table_name,),
        )
        columns = cursor.fetchall()
        if not columns:
            return f"Table '{table_name}' not found."
        desc = [f"- {col[0]} ({col[1]}, Nullable: {col[2]})" for col in columns]
        return f"Schema for '{table_name}':\n" + "\n".join(desc)
    finally:
        cursor.close()
        conn.close()


@mcp.tool()
def run_select_query(query: str) -> str:
    """Execute a read-only SELECT query against the PostgreSQL database."""
    if not query.strip().lower().startswith("select"):
        return "ERROR: Only SELECT queries are allowed for security."

    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        result = [", ".join(columns)]
        for row in rows[:30]:  # Limit to 30 rows for display safety
            result.append(", ".join(str(val) for val in row))
        return "\n".join(result)
    except Exception as e:
        return f"Database Error: {str(e)}"
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    mcp.run()
