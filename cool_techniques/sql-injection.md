# References
**Sure**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection

**Convenient**: https://portswigger.net/web-security/sql-injection/cheat-sheet

# List table in current database(MySQL, PostgreSQL,...)
```
SELECT .......... WHERE table_schema='local'-- -
```

# Oracle
On Oracle databases, every SELECT statement must specify a table to select FROM. If your UNION SELECT attack does not query from a table, you will still need to include the FROM keyword followed by a valid table name.
