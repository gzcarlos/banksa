import psycopg2
from psycopg2 import sql
import pandas as pd
import os

def get_db_connection():
    return psycopg2.connect(
        dbname="banksa",
        user="root",
        password="root",
        host="localhost",
        port="5432"
    )

def add_folder_to_db(folder_path):
    # if not os.path.isdir(folder_path):
    #     return f"The folder '{folder_path}' does not exist on the system."
    cur = None
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the folder already exists in the database
        cur.execute("SELECT id FROM folders WHERE id = %s", (folder_path,))
        if cur.fetchone() is not None:
            return f"The folder '{folder_path}' is already in the database."

        # Insert the new folder
        cur.execute(
            sql.SQL("INSERT INTO folders (id) VALUES ({})").format(sql.Literal(folder_path))
        )
        conn.commit()
        return f"Folder '{folder_path}' has been added to the database."

    except Exception as e:
        return f"An error occurred: {str(e)}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def get_current_folder_from_db():
    cur = None
    conn = None
    id = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Check if the folder already exists in the database
        cur.execute("SELECT id FROM folders")
        results = cur.fetchall()
        for row in results:
            id = row[0]
        return id, f"There is a folder id already in database."

    except Exception as e:
        return None, f"An error occurred: {str(e)}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def update_folder_in_db(folder_path):
    # if not os.path.isdir(folder_path):
    #     return f"The folder '{folder_path}' does not exist on the system."
    cur = None
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Update existing folder
        cur.execute(
            sql.SQL("UPDATE folders set id = {}").format(sql.Literal(folder_path))
        )
        rows_updated = cur.rowcount
        conn.commit()
        return rows_updated, f"Folder '{folder_path}' has been updated in the database."

    except Exception as e:
        return 0, f"An error occurred: {str(e)}"

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def file_exists(file_name, file_size):
    cur = None
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            sql.SQL("SELECT 1 from files where name = {} and size = {}").format(sql.Literal(file_name), sql.Literal(file_size))
        )
        if cur.rowcount > 0:
            return True
        return False
    except Exception as e:
        print(f'Error on exsits: {str(e)}')
        return False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def insert_file(file_name, file_size, file_text):

    cur = None
    conn = None
    file_size = round(file_size, 2)
    exists = file_exists(file_name, file_size)
    if not exists:
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Insert new file
            cur.execute(
                sql.SQL("INSERT INTO files(name, size, file_text) values ( {}, {}, {} )").format(sql.Literal(file_name), sql.Literal(file_size), sql.Literal(file_text))
            )
            rows_inserted = cur.rowcount
            conn.commit()
            return rows_inserted, f"File '{file_name}' with has been inserted in the database."

        except Exception as e:
            return 0, f"An error occurred: {str(e)}"

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    else:
        return 0, f"File {file_name} with size of {file_size} KB has already been loaded"
    
def get_uploaded_files():
    cur = None
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = sql.SQL("""
            select 
              a.id
              , a.name as file_name
              , a.size as file_size
              , case 
                  when a.json_extracted then 'Yes'
                  else 'No'
                  end as content_processed
              , case 
                  when a.transactions_extracted then 'Yes'
                  else 'No'
                  end as transactions_extracted
              , count(b.id) n_transactions
            from files a
            left join transactions b
              on a.id = b.file_id
            group by a.id, a.name, a.size, a.json_extracted, a.transactions_extracted
            order by a.created_at desc 
            """)
        
        cur.execute(query)

        column_names = [desc[0] for desc in cur.description]
        results = cur.fetchall()

        df = pd.DataFrame(results, columns=column_names)
        return df, "Successfully retrieved file list from database."
    except Exception as e:
        print(str(e))
        return pd.DataFrame(), f"An error ocurred: {str(e)}"
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
def get_file_transactions(file_id):
    cur = None
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        query = sql.SQL("""
            select 
              a.id
              , a.statement_date
              , a.statement_year
              , a.statement_month
              , coalesce(a.date, a._date) as date -- same as ISNULL
              , a.description
              , coalesce(
                  a.suggested_category,
                  coalesce(
                      a.predicted_category, 
                      a.category
                  )
                ) as category
              , a.amount
              , a.currency
              , coalesce(a._type, a.type) as "type"
            from transactions a
            where a.file_id = {} 
            """).format(sql.Literal(file_id))
        
        cur.execute(query)

        column_names = [desc[0] for desc in cur.description]
        results = cur.fetchall()

        df = pd.DataFrame(results, columns=column_names)

        return df, "Successfully retrieved file list from database."
    except Exception as e:
        print(f"An error ocurred: {str(e)}")
        return pd.DataFrame(), f"An error ocurred: {str(e)}"
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
