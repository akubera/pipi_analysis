/**
 * RunMe.C
 *
 * My ROOT macro entry point
 */

bool rungrid = false;
bool force_exit = false;
bool is_mc_analysis = false;

TString grid_working_dir = "Multi_PiLam_v01";
TString runmode = "full";
TString run_xml_file;


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

TString output_filename = "MultiResults.root",
           femto_config = "ConfigFemtoAnalysis.C";

// std::vector<TString> local_libraries = {"PilamEventCut.cxx"};

TString local_library_string =
//   " PilamKStarByAvgSep.cxx"
  // " PilamEventCut.cxx"
  // " PilamPionCut.cxx"
  // " PilamLambdaCut.cxx"
  // " PilamPairCut.cxx"
  // " KuberCF.cxx"
  // " PilamKStarByAvgSep.cxx"
  // " PilamMultiAnalysis.cxx"
  "";

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

  // Setup includes
  gInterpreter->AddIncludePath("$ALICE_ROOT/include");
  gInterpreter->AddIncludePath("$ALICE_PHYSICS/include");

  gSystem->Load("libOADB.so");

  TObjArray* libraries = local_library_string.Tokenize(" ");
  TIter lib_iter(libraries);
  TObjString *next = NULL;
  bool success = true;
  while ((next = (TObjString*)lib_iter())) {
   //     local_libraries.push_back(next->GetString());
// gInterpreter->LoadMacro(next->GetString() + "+g", (TInterpreter::EErrorCode*)&status);
//     gROOT-> ProcessLineSync (TString(".L ") + next->GetString() + "+g", &status);
//     gROOT->ProcessLineSync(".!echo $?");
    int status = gROOT->LoadMacro(next->GetString() + "+g");

    if (status != 0) {
      success = false;
    }
  }
  delete libraries;

  if (!success) {
    cerr << "\033[1;31mError:\033[1;0m"
            " Local libraries did NOT compile. Fix the error and try again.\n";
    return;
  }

  cout << "Local libraries compiled successfull.\n";

  // if (gROOT->LoadMacro("macros/utils.C")) {
  //   cerr << "\033[1;31mError:\033[1;0m"
  //           " Could not load utility macro 'macros/utils.C' Please fix.\n";
  //   return;
  // }

  // process_arguments();

  // No XML file or runs specified
  if (run_xml_file == "" && runs.size() == 0) {
    cout << "Runs not specified - Using default.\n";
    int i = 0;
    while (use_runs[i]) {
      runs.insert(use_runs[i++]);
    }
  }

  // Create Analysis Manager
  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "My Analysis Manager");
  // mgr->SetDebugLevel(2);
  //    mgr->SetUseProgressBar(kTRUE);

  if (rungrid) {
    cout << "*** Setting up grid.\n";
    gROOT->LoadMacro("SetupGrid.C");
    AliAnalysisAlien *alienHandler = SetupGrid();
    mgr->SetGridHandler(alienHandler);
  }

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  // input_handler->CreatePIDResponse(is_mc_analysis ? kFALSE : kTRUE);
  input_handler->CreatePIDResponse(is_mc_analysis);
  mgr->SetInputEventHandler(input_handler);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  AddTaskVZEROEPSelection();

  // Create the AliFemto task using configuration from ConfigFemtoAnalysis.C
  AliAnalysisTaskFemto *pilamtask = new AliAnalysisTaskFemto(
    "PilamTask",
    femto_config,
    "",
    kFALSE
  );

  pilamtask->SelectCollisionCandidates(AliVEvent::kMB | AliVEvent::kCentral | AliVEvent::kSemiCentral);
  //  pilamtask->SelectCollisionCandidates(AliVEvent::kMB);
  //  pilamtask->SelectCollisionCandidates(AliVEvent::kSemiCentral);
  //  pilamtask->SelectCollisionCandidates(AliVEvent::kCentral);

  //  pilamtask->SelectCollisionCandidates(AliVEvent::kAny);

  // ((TCollection*)pilamtask->GetOutputData(0))->SetOwner();

  // MyTask *pilamtask = new MyTask("TaskFemto", "ConfigFemtoAnalysis.C", "", kTRUE);

  AliAnalysisDataContainer *femtolist = mgr->CreateContainer("femtolist",
          TList::Class(),
          AliAnalysisManager::kOutputContainer,
          output_filename.Data());

  mgr->AddTask(pilamtask);
  bool out_cnx = mgr->ConnectOutput(pilamtask, 0, femtolist);
  mgr->ConnectInput(pilamtask, 0, mgr->GetCommonInputContainer());

  /*
    mgr->AddTask(taskfemto_1);
    mgr->ConnectOutput(taskfemto_1, 0, lam_pip);
    mgr->ConnectInput(taskfemto_1, 0, mgr->GetCommonInputContainer());
   */

  if (!mgr->InitAnalysis()) {
    cerr << "Error Initting Analysis. Exiting.\n";
    exit(1);
  }

  mgr->PrintStatus();

  if (rungrid) {
    gROOT->ProcessLine(".include");
    mgr->StartAnalysis("grid");
  } else {
    TChain *input_files = new TChain("aodTree");
    //input_files->SetOwner();
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
          ifstream file_list("short_file_list.txt");
          // ifstream file_list("local_files.txt");
          while (file_list.good()) {
            std:string line;
            std::getline(file_list, line);
            if (line[0] == '/') {
                cout << "Adding file '" << line <<"'\n";
                input_files->Add(line.c_str());}
            }
      // input_files->Add("/alice/data/2011/LHC11h_2/000170593/ESDs/pass2/AOD/0001/AliAOD.root");
      input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0001/AliAOD.root");
//      input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0002/AliAOD.root");
//      input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0003/AliAOD.root");
//      input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0004/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0005/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0026/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/0034/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000169506/ESDs/pass2/AOD145/1226/AliAOD.root");
      //
      // input_files->Add("/alice/data/2011/LHC11h_2/000167987/ESDs/pass2/AOD145/0793/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000168108/ESDs/pass2/AOD145/0411/AliAOD.root");
      //
      // input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0026/AliAOD.root");
      // input_files->Add("/alice/data/2011/LHC11h_2/000168514/ESDs/pass2/AOD145/0100/AliAOD.root");
    }

    mgr->StartAnalysis("local", input_files);

    std::cout << ConfigFemtoAnalysis()->Finish() << '\n';
  }

  if (force_exit) {
    gSystem->Exit(0);
  }
}
