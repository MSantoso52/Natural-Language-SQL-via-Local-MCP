import asyncio
import os
import sys
import requests
import re
import streamlit as st
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

st.set_page_config(page_title="Local Postgres MCP + Gemma", layout="wide")

st.markdown(
    """
    <style>
    .stMainBlockContainer h1 {
        font-size: 2rem; /* adjust e.g. 1.5rem, 2.25rem, or 32px */
        line-height: 1.2;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🚀 Local Data Engineer (Postgres + MCP + Gemma)", width="stretch")
st.sidebar.header("⚙️ Configuration")
ollama_model = st.sidebar.selectbox("Ollama Model", ["gemma2:2b"], index=0)
ollama_url = st.sidebar.text_input(
    "Ollama endpoint", "http://localhost:11434/api/generate"
)

def query_ollama(prompt: str) -> str:
    payload = {
        "model": ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = requests.post(ollama_url, json=payload, timeout=180)
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Ollama Error ({response.status_code}): {response.text}"
    except Exception as e:
        return f"Connection Error on Ollama: {str(e)}"


async def run_mcp_action(tool_name: str, arguments: dict | None = None):
    server_param = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
        env=os.environ.copy(),
    )
    async with stdio_client(server_param) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            if tool_name == "list_tools":
                return await session.list_tools()

            result = await session.call_tool(tool_name, arguments or {})
            return result.content[0].text

def _extract_sql(text: str) -> str | None:
    match = re.search(r"```sql\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if match:
        sql = match.group(1).strip()
        return None if sql.upper() == "NONE" else sql
    return None

tab1, tab2 = st.tabs(["🤖 AI Assistant & SQL Generator", "📊 Live Data Inspector"])

with tab1:
    st.subheader("Chat with your database via Ollama & MCP")

    user_prompt = st.text_area(
        "Ask about your database or request SQL query:",
        placeholder="e.g., What tables do we have and what are their schemas?",
    )
    if st.button("Run AI Assistant"):
        if not user_prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Fetching tables, generating SQL, and executing via MCP..."):
                mcp_tables = asyncio.run(run_mcp_action("list_tables"))

                sql_prompt = f"""You are an expert PostgreSQL Data Engineer assistant.
                    Available tables from MCP server:
                    {mcp_tables}

                    User Request: {user_prompt}

                    If answering requires reading data from PostgreSQL, output a single read-only SELECT query inside a ```sql code block.
                    If no SQL query is needed, output ```sql\nNONE\n```.
                    """
                draft_response = query_ollama(sql_prompt)
                generated_sql = _extract_sql(draft_response)

                query_result = None
                if generated_sql:
                    query_result = asyncio.run(
                        run_mcp_action("run_select_query", {"query": generated_sql})
                    )

                final_prompt = f"""You are an expert PostgreSQL Data Engineer assistant.
                                User Request: {user_prompt}
                                Generated SQL: {generated_sql or "None"}
                                MCP Query Result:
                                    {query_result if query_result is not None else "No SQL executed."}

                                Provide a clear, direct answer based on the MCP Query Result above. Do not invent rows or columns not present in the result.
                                """
                final_answer = query_ollama(final_prompt)

            st.markdown("### Final Answer:")
            st.write(final_answer)

            if generated_sql:
                st.markdown("### Executed SQL (`run_select_query`):")
                st.code(generated_sql, language="sql")

            if query_result is not None:
                st.markdown("### MCP Query Result:")
                st.code(query_result) 

with tab2:
    st.subheader("Direct MCP Server Tool Execution")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("List All Tables (MCP Tool)"):
            res = asyncio.run(run_mcp_action("list_tables"))
            st.code(res)

        table_to_inspect = st.text_input("Table name to describe:")
        if st.button("Describe Table (MCP Tool)") and table_to_inspect:
            res = asyncio.run(
                run_mcp_action("describe_table", {"table_name": table_to_inspect})
            )
            st.code(res)

    with col2:
        sql_input = st.text_area(
            "Run Raw SELECT Query (MCP Tool):",
            placeholder="SELECT * FROM my_table LIMIT 5;",
        )
        if st.button("Execute Query") and sql_input:
            res = asyncio.run(run_mcp_action("run_select_query", {"query": sql_input}))
            st.code(res)


            # with st.spinner("Fetching database metadata via MCP & querying Gemma2:2b..."):
            #   mcp_tables = asyncio.run(run_mcp_action("list_tables"))
        
            #   augmented_prompt = f"""You are an expert Data Engineer assistant.
            #                      Database tables from MCP server:
            #                        {mcp_tables}
            #
            #                        User Request: {user_prompt}

            #                       Provide appropriate SQL query if requested, then execute it by feed into run_mcp_action function to get the result.
            #                       """
            #    ai_response = query_ollama(augmented_prompt)
            #    st.markdown("### AI Response:")
            #    st.write(ai_response)
           
