/**
 * RunParallel_11.C
 *
 * AliROOT macro designed to run over ALICE 2011 (11h) data in multiple processes.
 */

bool rungrid = false;
bool force_exit = false;
bool is_mc_analysis = false;

#define DEV_LOCAL

#ifndef __CINT__

#include <TFile.h>
#include <TROOT.h>
#include <TSystem.h>
#include <TInterpreter.h>
#include <TMap.h>

#include <AliAnalysisAlien.h>
#include <AliAnalysisManager.h>
#include <AliAODInputHandler.h>
#include <AliAnalysisTaskSE.h>
#include <AliAnalysisTaskFemto.h>

#include <vector>
#include <iostream>
#include <set>

using namespace std;

#endif

#include <TObjString.h>

//#include "PilamEventCut.h"

// std::vector<int> runs;
std::set<int> runs;
std::vector<int>* gBitmap;

TString output_filename = "",
         macro_filename = "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysis.C";

// const TString config = "\"@vertex_bins = 5;{0:5, 0:10:20:30}; +p; +m; ~do_kt_qinv = true;\"";
// const TString config = "\"\"";
TString config = "\""
"+p;"
// "~do_avg_sep_cf = true; "
"~do_deltaeta_deltaphi_cf = true;"
"@enable_pair_monitors = false;"
"@verbose = false; "
"@min_coll_size = 1; "

// "$event_MultMin = 28000; "

"$pion_1_PtMin = 0.14; "
"$pion_1_PtMax = 2.0; "
"$pion_1_max_impact_z = 0.15; "
"$pion_1_max_impact_xy = 0.2; "
"$pion_1_max_tpc_chi_ndof = 3.0; "
"$pion_1_max_its_chi_ndof = 3.0; "
"$pair_delta_eta_min = 0.00; "
"$pair_delta_phi_min = 0.00; "

"\"";

int use_runs[] = {170163, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 0};
//int use_runs[]   = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 0};
// int use_runs[]= {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163, 0};
//  int good_runs[21]={170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163};

Int_t id = 0;

void process_arguments()
{
  char **argv = gApplication->Argv();
  int argc = gApplication->Argc();
  // std::vector<TString> args(argv, argv + argc);
  std::vector<TString> args;
  size_t i = 0;
  for (i = 0; i < argc; i++) {
    args.push_back(TString(argv[i]));
  }

  std::vector<TString>::iterator nxt = args.begin();

  while (!nxt->Contains("RunParallel_11.C") && nxt != args.end()) {
    cout << "> " << *nxt << "\n";
    ++nxt;
  }

  if (nxt++ == args.end()) {
    return;
  }

  Int_t count = 0;

  for (; nxt != args.end(); nxt++, count++) {

    switch (count) {
    // first arg is group identification
    case 0:
      id = nxt->Atoi();

      if (id == 0) {
        cout << "Error, bad id num '" << argv[argc-1] << "'. Aborting.\n";
        exit(1);
      }

      break;

    // second arg is output filename, with .id before root
    case 1:
      nxt->ReplaceAll(".root", TString::Format(".%02d.root", id));
      output_filename = *nxt;
      break;
    default:
      cout << "Ignoring argument # " << count << ", '" << *nxt << "'\n";
    }
  }

  if (id == 0) {
    cout << "ID not set. Aborting.\n";
    exit(1);
  }

}

void
RunParallel_11()
{
  cout << "[RunMe] Begin\n";

  TStopwatch timer;
  timer.Start();

  // Setup includes
  gInterpreter->AddIncludePath("$ALICE_ROOT/include");
  gInterpreter->AddIncludePath("$ALICE_PHYSICS/include");

  gSystem->Load("libVMC.so");
  gSystem->Load("libOADB.so");
  gSystem->Load("libTree.so");
  gSystem->Load("libAOD.so");

  gSystem->Load("libANALYSIS.so");
  gSystem->Load("libANALYSISalice.so");

  gSystem->Load("libPWGCFfemtoscopy.so");
  gSystem->Load("libPWGCFfemtoscopyUser.so");

  process_arguments();

  // Create Analysis Manager
  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "My Analysis Manager");

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  input_handler->CreatePIDResponse(is_mc_analysis);
  mgr->SetInputEventHandler(input_handler);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  AddTaskVZEROEPSelection();

  // Create the AliFemto task using configuration from ConfigFemtoAnalysis.C
  AliAnalysisTaskFemto *pipitask = new AliAnalysisTaskFemto(
    "PiPiTask",
    macro_filename,
    config,
    kFALSE
  );

  pipitask->SelectCollisionCandidates(
    AliVEvent::kMB
    | AliVEvent::kCentral
    | AliVEvent::kSemiCentral
    // | AliVEvent::kAny
    // AliVEvent::kINT7
  );
  //  pipitask->SelectCollisionCandidates(AliVEvent::kAny);

  if (output_filename == "") {
    TDatime d;
    output_filename = TString::Format("MultiResults_%04d-%02d-%02d_%06d.root",
      d.GetYear(),
      d.GetMonth(),
      d.GetDay(),
      d.GetTime());
  }


  AliAnalysisDataContainer *femtolist = mgr->CreateContainer(
    "femtolist",
    TList::Class(),
    AliAnalysisManager::kOutputContainer,
    output_filename
  );

  mgr->AddTask(pipitask);

  mgr->ConnectOutput(pipitask, 0, femtolist);
  mgr->ConnectInput(pipitask, 0, mgr->GetCommonInputContainer());

  if (!mgr->InitAnalysis()) {
    cerr << "Error Initting Analysis. Exiting.\n";
    exit(1);
  }

  mgr->PrintStatus();

  TChain *input_files =
    load_file_set();
    //load_files(new TChain("aodTree"));

  mgr->StartAnalysis("local", input_files);

  timer.Stop();
  timer.Print();
}

