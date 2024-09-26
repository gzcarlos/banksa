# Setup Guide

For this app, the following tools are required:
1. **PostgreSQL**: as the main database.
2. **MageAI**: as the worker orchestrator (pipelines).
3. **Elasticsearch**: as the vector database to store descriptions and categories you give feedback on.
4. **pgAdmin**: as the Database IDE.

This document specifies how to do an initial setup using [Docker Compose](#with-docker-compose) or a [Manual setup](#manual-setup) for the project. After completing either of them, you should continue with:

1. [Common Setup](#common-setup)
2. [Other services](#other-services)

## With Docker Compose

Execute these two commands to complete the creation of the environment:
```bash
# Create all the images and pull some others needed
docker compose build
# Run all the images
docker compose up -d
```

## Manual Setup

Create a network for Docker:
```bash
docker network create banksa-network
```

### Mage AI setup

Create a Docker container for MageAI using the folder `/mageai` as the source archive for all the files:
```bash
docker run -d \
  --name mage \
  -p 6789:6789 \
  -v $(pwd)/mageai:/home/src \
  --network=banksa-network \
  mageai/mageai mage start magic
```

Make sure to have a `.env` file (you may use the template from the [sample.env](/sample.env) file) and complete these two variables:

```bash
GROQ_API_KEY=your_api_key_for_groq.console
OPENAI_API_KEY=your_api_key_for_openai.platform
```

The final service is available at [http://localhost:6789](http://localhost:6789)

### PostgreSQL setup

Install the database service and the IDE (pgAdmin):

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

The pgAdmin service is available at [http://localhost:8082](http://localhost:8082). Use the credentials from the previous commands.

### Elasticsearch setup

Install with this command:
```bash
docker run -d \
    --name elasticsearch \
    -p 9200:9200 \
    -p 9300:9300 \
    -e "discovery.type=single-node" \
    -e "xpack.security.enabled=false" \
    --network=banksa-network \
    -v ./vectordb-data:/usr/share/elasticsearch/data \
    docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

Check status at [http://localhost:9200/_cluster/health?pretty](http://localhost:9200/_cluster/health?pretty)

## Common setup

Install missing packages inside the `mage` container:

```bash
docker exec -it mage bash
pip install groq openai sentence-transformers
```

Also install these in [/mageai/magic/](../mageai/magic/) for the Mage AI app to use them.

For database configuration, make sure to add the following section in [io_config.yaml](../mageai/magic/io_config.yaml):

```yaml
dev:
  # PostgreSQL
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: banksa
  POSTGRES_SCHEMA: public # Optional
  POSTGRES_USER: root
  POSTGRES_PASSWORD: root
  POSTGRES_HOST: pg-database
  POSTGRES_PORT: 5432
```

## Other services

Other services used in this solution are:
1. **Groq**: as a free LLM source in case you don't have an OpenAI subscription. Useful for using the `llama3.1-70B` model.
2. **OpenAI**: as the LLM used to extract the content and generate categories for transactions when you are not giving feedback.

These services are used for RAG (Retrieval-Augmented Generation) on PDF content and getting transaction categories.
