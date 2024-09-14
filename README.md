# Bank Statement Analyser (banksa)
 
An app that extracts your transactions using LLM's and categorize them to let you know how your expenses are going.


## The problem

You probably have a PDF for each month of your Credit Card Statement or Account statement.
Those transactions may not be loaded and centralized for every bank were you have on of those products.

And you would like to have a centrilized solution that takes all the transactiones, "categorize" them in order to show you all in different ways
1. Simple list of all transactions
2. Some dashboards with all the categories and which is the category you use the most weighted by the sum of amounts. Aldo the category where you consume the least of your credit or expenses.

## The Solution

With this app you would
1. Upload the PDF and the content's text will be extracted
2. An LLM model would be used to extract the transactions from the PDF text's.
3. For all new descriptions not previously known for the app, you could give feedback to indicate if the category suits the description of the transaction. You would give only feedback once each new transaction description.
4. The app workers (pipelines in Mage) will also try to generate the right category after the transactions are extraced using as reference your own feedback

## Setup

> This setup has a been used in a Github Codespaces with 4-cores machine.

For this app some other apps are going to be used
1. **PostgresSQL**: as main database.
2. **MageAI**: as workers orchestrator (pipelines).
3. **ElasticSearch**: as vector database to store descriptions and categories you give feedback.
4. **PgAdmin**: as Database IDE.

Other services used in this solution are:
1. Groq: as free LLM source in case you don't have a OpenAI subscription. Usefull for using `llama3.1-70B` model
2. OpenAI: as LLM used to extract the content and generate categories for transactions when you are note giving feedback.

This services are used for RAG on PDF content and getting transactions categories.

From now on you can use the `Docker Compose guide` for installing or the `Manual setup`. After that runs the `Common setup`. And then continue with the `database schema` section

### Docker Compose guide

Execute this 2 commands to complete the creation of the 
```bash
# create all the images and pull some others needeed
docker compose build
# run all the images
docker compose up -d
```

### Manual setup

Create a network for docker
```bash
docker network create banksa-network
```


### Mage AI

Create docker container for MageAI using the folder `/mageai` as source archive for all the files
```bash
docker run -d \
  --name mage \
  -p 6789:6789 \
  -v $(pwd)/mageai:/home/src \
  --network=banksa-network \
  mageai/mageai mage start magic
```

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

### Elasticsearch

Install with this command
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

Check status on [http://localhost:9200/_cluster/health?pretty](http://localhost:9200/_cluster/health?pretty)


### Common setup

Instal missing packages inside the `mage` container

```bash
docker exec -it mage bash
pip install groq openai sentence-transformers
```

### Database schema

**In pgadmin**
1. Access to pdadmin on the browser [http://localhost:8082](http://localhost:8082)
2. On the `Servers` right click and select `Register` and set `Name`. In Connections use the host `pg-database` and credentials from the previous commands
3. You should see `banksa` database and can create a table under `schemas/tables`

Then inside the database, execute all this objects creation
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
create or replace view v_knowledge_base as 
SELECT a.id
  , a.description
  , CASE
      WHEN a.upvoted = true THEN a.category
      WHEN a.downvoted = true AND a.suggested_category IS NOT NULL THEN a.suggested_category
      ELSE a.category
    END AS category
  , a.indexed
  , a.created_at
  , a.updated_at
FROM knowledge_base a
WHERE a.upvoted = true 
  OR (
    a.downvoted = true 
    AND a.suggested_category IS NOT NULL
  )
;
create table evaluations(
	id serial primary key,
	concept text,
	cosine_similarity_mean float, 
	cosine_similarity_min float, 
	cosine_similarity_max float, 
	hit_rate float,
	created_at timestamp default current_timestamp
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


## The operations

This app consists in

### Upload
1. Letting the user upload PDF files. The files are supposed to be bank statement files containing transactions
    1.  Each file text is extracted and stored in the database.
    2. Every file uploaded can only be loaded into the system once. The key fields to identify its uniqueness is the `file_name` and `file_size`.
2. After background process #1, The user can also see `transactions` from each file.
3. And also can see some transactions descriptions to give `feedback` if there are any.
    1. In order to give `feedback` the user can mark `Yes` or `No` if the first category (guessed by the LLM on extraction of `json` from the file text)
    2. When answered `Yes` the transactions with the same descriptions gets updated.
    3. When `No` the user can give a suggestion on `category` and that `category` will be used in all exisiting transactions with the same description.
    4. The user can only give one feedback on each transaction description.
    5. And feedback made on each description would be considered as `knowledge base` for the time when the app would need to predict the category of not answered transactions description. See process #4.



### Background

All this processes are made in a Mage Pipeline.

**1. get_files_missing_json**
This process gets the files with no `json` data extracted (the `json` data contains the `transactions` and the main data from the statement like `date`)

Also this transactions unique descriptions are stored in the knowledge data base for further feedback from the user

**2. index_knowledge_base** Every 10 mins the this process will look for every feedback made by the user and not stored in the vectorDB (ElasticSearch)

**3. extract_file_transactions** Every 10 mins this process will look for the files which transactions are not extracted and saved to the database. 

**4. complete_transactions_categories** This process runs every 10 mins and try to predict the category of every not confirmed transaction's category using LLM and the `knowledge_base` created by the user's feedback.