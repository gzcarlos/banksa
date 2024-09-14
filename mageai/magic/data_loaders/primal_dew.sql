-- Docs: https://docs.mage.ai/guides/sql-blocks
with hit_rate_vals as (
	select 
	  sum(case when downvoted = true then 1 else 0 end) as total_downvoted
	  , count(*) as total
	from public.knowledge_base
)
select a.id, a.description, a.category as initial_category, a.suggested_category, b.total_downvoted, b.total
from public.transactions a
	cross join  hit_rate_vals b
where a.confirmed_category = true