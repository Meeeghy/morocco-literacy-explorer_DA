import pandas as pd

literacy = pd.read_csv("data/raw/literacy.csv", skiprows=4)
gdp = pd.read_csv("data/raw/gdp.csv", skiprows=4)
poverty = pd.read_csv("data/raw/poverty.csv", skiprows=4)

print(gdp.head())