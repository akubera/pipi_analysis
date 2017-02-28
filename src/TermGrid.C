/**
 * RunMe.C
 *
 * My ROOT macro entry point
 */

bool rungrid = false;
bool force_exit = false;

bool use_local_config = false;

TDatime date;

TString grid_output_dir = "output";
TString grid_working_dir = "work_pipi";
TString subdir = "default";

int data_year =
  // 2010;
  // 2011;
  2015;

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


// Global Configuration - set by CommonConfig.C
bool is_mc_analysis;

TString macro_config;
Int_t collision_trigger;

TString aliphysics_version = "vAN-20170214-1";

TString output_filename = "PiPi_Analysis_Results.root";
TString xml_filename =
 "";
  // "/alice/cern.ch/user/a/akubera/xml/"
    // "15o.m00.xml";
    // "m00";

int use_runs[] =
// {170163, 0};

// {170593, 170572, 170388, 170387, 0};

// {170593, 170572, 170388, 170387, 170315, 170313, 170312, 0};
// {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 0};

// int use_runs[]= {170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163, 0};
//  int good_runs[21]={170593, 170572, 170388, 170387, 170315, 170313, 170312, 170311, 170309, 170308, 170306, 170270, 170269, 170268, 170230, 170228, 170207, 170204, 170203, 170193, 170163};
/*
{ 246994, 246991, 246989, 246984, 246982, 246980, 246949, 246948, 246945,
  246942, 246937, 246930, 246928, 246871, 246870, 246867, 246865, 246864,
  246859, 246858, 246855, 246851, 246847, 0 };
*/
 // LHC15o (++) pp.0
 // { 244918, 244982, 244983, 0 };
 // { 244982, 0 };
  // { 244918, 0 };
// {246994, 246991, 246989, 246984, 246982, 246980, 246948, 246945, 246928, 246851, 246847,
//  246846, 246845, 246844, 246810, 246809, 246808, 246807, 246805, 246804, 246766, 246765,
//  // 246763, 246760, 246759, 246758, 246757, 246751, 246750, 246676, 246675, 246495, 246493,
//  // 246488, 246487, 246434, 246431, 246428, 246424, 246276, 246275, 246272, 246271, 246225,
//  // 246222, 246217, 246185, 246182, 246181, 246180, 246178, 246153, 246152, 246151, 246115,
//  // 246113, 246089, 246087, 246053, 246052, 246049, 246048, 246042, 246037, 246036, 246012,
//  246003, 246001, 245954, 245952, 245949, 245923, 245833, 245831, 245829, 245705, 245702,
//  245700, 245692, 245683, 0};

/// LHC10
// {137231, 137366, 0};
// {137431, 137432, 137434, 137441, 137539, 137541, 137544, 137549, 137595, 137608, 0};
// { 137638, 137686,137691, 137692, 137704, 137718, 137722, 137724, 137748, 137751, 137752,
//   137843, 137848, 138190, 138192, 138197, 138200, 138201, 138225, 13827, 0};


// { 137231, 137366, 137431, 137432, 137434, 137441, 137539, 137541, 137544,
//   137549, 137595, 137608, 137638, 137686, 137691, 137692, 137704, 137718,
//   137722, 137724, 137748, 137751, 137752, 137843, 137848, 138190, 138192,
//   138197, 138200, 138201, 138225, 13827, 0}

// // LHC10h ()++)
// {138359, 138364, 138396, 138439, 138442, 138469, 138534, 138578, 138582, 138583, 138621, 138624,
// 138638, 138653, 138662, 138666, 138740, 138796, 138837, 138870, 138871, 138978, 138979, 139029,
// 139036, 139037, 139038, 139042, 139107, 139173, 139309, 139310, 139314, 139328, 139329, 139437,
// 139438, 139440, 139441, 139465, 139507, 139510, 139511, 139513, 0};

// LHC10h ()++)
{245064, 0};


void
TermGrid()
{
  cout << "[RunMe] Begin\n";
  cout << "        XML : " << xml_filename << "\n";

  AliAnalysisAlien *alienHandler = new AliAnalysisAlien();
  if (!alienHandler) {
    cerr << "Error. Could not create Alien Handler. Exiting.\n";
    exit(1);
  }

  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "PiPi Manager");

  // get configuration from macro
  gROOT->LoadMacro("src/CommonConfig.C");
  CommonConfig();

  subdir = TString::Format("%06d", date.GetTime());
  // subdir = "220409";

  grid_working_dir += (data_year == 2015) ? "/15o"
                    : (data_year == 2011) ? "/11h"
                    : (data_year == 2010) ? "/10h"
                    : "/unknown";

  grid_working_dir += TString::Format("/2016-%02d-%02d/%s", date.GetMonth(), date.GetDay(), subdir.Data());
  // grid_working_dir += TString::Format("/2016-10-12/%s", subdir.Data());

  grid_working_dir = "work_pipi/15o/2017-02-28/083206";

  alienHandler->SetOverwriteMode();
  alienHandler->SetRunMode(runmode);
  alienHandler->SetAPIVersion("V1.1x");
  alienHandler->SetAliPhysicsVersion(aliphysics_version);
  // alienHandler->SetRunPrefix("000");
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

  if (use_local_config) {
    alienHandler->SetAdditionalLibs("ConfigFemtoAnalysis.C");
  }

  if (data_year == 2015) {
    // 2015
    // alienHandler->SetGridDataDir("/alice/data/2015/LHC15o");
    // // alienHandler->SetDataPattern("*pass1/AOD/*/AliAOD.root");
    // alienHandler->SetDataPattern("*/pass_lowint_firstphys/AOD/*/AliAOD.root");
    alienHandler->SetGridDataDir("/alice/sim/2015/LHC15k1a1");
    alienHandler->SetDataPattern("*/AOD/*/AliAOD.root");
  } else if (data_year == 2011) {
    // 2011
    alienHandler->SetGridDataDir("/alice/data/2011/LHC11h_2");
    alienHandler->SetDataPattern("*ESDs/pass2/AOD145/*/AliAOD.root");
  } else if (data_year == 2010) {
    alienHandler->SetGridDataDir("/alice/data/2010/LHC10h");
    alienHandler->SetDataPattern("*ESDs/pass2/AOD073/*/AliAOD.root");
  }

  alienHandler->SetGridWorkingDir(grid_working_dir);
  alienHandler->SetGridOutputDir(grid_output_dir);

  alienHandler->SetCheckCopy(kFALSE);

  alienHandler->SetMergeViaJDL(kTRUE);

  alienHandler->SetMaxMergeFiles(30);
  alienHandler->SetMaxMergeStages(3);
  alienHandler->SetSplitMaxInputFileNumber(5);

  mgr->SetGridHandler(alienHandler);

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  mgr->SetInputEventHandler(input_handler);

  if (data_year == 2015) {
    gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
    AddTaskMultSelection()->SetSelectedTriggerClass(collision_trigger);
  }
  // AliMultSelectionTask *mult_task = AddTaskMultSelection(kFALSE);
  // mult_task->SetSelectedTriggerClass(collision_trigger);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  // gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  // AddTaskVZEROEPSelection();

//   TString macro_filename = (use_local_config)
//                          ? "ConfigFemtoAnalysis.C"
//                          : (is_2015_data)
//                            ? "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysisRun2.C";
//                            : "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysis.C";

  TString macro_filename = "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysisRun2.C";

  // Create the AliFemto task using configuration from ConfigFemtoAnalysis.C
  AliAnalysisTaskFemto *pipitask = new AliAnalysisTaskFemto(
    "PiPiTask",
    macro_filename,
    macro_config,
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
