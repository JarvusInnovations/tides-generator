# tides-generator

Tools for generating synthetic TIDES-compliant data files from GTFS inputs.

## Vehicle Locations Generator

The `generate_vehicle_locations.py` script creates synthetic vehicle location data that follows the [TIDES vehicle_locations schema](https://github.com/MobilityData/TIDES/blob/main/spec/vehicle_locations.schema.json).

### Prerequisites

- Python 3.x
- pandas library (`pip install pandas`)
- GTFS data files (routes.txt, trips.txt, stops.txt, stop_times.txt)

### Installation

```bash
git clone https://github.com/your-username/tides-generator.git
cd tides-generator
pip install pandas
```

### Usage

```bash
python3 generate_vehicle_locations.py <gtfs_path> --routes <route_ids> --start-date <start_date> --end-date <end_date> [--output <output_file>]
```

Arguments:

- `gtfs_path`: Path to directory containing GTFS files
- `--routes`: Comma-separated list of route IDs to generate data for
- `--start-date`: Start date in YYYY-MM-DD format
- `--end-date`: End date in YYYY-MM-DD format
- `--output`: Output file path (default: vehicle_locations.csv)

Example:

```bash
# Generate one day of data for route 1
python3 generate_vehicle_locations.py septa-gtfs-bus --routes 1 --start-date 2024-01-01 --end-date 2024-01-01

# Generate a month of data for multiple routes
python3 generate_vehicle_locations.py septa-gtfs-bus --routes 1,2,3 --start-date 2024-01-01 --end-date 2024-01-31 --output january_locations.csv
```

### Output Format

The script generates a CSV file following the TIDES vehicle_locations schema with these fields:

- location_ping_id: Unique identifier for each location event
- service_date: Date of service
- event_timestamp: Timestamp of the location event
- trip_id_performed: ID of the performed trip
- trip_id_scheduled: ID of the scheduled trip
- trip_stop_sequence: Order of stops within the trip
- scheduled_stop_sequence: Scheduled order of stops
- vehicle_id: Vehicle identifier
- device_id: Device identifier
- pattern_id: Route pattern identifier
- stop_id: Current or next stop ID
- current_status: Vehicle status (Stopped at/In transit to)
- latitude: Vehicle latitude
- longitude: Vehicle longitude
- gps_quality: GPS signal quality
- heading: Vehicle heading in degrees
- speed: Vehicle speed in meters per second
- odometer: Vehicle odometer reading
- schedule_deviation: Schedule adherence in seconds
- headway_deviation: Headway adherence in seconds
- trip_type: Type of trip (In service/Deadhead/etc.)
- schedule_relationship: Stop status (Scheduled/Skipped/etc.)

The generated data includes realistic vehicle movements interpolated between stops, with appropriate status changes, speed variations, and schedule deviations.

## Validation

The `validate_vehicle_locations.py` script validates generated files against the TIDES schema using the frictionless data toolkit.

### Prerequisites

- frictionless library (`pip install frictionless`)

### Usage

```bash
python3 validate_vehicle_locations.py <vehicle_locations.csv>
```

Example:
```bash
# Validate a generated file
python3 validate_vehicle_locations.py test_vehicle_locations.csv
```

The validator will check that:
- All required fields are present
- Field values match their specified types
- Values are within allowed ranges
- Enumerated fields contain valid values
- Foreign key references are valid

If validation fails, the script will output detailed error messages indicating which rows and fields have issues.
