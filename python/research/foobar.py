import sys
import pandas as pd
import numpy as np

def main(args):
    df = pd.read_csv("baseline.csv", index_col="Date")[['Backtest_r','VBINX']]
    for x in ("implement", "kitchensink"):
      df[x] = pd.read_csv(x+".csv", index_col="Date")['Backtest_r']
    df.index = df.index.to_datetime()
    gp = df.groupby(pd.Grouper(freq="M"))
    mr = gp.apply(lambda x: np.prod(1+x)-1)
    print(mr)
    mr.to_csv("feebar.csv")
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
