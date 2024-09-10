-- Docs: https://docs.mage.ai/guides/sql-blocks
update transactions a
set predict_category = (select b.predict_category from {{ df_1 }} b where a.id = b.id)
  , predicted_category = (select b.predicted_category from {{ df_1 }} b where a.id = b.id)
  , updated_at = current_timestamp
where predict_category = true

update transactions a
set a.predict_category = b.precit_category
  , a.predicted_category = b.predicted_category
  , a.updated_at = current_timestamp
from {{ df_1 }} b
where a.precit_category = true
  and b.id = a.id