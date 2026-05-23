SELECT year, male_rate_pct, female_rate_pct, gender_gap_pct
FROM literacy_data
WHERE iso_code = 'MAR'
AND year IN (1982, 1994, 2004, 2011, 2014)
AND male_rate_pct IS NOT NULL
ORDER BY year ASC;