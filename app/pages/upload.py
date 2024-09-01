import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash_uploader as du
import os

from pypdf import PdfReader

from model.connections import (
    insert_file
)

UPLOAD_FOLDER_ROOT = "uploads"

layout = html.Div(
    children=[
        dcc.Location(id='url', refresh=False),
        dbc.Container(
            children=[
                html.H1("File Upload", className="my-4"),
                html.Div(
                    children = [
                        du.Upload(id='uploader', max_file_size=20000)
                    ]
                    , className="mb-3"
                ),
                html.Div(id="upload-output-message"),
            ],
            id='upload-container'
        )
    ]
)


def get_file_path(filename):
    for root, dirs, files in os.walk(UPLOAD_FOLDER_ROOT):
        if filename in files:
            return os.path.join(root, filename)
    return None

def process_file(file_path, file_name, file_size):
    file = os.path.join(file_path, file_name)
    page_number = 1
    try:
        reader = PdfReader(file)
        file_text = ''
        for page in reader.pages:
            text = page.extract_text()
            file_text += text
            page_number += 1
    except Exception as e:
        err = f'Error reading PDF: {str(e)}'
        print(err)
        return 0, err

    return insert_file(file_name, file_size, file_text)
    


@callback( 
    Output("upload-output-message", "children"),
    Input('uploader', 'isCompleted'),
    State('uploader', 'fileNames'),
    prevent_initial_call=True
)
def handle_add_folder(is_completed, filenames):
    if is_completed and filenames is not None:
        file_path = get_file_path(filenames[0])
        if file_path:
            file_size = os.path.getsize(file_path) / 1024
            # delete the file
            try:
                # Remove the parent directory if it's empty
                parent_dir = os.path.dirname(file_path)
                print(f'{parent_dir=} {os.listdir(parent_dir)=}')
                for f in os.listdir(parent_dir):
                    # extract text from file and save it in DB
                    rows, message = process_file(parent_dir, f, file_size)
                    if rows < 1:
                        return message
                    os.remove(os.path.join(parent_dir, f))
                # finally delete de UUID folder generated
                os.rmdir(parent_dir)
            except Exception as e:
                return f"Error deleting file: {str(e)}"
            output_text = f"File uploaded: {filenames[0]}, Size: {file_size:.2f} KB"
            print(output_text)
            return output_text



# Register the page
dash.register_page(__name__, path='/upload', layout=layout, name='Upload')