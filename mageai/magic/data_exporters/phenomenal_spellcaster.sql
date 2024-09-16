-- Docs: https://docs.mage.ai/guides/sql-blocks
update files a
  , a.json_extracted = b.json_extracted
  , a.generated_json = b.generated_json
  , a.updated_at = current_timestamp
from {{ df_1 }} b
where a.id = b.id
