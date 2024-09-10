if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


import pandas as pd

import importlib

from magic.utils import helpers

def predict_category(row):
    if row['predict_category'] == True:
        description = row['description']
        row['predicted_category'] = helpers.get_json_from_description_oa(description)
        row['predict_category'] = False
    
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
    importlib.reload(helpers)
    
    # data = data.iloc[0:1]
    data = data.apply(predict_category, axis=1)

    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
