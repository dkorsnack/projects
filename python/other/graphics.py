# $Id: graphics.py 45 2013-10-06 15:57:20Z korsnack $
#!/bin/python

__all__ = ["outputImage", "barChart", "histogram", "lineGraph", "scatterPlot"]

import warnings
warnings.filterwarnings('ignore', r'Deprecation')
import numpy
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

from lib.logfile import *
from lib.pyutils import chmod, iif

# define colors and directory for saved images
phaseOrange = [0.8125, 0.4883, 0.0117]
phaseGrey   = [0.4414, 0.4414, 0.4571]
altColor1   = [0.8000, 0.3000, 0.2500]
altColor2   = [0.1500, 0.6000, 0.6500]
lightGrey   = [0.7000, 0.7000, 0.7000]
colorstart  = [0.2000, 0.4000, 0.9000]
colorend    = [0.9000, 0.1000, 0.1000]
target      = "/wdrive/usr/dkorsnack/plots/"

#=======================================
def outputImage(plt, target, lg=LogFile(), args={}):
    kwargs = {
        "facecolor"   : "white",
        "edgecolor"   : "white",
        "orientation" : "landscape",
        "dpi"         : 240
    }
    kwargs.update(args)
    plt.savefig(target, **kwargs)
    chmod(target)
    try:
        os.chmod(foo, 0o664)
    except:
        pass
    lg.info("SAVEFIG: %s completed" % target)
    return 1

#=======================================
def barChart(data,               # list of dictionaries of data [{x:y},...]
             data_values = True, # show data values?
             save_image  = None, # save image? if so, give target location
             legend      = None, # list of string values for the legend
             plot_title  = None, # string of title
             xaxis_label = None, # string of x axis label
             yaxis_label = None, # string of y axis label
             xticks      = None, # string of x axis tickmarks
             bar_width   = 0.8,
             outputargs  = {}
             ):
    try:
        # function specific variables
        width = bar_width / len(data)

        # define x axis positions
        xlocations = list(range(len(data[0])))

        # creating the legend
        if not legend:
            legend = []
            for d in range(len(data)):
                legend.append("bar" + str(d))

        # iterating over the data set to create the graphics
        global_max =  max([max([abs(d[x]) for x in sorted(d.keys())]) for d in data])
        for d in range(len(data)):
            # disecting the dictionaries of data
            keys   = sorted(data[d].keys())
            values = [data[d][x] for x in keys]

            # define the color scheme
            if d == 0:
                color = phaseOrange
            elif d == 1:
               color = phaseGrey
            elif d == 2:
               color = altColor1
            elif d == 3:
               color = altColor2
            else:
               color = [random.random(),
                        random.random(),
                        random.random()
                        ]

            # creating the bars
            plt.bar([x + (1 - bar_width) / 2 + d * width for x in xlocations],
                    values,
                    width     = width,
                    edgecolor = color,
                    color     = color,
                    label     = legend[d]
                    )

            # labeling each bar with its value:
            if data_values:
                max_value = max(values)
                for v in range(len(values)):
                    if values[v] >= 0.:
                        align = 'bottom'
                    else:
                        align = 'top'
                    plt.text(
                        xlocations[v]+(1-bar_width)/2+width*(d+0.5),
                        values[v]+(cmp(values[v], 0) or 1)*global_max*0.02,
                        "%0.0f" % values[v],
                        ha = 'center',
                        va = align,
                        fontsize = 10,
                    )

        # putting it all together
        if plot_title:  plt.title(plot_title)
        if xaxis_label: plt.xlabel(xaxis_label)
        if yaxis_label:
            plt.ylabel(yaxis_label)
            plt.gca().yaxis.grid(True)
        plt.legend(loc = 'best').draw_frame(False)
        plt.axhline(y = 0., color = 'black')
        if xticks:
            plt.xticks(*xticks,
                       rotation = 90
                       )
        else:
            plt.xticks([x + 0.5 for x in xlocations],
                       [str(x) for x in keys],
                       rotation = 90
                       )
        if save_image:
            outputImage(plt, save_image)
            return plt.close()
        else:
            return plt.show()
    except:
        LogFile().warning("Unexpected ERROR: %s" % sys.exc_info()[0])
        plt.plot(list(range(10)))
        plt.title('ERROR!')
        plt.xlabel(sys.exc_info()[0])
        outputImage(plt, save_image)
        return plt.close()

