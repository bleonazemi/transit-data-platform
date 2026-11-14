with source as (
    select * from {{ source('gtfs_raw', 'stops') }}
),

renamed  as (
    select 
        stop_id,
        stop_code,
        trim(stop_name) as stop_name,
        stop_lat as latitude,
        stop_lon as longitude,
        coalesce(location_type, 0) as location_type,
        parent_station
    from source
)

select * from renamed