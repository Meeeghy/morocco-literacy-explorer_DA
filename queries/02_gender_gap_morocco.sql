SELECT year, male_rate_pct, female_rate_pct, gender_gap_pct
FROM literacy_data
WHERE iso_code = 'MAR'
AND male_rate_pct IS NOT NULL
AND female_rate_pct IS NOT NULL
ORDER BY year ASC;