#=======================================
def histogram(data,                # list of dictionaries of data [{x:y}...]
              pdf         = False, # normalize results (to create PDF)
              save_image  = None,  # save image? if so, give target location
              bin         = None,  # bin size
              legend      = None,  # list of string values for the legend
              plot_title  = None,  # string of title
              xaxis_label = None,  # string of x axis label
              yaxis_label = None,  # string of y axis label
              vert_line   = None   # float of vertical line location
              ):
    try:
        # determine the binning
        all_values = []
        list(map(lambda x: all_values.extend(list(x.values())), data))
        lowest  = min(all_values)
        highest = max(all_values)
        if bin:
            bin = sorted(set([round(x, round(-numpy.log(bin)/numpy.log(10))) for x in list(
                    numpy.arange(numpy.floor(lowest / bin) * bin, 0., bin)
                )+list(
                    numpy.arange(0., numpy.ceil(highest / bin) * bin, bin)
                )]))
        else:
           opt_bin = 3.5 * numpy.std(all_values) / len(all_values) ** (1. / 3)
           bin = list(numpy.arange(lowest, 0.,
                      abs(lowest) / numpy.ceil(abs(lowest) / opt_bin))) + \
             list(numpy.arange(0., highest,
                  abs(highest) / numpy.ceil(abs(highest) / opt_bin)))

        # iterating over the data to create the graphics
        if len(data) == 1:
            # disecting the dictionary of data
            keys   = sorted(data[0].keys())
            values = [data[0][x] for x in keys]

            # seperate positive and negative values
            pos = []
            neg = []
            for v in range(len(values)):
                if values[v] >= 0.:
                    pos.append(values[v])
                else:
                    neg.append(values[v])

            # plotting the histogram
            h1 = plt.hist(neg,
                          facecolor = lightGrey,
                          edgecolor = [1, 1, 1],
                          normed    = pdf,
                          bins      = bin,
                          )
            h2 = plt.hist(pos,
                      facecolor = phaseGrey,
                      edgecolor = [1, 1, 1],
                      normed    = pdf,
                      bins      = bin,
                      )
            plt.axis([int(numpy.floor(min(min(h1[1]), min(h2[1])) * 110)) / 110.,
                      int(numpy.ceil(max(max(h1[1]), max(h2[1])) * 110)) / 110.,
                      0,
                      int(numpy.ceil(max(max(h1[0]), max(h2[0])) * 1.1))
                  ])
        else:
            # creating the legend
            if not legend:
               legend = []
               for d in range(len(data)):
                   legend.append("histogram" + str(d))

            for d in range(len(data)):
                # disecting the dictionaries of data
                keys   = sorted(data[d].keys())
                values = [data[d][x] for x in keys]

                # define the color scheme
                if d == 0:
                   color = phaseOrange
                elif d == 1:
                   color = phaseGrey
                else:
                   color = [random.random(),
                            random.random(),
                            random.random()
                            ]

                # creating the legend
                if not legend:
                   legend = []
                   for d in range(len(data)):
                       legend.append("bar" + str(d))

                # plotting the histogram
                plt.hist(values,
                         facecolor = color,
                         edgecolor = color,
                         normed    = pdf,
                         alpha     = 0.50,
                         label     = legend[d],
                         bins      = bin
                         )
                plt.legend(loc = 'best').draw_frame(False)

        # putting it all together
        if plot_title:  plt.title(plot_title)
        if xaxis_label: plt.xlabel(xaxis_label)
        if yaxis_label: plt.ylabel(yaxis_label)
        if vert_line: plt.axvline(x = vert_line,
                                  color = phaseOrange,
                                  linewidth = 3
                                  )
        if save_image:
            outputImage(plt, save_image)
            plt.close()
        else:
            return plt.show()
    except:
        LogFile().warning("Unexpected ERROR: %s" % sys.exc_info()[0])
        plt.plot(list(range(10)))
        plt.title('ERROR!')
        plt.xlabel(sys.exc_info()[0])
        outputImage(plt, save_image)
        return plt.close()

