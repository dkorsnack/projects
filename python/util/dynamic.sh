#!/bin/bash

cd ../../../research 

for x in 1 0; do
    for y in '_0_50_75_8' '_1_100_75_8'; do
        python3 dynamic.py -b $x$y && 
        pdflatex backtest.tex &&
        mv backtest.pdf $x$y.pdf
    done
done
rm *.aux *.log *.out *.png
