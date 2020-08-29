import numpy as np
import matplotlib.pyplot as plt
import csv


with open('KC.csv','rt') as f:
    reader = csv.reader(f)
    KCrecords = list(reader)

with open('Lincoln.csv','rt') as f:
    reader = csv.reader(f)
    LincolnRecords = list(reader)

KCidx = {}
KCidx["SNOW"] = KCrecords[0].index("SNOW")
KCidx["SNWD"] = KCrecords[0].index("SNWD")
KCidx["TMIN"] = KCrecords[0].index("TMIN")
KCidx["TMAX"] = KCrecords[0].index("TMAX")
KCidx["WT11"] = KCrecords[0].index("WT11")

LinIdx = {}
LinIdx["SNOW"] = LincolnRecords[0].index("SNOW")
LinIdx["SNWD"] = LincolnRecords[0].index("SNWD")
LinIdx["TMIN"] = LincolnRecords[0].index("TMIN")
LinIdx["TMAX"] = LincolnRecords[0].index("TMAX")
LinIdx["WT11"] = LincolnRecords[0].index("WT11")

for KCentry, LincolnEntry in zip(KCrecords,LincolnRecords):
    if KCentry[0] != "STATION":
        d = KCentry[5]
        kc_tmax = KCentry[KCidx["TMAX"]]
        lin_tmax = LincolnEntry[LinIdx["TMAX"]]
        kc_tmin = KCentry[KCidx["TMIN"]]
        lin_tmin = LincolnEntry[LinIdx["TMIN"]]
        kc_snow = KCentry[KCidx["SNOW"]]
        lin_snow = LincolnEntry[LinIdx["SNOW"]]
        kc_snwd = KCentry[KCidx["SNWD"]]
        lin_snwd = LincolnEntry[LinIdx["SNWD"]]
        kc_wt11 = KCentry[KCidx["WT11"]]
        lin_wt11 = LincolnEntry[LinIdx["WT11"]]
        print("date %s, KC_tmin %s, Lin_tmin %s, KC_tmax %s, Lin_tmax %s, KC_snow %s, Lin_snow %s, KC_snwd %s, Lin_snwd %s, KC_wt11 %s, Lin_wt11 %s" %
              (d,kc_tmin,lin_tmin,kc_tmax,lin_tmax,kc_snow,lin_snow,kc_snwd,lin_snwd,kc_wt11,lin_wt11))

print(KCrecords)
print(LincolnRecords)