#=======================================
def lineGraph(data,                # list of dictionaries of data [{x:y},...]
              log_scale   = False, # show on log scale
              save_image  = None,  # save image? if so, give target location
              legend      = None,  # list of string values for the legend
              plot_title  = None,  # string of title
              xaxis_label = None,  # string of x axis label
              yaxis_label = None,  # string of y axis label
              yaxis_scale = None,  # integer to scale y axis
              xticks      = None,  # list of x axis tick mark arguments
              figsize     = None,
              colorspec   = [phaseOrange, phaseGrey, altColor1, altColor2],
              outputargs  = {},
              subsy       = None,
              ticklabels  = 5
              ):
    try:
        if figsize:
            plt.figure(figsize=figsize)

        # creating the legend
        if not legend:
            legend = []
            for d in range(len(data)):
                legend.append("line" + str(d))

        # iterating over the data set to create the graphics
        for d in range(len(data)):
            # disecting the dictionaries of data
            keys      = sorted(data[d].keys())
            values    = [data[d][x] for x in keys]
            linewidth = 2

            # define the color scheme
            if d < len(colorspec):
                color = colorspec[d]
            else:
                color = [random.random(), random.random(), random.random()]

            # creating the lines
            if log_scale:
                plt.semilogy(values,
                             linewidth          = linewidth,
                             color              = color,
                             label              = legend[d],
                             solid_joinstyle    = 'round',
                             subsy              = subsy,
                             )
                plt.grid(True, which = 'major')
                plt.grid(True, which = 'minor')

                # pretty printing y axis
                numbers, text = plt.yticks()
                if yaxis_scale:
                    text = ['%0.0f' % (x * yaxis_scale) for x in numbers]
                else:
                    text = ['%0.0f' % x for x in numbers]
                plt.yticks(numbers, text)
                if len(numbers) < 5:
                    nums = list(numbers)
                    if subsy:
                        candidates = nums
                        for x in nums[:-1]:
                            for y in subsy:
                                candidates.append(x*y)
                        s = numpy.array(sorted(candidates))
                    else:
                        s = numpy.array(sorted(
                            nums + [n*ticklabels for n in nums[:-1]]
                        ))
                    plt.yticks(s, s)
            else:
                plt.plot(values,
                         linewidth       = linewidth,
                         color           = color,
                         label           = legend[d],
                         solid_joinstyle = "round"
                         )
                plt.grid(True)

        # putting it all together
        if plot_title:  plt.title(plot_title)
        if xaxis_label: plt.xlabel(xaxis_label)
        if yaxis_label: plt.ylabel(yaxis_label)
        plt.legend(loc = 'best').draw_frame(False)
        plt.axhline(y = 0., color = 'black')
        if xticks:
            plt.xticks(*xticks, rotation=90)
        else:
            plt.xticks(list(range(len(values))),
                       [str(x) for x in keys],
                       rotation = 90
                       )
        if save_image:
            outputImage(plt, save_image, args=outputargs)
            plt.close()
        else:
            return plt.show()
    except:
        LogFile().warning("Unexpected ERROR: %s" % sys.exc_info()[0])
        plt.plot(list(range(10)))
        plt.title('ERROR!')
        plt.xlabel(sys.exc_info()[0])
        outputImage(plt, save_image)
        return plt.close()

