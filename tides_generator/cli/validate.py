#!/usr/bin/env python3
import sys
from frictionless import Resource, Schema

def validate_vehicle_locations(file_path: str) -> bool:
    """
    Validate a vehicle_locations.csv file against the TIDES schema.
    Returns True if validation passes, False otherwise.
    """
    # Load the TIDES schema
    schema = Schema('TIDES/spec/vehicle_locations.schema.json')

    # Create a resource with the CSV file
    resource = Resource(file_path, schema=schema)

    # Validate the resource
    report = resource.validate()

    # Print validation results
    print(f"\nValidation Report for {file_path}:")
    print("-" * 50)

    if report.valid:
        print("✅ Validation passed! The file is compliant with the TIDES schema.")
        return True
    else:
        print("❌ Validation failed! The following errors were found:")
        for task in report.tasks:
            if task.errors:
                print(f"\nTask: {task.resource.path}")
                for error in task.errors:
                    print(f"- {error.message}")
                    if hasattr(error, 'fieldName'):
                        print(f"  Field: {error.fieldName}")
                    if hasattr(error, 'rowNumber'):
                        print(f"  Row: {error.rowNumber}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: validate-vehicle-locations <vehicle_locations.csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    success = validate_vehicle_locations(file_path)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
