/**
 * RunMe.C
 *
 * My ROOT macro entry point
 */

bool rungrid = false;
bool force_exit = false;
bool is_mc_analysis = false;

bool is_2015_data = true;

TDatime date;

TString grid_output_dir = "output";
TString grid_working_dir = "work_pipi";
TString subdir = "mult_selection.CL0";

TString runmode =
  // "full";
   "terminate";


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

TString macro_config = ""
"+p; "
"{0:50}; "

"~do_avg_sep_cf = false; "
"~do_deltaeta_deltaphi_cf = false; "
// "@verbose = true; "

"@enable_pair_monitors = false;"
"@min_coll_size = 1; "

"$event_VertexZMin = -8; "
"$event_VertexZMax = 8; "

"$pion_1_PtMin = 0.14; "
"$pion_1_PtMax = 2.0; "
"$pion_1_max_impact_z = 0.15; "
"$pion_1_max_impact_xy = 0.2; "
"$pion_1_max_tpc_chi_ndof = 0.010; "
"$pion_1_max_its_chi_ndof = 0.010;"
;

TString output_filename = "PiPi_Analysis_Results.root";
TString xml_filename =
 "";
  // "/alice/cern.ch/user/a/akubera/xml/"
    // "15o.m00.xml";
    // "m00";

int use_runs[] = // {170163, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 0};
//int use_runs[] = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 0};
//int use_runs[]   = {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 0};
// int use_runs[]= {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163, 0};
//  int good_runs[21]={170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163};
/*
{ 246994, 246991, 246989, 246984, 246982, 246980, 246949, 246948, 246945,
  246942, 246937, 246930, 246928, 246871, 246870, 246867, 246865, 246864,
  246859, 246858, 246855, 246851, 246847, 0 };
*/
 { 244918, 0 };

void
RunGrid()
{
  cout << "[RunMe] Begin\n";
  cout << "        XML : " << xml_filename << "\n";
  bool is_mc_analysis = kFALSE;

  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "PiPi Manager");

  AliAnalysisAlien *alienHandler = new AliAnalysisAlien();
  if (!alienHandler) {
    cerr << "Error. Could not create Alien Handler. Exiting.\n";
    exit(1);
  }

  grid_working_dir += (is_2015_data) ? "/15o" : "/11h";
  grid_working_dir += TString::Format("/2016-%02d-%02d/%s", date.GetMonth(), date.GetDay(), subdir.Data());

  alienHandler->SetOverwriteMode();
  alienHandler->SetRunMode(runmode);
  alienHandler->SetAPIVersion("V1.1x");
  alienHandler->SetAliPhysicsVersion("vAN-20160119-1");
  alienHandler->SetRunPrefix("000");
  alienHandler->SetDropToShell(kFALSE);

  alienHandler->AddIncludePath("$ALICE_PHYSICS/include");

  if (xml_filename != "") {
    cout << "Adding data file: " << xml_filename << "\n";
    alienHandler->AddDataFile(xml_filename);
    alienHandler->SetNrunsPerMaster(30);

  } else {
    cout << "Using secified runs.\n";
    // No XML file or runs specified
    int i = 0;
    while (use_runs[i]) {
      runs.insert(use_runs[i++]);
    }

    if (runs.size()) {
      for (std::set<int>::iterator it = runs.begin(); it != runs.end(); ++it) {
        alienHandler->AddRunNumber(*it);
      }
      alienHandler->SetNrunsPerMaster((int)runs.size());
    }
  }

 alienHandler->SetAdditionalLibs("ConfigFemtoAnalysis.C");

  if (is_2015_data) {
    // 2015
    alienHandler->SetGridDataDir("/alice/data/2015/LHC15o");
    alienHandler->SetDataPattern("*pass1/AOD/*/AliAOD.root");
  } else {
    // 2011
    alienHandler->SetGridDataDir("/alice/data/2011/LHC11h_2");
    alienHandler->SetDataPattern("*ESDs/pass2/AOD145/*/AliAOD.root");
  }

  alienHandler->SetGridWorkingDir(grid_working_dir);
  alienHandler->SetGridOutputDir(grid_output_dir);

  alienHandler->SetCheckCopy(kFALSE);

  alienHandler->SetMergeViaJDL(kTRUE);

  alienHandler->SetMaxMergeFiles(30);
  alienHandler->SetMaxMergeStages(3);
  alienHandler->SetSplitMaxInputFileNumber(40);

  mgr->SetGridHandler(alienHandler);

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  mgr->SetInputEventHandler(input_handler);


  const Int_t collision_trigger = AliVEvent::kINT7;


  gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
  AddTaskMultSelection()->SetSelectedTriggerClass(collision_trigger);
  // AliMultSelectionTask *mult_task = AddTaskMultSelection(kFALSE);
  // mult_task->SetSelectedTriggerClass(collision_trigger);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  // gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  // AddTaskVZEROEPSelection();

  // Create the AliFemto task using configuration from ConfigFemtoAnalysis.C
  AliAnalysisTaskFemto *pipitask = new AliAnalysisTaskFemto(
    "PiPiTask",
    // "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysis.C",
   "ConfigFemtoAnalysis.C",
    "\"" + macro_config + "\"",
    kFALSE
  );

  mgr->AddTask(pipitask);

  CreateContainer(mgr, pipitask);

  pipitask->SelectCollisionCandidates(collision_trigger);

  if (!mgr->InitAnalysis()) {
    cerr << "Error Initting Analysis. Exiting.\n";
    exit(1);
  }

  mgr->PrintStatus();
  mgr->StartAnalysis("grid");

  cout << "Done." << std::endl;
}


void
CreateContainer(AliAnalysisManager *mgr, AliAnalysisTask *task)
{
  AliAnalysisDataContainer *femtolist = mgr->CreateContainer(
    "femtolist",
    TList::Class(),
    AliAnalysisManager::kOutputContainer,
    output_filename
  );

  mgr->ConnectOutput(task, 0, femtolist);
  mgr->ConnectInput(task, 0, mgr->GetCommonInputContainer());
}
