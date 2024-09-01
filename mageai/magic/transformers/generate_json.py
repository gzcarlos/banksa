from magic import utils

import importlib


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test



@transformer
def transform(data, *args, **kwargs):
    
    importlib.reload(utils)

    jsons_list = []
    extracted_list = []
    for index, row in data.iterrows():
        generated_json = utils.get_json_from_text([row['file_text']])
        extracted = True
        jsons_list.append(generated_json)
        extracted_list.append(extracted)

    data['generated_json'] = jsons_list
    data['text_extracted'] = extracted_list

    return data


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'
