from fastmcp import FastMCP
import psycopg2
import os
from typing import Optional

# Initialize MCP server
mcp = FastMCP("KOBACO Ad Data Layer")

def get_db_connection():
    dsn = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/ad_data_layer")
    return psycopg2.connect(dsn)

@mcp.tool()
def search_media(query: str) -> str:
    """Search for media channels by name or owner."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        sql = "SELECT id, media_owner, media_name, media_type, pricing_model FROM media_records WHERE media_name ILIKE %s OR media_owner ILIKE %s LIMIT 10"
        cur.execute(sql, (f"%{query}%", f"%{query}%"))
        results = cur.fetchall()
        if not results:
            return "No media found matching query."

        output = []
        for row in results:
            output.append(f"ID: {row[0]}, Owner: {row[1]}, Name: {row[2]}, Type: {row[3]}, Pricing: {row[4]}")
        return "\n".join(output)
    finally:
        conn.close()

@mcp.tool()
def get_media_detail(media_id: str) -> str:
    """Get detailed information about a specific media channel including evidence."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        # Get record
        cur.execute("SELECT * FROM media_records WHERE id = %s", (media_id,))
        if cur.description:
            col_names = [desc[0] for desc in cur.description]
        else:
            return "Error retrieving columns."

        row = cur.fetchone()
        if not row:
            return "Media not found."

        record = dict(zip(col_names, row))

        # Get evidence
        cur.execute("SELECT field, quote, page FROM evidence WHERE record_id = %s AND record_kind = 'approved'", (media_id,))
        evidence_rows = cur.fetchall()
        evidence_text = "\n".join([f"- {r[0]}: \"{r[1]}\" (Page {r[2]})" for r in evidence_rows])

        detail = f"""
Media: {record.get('media_name')} ({record.get('media_owner')})
Type: {record.get('media_type')}
Product: {record.get('product_name')}
Pricing: {record.get('pricing_model')} ({record.get('price_text')})
Targeting: {record.get('targeting_text')}
Specs: {record.get('specs_text')}
KPIs: {record.get('kpi_text')}
Valid Until: {record.get('valid_until')}

Evidence:
{evidence_text}
"""
        return detail
    finally:
        conn.close()

@mcp.tool()
def shortlist_for_brief(brief_summary: str, media_type: Optional[str] = None) -> str:
    """
    Suggest a shortlist of media based on a brief summary and optional media type.
    This is a heuristic search.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # Simple heuristic: filter by media_type if provided, else just list top 5 recent
        params = []
        sql = "SELECT id, media_name, media_owner, targeting_text FROM media_records WHERE 1=1"
        if media_type:
            sql += " AND media_type ILIKE %s"
            params.append(f"%{media_type}%")

        sql += " ORDER BY created_at DESC LIMIT 5"

        cur.execute(sql, tuple(params))
        results = cur.fetchall()

        if not results:
            return "No matching media found."

        output = [f"Here are some candidates for '{brief_summary}':"]
        for row in results:
            output.append(f"- {row[1]} ({row[2]}): Targeting '{row[3]}'. ID: {row[0]}")

        return "\n".join(output)
    finally:
        conn.close()

if __name__ == "__main__":
    mcp.run()
