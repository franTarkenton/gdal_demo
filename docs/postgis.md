### List Schemas
```
select schema_name
from information_schema.schemata;
```

What is the current database:
```
\dt
```

list tables:
```
SELECT
   *
FROM
   pg_catalog.pg_tables
WHERE
   schemaname != 'pg_catalog'
AND schemaname != 'information_schema';
```