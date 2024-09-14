if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import pandas as pd

from sentence_transformers import SentenceTransformer

from magic.utils import helpers

model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

def fill_similarity(row):
    initial_category = row['initial_category']
    suggested_category = row['suggested_category']
    row['cosine'] = helpers.compute_similarity_mod(initial_category, suggested_category, model)
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
    
    data = data.apply(fill_similarity, axis=1)
    total_downvoted = int(data['total_downvoted'].iloc[0])
    total = int(data['total'].iloc[0])
    hit_rate = total_downvoted / total
    evaluations = [
        {
            "concept": "initial",
            "cosine_similarity_mean": data['cosine'].mean(),
            "cosine_similarity_min": data['cosine'].min(),
            "cosine_similarity_max": data['cosine'].max(),
            "hit_rate": hit_rate

        }
    ]
    
    df_eval = pd.DataFrame(evaluations)


    return df_eval


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
