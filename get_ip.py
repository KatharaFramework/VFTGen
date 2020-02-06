#!/usr/bin/python3

import json
import sys
import argparse
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--d', type=str, required=True)
    parser.add_argument('--type', type=str, required=False)

    args = parser.parse_args()

    with open(os.path.join(args.d, 'lab.json')) as lab_json:
        lab = json.load(lab_json)
        if not args.type:
            print("--------------------- AGGREGATION LAYER ------------------------\n")
            for node in lab["aggregation_layer"].values():
                print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])

            for (k, p) in lab["pod"].items():
                print("\n--------------------------- pod_%s ------------------------------\n" % k)
                for node in p.values():
                    print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
        else:
            if args.type == 'tof':
                for node in lab["aggregation_layer"].values():
                    print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
            for p in lab["pod"].values():
                for node in p.values():
                    if args.type in node["name"]:
                        print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
