SELECT c.country_name, l.iso_code, l.year, l.male_rate_pct, l.female_rate_pct, l.gender_gap_pct
FROM literacy_data l
JOIN countries c ON l.iso_code = c.iso_code
WHERE l.gender_gap_pct IS NOT NULL
AND (l.iso_code, l.year) IN (
    SELECT iso_code, MAX(year)
    FROM literacy_data
    WHERE gender_gap_pct IS NOT NULL
    GROUP BY iso_code
)
ORDER BY l.gender_gap_pct DESC
LIMIT 1;