from mage_ai.orchestration.run_status_checker import check_status

from mage_ai.settings.repo import get_repo_path
from mage_ai.io.config import ConfigFileLoader
from mage_ai.io.postgres import Postgres
from os import path

from magic import utils

if 'sensor' not in globals():
    from mage_ai.data_preparation.decorators import sensor


@sensor
def check_condition(*args, **kwargs) -> bool:
    config_path = path.join(get_repo_path(), 'io_config.yaml')
    config_profile = 'dev'

    query = 'select name, size from files where not extracted '  # Specify your SQL query here

    with Postgres.with_config(
            ConfigFileLoader(config_path, config_profile)) as loader:
        df = loader.load(query)

        # if no rows are returned
        if df.empty and df.shape[0] == 0:
            return False
        

    return True
