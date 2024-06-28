#!/usr/bin/env python

"""
zdx_cloudpath_cli.py
====================

CLI tool to interact with ZDX Cloudpath APIs.

**Usage**::

    zdx_cloudpath_cli.py

**Examples**:

List all cloudpath probes for a device and application:
    $ python3 zdx_cloudpath_cli.py

Get details of a specific cloudpath probe:
    $ python3 zdx_cloudpath_cli.py

Get cloudpath data for a specific cloudpath probe:
    $ python3 zdx_cloudpath_cli.py

"""

import os
import logging
import argparse
from prettytable import PrettyTable
from zscaler.zdx import ZDXClientHelper
from zscaler.zdx.devices import DevicesAPI


def prompt_for_input(prompt_message, required=True):
    while True:
        user_input = input(prompt_message).strip()
        if user_input or not required:
            return user_input
        print("This field is required.")


def prompt_for_since():
    try:
        since_input = input("Enter the number of hours to look back (optional): ").strip()
        if since_input:
            return int(since_input)
        else:
            return None  # Optional field
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None


def display_table(data, headers):
    if not data:
        print("No data available.")
        return

    table = PrettyTable(headers)
    for row in data:
        table.add_row(row)
    print(table)


def extract_probes_data(probes):
    extracted_data = []
    for probe in probes:
        probe_id = probe.get('id')
        name = probe.get('name')
        num_probes = probe.get('num_probes')
        avg_latencies = probe.get('avg_latencies', [])

        for latency in avg_latencies:
            leg_src = latency.get('leg_src')
            leg_dst = latency.get('leg_dst')
            latency_value = latency.get('latency')
            extracted_data.append([probe_id, name, num_probes, leg_src, leg_dst, latency_value])
    return extracted_data


def extract_probe_details(probes):
    extracted_data = []
    for probe in probes:
        leg_src = probe.get('leg_src')
        leg_dst = probe.get('leg_dst')
        stats = probe.get('stats', [])

        for stat in stats:
            metric = stat.get('metric')
            unit = stat.get('unit')
            datapoints = stat.get('datapoints', [])

            for datapoint in datapoints:
                timestamp = datapoint.get('timestamp')
                value = datapoint.get('value')
                extracted_data.append([leg_src, leg_dst, metric, unit, timestamp, value])
    return extracted_data


def extract_cloudpath_data(cloudpath_data):
    extracted_data = []
    for leg in cloudpath_data.get('legs', []):
        leg_src = leg.get('leg_src')
        leg_dst = leg.get('leg_dst')
        metrics = leg.get('metrics', [])

        for metric in metrics:
            metric_name = metric.get('metric_name')
            unit = metric.get('unit')
            datapoints = metric.get('datapoints', [])

            for datapoint in datapoints:
                timestamp = datapoint.get('timestamp')
                value = datapoint.get('value')
                extracted_data.append([leg_src, leg_dst, metric_name, unit, timestamp, value])
    return extracted_data


def main():
    parser = argparse.ArgumentParser(description="Interact with ZDX Cloudpath APIs")
    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(level=logging.DEBUG)

    # Initialize ZDXClientHelper
    ZDX_CLIENT_ID = os.getenv("ZDX_CLIENT_ID")
    ZDX_CLIENT_SECRET = os.getenv("ZDX_CLIENT_SECRET")

    client = ZDXClientHelper(
        client_id=ZDX_CLIENT_ID,
        client_secret=ZDX_CLIENT_SECRET,
    )

    devices_api = DevicesAPI(client)

    # Prompt the user for action choice
    print("Choose an action:")
    print("a. List all cloudpath probes for a device and application")
    print("b. Get details of a specific cloudpath probe")
    print("c. Get cloudpath data for a specific cloudpath probe")
    action_choice = prompt_for_input("Enter choice (a/b/c): ")

    # Prompt the user for common inputs
    device_id = prompt_for_input("Enter the device ID: ")
    app_id = prompt_for_input("Enter the app ID: ")
    since = prompt_for_since()

    # Prepare keyword arguments
    kwargs = {
        "since": since,
    }
    
    # Remove None values from kwargs
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    if action_choice == "a":
        # Call the API to list cloudpath probes
        try:
            cloudpath_probes_iterator = devices_api.list_cloudpath_probes(device_id, app_id, **kwargs)
            cloudpath_probes = list(cloudpath_probes_iterator)
            headers = ['ID', 'Name', 'Num Probes', 'Leg SRC', 'Leg DST', 'Latency']
            data = extract_probes_data(cloudpath_probes)
            display_table(data, headers)
        except Exception as e:
            print(f"An error occurred while fetching cloudpath probes: {e}")
    elif action_choice == "b":
        # Prompt the user for probe ID
        probe_id = prompt_for_input("Enter the probe ID: ")

        # Call the API to get cloudpath probe details
        try:
            cloudpath_probe = devices_api.get_cloudpath_probe(device_id, app_id, probe_id, **kwargs)
            headers = ['Leg SRC', 'Leg DST', 'Metric', 'Unit', 'Timestamp', 'Value']
            data = extract_probe_details([cloudpath_probe])
            display_table(data, headers)
        except Exception as e:
            print(f"An error occurred while fetching cloudpath probe details: {e}")
    elif action_choice == "c":
        # Prompt the user for probe ID
        probe_id = prompt_for_input("Enter the probe ID: ")

        # Call the API to get cloudpath data
        try:
            cloudpath_data = devices_api.get_cloudpath(device_id, app_id, probe_id, **kwargs)
            headers = ['Leg SRC', 'Leg DST', 'Metric', 'Unit', 'Timestamp', 'Value']
            data = extract_cloudpath_data(cloudpath_data)
            display_table(data, headers)
        except Exception as e:
            print(f"An error occurred while fetching cloudpath data: {e}")
    else:
        print("Invalid choice. Please enter 'a', 'b', or 'c'.")

if __name__ == "__main__":
    main()
