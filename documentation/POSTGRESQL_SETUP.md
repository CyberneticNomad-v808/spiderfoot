# PostgreSQL Configuration for SpiderFoot

SpiderFoot requires PostgreSQL for database storage. SQLite support has been removed as of the PostgreSQL migration.

## Quick Start

### Docker Compose (Recommended)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: spiderfoot_db
      POSTGRES_USER: spiderfoot
      POSTGRES_PASSWORD: your_secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - spiderfoot_net

  spiderfoot:
    image: spiderfoot/spiderfoot:latest
    environment:
      - SPIDERFOOT_DB_TYPE=postgresql
      - SPIDERFOOT_DB_HOST=postgres
      - SPIDERFOOT_DB_PORT=5432
      - SPIDERFOOT_DB_NAME=spiderfoot_db
      - SPIDERFOOT_DB_USER=spiderfoot
      - SPIDERFOOT_DB_PASSWORD=your_secure_password
    ports:
      - "5001:5001"
    depends_on:
      - postgres
    networks:
      - spiderfoot_net

volumes:
  postgres_data:

networks:
  spiderfoot_net:
```

### Standalone Installation

1. Install PostgreSQL:
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

2. Create database and user:
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Create database and user
CREATE DATABASE spiderfoot_db;
CREATE USER spiderfoot WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE spiderfoot_db TO spiderfoot;
\q
```

3. Configure environment variables:
```bash
export SPIDERFOOT_DB_TYPE=postgresql
export SPIDERFOOT_DB_HOST=localhost
export SPIDERFOOT_DB_PORT=5432
export SPIDERFOOT_DB_NAME=spiderfoot_db
export SPIDERFOOT_DB_USER=spiderfoot
export SPIDERFOOT_DB_PASSWORD=your_secure_password
```

4. Start SpiderFoot:
```bash
python sf.py -l 127.0.0.1:5001
```

## Environment Variables

### Required

| Variable | Example | Description |
|----------|---------|-------------|
| `SPIDERFOOT_DB_NAME` or `SPIDERFOOT_DB` | `spiderfoot_db` | PostgreSQL database name (REQUIRED) |

### Optional (with defaults)

| Variable | Default | Description |
|----------|---------|-------------|
| `SPIDERFOOT_DB_TYPE` | `postgresql` | Database type (must be 'postgresql') |
| `SPIDERFOOT_DB_HOST` | `localhost` | PostgreSQL server hostname |
| `SPIDERFOOT_DB_PORT` | `5432` | PostgreSQL server port |
| `SPIDERFOOT_DB_USER` | `spiderfoot` | Database username |
| `SPIDERFOOT_DB_PASSWORD` or `SPIDERFOOT_DB_PASS` | *(none)* | Database password (strongly recommended) |

### Legacy Variables (backward compatibility)

For backward compatibility, SpiderFoot also supports these legacy variable names:
- `SPIDERFOOT_DB` → Same as `SPIDERFOOT_DB_NAME` (deprecated, use `SPIDERFOOT_DB_NAME`)
- `SPIDERFOOT_DB_PASS` → Same as `SPIDERFOOT_DB_PASSWORD` (deprecated, use `SPIDERFOOT_DB_PASSWORD`)

### Advanced

| Variable | Description |
|----------|-------------|
| `SPIDERFOOT_DATABASE` | Full PostgreSQL DSN URI (overrides individual variables) |

Example:
```bash
export SPIDERFOOT_DATABASE="postgresql://user:password@host:5432/database"
```

## Connection String Format

SpiderFoot uses PostgreSQL DSN URI format:
```
postgresql://username:password@hostname:port/database
```

Examples:
- `postgresql://spiderfoot:mypass@localhost:5432/spiderfoot_db`
- `postgresql://spiderfoot@localhost:5432/spiderfoot_db` (no password)
- `postgresql://user:p%40ss%3Aword@db.example.com:5432/sf` (URL-encoded password)

**Note**: Passwords with special characters (@, :, /, etc.) are automatically URL-encoded by SpiderFoot.

## Troubleshooting

### Error: "Database name is required"

**Cause**: The `SPIDERFOOT_DB_NAME` or `SPIDERFOOT_DB` environment variable is not set.

**Solution**: Set the required environment variable:
```bash
export SPIDERFOOT_DB_NAME=spiderfoot_db
```

### Error: "PostgreSQL connection failed"

**Cause**: Cannot connect to PostgreSQL server.

**Troubleshooting steps**:

1. **Check PostgreSQL is running**:
```bash
# Linux
sudo systemctl status postgresql

# macOS
brew services list | grep postgresql

# Test connection
pg_isready -h localhost -p 5432
```

2. **Verify database exists**:
```bash
psql -h localhost -U spiderfoot -d spiderfoot_db -c '\dt'
```