#=======================================
def scatterPlot(data,               # list of dictionaries of data [{xk:xv},{yk:yv}]
                regression  = True, # linear regression on data
                save_image  = None, # save image? if so, give target location
                plot_title  = None, # string of title
                xaxis_label = None, # string of x axis label
                yaxis_label = None, # string of y axis label
                color_spec  = None
                ):
    try:
        # disecting the dictionaries of data
        x_values = [val for (key, val) in sorted(data[0].items())]
        y_values = [val for (key, val) in sorted(data[1].items())]

        if not color_spec:
            color_spec = [(0, x) for x in range(len(data[0]))]

        color = (
            lambda m_min, m_max: [[colorstart[i] \
                        + float(x-m_min)/(m_max-m_min) \
                        * (colorend[i]-colorstart[i]) for i in range(3)] for x in [x[1] for x in color_spec]])(*(
                lambda s: (s[0], s[-1]))(*[sorted([x[1] for x in color_spec])]))

        scat = plt.scatter(x_values,
                           y_values,
                           s     = 10,
                           color = color
                           )

        # perform linear regression
        if regression:
            from scipy import stats
            regress = stats.linregress(x_values, y_values)
            x_vals  = [max(x_values), min(x_values)]
            y_vals  = [regress[0] * x + regress[1] for x in x_vals]
            plt.plot(x_vals,
                     y_vals,
                     color     = phaseOrange,
                     linewidth = 2
                     )
            plt.suptitle("y = %0.5fx %s %0.5f\n" \
                         "R^2 = %0.5f"  % (regress[0],
                                           iif(regress[1] >= 0.,
                                               "+",
                                               "-"),
                                           abs(regress[1]),
                                           regress[2] ** 2),
                         color = phaseOrange,
                         ha    = 'left',
                         x     = 0.15,
                         y     = 0.85
                         )

        # putting it all together
        if plot_title:  plt.title(plot_title)
        if xaxis_label: plt.xlabel(xaxis_label)
        if yaxis_label: plt.ylabel(yaxis_label)
        plt.axhline(y = 0., color = 'black')
        plt.axvline(x = 0., color = 'black')
        if save_image:
            outputImage(plt, save_image)
            plt.close()
        else:
            return plt.show()
    except:
        LogFile().warning("Unexpected ERROR %s:" % sys.exc_info()[0])
        plt.plot(list(range(10)))
        plt.title('ERROR!')
        plt.xlabel(sys.exc_info()[0])
        outputImage(plt, save_image)
        return plt.close()

#=======================================
def autoCorrelation(data,               # dictionary of data {k:v}
                    lag         = 40,   # maximum lag
                    save_image  = None, # save image? if so, give target location
                    plot_title  = None, # string of title
                    xaxis_label = None, # string of x axis label
                    yaxis_label = None  # string of y axis label
                    ):
    try:
        # obtaining the data
        data = [data[x] for x in sorted(data.keys())]

        # plotting the function
        plt.acorr(data,
                  usevlines = 'True',
                  normed    = 'True',
                  maxlags   = lag,
                  lw        = 4,
                  color     = phaseOrange
                  )

        # putting it all together
        if plot_title: plt.title(plot_title)
        if xaxis_label: plt.xlabel(xaxis_label)
        if yaxis_label: plt.ylabel(yaxis_label)
        plt.axhline(y = 0., color = 'black', linewidth = 2)
        if save_image:
            outputImage(plt, save_image)
            plt.close()
        else:
            return plt.show()
    except:
        LogFile().warning("Unexpected ERROR: %s" % sys.exc_info()[0])
        plt.plot(list(range(10)))
        plt.title('ERROR!')
        plt.xlabel(sys.exc_info()[0])
        outputImage(plt, save_image)
        return plt.close()
