#!/bin/python

import sys
import numpy as np
from matplotlib import pyplot as plt
from LogFile import LogFile
from TVM import TVM

def main(args):
    ptax = 0.0105
    rate = 0.0375
    homes = {
      "Sigali": {"Price":400000, "HOA":0, "MLR":0, "SQFT":1000},
      #"DesertWillow": {"Price":1249900, "HOA":160, "MLR":0, "SQFT":2877},
      #"Prisidio": {"Price":978000, "HOA":38, "MLR":0, "SQFT":2825},
       "Hillsdale": {"Price":1180000, "HOA":140, "MLR":1135, "SQFT":3200},
      # "Kempton": {"Price":1102000, "HOA":185, "MLR":4194, "SQFT":3815, "C":"r"},
      #"Pickering": {"Price":899000, "HOA":185, "MLR":3209, "SQFT":2800, "C":"r"},
      #"Hiskey": {"Price":1125000, "HOA":210, "MLR":0, "SQFT":2700},
      # "Ventia": {"Price":1100000, "HOA":38, "MLR":0, "SQFT":3463},
      # "Vellejo": {"Price":1150000, "HOA":114/3., "MLR":0, "SQFT":2950},
      #"Highland": {"Price":1090000, "HOA":125, "MLR":0, "SQFT":2389},
      #"Lynnfield": {"Price":1279000, "HOA":155, "MLR":0, "SQFT":2800},
      #"HawkHill": {"Price":930000, "HOA":199, "MLR":0, "SQFT":2600, "C":"r"},
      #"Dean": {"Price":1125000, "HOA":78, "MLR":0, "SQFT":3500, "C":"m"},
      #"Cressa1": {"Price":982800, "HOA":134, "MLR":5000, "SQFT":2440, "C":"y"},
      #"Cressa2": {"Price":1032800, "HOA":134, "MLR":5000, "SQFT":2600, "C":"y"},
      ######
      #"Sebastian": {"Price":1089000, "HOA":176, "MLR":0, "SQFT":2400},
      #"Blossom": {"Price":939000, "HOA":190, "MLR":0, "SQFT":2456},
      #"Marks": {"Price":980000, "HOA":155+80, "MLR":1200, "SQFT":2600},
      #"Belvidere2": {"Price":1192000, "HOA":125, "MLR":0.003*1192000, "SQFT":2605, "C":"y"},
      #"Belvidere3X": {"Price":1342000, "HOA":125, "MLR":0.003*1342000, "SQFT":2952, "C":"y"},
      #"Monument": {"Price":1075000, "HOA":0, "MLR":1100, "SQFT":2850},
      #"PacificCrest": {"Price":1288888, "HOA":110, "MLR":0, "SQFT":3560},
      #"Ronocolus": {"Price":1149999, "HOA":193, "MLR":4979, "SQFT":3850, "C":"r"},
      #"Conservancy": {"Price":980000, "HOA":268, "MLR":0, "SQFT":2950},
      #"Welton3": {"Price":1088480, "HOA":216, "MLR":5000, "SQFT":2700, "C":"y"},
      #"Welton2": {"Price":1005990, "HOA":216, "MLR":5000, "SQFT":2200, "C":"y"},
      #"Melody3": {"Price":1104990, "HOA":216, "MLR":7532, "SQFT":2678, "C":"y"},
      #"Melody4": {"Price":1090990, "HOA":216, "MLR":8190, "SQFT":2774, "C":"y"},
      #"Piedmont1": {"Price":1003000, "HOA":125, "MLR":3064, "SQFT":2165, "C":"y"},
      #"Piedmont2X": {"Price":1083000, "HOA":125, "MLR":3064, "SQFT":2546, "C":"y"},
      #"Calistoga": {"Price":1300000, "HOA":125, "MLR":0.0026*1300000, "SQFT":3034, "C":"y"},
      #"Legado4": {"Price":912900, "HOA":245, "MLR":4231, "SQFT":2344, "C":"y"},
      #"Villager": {"Price":1078000, "HOA":110, "MLR":0, "SQFT":2734},
      #"SpyRock": {"Price":1150000, "HOA":80, "MLR":0, "SQFT":2407},
      #"Cortina": {"Price":1175000, "HOA":38, "MLR":0, "SQFT":3337},
      #"Catalonia": {"Price":1200000, "HOA":124, "MLR":0, "SQFT":3200},
      #"Upland": {"Price":1150000, "HOA":166, "MLR":0, "SQFT":2800},
      #"Bloomington": {"Price":1050000, "HOA":150, "MLR":0, "SQFT":2830},
      #"TwinGables": {"Price":1050000, "HOA":273, "MLR":0, "SQFT":2299},
      #"Wicker": {"Price":980000, "HOA":181, "MLR":0, "SQFT":2000},
      #"Compass": {"Price":1100000, "HOA":193, "MLR":0, "SQFT":2560},
      #"HoneyLocust": {"Price":1200000, "HOA":160, "MLR":0, "SQFT":3260},
      #"Homeland": {"Price":950000, "HOA":176, "MLR":0, "SQFT":2495},
      #"Snowdrop": {"Price":1175000, "HOA":160, "MLR":0, "SQFT":2803},
      #"Arden": {"Price":900000, "HOA":127, "MLR":0, "SQFT":2105},
      #"Canopy": {"Price":1000000, "HOA":207, "MLR":0, "SQFT":2300},
      #"SecretGarden": {"Price":1100000, "HOA":130, "MLR":0, "SQFT":2460},
      #"BlueSpruce": {"Price":1250000, "HOA":110, "MLR":0, "SQFT":2680},
      #"Lynnfield": {"Price":1200000, "HOA":155, "MLR":0, "SQFT":2800},
      #"Ashford": {"Price":1200000, "HOA":141, "MLR":0, "SQFT":3200},
      #"Foxchase": {"Price":975000, "HOA":153, "MLR":0, "SQFT":2400},
      #"Newman": {"Price":1200000, "HOA":240, "MLR":0, "SQFT":3000},
      #"Ventia": {"Price":1100000, "HOA":38, "MLR":0, "SQFT":3463},
      #"McDougall": {"Price":1175000, "HOA":75, "MLR":0, "SQFT":3000},
      #"Highland": {"Price":1090000, "HOA":137, "MLR":0, "SQFT":2400},
      #"SecretGarden": {"Price":1100000, "HOA":130, "MLR":3170, "SQFT":2460},
      #"Poway": {"Price":1200000, "HOA":166, "MLR":0, "SQFT":3000},
      #"Hancock": {"Price":998000, "HOA":0, "MLR":0, "SQFT":2391},
    }
    shomes = sorted(list(homes.items()), key=lambda n_d: n_d[1]["SQFT"])
    data = []
    for (name, stats) in shomes: 
        pni = TVM(pv=-stats["Price"]*0.8, fv=0, n=30*12, i=rate/12).pmt
        tax = stats["Price"]*ptax/12
        oth = stats["MLR"]/12.+stats["HOA"]
        tot = pni+tax+oth
        sqft = float(stats["SQFT"])
        LogFile().info(
            "%-20s %0.2f %10i %10i %10i %10i %10i" % (
                name, tot/sqft, sqft, pni, tax, oth, tot
            )
        )
        data.append((stats["SQFT"], tot, stats.get("C","b")))
    """
    xs,ys,colors = zip(*data)
    z = np.polyfit(xs,ys,1)
    q = np.poly1d(z)
    lines = [
        (-m*1e5*ptax/12+TVM(pv=m*1e5*0.8,fv=0,n=30*12,i=rate/12).pmt,-m*1e5)
        for m in range(-14,-8)
    ]
    plt.scatter(xs, ys, color=colors, s=40)
    for (y,l) in lines:
        plt.axhline(y=y, color='c')
        plt.annotate(
            "$%i ($%i house, $%i loan)" % (y,l,l*0.8),
            (1500, y),
            color='c'
        )
    for i, name in enumerate(zip(*shomes)[0]):
        plt.annotate(name, (xs[i],ys[i]))
    plt.title("$y=$"+"+".join(
        ["\$%0.2f$x^{%i}$" % (q[i],i) for i in range(len(z))]
    ))
    plt.ylabel("monthly_price")
    plt.xlabel("square_foot")
    plt.plot(xs,q(xs))
    plt.grid(True)
    plt.show()
    """

if __name__ == "__main__":
    sys.exit(main(sys.argv))
