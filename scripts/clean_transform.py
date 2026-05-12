import pandas as pd

# Load raw GDP data (skip World Bank metadata rows)
gdp = pd.read_csv("data/raw/gdp.csv", skiprows=4)

print("RAW GDP SHAPE:", gdp.shape)
print(gdp.head())

gdp_long = gdp.melt(
    id_vars=["Country Name", "Country Code", "Indicator Name"],
    var_name="year",
    value_name="gdp_per_capita_usd"
)

print("LONG FORMAT SHAPE:", gdp_long.shape)
print(gdp_long.head())

gdp_long["year"] = pd.to_numeric(gdp_long["year"], errors="coerce")

countries = [
    "Morocco", "Algeria", "Tunisia", "Egypt",
    "Jordan", "Lebanon", "Saudi Arabia", "Yemen", "Libya"
]

gdp_long = gdp_long[gdp_long["Country Name"].isin(countries)]

print("FILTERED SHAPE:", gdp_long.shape)

gdp_long = gdp_long.dropna(subset=["gdp_per_capita_usd"])

gdp_long = gdp_long.sort_values(["Country Name", "year"])

gdp_long.to_csv("data/cleaned/gdp_clean.csv", index=False)









literacy = pd.read_csv("data/raw/literacy.csv", skiprows=4)

print("RAW LITERACY SHAPE:", literacy.shape)
print(literacy.head())
print(literacy.columns)

# detect correct column names safely
literacy.columns = literacy.columns.str.strip()

# rename first columns to standard names
literacy = literacy.rename(columns={
    literacy.columns[0]: "country",
    literacy.columns[1]: "country_code",
    literacy.columns[2]: "year",
    literacy.columns[3]: "literacy_rate_pct"
})

literacy["year"] = pd.to_numeric(literacy["year"], errors="coerce")

literacy = literacy[literacy["country"].isin(countries)]
literacy = literacy.dropna(subset=["literacy_rate_pct"])







poverty = pd.read_csv("data/raw/poverty.csv", skiprows=4)

print("RAW POVERTY SHAPE:", poverty.shape)

poverty_long = poverty.melt(
    id_vars=["Country Name", "Country Code", "Indicator Name"],
    var_name="year",
    value_name="poverty_rate_pct"
)

poverty_long["year"] = pd.to_numeric(poverty_long["year"], errors="coerce")

poverty_long = poverty_long[poverty_long["Country Name"].isin(countries)]
poverty_long = poverty_long.dropna(subset=["poverty_rate_pct"])





# =========================
# 4. MERGE ALL DATASETS
# =========================
merged = literacy.merge(
    gdp_long,
    left_on=["country", "country_code", "year"],
    right_on=["Country Name", "Country Code", "year"],
    how="outer"
)

merged = merged.merge(
    poverty_long,
    left_on=["country", "country_code", "year"],
    right_on=["Country Name", "Country Code", "year"],
    how="outer"
)

# =========================
# 5. CLEAN FINAL OUTPUT
# =========================
merged = merged.rename(columns={
    "country": "country",
    "country_code": "country_code"
})

merged = merged.sort_values(["country", "year"])

merged.to_csv("data/cleaned/final_dataset.csv", index=False)

print("FINAL SHAPE:", merged.shape)
print(merged.head())