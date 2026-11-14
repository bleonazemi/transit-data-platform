with source as (
    select * from {{ source('gtfs_raw', 'trips') }}
),

renamed as (
    select
        trip_id,
        route_id,
        service_id,
        coalesce(direction_id, 0) as direction_id,
        trim(direction) as direction_name,
        coalesce(wheelchair_accessible, 0) = 1 as is_wheelchair_accessible,
        block_id,
        shape_id,
        schd_trip_id
    from source
)

select * from renamed