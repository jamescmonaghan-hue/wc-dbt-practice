with raw_matches as (
    select
        loaded_at,
        unnest(from_json(payload, '{"matches": "JSON[]"}').matches) as match
    from {{ source('raw', 'matches_raw') }}
)

select
    match->>'id'                                          as match_id,
    cast(match->>'utcDate' as timestamp)                   as match_date,
    match->>'status'                                       as status,
    cast(match->>'matchday' as integer)                    as matchday,
    match->>'stage'                                        as stage,
    match->>'group'                                        as group_name,

    match->'homeTeam'->>'name'                             as home_team,
    match->'homeTeam'->>'tla'                              as home_team_code,
    match->'awayTeam'->>'name'                             as away_team,
    match->'awayTeam'->>'tla'                              as away_team_code,

    match->'score'->>'winner'                              as winner_side,
    cast(match->'score'->'fullTime'->>'home' as integer)   as home_score,
    cast(match->'score'->'fullTime'->>'away' as integer)   as away_score,
    cast(match->'score'->'halfTime'->>'home' as integer)   as home_score_ht,
    cast(match->'score'->'halfTime'->>'away' as integer)   as away_score_ht,

    loaded_at
from raw_matches