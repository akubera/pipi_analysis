/**
 * RunMe.C
 *
 * My ROOT macro entry point
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

void process_arguments();

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
"@verbose = true; "
"@min_coll_size = 40; "
"$pion_1_max_impact_z = 0.15; "
"$pion_1_max_impact_xy = 0.2; "
"$pion_1_max_tpc_chi_ndof = 0.025; "
"$pion_1_max_its_chi_ndof = 0.025; "
// "$pair_delta_eta_min = 0.02; "
// "$pair_delta_phi_min = 0.04; "

"\"";

int use_runs[] = {170163, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 0};
//int use_runs[]   = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 0};
// int use_runs[]= {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163, 0};
//  int good_runs[21]={170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163};

void
RunMe()
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

  // process_arguments();

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
    // AliVEvent::kMB
    // AliVEvent::kCentral
    // | AliVEvent::kSemiCentral
    // | AliVEvent::kAny
    AliVEvent::kINT7
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

  TChain *input_files = load_files(new TChain("aodTree"));

  mgr->StartAnalysis("local", input_files);

  timer.Stop();
  timer.Print();
}


TChain*
load_files(TChain *input_files = NULL)
{
  if (!input_files) {
    input_files = new TChain("aodTree");
  }

  if (is_mc_analysis) {

      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0001/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0002/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0003/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0004/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0005/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0006/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0007/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0008/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0009/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0010/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0011/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0012/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0013/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0014/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0015/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0016/AliAOD.root");
      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0017/AliAOD.root");

      input_files->Add("/alice/sim/2012/LHC12a17a_fix/170593/AOD149/0034/AliAOD.root");

      ///alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/1226/AliAOD.root");
      // input_files->Add("/alice/sim/2012/LHC12a17d_fix/170593/AOD149/0002/AliAOD.root");
    } else {
/*
          ifstream file_list("short_file_list.txt");
          // ifstream file_list("local_files.txt");
          // int i = 2;
          // ifstream file_list("aod_list_15o.txt");
          while (file_list.good()) {
            std:string line;
            std::getline(file_list, line);
            if (line[0] == '/') {
                cout << "Adding file '" << line <<"'\n";
                input_files->Add(line.c_str());
            }
          }
*/
      // input_files->Add("/alice/data/2011/LHC11h_2/000170593/ESDs/pass2/AOD/0001/AliAOD.root");

      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0001/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0002/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0003/AliAOD.root");

      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0004/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0005/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0026/AliAOD.root");

      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0034/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/1226/AliAOD.root");
      //
      // input_files->Add("/alice/data/2011/LHC11h_2/000167987/ESDs/pass2/AOD145/0793/AliAOD.root");
//       input_files->Add("/alice/data/2011/LHC11h_2/000168108/ESDs/pass2/AOD145/0411/AliAOD.root");
      //
      // input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0026/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0100/AliAOD.root");


       // group 1
       input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/001/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/006/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/002/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/008/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/005/AliAOD.root");

       // group 2
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/007/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/004/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/010/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/009/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/003/AliAOD.root");

        // group 3
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/011/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/012/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/013/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/014/AliAOD.root");
//        input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/015/AliAOD.root");

        // group 4
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/016/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/017/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/018/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/019/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/020/AliAOD.root");

    }
  return input_files;
}
