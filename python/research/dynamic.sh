#!/bin/bash

python3 dynamic.py -c ^GSPC,VBMFX -w 50 -v 8 -o RB:3,1 && pdflatex dynamic.tex && mv dynamic.pdf rb_l.pdf
python3 dynamic.py -c SPY,IEF -w 100 -v 8 -o RB:3,1 -s VBINX -i && pdflatex dynamic.tex && mv dynamic.pdf rb.pdf
rm *.aux *.log *.out *.png
