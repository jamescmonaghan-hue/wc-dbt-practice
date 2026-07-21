-- A finished match should always have a final score.
-- This returns any rows that violate that — an empty result means the test passes.
select match_id
from {{ ref('stg_matches') }}
where status = 'FINISHED'
  and (home_score is null or away_score is null)