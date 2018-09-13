#!/bin/bash

cd $PYTHONPATH/research

python3 dynamic.py -c ^GSPC,VBMFX,VGPMX -w 50 -v 8 -o RB:7,2,1 && pdflatex dynamic.tex && mv dynamic.pdf rb_l.pdf
python3 dynamic.py -c SPY,IEF,GLD -w 100 -v 8 RB:7,2,1 -s VBINX -i && pdflatex dynamic.tex && mv dynamic.pdf rb.pdf
rm *.aux *.log *.out *.png
