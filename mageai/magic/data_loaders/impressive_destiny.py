if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


import pandas as pd

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    got_result, df = args[0]

    result_df = pd.DataFrame()
    if got_result:

        transactions_list = []

        for index, row in df.iterrows():
            file_id = row['id']
            generated_json = row['generated_json']
            
            bank_statement = generated_json['bank_statement']
            statement_date = bank_statement['date']
            statement_year = int(bank_statement['year'])
            statement_month = int(bank_statement['month'])

            transactions = bank_statement['transactions']

            for t in transactions:
                transaction_obj = {}
                transaction_obj['file_id'] = file_id
                transaction_obj['statement_date'] = statement_date
                transaction_obj['statement_year'] = statement_year
                transaction_obj['statement_month'] = statement_month
                transaction_obj.update(t)
                transactions_list.append(transaction_obj)
        
        # prepare final df
        result_df = pd.concat([result_df, pd.DataFrame(transactions_list)], ignore_index=True)



    return result_df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'

