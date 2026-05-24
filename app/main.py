from fastapi import FastAPI, Query
from typing import Optional
import psycopg2
import psycopg2.extras

app = FastAPI(title="Morocco Literacy Explorer API")

def get_conn():
    return psycopg2.connect(
        dbname="morocco_literacy",
        user="postgres",
        password="2004",
        host="localhost"
    )

@app.get("/api/v1/countries")
def get_countries():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT iso_code, country_name, region, is_primary FROM countries ORDER BY country_name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/literacy")
def get_literacy(
    country_iso: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = "SELECT * FROM literacy_data WHERE 1=1"
    params = []
    if country_iso:
        query += " AND iso_code = %s"
        params.append(country_iso)
    if year_from:
        query += " AND year >= %s"
        params.append(year_from)
    if year_to:
        query += " AND year <= %s"
        params.append(year_to)
    query += " ORDER BY iso_code, year"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/trends/{iso_code}")
def get_trends(iso_code: str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT year, literacy_rate_pct, male_rate_pct, female_rate_pct, gender_gap_pct
        FROM literacy_data
        WHERE iso_code = %s
        ORDER BY year
    """, (iso_code.upper(),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/compare")
def compare(
    countries: str = Query(..., description="Comma separated ISO codes e.g. MAR,DZA,TUN"),
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
):
    iso_list = [c.strip().upper() for c in countries.split(",")]
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = """
        SELECT l.iso_code, c.country_name, l.year, l.literacy_rate_pct
        FROM literacy_data l
        JOIN countries c ON l.iso_code = c.iso_code
        WHERE l.iso_code = ANY(%s)
        AND l.literacy_rate_pct IS NOT NULL
    """
    params = [iso_list]
    if year_from:
        query += " AND l.year >= %s"
        params.append(year_from)
    if year_to:
        query += " AND l.year <= %s"
        params.append(year_to)
    query += " ORDER BY l.year, l.iso_code"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/gender-gap")
def gender_gap(country_iso: str = "MAR"):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT year, male_rate_pct, female_rate_pct, gender_gap_pct
        FROM literacy_data
        WHERE iso_code = %s
        AND male_rate_pct IS NOT NULL
        AND female_rate_pct IS NOT NULL
        ORDER BY year
    """, (country_iso.upper(),))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/economic")
def economic(country_iso: str = "MAR", year_from: Optional[int] = None, year_to: Optional[int] = None):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    query = """
        SELECT year, gdp_per_capita_usd, poverty_headcount_pct
        FROM literacy_data
        WHERE iso_code = %s
        AND gdp_per_capita_usd IS NOT NULL
    """
    params = [country_iso.upper()]
    if year_from:
        query += " AND year >= %s"
        params.append(year_from)
    if year_to:
        query += " AND year <= %s"
        params.append(year_to)
    query += " ORDER BY year"
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/api/v1/morocco/summary")
def morocco_summary():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT literacy_rate_pct, male_rate_pct, female_rate_pct, gender_gap_pct, year
        FROM literacy_data
        WHERE iso_code = 'MAR' AND literacy_rate_pct IS NOT NULL
        ORDER BY year DESC LIMIT 1
    """)
    latest = cur.fetchone()
    cur.execute("""
        SELECT literacy_rate_pct FROM literacy_data
        WHERE iso_code = 'MAR' AND year = (
            SELECT MIN(year) FROM literacy_data
            WHERE iso_code = 'MAR' AND literacy_rate_pct IS NOT NULL
        )
    """)
    earliest = cur.fetchone()
    cur.execute("""
        SELECT COUNT(*) + 1 AS rank FROM (
            SELECT iso_code, MAX(literacy_rate_pct) AS rate
            FROM literacy_data WHERE literacy_rate_pct IS NOT NULL
            GROUP BY iso_code
        ) t WHERE t.rate > %s
    """, (latest["literacy_rate_pct"],))
    rank = cur.fetchone()
    cur.close()
    conn.close()
    return {
        "current_year": latest["year"],
        "current_rate": latest["literacy_rate_pct"],
        "male_rate": latest["male_rate_pct"],
        "female_rate": latest["female_rate_pct"],
        "gender_gap": latest["gender_gap_pct"],
        "rate_in_1982": earliest["literacy_rate_pct"],
        "improvement": round(float(latest["literacy_rate_pct"]) - float(earliest["literacy_rate_pct"]), 2),
        "mena_rank": rank["rank"]
    }