TChain*
load_file_set(TChain *input_files = NULL)
{
  const TString data_prefix = "/alice/data/2011/LHC11h_2";

  if (!input_files) {
    input_files = new TChain("aodTree");
  }

  cout << "ID: " << id << "\n";

  switch (id) {
  case 1:
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/0355/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/0733/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/0791/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/1190/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/1280/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/1300/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169411/ESDs/pass2/AOD145/1426/AliAOD.root");
    break;
  case 2:
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0590/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0186/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0520/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0260/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0508/AliAOD.root");
    break;
  case 3:
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0590/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0186/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0520/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0260/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0508/AliAOD.root");
    break;
  case 4:
    input_files->Add("/alice/data/2011/LHC11h_2/000169138/ESDs/pass2/AOD145/0049/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169138/ESDs/pass2/AOD145/0096/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169138/ESDs/pass2/AOD145/1843/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169138/ESDs/pass2/AOD145/1882/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169138/ESDs/pass2/AOD145/1923/AliAOD.root");
    break;
  case 5:
    input_files->Add("/alice/data/2011/LHC11h_2/000168992/ESDs/pass2/AOD145/0176/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168992/ESDs/pass2/AOD145/0321/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168992/ESDs/pass2/AOD145/0358/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168992/ESDs/pass2/AOD145/0465/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169035/ESDs/pass2/AOD145/0017/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000169035/ESDs/pass2/AOD145/0870/AliAOD.root");
    break;
  case 6:
    input_files->Add("/alice/data/2011/LHC11h_2/000168826/ESDs/pass2/AOD145/0715/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168826/ESDs/pass2/AOD145/1167/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168826/ESDs/pass2/AOD145/1648/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168826/ESDs/pass2/AOD145/1760/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168826/ESDs/pass2/AOD145/1776/AliAOD.root");
    break;
  case 7:
    input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0026/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0067/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0100/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0103/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0107/AliAOD.root");
    break;
  case 8:
    input_files->Add("/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/0027/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/0186/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/0563/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/0652/AliAOD.root");
    input_files->Add("/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/1062/AliAOD.root");
    break;
  }

  // const char **filenames = (id == 1)
  //                        ? {"/alice/data/2011/LHC11h_2/000169144/ESDs/pass2/AOD145/0363/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000169144/ESDs/pass2/AOD145/0023/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168777/ESDs/pass2/AOD145/0003/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168076/ESDs/pass2/AOD145/1036/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0432/AliAOD.root", 0}
  //                        :
  //                         {"/alice/data/2011/LHC11h_2/000169144/ESDs/pass2/AOD145/0363/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000169144/ESDs/pass2/AOD145/0023/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168777/ESDs/pass2/AOD145/0003/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168076/ESDs/pass2/AOD145/1036/AliAOD.root",
  //                           "/alice/data/2011/LHC11h_2/000168988/ESDs/pass2/AOD145/0432/AliAOD.root", 0};
  //
  // const char ** strptr = filenames;
  //
  // while (*strptr) {
  //   cout << *strptr << '\n';
  //   input_files->Add(*strptr++);
  // }
/*
  const char fmt[] = "/alice/data/2015/LHC15o/000245145/pass1/AOD/%03d/AliAOD.root";
  int start = 5 * (id - 1) + 1,
       stop = 5 * id + 1;

  cout << "ID: " << id << "  " << start << " -- " << stop << "\n";
  for (int i = start; i < stop; ++i) {
    cout << TString::Format(fmt, i) << "\n";
    input_files->Add(TString::Format(fmt, i));
  }
*/
  return input_files;
}
