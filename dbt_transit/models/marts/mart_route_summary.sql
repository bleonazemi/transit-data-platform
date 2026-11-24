with schedule as (
    select * from {{ ref('fct_stop_schedule') }}
),

trip_metrics as (
    select
        route_id,
        route_short_name,
        route_long_name,
        route_mode,
        direction_name,
        trip_id,
        count(*) as stops_in_trips,
        (
            max(coalesce(departure_seconds_since_midnight, arrival_seconds_since_midnight)) - min(coalesce(arrival_seconds_since_midnight, departure_seconds_since_midnight))
        ) / 60.0 as trip_duration_minutes
    from schedule 
    group by
        route_id,
        route_short_name,
        route_long_name,
        route_mode,
        direction_name,
        trip_id
),

route_summary as (
    select 
        route_id,
        route_short_name,
        route_long_name,
        route_mode,
        direction_name,
        count(trip_id) as total_scheduled_trips,
        sum(stops_in_trips) as total_stop_events,
        round(avg(nullif(trip_duration_minutes, 0)), 1) as avg_trip_duration_minutes,
        round(avg(stops_in_trips), 1) as avg_stops_per_trip
    from trip_metrics
    group by
        route_id,
        route_short_name,
        route_long_name,
        route_mode,
        direction_name
)

select * from route_summary