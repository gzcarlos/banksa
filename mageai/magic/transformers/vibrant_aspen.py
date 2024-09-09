if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from sentence_transformers import SentenceTransformer
import pandas as pd
from elasticsearch import Elasticsearch

model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(model_name)

def add_row_embeddings(row):
    row['description_vector'] = embedding_model.encode( row['description'])
    return row    


@transformer
def transform(data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    data = data[['id', 'description', 'category']]

    data = data.apply(add_row_embeddings, axis=1)
    cats = data.to_dict('records')

    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
