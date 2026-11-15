with source as (
    select * from {{ source('gtfs_raw', 'stop_times') }}
),

renamed as (
    select
        trip_id,
        stop_id,
        stop_sequence::integer as stop_sequence,
        trim(arrival_time) as arrival_time,
        trim(departure_time) as departure_time,
        (
            split_part(trim(arrival_time), ':', 1)::integer * 3600
            + split_part(trim(arrival_time), ':', 2)::integer * 60
            + split_part(trim(arrival_time), ':', 3)::integer
        ) as arrival_seconds_since_midnight,
        (
            split_part(trim(departure_time), ':', 1)::integer * 3600
            + split_part(trim(departure_time), ':', 2)::integer * 60
            + split_part(trim(departure_time), ':', 3)::integer
        ) as departure_seconds_since_midnight,
        coalesce(pickup_type, 0) as pickup_type,
        shape_dist_traveled
    from source
)

select * from renamed