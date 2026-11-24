with stop_times as (
    select * from {{ ref('stg_stop_times')}}
),
trips as (
    select * from {{ ref('stg_trips')}}
),
routes as (
    select * from {{ ref('stg_routes')}}
),
stops as (
    select * from {{ ref('stg_stops')}}
),
joined as (
    select 
    -- Keys and sequence --
    st.trip_id,
    st.stop_sequence,
    t.route_id,
    st.stop_id,
    t.service_id,

    -- Route attributes --
    r.route_short_name,
    r.route_long_name,
    r.route_mode,
    r.route_color,

    -- Trip attributes --
    t.direction_id,
    t.direction_name,
    t.is_wheelchair_accessible,

    -- Stop attributes --
    s.stop_name,
    s.latitude,
    s.longitude,

    -- Schedule and dwell times --
    st.arrival_time,
    st.departure_time,
    st.arrival_seconds_since_midnight,
        st.departure_seconds_since_midnight,
        (st.departure_seconds_since_midnight - st.arrival_seconds_since_midnight) as dwell_seconds,
        st.shape_dist_traveled
    from stop_times as st
    inner join trips as t
        on st.trip_id = t.trip_id
    inner join routes as r
        on t.route_id = r.route_id
    inner join stops as s
        on st.stop_id = s.stop_id
)

select * from joined