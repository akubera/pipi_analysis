#!/usr/bin/env python
#
# momentum_correction_sanity_test.py
#

import ROOT
import numpy as np
from stumpy import Histogram
from root_numpy import array2hist, hist2array
from pionpion.root_helpers import get_root_object

correction_data = np.array([
    [1.0, 0.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 0.0, 1.0],
])
cfilename = "sanity_check/ident_correction.root"


c_hist = ROOT.TH2D(
    "cdata",
    "Correction Data",
    correction_data.shape[0], 0.0, 1.0,
    correction_data.shape[1], 0.0, 1.0,
)
array2hist(correction_data, c_hist)



correction_file = ROOT.TFile(cfilename, "RECREATE")
femtolist = ROOT.TList()
analysis = ROOT.TObjArray()
analysis.SetName("analysis")
analysis.Add(c_hist)
femtolist.Add(analysis)
femtolist.Write('femtolist', ROOT.TObject.kSingleKey)
correction_file.Close()


cf_data = np.array([ 35.89,  53.79 ,  89.77,  98.06,  39.42])
c_hist = ROOT.TH1D("Num_qinv_pip", "_qinv_pip", cf_data.shape[0], 0.0, 1.0)
array2hist(cf_data, c_hist)

correlation_filename = "sanity_check/rnd_cd_data.root"
correlation_file = ROOT.TFile(correlation_filename, "RECREATE")
femtolist = ROOT.TList()
analysis = ROOT.TObjArray()
analysis.SetName("analysis")
analysis.Add(c_hist)
femtolist.Add(analysis)
femtolist.Write('femtolist', ROOT.TObject.kSingleKey)
correlation_file.Close()


from momentum_correction import main as momentum_correct

output_filename = "sanity_check/test_output.root"
momentum_correct([
    '--correction-file=' + cfilename,
    '--correction-hist-path=cdata',
    '--output=' + output_filename,
    correlation_filename,
])

results = ROOT.TFile(output_filename, 'READ')
cf_results = get_root_object(results, 'femtolist.analysis.Num_qinv_pip')
cf_res_array = hist2array(cf_results)

matches = cf_res_array == cf_data
print(matches)
if not np.all(matches):
    print(cf_res_array)
    print(cf_data)




correction_data = np.ascontiguousarray(np.array([
    # q_rec ↦
    [0.8, 0.2, 0.0, 0.0, 0.0],  # q_true
    [0.2, 0.5, 0.3, 0.0, 0.0],  #  ↧
    [0.0, 0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 2.0, 0.0],
    [0.0, 0.0, 0.0, 1.5, 1.5],
]).T)
#
# correction_data = np.ascontiguousarray(np.array([
#     # q_rec ↦
#     [0.8, 0.2, 0.0, 0.0, 0.0],  # q_true
#     [1.0, 0.5, 0.3, 0.0, 0.0],  #  ↧
#     [1.0, 0.0, 1.0, 0.0, 0.0],
#     [1.0, 0.0, 0.0, 2.0, 0.0],
#     [1.0, 0.0, 0.0, 1.5, 1.5],
# ]).T)

cfilename = "sanity_check/non_ident_correction.root"

c_hist = ROOT.TH2D(
    "cdata",
    "Correction Data; q_{inv}^{r}; q_{inv}^{t}",
    correction_data.shape[0], 0.0, 1.0,
    correction_data.shape[1], 0.0, 1.0,
)
array2hist(correction_data, c_hist)

assert c_hist.GetBinContent(c_hist.FindBin(0.45, 0.22)) == 0.3

correction_file = ROOT.TFile(cfilename, "RECREATE")
femtolist = ROOT.TList()
analysis = ROOT.TObjArray()
analysis.SetName("analysis")
analysis.Add(c_hist)
femtolist.Add(analysis)
femtolist.Write('femtolist', ROOT.TObject.kSingleKey)
correction_file.Close()


cf_data = np.array([ 35.89,  53.79 ,  89.77,  98.06,  39.42])
c_hist = ROOT.TH1D("Num_qinv_pip", "_qinv_pip", cf_data.shape[0], 0.0, 1.0)
array2hist(cf_data, c_hist)

correlation_filename = "sanity_check/rnd_cd_data.root"
correlation_file = ROOT.TFile(correlation_filename, "RECREATE")
femtolist = ROOT.TList()
analysis = ROOT.TObjArray()
analysis.SetName("analysis")
analysis.Add(c_hist)
femtolist.Add(analysis)
femtolist.Write('femtolist', ROOT.TObject.kSingleKey)
correlation_file.Close()


from momentum_correction import main as momentum_correct

output_filename = "sanity_check/test_output.root"
momentum_correct([
    '--correction-file=' + cfilename,
    '--correction-hist-path=cdata',
    '--output=' + output_filename,
    correlation_filename,
])

results = ROOT.TFile(output_filename, 'READ')
cf_results = get_root_object(results, 'femtolist.analysis.Num_qinv_pip')
cf_expected = np.array([
    35.89 * 0.8 + 53.79 * 0.2,
    35.89 * 0.2 + 53.79 * 0.5 + 89.77 * 0.3,
    89.77,
    98.06,
    98.06 * 0.5 + 39.42 * 0.5
])
# cf_expected = np.array([
#     35.89 * 0.8 + 53.79 * 0.28571429,
#     35.89 * 0.2 + 53.79 * 0.71428571 + 89.77 * 0.23076923,
#     89.77 * 0.76923077,
#     98.06 * 0.57142857,
#     98.06 * 0.42857143 + 39.42 * 1.0
# ])
# cf_expected = np.array([
#     35.89 * 0.8 + 53.79 * 0.28571429,
#     35.89 * 0.2 + 53.79 * 0.71428571 + 89.77 * 0.23076923,
#     89.77 * 0.76923077,
#     98.06 * 0.66666667,
#     98.06 * 0.33333333 + 39.42 * 1.0
# ])

cf_res_array = hist2array(cf_results)
matches = cf_res_array == cf_expected
print(matches)
if not np.all(matches):
    print(sum(cf_data), cf_data)
    print(sum(cf_res_array), cf_res_array)
    print(sum(cf_expected), cf_expected)
