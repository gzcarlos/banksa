# Bank Statement Analyser (banksa)
 
An app that extracts your transactions using LLM's and categorize them to let you know how your expenses are going.


This App was made initialy as the project for [LLM Zoomcamp 2024](https://github.com/DataTalksClub/llm-zoomcamp) of 2024 from [DataTalks.Club](https://datatalks.club/) to whom do I owe my thanks.

## Content

1. The problem
2. The Solution
3. Setup
    1. Docker compose guide
    2. Manual docker setup
        1. Mage AI setup
        2. PostgreSQL setup
        3. Elasticsearch setup
    3. Common setup
    4. Database schema
4. The Operations
    1. Upload
    2. Feedback
    3. Transactions
    4. Dashboards
    5. Evaluations
    6. Backgroun (workflows)


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

### Manual docker setup

Create a network for docker
```bash
docker network create banksa-network
```


### Mage AI setup

Create docker container for MageAI using the folder `/mageai` as source archive for all the files
```bash
docker run -d \
  --name mage \
  -p 6789:6789 \
  -v $(pwd)/mageai:/home/src \
  --network=banksa-network \
  mageai/mageai mage start magic
```

Make sure to have a `.env` file (may use the template from [sample.env](/sample.env) file) and complete this 2 variables

```bash
GROQ_API_KEY=your_api_key_for_groq.console
OPENAI_API_KEY=your_api_key_for_openai.platform
```
And also copy that file in [/mageai/magic/](/mageai/magic/) for Mage AI app to use them.

For database configuration make sure to add in [io_config.yaml](/mageai/magic/io_config.yaml) the following sections

```bash
dev:
  # PostgresSQL
  POSTGRES_CONNECT_TIMEOUT: 10
  POSTGRES_DBNAME: banksa
  POSTGRES_SCHEMA: public # Optional
  POSTGRES_USER: root
  POSTGRES_PASSWORD: root
  POSTGRES_HOST: pg-database
  POSTGRES_PORT: 5432
```

### PostgreSQL setup

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

### Elasticsearch setup

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



## The operations

This app consists in

### Upload
1. Letting the user upload PDF files. The files are supposed to be bank statement files containing transactions
    1.  Each file text is extracted and stored in the database.
    2. Every file uploaded can only be loaded into the system once. The key fields to identify its uniqueness is the `file_name` and `file_size`.
    2. After background process #1, The user can also see `transactions` from each file.
    3. And also can see some transactions descriptions to give `feedback` if there are any.


### Feedback

  1. In order to give `feedback` the user can mark `Yes` or `No` if the first category (guessed by the LLM on extraction of `json` from the file text)
  2. When answered `Yes` the transactions with the same descriptions gets updated.
  3. When `No` the user can give a suggestion on `category` and that `category` will be used in all exisiting transactions with the same description.
  4. The user can only give one feedback on each transaction description.
  5. And feedback made on each description would be considered as `knowledge base` for the time when the app would need to predict the category of not answered transactions description. See process #4.

### Transactions

  1. The user will have available a section in the `App` for transactions where he would see every transaction extracted from each file (filtered by file)
  2. Each transaction have:
      1. **Date**: on which was made the transaction 
      2. **Description**: The whole description of the commerce or motive of the transaction
      3. **Category**: The initial category predicted from the transactions description, or the predicted category if no feedback was made (using the LLM and the reference from the knowledge base created using feedbacks) or finally the suggested category from the feedback made if the initial was not correct.
      4. **Amount**: as self described
      5. **Currency**: used in the transaction
      6. **Type**: Debit or credit, (all payments are treated as `Credit` and all other transactions like `Debit`)


### Dashboards

In the all there are 2 types of graphs page based on the role of the user

  1. **User**: Can see all data related to the details of the transactions grouped by `amount` and  and `quantity`
  2. **Admin**: (_more like a health checker for the app_) Can see 

      1. All the the feedbacks distribution, how many descriptions were `downvoted` and hoy many were `upvoted`.
      2. The result of the `consine similarity` evaluation over time.
      3. The result of the `hit-rate` evaluation over time.

### Evaluations

For the purpose of this solution tried to evaluate the texts from `description` and `category` combined and separately, and found the result is better when the `description` is evaluated so, as can be appretiated on the notebook [evaluate_vector_search_fields.ipynb](/notebooks/evaluate_vector_search_fields.ipynb)

Used 2 metrics for evaluation the results between the knowledge base used in the VectorDB (Elasticsearch) and the results:
1. **Hit-rate**: how relevant is the each text when searched with itself.
2. **MRR (Mean Reciprocal Rank)**: How is each text is related with each other text.

Used the data from the knowledge base and tried each metrinc on every field combination. Found the result is optimal when `description` is used, so used it in the evaluation workflow.

### Background (workflows)

All this processes are made in a Mage Pipeline.

  1. **fill_files_missing_json** This process gets the files with no `json` data extracted (the `json` data contains the `transactions` and the main data from the statement like `date`).

      Also this transactions unique descriptions are stored in the knowledge data base for further feedback from the user

  2. **index_knowledge_base** Every 10 mins the this process will look for every feedback made by the user and not stored in the vectorDB (ElasticSearch) to save them in Elasticsearch

  3. **extract_file_transactions** Every 10 mins this process will look for the files which transactions are not extracted and saved to the database. 

  4. **complete_transactions_categories** This process runs every 10 mins and try to predict the category of every not confirmed transaction's category using LLM and the `knowledge_base` created by the user's feedback.

  5. **get_evaluations** execute 2 evaluations of the efectiveness from the prediction and the feedback. The first is a _cosine similarity_ between sugested categories (on feedback) and the initial category made when extracting the transactions. Other evaluation used is _hit rate_ for determine how much of all transactions had an incorrect category, determined by de down votes on feedback results. For more information look at the `Evaluations` in `The Operations` section

## LLM's used

LLM's _(Large Language Models)_ are a core utility used in this solution. 

Mainly they are used in:
1. Transactions JSON generated from file text
2. To predict a category passing as reference the top 2 results from the knowledge base (VectorDB - Elasticsearch)

Tried to use some models offered freely from providers like [Groq Console](https://console.groq.com/playground) which offers a `llama-3.1-70b-versatile` available, but the results for the transactions list from each file text do not provided a constant `JSON` text to extract.

So tried another model used with minumum cost like [OpenAI](https://platform.openai.com/)'s Platform page, selecting `gpt-4o-mini`.

All implementations of this model are are defined in [helpers.py](/mageai/magic/utils/helpers.py) file.