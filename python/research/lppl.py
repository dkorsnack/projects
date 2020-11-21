import sys
import pandas as pd

def main(args):
    df = pd.read_excel("~/Downloads/lppl_merged_200001.xlsx")
    print(df.tail())
    return

if __name__ == "__main__":
    sys.exit(main(sys.argv))
