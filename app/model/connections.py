import psycopg2
from psycopg2 import sql
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