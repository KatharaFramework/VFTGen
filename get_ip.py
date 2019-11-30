#!/usr/bin/python

import json
import sys

with open('lab.json') as lab_json:
    lab = json.load(lab_json)
    if len(sys.argv) == 1:
        print("--------------------- AGGREGATION LAYER ------------------------\n")
        for node in lab["aggregation_layer"].values():
            print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])

        for (k, p) in lab["pod"].items():
            print("\n--------------------------- %s ------------------------------\n" % k)
            for node in p.values():
                print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
    else:
        if sys.argv[1] == 'tof':
            for node in lab["aggregation_layer"].values():
                print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
        for p in lab["pod"].values():
            for node in p.values():
                if sys.argv[1] in node["name"]:
                    print(node["name"], [interface["ip_address"] for interface in node["interfaces"]])
