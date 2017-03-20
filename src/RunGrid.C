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
  // 2012;
   2015;
  // 2017;

TString runmode =
  "full";
  // "terminate";


const bool is_run2_data = data_year >= 2015;


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

TString aliphysics_version = "vAN-20170201-1";

TString output_filename = "PiPi_Analysis_Results.root";
TString xml_filename =
  "";
  // "/alice/cern.ch/user/a/akubera/xml/"
  // "15o.m00.xml";
  // "m00";
  // "LHC17a1a.xml";

// int use_runs[] =
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
//{ 246994, 246991, 246989, 246984, 246982, 246980, 246948, 246945, 246928, 246871, 246870,
//  246867, 246865, 246864, 246859, 246858, 246851, 246847, 246846, 246845, 246844, 246810,
//  246809, 246808, 246807, 246805, 246804, 246766, 246765, 246763, 246760, 246759, 246758,
//  246757, 246751, 246750, 246676, 246675, 246540, 246495, 246493, 246488, 246487, 246434,
//  246431, 246428, 246424, 246276, 246275, 246272, 246271, 246225, 246222, 246217, 246185,
//  246182, 246181, 246180, 246178, 246153, 246152, 246151, 246148, 246115, 246113, 246089,
//  246087, 246053, 246052, 246049, 246048, 246042, 246037, 246036, 246012, 246003, 246001,
//  245963, 245954, 245952, 245949, 245923, 245833, 245831, 245829, 245705, 245702, 245700,
//  245692, 245683, 0};
// const TString data_selection = "LHC15o_pass1";

// { 245145, 245146, 245148, 245151, 245152, 245231, 245232, 245233, 245259, 245343, 245345, 245346, 245347, 245349, 245353,
//  245396, 245397, 245401, 245407, 245409, 245410, 245411, 245439, 245441, 245446, 245450, 245452, 245453, 245454, 245496,
//  { 245497, 245501, 245504, 245505, 245507, 245535,
//	  245540, 245542, 245543, 245544, 245545, 245554, 0};
// const TString data_selection = "LHC15o_pass1_pidfix";

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
// {245064, 0};

// LHC12a17a_fix
// { 168777, 0};

// { 167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108, 0, 168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458, 168460, 168464, 168467, 168511, 0};

// { 167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108, 168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458, 168460, 168464, 168467, 168511, 168512, 168514, 168777, 168826, 168988, 168992, 169035, 169040, 169044, 169045, 169091, 169094, 169099, 169138, 169144, 169145, 169148, 169156, 169160, 169167, 169238, 169411, 169415, 169417, 169418, 169419, 169420, 169475, 169498, 169504, 169506, 169512, 169515, 169550, 169553, 169554, 169555, 169557, 169586, 169587, 169588, 169590, 169591, 169835, 169837, 169838, 169846, 169855, 169858, 169859, 169923, 169965, 170027, 170040, 170081, 170083, 170084, 170085, 170088, 170089, 170091, 170155, 170159, 170163, 170193, 170203, 170204, 170207, 170228, 170230, 170268, 170269, 170270, 170306, 170308, 170309, 170311, 170312, 170313, 170315, 170387, 170388, 170572, 170593, 0};

// {246751, 0};
// const TString data_selection = "LHC16k3b";

//{244918, 244975, 244980, 244982, 244983, 245061, 245064, 245066, 245068, 245145, 245146, 245148, 245151,
// 245152, 245231, 245232, 245259, 245343, 245345, 245346, 245347, 245349, 245353, 245396, 245397, 245401,
// 245407, 245409, 245410, 245411, 245439, 245441, 245446, 245450, 245452, 245454, 245496, 245497, 245501,
// 245504, 245505, 245507, 245535, 245540, 245542, 245543, 245544, 245545, 245554, 245683, 245692, 245700,
// 245702, 245705, 245729, 245731, 245738, 245752, 245759, 245766, 245775, 245785, 245793, 245829, 245831,
// 245833, 245923, 245949, 245952, 245954, 246001, 246003, 246012, 246036, 246037, 246042, 246048, 246049,
 // 246052, 246053, 246087, 246089, 246113, 246115, 246151, 246152, 246153, 246178, 246180, 246181, 246182,
 // 246185, 246217, 246222, 246225, 246271, 246272, 246275, 246276, 246390, 246391, 246392, 246424, 246428,
 // 246431, 246434, 246487, 246488, 246493, 246495, 246553, 246575, 246583, 246648, 246675, 246676, 246750,
 // 246751, 246757, 246758, 246759, 246760, 246763, 246765, 246766, 246804, 246805, 246807, 246808, 246809,
