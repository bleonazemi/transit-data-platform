with source as (
    select * from {{ source('gtfs_raw', 'routes') }}
),

renamed  as (
    select 
        route_id,
        trim(route_short_name) as route_short_name,
        trim(route_long_name) as route_long_name,
        route_type,
        case 
            when route_type in (0, 1) then 'Rail'
            when route_type = 3 then 'Bus'
            else 'Other'
        end as route_mode,
        route_url,
        upper(trim(route_color)) as route_color,
        upper(trim(route_text_color)) as route_text_color,
    from source
)

select * from renamed