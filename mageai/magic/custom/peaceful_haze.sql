-- Docs: https://docs.mage.ai/guides/sql-blocks
update files
set transactions_extracted = True 
where id in (select distinct file_id from {{ df_1 }} union all select 0)