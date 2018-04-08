#!/bin/bash

python3 prcm.py -w 50 && pdflatex ../../LaTeX/prcm/prcm_d.tex > /dev/null
python3 prcm.py -w 100 -i && pdflatex ../../LaTeX/prcm/prcm_i.tex > /dev/null
rm *.aux *.log *.out *.png