3. **Check credentials**:
- Ensure username and password are correct
- Check `pg_hba.conf` allows password authentication

4. **Verify network access**:
- Check firewall allows connections on port 5432
- For Docker: ensure containers are on same network

5. **Check PostgreSQL logs**:
```bash
# Linux
sudo tail -f /var/log/postgresql/postgresql-*.log

# macOS
tail -f /usr/local/var/log/postgresql@15.log

# Docker
docker logs postgres_container_name
```

### Error: "Invalid PostgreSQL connection string"

**Cause**: The connection string format is incorrect or contains a SQLite path.

**Solution**: Ensure you're using PostgreSQL DSN URI format, not a file path:
- ✅ Correct: `postgresql://user:pass@host:5432/db`
- ❌ Wrong: `/home/spiderfoot/data/spiderfoot.db`

### Error: "SQLite is not supported"

**Cause**: Trying to use SQLite, which is no longer supported.

**Solution**: Migrate to PostgreSQL using the steps in this guide.

### Database initialization fails

**Cause**: User lacks permissions to create tables.

**Solution**: Grant proper permissions:
```sql
-- As PostgreSQL superuser
GRANT ALL PRIVILEGES ON DATABASE spiderfoot_db TO spiderfoot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO spiderfoot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO spiderfoot;
```

### Connection timeout / "No route to host"

**Cause**: Network/firewall blocking connection.

**Solutions**:
1. Check `postgresql.conf` has `listen_addresses = '*'` (or appropriate IP)
2. Check `pg_hba.conf` allows connections from your IP:
   ```
   host    all    all    0.0.0.0/0    md5
   ```
3. Restart PostgreSQL after config changes:
   ```bash
   sudo systemctl restart postgresql
   ```

## Production Recommendations

### Security

1. **Use strong passwords**: Generate with `openssl rand -base64 32`
2. **Restrict network access**: Only allow connections from SpiderFoot hosts
3. **Use SSL/TLS**: Configure PostgreSQL to require encrypted connections
4. **Regular backups**: Use `pg_dump` or continuous archiving

### Performance

1. **Connection pooling**: Use PgBouncer for high-load deployments
2. **Tune PostgreSQL**:
   ```sql
   -- Example settings (adjust based on your hardware)
   shared_buffers = 256MB
   effective_cache_size = 1GB
   work_mem = 4MB
   maintenance_work_mem = 64MB
   ```
3. **Regular maintenance**:
   ```sql
   VACUUM ANALYZE;  -- Run periodically
   ```

### Backup & Recovery

**Backup**:
```bash
# Backup database
pg_dump -h localhost -U spiderfoot spiderfoot_db > backup.sql

# With compression
pg_dump -h localhost -U spiderfoot spiderfoot_db | gzip > backup.sql.gz
```

**Restore**:
```bash
# Restore database
psql -h localhost -U spiderfoot spiderfoot_db < backup.sql

# From compressed backup
gunzip -c backup.sql.gz | psql -h localhost -U spiderfoot spiderfoot_db
```

## Migration from SQLite

If you're migrating from a previous SQLite-based SpiderFoot installation:

1. **Export data from SQLite** (if needed):
```bash
# Backup SQLite database
cp /path/to/spiderfoot.db spiderfoot.db.backup
```

2. **Set up PostgreSQL** (see Quick Start above)

3. **Start SpiderFoot with PostgreSQL**:
   - SpiderFoot will automatically create the schema on first run
   - Note: Automatic data migration from SQLite is not supported
   - You'll start with a fresh database

4. **Manual data migration** (advanced):
   - Use `pgloader` to migrate data from SQLite to PostgreSQL
   - See: https://pgloader.readthedocs.io/

## Docker Networking

When using Docker, ensure SpiderFoot and PostgreSQL containers can communicate:

**Same network**:
```yaml
networks:
  spiderfoot_net:
    driver: bridge
```

**DNS resolution**:
- Use service name as hostname: `SPIDERFOOT_DB_HOST=postgres`
- Docker handles DNS resolution automatically

**Port mapping** (for external access):
```yaml
postgres:
  ports:
    - "5432:5432"  # Only if you need external access
```

## Health Checks

Test database connectivity:

```bash
# Using psql
psql -h localhost -p 5432 -U spiderfoot -d spiderfoot_db -c "SELECT version();"

# Using Python
python3 -c "import psycopg2; conn = psycopg2.connect('postgresql://spiderfoot:pass@localhost:5432/spiderfoot_db'); print('OK')"
```

## Support

For issues:
1. Check this documentation
2. Review error messages for troubleshooting steps
3. Check logs: SpiderFoot logs and PostgreSQL logs
4. Create issue at: https://github.com/smicallef/spiderfoot/issues

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 (Python PostgreSQL adapter): https://www.psycopg.org/
- Docker Compose: https://docs.docker.com/compose/
