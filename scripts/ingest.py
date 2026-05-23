import pandas as pd
import psycopg2

conn = psycopg2.connect(
    dbname="morocco_literacy",
    user="postgres",
    password="2004",
    host="localhost"
)
cur = conn.cursor()

COUNTRIES = {
    "MAR": "Morocco", "DZA": "Algeria", "TUN": "Tunisia",
    "EGY": "Egypt",   "JOR": "Jordan",  "LBN": "Lebanon",
    "SAU": "Saudi Arabia", "YEM": "Yemen", "LBY": "Libya"
}

for iso, name in COUNTRIES.items():
    cur.execute("""
        INSERT INTO countries (iso_code, country_name, is_primary)
        VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
    """, (iso, name, iso == "MAR"))
conn.commit()
print("Countries inserted.")

def load_wb(filepath, value_col):
    df = pd.read_csv(filepath, skiprows=4)
    df = df[df["Country Code"].isin(COUNTRIES.keys())]
    year_cols = [c for c in df.columns if c.isdigit()]
    df = df.melt(id_vars=["Country Code"], value_vars=year_cols,
                 var_name="year", value_name=value_col)
    df["year"] = df["year"].astype(int)
    df = df[df["year"].between(1970, 2024)]
    df = df.rename(columns={"Country Code": "iso_code"})
    return df

df_male   = load_wb("data/raw/literacy_male.csv", "male_rate")
df_female = load_wb("data/raw/literacy_female.csv", "female_rate")
df_gdp    = load_wb("data/raw/gdp.csv", "gdp")

df_overall = pd.read_csv("data/raw/literacy.csv")
df_overall = df_overall[df_overall["Code"].isin(COUNTRIES.keys())]
df_overall = df_overall.rename(columns={
    "Code": "iso_code",
    "Year": "year",
    "Literacy rate among adults": "literacy_rate"
})
df_overall = df_overall[["iso_code", "year", "literacy_rate"]]

df = df_overall.merge(df_male,   on=["iso_code", "year"], how="outer")
df = df.merge(df_female, on=["iso_code", "year"], how="outer")
df = df.merge(df_gdp,    on=["iso_code", "year"], how="outer")
df = df[df["iso_code"].isin(COUNTRIES.keys())]

cur.execute("DELETE FROM literacy_data")
conn.commit()

count = 0
for _, row in df.iterrows():
    year = int(row["year"])
    literacy = None if pd.isna(row.get("literacy_rate", float("nan"))) else float(row["literacy_rate"])
    male     = None if pd.isna(row.get("male_rate",     float("nan"))) else float(row["male_rate"])
    female   = None if pd.isna(row.get("female_rate",   float("nan"))) else float(row["female_rate"])
    gdp      = None if pd.isna(row.get("gdp",           float("nan"))) else float(row["gdp"])

    cur.execute("""
        INSERT INTO literacy_data
            (iso_code, year, literacy_rate_pct, male_rate_pct, female_rate_pct, gdp_per_capita_usd)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (row["iso_code"], year, literacy, male, female, gdp))
    count += 1

conn.commit()
cur.close()
conn.close()
print(f"Done! {count} rows inserted.")