from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from pandas import DataFrame
from os import path

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter


@data_exporter
def export_data_to_postgres(df: DataFrame, **kwargs) -> None:
    """
    Template for exporting data to a PostgreSQL database.
    Specify your configuration settings in 'io_config.yaml'.

    Docs: https://docs.mage.ai/design/data-loading#postgresql
    """
    schema_name = 'public'  # Specify the name of the schema to export data to
    table_name = 'transactions'  # Specify the name of the table to export data to
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'dev'

    with Postgres.with_config(ConfigFileLoader(config_path, config_profile)) as loader:
        # loader.export(
        #     df,
        #     schema_name,
        #     table_name,
        #     index=False,  # Specifies whether to include index in exported table
        #     if_exists='replace',  # Specify resolution policy if table name already exists
        # )
        for index, row in df.iterrows():
            update_query = f"""
              update transactions a
              set predict_category = {row['predict_category']}
                , predicted_category = '{row['predicted_category']}'
                , updated_at = current_timestamp
              where predict_category = true 
                and id = {row['id']}
            """

            loader.execute(update_query)
        
        loader.commit()