// 246810, 246844, 246845, 246846, 246847, 246851, 246865, 246867, 246870, 246871, 246928, 246945, 246948,
// 246980, 246982, 246984, 246989, 246991, 246994, 0};
//const TString data_selection = "LHC17a1a"; // Pb-Pb, 5.02 TeV - Hijing+injected Xi high pt 0-10% cent (LHC15o), ALIROOT-7082


  const TString data_selection = "LHC11h_AOD145-FemtoMinus";

void
RunGrid()
{
  cout << "[RunMe] Begin\n";
  cout << "        XML : " << xml_filename << "\n";

  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "PiPi Manager");

  // get configuration from macro
  gROOT->LoadMacro("src/CommonConfig.C");
  CommonConfig();

  subdir = TString::Format("%06d", date.GetTime());
  // subdir = "220409";


  macro_config = "+p;
{0:5:10:20:30:50:70};
~do_deltaeta_deltaphi_cf=true;
~do_kt_qinv=true;
~do_trueq_cf=false;
~do_kt_q3d=false;
~qinv_bin_size_MeV=2.5;
@is_mc_analysis = true;
@enable_pair_monitors = true;
@output_settings = false;
@min_coll_size = 100;
@num_events_to_mix = 2;
$pair_delta_eta_min = 0.00;
$pair_delta_phi_min = 0.00;
$pion_1_PtMin = 0.14;
$pion_1_PtMax = 2.0;
$pion_1_max_impact_z = 3.0;
$pion_1_max_impact_xy = 2.4;
$pion_1_max_tpc_chi_ndof = 3.010;
$pion_1_max_its_chi_ndof = 3.010;
                   ";

  grid_working_dir += (data_year == 2017) ? "/17"
                    : (data_year == 2015) ? "/15o"
                    : (data_year == 2011) ? "/11h"
                    : (data_year == 2010) ? "/10h"
                    : (data_year == 2012) ? "/12"
                    : "unknown";

  grid_working_dir += TString::Format("/2017-%02d-%02d/%s", date.GetMonth(), date.GetDay(), subdir.Data());
  // grid_working_dir += TString::Format("/2016-10-12/%s", subdir.Data());

  AliAnalysisAlien *alienHandler = CreateAlienHandler(data_selection);
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

  const TString macro_filename = (use_local_config)
                               ? "ConfigFemtoAnalysis.C"
                               : "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysisRun2.C";
                              //  : "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysis.C";

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
    // No XML file or runs specified
    /*int i = 0;
    while (use_runs[i]) {
      runs.insert(use_runs[i++]);
    }

    if (runs.size()) {
      for (std::set<int>::iterator it = runs.begin(); it != runs.end(); ++it) {
        alienHandler->AddRunNumber(*it);
    }*/
  }

  if (use_local_config) {
    alienHandler->SetAdditionalLibs("ConfigFemtoAnalysis.C");
  }

  alienHandler->SetGridWorkingDir(grid_working_dir);
  alienHandler->SetGridOutputDir(grid_output_dir);

  alienHandler->SetCheckCopy(kFALSE);

  alienHandler->SetMergeViaJDL(kTRUE);

  alienHandler->SetMaxMergeFiles(30);
  alienHandler->SetMaxMergeStages(3);
  alienHandler->SetSplitMaxInputFileNumber(18);

  return alienHandler;
}
