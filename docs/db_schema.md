# Database Setup Guide

As DB engine we are using **PostgreSQL** and for IDE **pgAdmin**.

**In pgAdmin**
1. Access pgAdmin in the browser at [http://localhost:8082](http://localhost:8082) 
    ```
    User: admin@admin.com
    Password: root
    ```
2. On the `Servers` node, right-click and select `Register` and set `Name`. In Connections, use the host `pg-database` and credentials from the previous step.
3. You should see the `banksa` database and can create tables under `Schemas/Tables`.

Then inside the database, execute all these object creation statements:

```sql
CREATE TABLE files (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  size FLOAT,
  file_text TEXT,
  generated_json JSONB,
  json_extracted BOOLEAN DEFAULT FALSE,
  transactions_extracted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE folders (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  file_id INTEGER,
  statement_date DATE,
  statement_year INTEGER,
  statement_month INTEGER,
  amount FLOAT,
  category TEXT,
  currency TEXT,
  date DATE,
  description TEXT,
  type TEXT,
  _statement_date DATE,
  _statement_year INTEGER,
  _statement_month INTEGER,
  _amount FLOAT,
  _category TEXT,
  _currency TEXT,
  _date DATE,
  _description TEXT,
  _type TEXT,
  predict_category BOOLEAN DEFAULT TRUE,
  predicted_category TEXT,
  confirmed_category BOOLEAN,
  suggested_category TEXT,  
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP,
  CONSTRAINT trans_fk1 FOREIGN KEY (file_id) REFERENCES files(id)
);

CREATE TABLE knowledge_base (
  id SERIAL PRIMARY KEY,
  description TEXT,
  category TEXT, 
  upvoted BOOLEAN,
  downvoted BOOLEAN,
  suggested_category TEXT,
  updated_transactions BOOLEAN DEFAULT FALSE,
  indexed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE OR REPLACE VIEW v_knowledge_base AS 
SELECT 
  a.id,
  a.description,
  CASE
    WHEN a.upvoted = TRUE THEN a.category
    WHEN a.downvoted = TRUE AND a.suggested_category IS NOT NULL THEN a.suggested_category
    ELSE a.category
  END AS category,
  a.indexed,
  a.created_at,
  a.updated_at
FROM knowledge_base a
WHERE a.upvoted = TRUE 
  OR (a.downvoted = TRUE AND a.suggested_category IS NOT NULL);

CREATE TABLE evaluations (
  id SERIAL PRIMARY KEY,
  concept TEXT,
  cosine_similarity_mean FLOAT, 
  cosine_similarity_min FLOAT, 
  cosine_similarity_max FLOAT, 
  hit_rate FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
