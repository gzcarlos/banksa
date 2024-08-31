# banksa
Bank Statement Analyser app with LLMs


## Setup

### General

Create a network for docker
```bash
docker network create banksa-network
```

### Mage AI

```bash
docker run -d \
  --name mage \
  -p 6789:6789 \
  -v $(pwd)/mageai:/home/src \
  --network=banksa-network \
  mageai/mageai mage start magic
```

### Google Drive API
1. Create [Google Cloud Project](https://console.cloud.google.com/):
2. Go to the Google Cloud Console.
3. Create a new project.
4. Enable the Google Drive API for your project.
5. Configure the OAuth consent screen.
6. Create credentials (OAuth 2.0 Client IDs) and download the `credentials.json` file.
7. Create a folder in [google drive](https://drive.google.com/) and `Manage Access` to anyone with the link can `view`
8. Run the `/notebooks/test_google_drive_api.ipynb` using the previous folder  to generate a `token.json` in `/notebooks` folder

### PostgreSQL

Install the database service and the IDE (pgadmin)

```bash
docker run -d \
  -e POSTGRES_USER="root" \
  -e POSTGRES_PASSWORD="root" \
  -e POSTGRES_DB="banksa" \
  -v postgres_volume_local:/var/lib/postgresql/data \
  -p 5432:5432 \
  --network=banksa-network \
  --name pg-database \
  postgres:13
docker run -d \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8082:80 \
  --network=banksa-network \
  --name pgadmin \
  dpage/pgadmin4
```

1. Access to pdadmin on the browser [http://localhost:8082](http://localhost:8082)
2. On the `Servers` right click and select `Register` and set `Name`. In Connections use the host `pg-database` and credentials from the previous commands
3. You should see `banksa` database and can create a table under `schemas/tables`


### Elasticsearch

Install with this command
```bash
docker run -d \
    --rm \
    --name elasticsearch \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    --network=banksa-network \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

Check status on [http://localhost:9200/_cluster/health?pretty](http://localhost:9200/_cluster/health?pretty)


### Database schema

```sql
CREATE TABLE files (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    size FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE folders (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
