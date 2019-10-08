#!/bin/env Rscript

cleanOval <- read.csv('clean_oval.csv', header=TRUE, sep=',')
summary(cleanOval)

oval <- read.csv('oval.csv', header=TRUE, sep=',')
summary(oval)

# carat has to be the largest driver of price ...
plot(oval$carat, oval$price)
# but boy is it non-linear (mostly at the extremes)

# instad of transforming carat to be more linear [ln(carat)]
# since the objective is to use this in my head when shopping,
# what if we filter the data to a more realistic subset?
subsetOval <- subset(oval, price > 10000 & price < 30000)
summary(subsetOval)
plot(subsetOval$carat, subsetOval$price)

# looks like the independent variables are not extremely independent ...
ovalPCA <- prcomp(subsetOval[, 2:12], center=TRUE, scale=TRUE)
summary(ovalPCA)
print(ovalPCA)

# how about visualizing (pariwise) all of the dependent/independent relationships...
panel.cor <- function(x, y, digits=2, prefix="", cex.cor, ...)
{
        usr <- par("usr"); on.exit(par(usr))
        par(usr = c(0, 1, 0, 1))
        r <- abs(cor(x, y))
        txt <- format(c(r, 0.123456789), digits=digits)[1]
        txt <- paste(prefix, txt, sep="")
        if(missing(cex.cor)) cex.cor <- 0.8/strwidth(txt)
            text(0.5, 0.5, txt, cex = cex.cor * r)
}
pairs(~price+carat+cut+color+clarity+polish+symmetry+flourescence+depth+table+lengthWidth+culet, data=subsetOval, lower.panel=panel.cor)

# are they all significantly significant?
fit0 <- lm(
'price~carat+cut+color+clarity+polish+symmetry+flourescence+depth+table+lengthWidth+culet',
data=subsetOval
)
summary(fit0)$r.squared

fit1 <- lm(
'price~0+carat+cut+color+clarity+polish+symmetry+flourescence+depth+table+lengthWidth+culet',
data=subsetOval
)
summary(fit1)$r.squared

# after a bunch more plotting and tinkerint ... this makes sense
fit2 <- lm('price~0+carat+color+clarity+lengthWidth', data=subsetOval)
summary(fit2)

model <- predict(fit2, data=subsetOval)
plot(subsetOval$price, model) 
