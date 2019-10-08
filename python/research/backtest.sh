#!/bin/bash

cd $PYTHONPATH/research

python3 backtest.py -c ^GSPC,VBMFX,VGPMX -w 50 -v 8 -o RB:7,2,1 && pdflatex backtest.tex && mv backtest.pdf rb_l.pdf
python3 backtest.py -c SPY,IEF,GLD -w 100 -v 8 RB:7,2,1 -s VBINX -i && pdflatex backtest.tex && mv backtest.pdf rb.pdf
rm *.aux *.log *.out *.png
