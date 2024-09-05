-- Docs: https://docs.mage.ai/guides/sql-blocks
insert into knowledge_base (description, category) 
(
  select distinct trim(description) as description, trim(category) as category
  from transactions a
  where not exists (select 1 from knowledge_base x where trim(a.description) = x.description)
)