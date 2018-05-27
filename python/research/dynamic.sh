#!/bin/bash

python dynamic.py -c ^GSPC,VBMFX -w 50 -v 8 -o RB:3,1 && pdflatex dynamic.tex && mv dynamic.pdf rb_l.pdf
python dynamic.py -c SPY,IEF,GLD -w 100 -v 8 -o RB:6,2,1 -s VBINX -i && pdflatex dynamic.tex && mv dynamic.pdf rb.pdf
rm *.aux *.log *.out *.png
