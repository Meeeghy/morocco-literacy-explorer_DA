SELECT year, literacy_rate_pct, male_rate_pct, female_rate_pct
FROM literacy_data
WHERE iso_code = 'MAR'
AND literacy_rate_pct IS NOT NULL
ORDER BY year ASC;