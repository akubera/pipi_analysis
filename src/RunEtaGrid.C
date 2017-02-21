/**
 * RunEtaGrid.C
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

int data_year = 0;
  // 2010;
//   2011;
  // 2012;
//    2015;
  // 2017;

TString runmode =
  "full";
  // "terminate";


bool is_run2_data = false;


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
  // "LHC17a1a.xml";

const TString dataset_name = "LHC11h_AOD145-FemtoMinus-1";

void
RunEtaGrid()
{
  cout << "[RunEtaGrid] Begin\n";
  cout << "        XML : " << xml_filename << "\n";

  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "PiPi Manager");

  data_year = 2000 + TString(dataset_name(3, 2)).Atoi();
  is_run2_data = data_year >= 2015;
  cout << "       YEAR : " << data_year << " " << (is_run2_data ? "(run2)" : "(run1)") << "\n";

  // get configuration from macro
  gROOT->LoadMacro("src/CommonConfig.C");
  CommonConfig();

  subdir = TString::Format("%06d", date.GetTime());
  // subdir = "220409";
//   data_year

  grid_working_dir += (data_year == 2017) ? "/17"
                    : (data_year == 2015) ? "/15o"
                    : (data_year == 2011) ? "/11h"
                    : (data_year == 2010) ? "/10h"
                    : (data_year == 2012) ? "/12"
                    : "unknown";

  grid_working_dir += TString::Format("/2017-%02d-%02d/%s", date.GetMonth(), date.GetDay(), subdir.Data());

  AliAnalysisAlien *alienHandler = CreateAlienHandler(dataset_name);
  mgr->SetGridHandler(alienHandler);

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  mgr->SetInputEventHandler(input_handler);

  if (is_run2_data) {
    gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
    AddTaskMultSelection()->SetSelectedTriggerClass(collision_trigger);
  }
  // AliMultSelectionTask *mult_task = AddTaskMultSelection(kFALSE);
  // mult_task->SetSelectedTriggerClass(collision_trigger);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  // gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  // AddTaskVZEROEPSelection();

  const TString macro_filename = "ConfigFemtoAnalysisDeta.C";

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


AliAnalysisAlien*
CreateAlienHandler(const TString &dataset)
{
  AliAnalysisAlien *alienHandler = new AliAnalysisAlien();
  if (!alienHandler) {
    cerr << "Error. Could not create Alien Handler. Exiting.\n";
    exit(1);
  }

  alienHandler->SetOverwriteMode();
  alienHandler->SetRunMode(runmode);
  alienHandler->SetAPIVersion("V1.1x");
  alienHandler->SetAliPhysicsVersion(aliphysics_version);
  if (!is_mc_analysis) {
    alienHandler->SetRunPrefix("000");
  }
  alienHandler->SetDropToShell(kFALSE);
  alienHandler->AddIncludePath("$ALICE_PHYSICS/include");

  gROOT->LoadMacro("src/Datasets.C+");

  SetupAlienPaths(*alienHandler, dataset);

  if (xml_filename != "") {
    cout << "Adding data file: " << xml_filename << "\n";
    alienHandler->AddDataFile(xml_filename);
    alienHandler->SetNrunsPerMaster(30);
  } else {
    cout << "Using secified runs.\n";
    load_runs(*alienHandler, dataset);
  }

  alienHandler->SetAdditionalLibs("ConfigFemtoAnalysisDeta.C "
                                  "AliFemtoCorrFctnEtaDEta.h AliFemtoCorrFctnEtaDEta.cxx");

  alienHandler->SetGridWorkingDir(grid_working_dir);
  alienHandler->SetGridOutputDir(grid_output_dir);

  alienHandler->SetCheckCopy(kFALSE);

  alienHandler->SetMergeViaJDL(kTRUE);

  alienHandler->SetMaxMergeFiles(30);
  alienHandler->SetMaxMergeStages(3);
  alienHandler->SetSplitMaxInputFileNumber(18);

  return alienHandler;
}
