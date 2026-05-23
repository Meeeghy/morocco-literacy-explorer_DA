SELECT l.year,
       MAX(CASE WHEN l.iso_code = 'MAR' THEN l.literacy_rate_pct END) AS morocco_rate,
       ROUND(AVG(CASE WHEN l.iso_code != 'MAR' THEN l.literacy_rate_pct END), 2) AS mena_avg
FROM literacy_data l
WHERE l.literacy_rate_pct IS NOT NULL
GROUP BY l.year
HAVING MAX(CASE WHEN l.iso_code = 'MAR' THEN l.literacy_rate_pct END) IS NOT NULL
ORDER BY l.year ASC;