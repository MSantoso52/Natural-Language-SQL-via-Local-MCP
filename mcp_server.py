import os
import psycopg2
from mcp.server.mcpserver import MCPServer

# Initialize MCP server
mcp = MCPServer("PostgresDataServer")

# Database configuration
DB_HOST = os.getenv("DB_HOST", "172.17.0.2")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "employee")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "duckdb")


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
