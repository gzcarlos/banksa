-- Docs: https://docs.mage.ai/guides/sql-blocks
insert into evaluations(concept, cosine_similarity_mean, cosine_similarity_min, cosine_similarity_max, hit_rate)
select * from {{ df_1 }}