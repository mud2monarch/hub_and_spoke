Schema for rides parquet:
```
    'ride_id': String,
    'rideable_type': Categorical,
    'started_at': Datetime(time_unit='ms', time_zone=None),
    'ended_at': Datetime(time_unit='ms', time_zone=None),
    'start_station_name': String,
    'start_station_id': String,
    'end_station_name': String,
    'end_station_id': String,
    'start_lat': Float64,
    'start_lng': Float64,
    'end_lat': Float64,
    'end_lng': Float64,
    'member_casual': Categorical
```