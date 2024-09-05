# banksa
Bank Statement Analyser app with LLMs


## Setup

### General

Create a network for docker
```bash
docker network create banksa-network
```

### Mage AI

Create container
```bash
docker run -d \
  --name mage \
  -p 6789:6789 \
  -v $(pwd)/mageai:/home/src \
  --network=banksa-network \
  mageai/mageai mage start magic
```

Instal missing packages inside the Mage container

```bash
docker exec -it mage bash
pip install groq openai
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
  file_text TEXT,
  generated_json JSONB,
  json_extracted BOOLEAN DEFAULT False,
  transactions_extracted BOOLEAN default False,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE folders (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
create table transactions(
  id SERIAL PRIMARY KEY ,
  file_id integer,

  statement_date date,
  statement_year integer,
  statement_month integer,
  amount float,
  category text,
  currency text,
  date date,
  description text,
  type text,
  
  _statement_date date,
  _statement_year integer,
  _statement_month integer,
  _amount float,
  _category text,
  _currency text,
  _date date,
  _description text,
  _type text,
  
  predict_category boolean default true,
  predicted_category text,

  confirmed_category boolean,
  suggested_category text,  
  
  created_at timestamp default current_timestamp,
  updated_at timestamp,
  constraint trans_fk1 foreign key(file_id) references files(id)
);
create table knowledge_base(
  id serial primary key,
  
  description text,
  category text, 

  upvoted boolean,
  downvoted boolean,
  suggested_category text,

  updated_transactions boolean default false,
  
  indexed boolean default false,
  
  created_at timestamp default current_timestamp,
  updated_at timestamp
);
```


Run extract_transactions_from_files
```bash
curl -X POST http://localhost:6789/api/pipeline_schedules/4/pipeline_runs/aa5cf2fcfd4c4e7fb64c7da8ef924b25 --header 'Content-Type: application/json'
```
```python
import requests
# do not wait for the response
try:
    requests.post("http://localhost:6789/api/pipeline_schedules/4/pipeline_runs/aa5cf2fcfd4c4e7fb64c7da8ef924b25", 
                  headers={"Content-Type": "application/json"}, 
                  timeout=0.01)
except requests.exceptions.ReadTimeout:
    pass  # This will almost always happen, which is what we want
```
