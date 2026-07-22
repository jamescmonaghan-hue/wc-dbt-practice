with raw_standings as (
    select
        loaded_at,
        -- Cast the JSON array directly to a DuckDB LIST, then unnest it —
        -- one row per group
        unnest((payload->'standings')::JSON[]) as grp
    from {{ source('raw', 'standings_raw') }}
),

group_rows as (
    select
        loaded_at,
        grp->>'group' as group_name,

        -- Same cast-then-unnest pattern for the nested "table" array —
        -- one row per team within this group
        unnest((grp->'table')::JSON[]) as row
    from raw_standings
)

select
    group_name,
    cast(row->>'position' as integer)        as position,
    row->'team'->>'name'                      as team_name,
    row->'team'->>'tla'                       as team_code,
    cast(row->>'playedGames' as integer)      as played_games,
    cast(row->>'won' as integer)              as won,
    cast(row->>'draw' as integer)             as draw,
    cast(row->>'lost' as integer)             as lost,
    cast(row->>'points' as integer)           as points,
    cast(row->>'goalsFor' as integer)         as goals_for,
    cast(row->>'goalsAgainst' as integer)     as goals_against,
    cast(row->>'goalDifference' as integer)   as goal_difference,
    loaded_at
from group_rows