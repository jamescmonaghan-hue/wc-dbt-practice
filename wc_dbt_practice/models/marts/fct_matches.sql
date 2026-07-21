{{ config(materialized='table') }}

select
    match_id,
    match_date,
    matchday,
    stage,
    group_name,
    home_team,
    home_team_code,
    away_team,
    away_team_code,
    status,
    home_score,
    away_score,
    home_score_ht,
    away_score_ht,
    winner_side
from {{ ref('stg_matches') }}