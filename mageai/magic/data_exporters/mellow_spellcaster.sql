-- Docs: https://docs.mage.ai/guides/sql-blocks
update knowledge_base
set indexed = true
  , updated_at = current_timestamp
where id in (select id from {{ df_1 }} where indexed = true)