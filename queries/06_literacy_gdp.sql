SELECT year, literacy_rate_pct, gdp_per_capita_usd
FROM literacy_data
WHERE iso_code = 'MAR'
AND literacy_rate_pct IS NOT NULL
AND gdp_per_capita_usd IS NOT NULL
ORDER BY year ASC;