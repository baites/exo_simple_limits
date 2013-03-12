#!/usr/bin/env python

'''
Created by Samvel Khalatyan, Jun 11, 2012
Copyright 2012, All rights reserved
'''

from __future__ import print_function,division

import copy
import math
import numpy
from optparse import OptionParser

from array import array
import ROOT

from loader import load_data,get_limits
import labels
import style
import theory
import smooth 
from exclusion import exclude

def plot(limit_type, filename, logy=True, smooth_data=True):
    '''
    Application entry point
    '''

    supported_limit_types = ("narrow", "wide", "kk")
    if limit_type not in supported_limit_types:
        raise RuntimeError("supported limit types: {0!r}".format(
                            supported_limit_types))

    data = load_data(filename,0.1)

    if smooth_data: smooth.data(data, n=40, log=logy)

    #print(sorted(data.keys()))
    #for m in sorted(data.keys()):
    #    print(m, data[m][0])

    legend = ROOT.TLegend(0.5, 0.50, 0.80, 0.88)

    line_width = 3
    combo = ROOT.TMultiGraph()

    # 2 sigma band
    cur = get_limits(data)
    graph = ROOT.TGraphAsymmErrors(len(cur["x"]), cur["x"], cur["expected"],
                                   cur["xerr"], cur["xerr"],
                                   cur["two_sigma_down"], cur["two_sigma_up"])
    graph.SetFillColor(ROOT.kGray + 1)
    graph.SetLineWidth(0)
    combo.Add(graph)
    g_2s = graph

    # 1 sigma band
    graph = ROOT.TGraphAsymmErrors(len(cur["x"]), cur["x"], cur["expected"],
                                   cur["xerr"], cur["xerr"],
                                   cur["one_sigma_down"], cur["one_sigma_up"])
    graph.SetFillColor(ROOT.kGray)
    graph.SetLineWidth(0)
    combo.Add(graph)
    g_1s = graph

    # expected
    graph = ROOT.TGraph(len(cur["x"]), cur["x"], cur["expected"])
    graph.SetLineColor(ROOT.kBlack)
    graph.SetLineWidth(line_width)
    combo.Add(graph)
    legend.AddEntry(graph, "Expected (95% Bayesian)", "l")

    # observed
    graph = ROOT.TGraph(len(cur["observed_x"]), cur["observed_x"], cur["observed"])
    graph.SetLineColor(ROOT.kRed + 1)
    graph.SetLineWidth(line_width)
    combo.Add(graph)
    legend.AddEntry(graph, "Observed (95% Bayesian)", "l")

    # Theory
    theories = {
            "narrow": ([theory.zprime, 1.2, False], ),
            "wide": ([theory.zprime, 10.0, False], ),
            "kk": ([theory.kkgluon, None, None], )
            }.get(limit_type)

    for index, (theory_function, theory_width, use_old_theory) in enumerate(theories, 0):
        class Theory(object): pass

        x, y, label = (theory_function(theory_width, use_old_theory)
                        if theory_width
                        else theory_function())

        # remove all the points below 500 GeV
        x, y = zip(*[(xi, yi) for xi, yi in zip(x, y) if not 750 > xi])

        graph = ROOT.TGraph(len(x), array('d', x), array('d', y))
        graph.SetLineColor([ROOT.kBlue + 1, ROOT.kMagenta + 1, ROOT.kGreen + 1][index] if index < 3 else ROOT.kBlue + 1)
        graph.SetLineWidth(3)
        graph.SetLineStyle(2)
        combo.Add(graph)
        legend.AddEntry(graph, label, "l")

        theory_data = Theory()
        theory_data.x = x
        theory_data.y = y

        expected_exclusion, observed_exclusion = exclude(cur, theory_data)
        print("Expected exclusion:", expected_exclusion)
        print("Observed exclusion:", observed_exclusion)

    legend.AddEntry(g_1s, "#pm 1 s.d. Expected", "f")
    legend.AddEntry(g_2s, "#pm 2 s.d. Expected", "f")

    # Draw
    cv = ROOT.TCanvas()
    style.canvas(cv)

    combo.Draw("3al")
    legend.Draw()

    if logy: cv.SetLogy(True)

    if limit_type == 'kk':
        style.combo(combo, ytitle = 'Upper Limit #sigma_{g_{KK}} x B [pb]', 
                    maximum=1e2 if logy else None,
                    minimum=1e-2 if logy else None)
    else:
        style.combo(combo, maximum=1e2 if logy else None)

    style.legend(legend)
    legend.SetTextSize(0.04)

    plot_labels = labels.create({
        "narrow": "Narrow Width Assumption",
        "wide": "10% Width Assumption",
        "kk": "KK Gluon Assumption"}.get(limit_type, None))

    map(ROOT.TObject.Draw, plot_labels)

    cv.Update()
    cv.SaveAs("limits-{0}.pdf".format(limit_type))
