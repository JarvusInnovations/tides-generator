#!/usr/bin/env python3
import argparse
import csv
import datetime
import math
import random
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

def load_gtfs_data(gtfs_path: str, route_ids: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and filter relevant GTFS data for the specified routes."""
    routes_df = pd.read_csv(f"{gtfs_path}/routes.txt")
    trips_df = pd.read_csv(f"{gtfs_path}/trips.txt")
    stops_df = pd.read_csv(f"{gtfs_path}/stops.txt")
    stop_times_df = pd.read_csv(f"{gtfs_path}/stop_times.txt")

    # Filter for specified routes
    filtered_routes = routes_df[routes_df['route_id'].isin(route_ids)]
    filtered_trips = trips_df[trips_df['route_id'].isin(filtered_routes['route_id'])]
    filtered_stop_times = stop_times_df[stop_times_df['trip_id'].isin(filtered_trips['trip_id'])]

    return filtered_routes, filtered_trips, stops_df, filtered_stop_times

def parse_gtfs_time(time_str: str) -> datetime.time:
    """Parse GTFS time string which may include hours > 24."""
    time_str = time_str.strip()
    hours, minutes, seconds = map(int, time_str.split(':'))
    if hours >= 24:
        hours = hours % 24
    return datetime.time(hours, minutes, seconds)

def interpolate_position(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float,
    progress: float
) -> Tuple[float, float, float]:
    """Interpolate position between two points and calculate heading."""
    lat = start_lat + (end_lat - start_lat) * progress
    lon = start_lon + (end_lon - start_lon) * progress

    # Calculate heading (0-360 degrees, where 0 is North)
    dx = end_lon - start_lon
    dy = end_lat - start_lat
    heading = math.degrees(math.atan2(dx, dy)) % 360

    return lat, lon, heading

def generate_vehicle_locations(
    gtfs_path: str,
    route_ids: List[str],
    start_date: datetime.date,
    end_date: datetime.date,
    output_file: str
):
    """Generate synthetic vehicle location data based on GTFS data."""

    # Load GTFS data
    routes_df, trips_df, stops_df, stop_times_df = load_gtfs_data(gtfs_path, route_ids)

    # Generate synthetic vehicle IDs (one per route)
    vehicles = {route_id: f"VEH_{i:03d}" for i, route_id in enumerate(route_ids)}

    # Setup output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Write header manually to ensure proper formatting
        headers = [
            'location_ping_id', 'service_date', 'event_timestamp',
            'trip_id_performed', 'trip_id_scheduled', 'trip_stop_sequence',
            'scheduled_stop_sequence', 'vehicle_id', 'device_id', 'pattern_id',
            'stop_id', 'current_status', 'latitude', 'longitude',
            'gps_quality', 'heading', 'speed', 'odometer',
            'schedule_deviation', 'headway_deviation', 'trip_type',
            'schedule_relationship'
        ]
        writer = csv.DictWriter(f, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        # Generate data for each day in range
        current_date = start_date
        while current_date <= end_date:
            # For each route
            for route_id in route_ids:
                route_trips = trips_df[trips_df['route_id'] == route_id]
                vehicle_id = vehicles[route_id]

                # For each trip
                for _, trip in route_trips.iterrows():
                    trip_stops = stop_times_df[stop_times_df['trip_id'] == trip['trip_id']].sort_values('stop_sequence')

                    # Generate locations between each pair of stops
                    for i in range(len(trip_stops) - 1):
                        current_stop = trip_stops.iloc[i]
                        next_stop = trip_stops.iloc[i + 1]

                        current_stop_data = stops_df[stops_df['stop_id'] == current_stop['stop_id']].iloc[0]
                        next_stop_data = stops_df[stops_df['stop_id'] == next_stop['stop_id']].iloc[0]

                        # Generate positions between stops
                        num_points = random.randint(3, 8)  # Random number of points between stops
                        for j in range(num_points):
                            progress = j / (num_points - 1)

                            # Calculate timestamp
                            departure_time = parse_gtfs_time(current_stop['departure_time'])
                            arrival_time = parse_gtfs_time(next_stop['arrival_time'])
                            event_time = datetime.datetime.combine(current_date, departure_time) + \
                                       (datetime.datetime.combine(current_date, arrival_time) -
                                        datetime.datetime.combine(current_date, departure_time)) * progress

                            # Interpolate position
                            lat, lon, heading = interpolate_position(
                                float(current_stop_data['stop_lat']),
                                float(current_stop_data['stop_lon']),
                                float(next_stop_data['stop_lat']),
                                float(next_stop_data['stop_lon']),
                                progress
                            )

                            # Generate row data
                            row = {
                                'location_ping_id': str(uuid.uuid4()),
                                'service_date': current_date.strftime('%Y-%m-%d'),
                                'event_timestamp': event_time.strftime('%Y-%m-%dT%H:%M:%S'),
                                'trip_id_performed': f"{trip['trip_id']}_performed",
                                'trip_id_scheduled': trip['trip_id'],
                                'trip_stop_sequence': i + 1,
                                'scheduled_stop_sequence': current_stop['stop_sequence'],
                                'vehicle_id': vehicle_id,
                                'device_id': f"DEV_{vehicle_id}",
                                'pattern_id': f"PAT_{route_id}",
                                'stop_id': current_stop['stop_id'] if progress < 0.1 else next_stop['stop_id'],
                                'current_status': 'Stopped at' if progress < 0.1 else 'In transit to',
                                'latitude': lat,
                                'longitude': lon,
                                'gps_quality': random.choice(['Excellent', 'Good', 'Good', 'Good']),
                                'heading': heading,
                                'speed': 0 if progress < 0.1 else random.uniform(5, 15),
                                'odometer': random.uniform(1000, 100000),
                                'schedule_deviation': random.randint(-300, 300),
                                'headway_deviation': random.randint(-180, 180),
                                'trip_type': 'In service',
                                'schedule_relationship': 'Scheduled'
                            }
                            writer.writerow(row)

            current_date += datetime.timedelta(days=1)

def main():
    parser = argparse.ArgumentParser(description='Generate synthetic TIDES vehicle location data from GTFS')
    parser.add_argument('gtfs_path', help='Path to GTFS directory')
    parser.add_argument('--routes', required=True, help='Comma-separated list of route IDs')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', default='vehicle_locations.csv', help='Output file path')

    args = parser.parse_args()

    route_ids = [r.strip() for r in args.routes.split(',')]
    start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()

    generate_vehicle_locations(
        args.gtfs_path,
        route_ids,
        start_date,
        end_date,
        args.output
    )

if __name__ == '__main__':
    main()
