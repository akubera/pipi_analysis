/**
 * RunEta.C
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
  // 2015;
  2017;

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


#include "Datasets.h"

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

TString aliphysics_version = "vAN-20170123-1";

TString output_filename = "PiPi_Analysis_Results.root";

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
// {245064, 0};

// LHC12a17a_fix
// { 168777, 0};

// { 167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108, 0, 168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458, 168460, 168464, 168467, 168511, 0};

// { 167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108, 168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458, 168460, 168464, 168467, 168511, 168512, 168514, 168777, 168826, 168988, 168992, 169035, 169040, 169044, 169045, 169091, 169094, 169099, 169138, 169144, 169145, 169148, 169156, 169160, 169167, 169238, 169411, 169415, 169417, 169418, 169419, 169420, 169475, 169498, 169504, 169506, 169512, 169515, 169550, 169553, 169554, 169555, 169557, 169586, 169587, 169588, 169590, 169591, 169835, 169837, 169838, 169846, 169855, 169858, 169859, 169923, 169965, 170027, 170040, 170081, 170083, 170084, 170085, 170088, 170089, 170091, 170155, 170159, 170163, 170193, 170203, 170204, 170207, 170228, 170230, 170268, 170269, 170270, 170306, 170308, 170309, 170311, 170312, 170313, 170315, 170387, 170388, 170572, 170593, 0};

// {246751, 0};
// const TString data_selection = "LHC16k3b";

{244918, 244975, 244980, 244982, 244983, 245061, 245064, 245066, 245068, 245145, 245146, 245148, 245151,
 245152, 245231, 245232, 245259, 245343, 245345, 245346, 245347, 245349, 245353, 245396, 245397, 245401,
 245407, 245409, 245410, 245411, 245439, 245441, 245446, 245450, 245452, 245454, 245496, 245497, 245501,
 245504, 245505, 245507, 245535, 245540, 245542, 245543, 245544, 245545, 245554, 245683, 245692, 245700,
 245702, 245705, 245729, 245731, 245738, 245752, 245759, 245766, 245775, 245785, 245793, 245829, 245831,
 245833, 245923, 245949, 245952, 245954, 246001, 246003, 246012, 246036, 246037, 246042, 246048, 246049,
 // 246052, 246053, 246087, 246089, 246113, 246115, 246151, 246152, 246153, 246178, 246180, 246181, 246182,
 // 246185, 246217, 246222, 246225, 246271, 246272, 246275, 246276, 246390, 246391, 246392, 246424, 246428,
 // 246431, 246434, 246487, 246488, 246493, 246495, 246553, 246575, 246583, 246648, 246675, 246676, 246750,
 // 246751, 246757, 246758, 246759, 246760, 246763, 246765, 246766, 246804, 246805, 246807, 246808, 246809,
 246810, 246844, 246845, 246846, 246847, 246851, 246865, 246867, 246870, 246871, 246928, 246945, 246948,
 246980, 246982, 246984, 246989, 246991, 246994, 0};
const TString data_selection = "LHC17a1a"; // Pb-Pb, 5.02 TeV - Hijing+injected Xi high pt 0-10% cent (LHC15o), ALIROOT-7082



void
RunEta()
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

  // get configuration from macro
  gROOT->LoadMacro("src/CommonConfig.C");
  CommonConfig();

  std::cout << "CONFIG\n" << macro_config << "\n\n---\n";

  if (data_year >= 2015) {
    collision_trigger = AliVEvent::kINT7;
  }

  // Create Analysis Manager
  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "PiPi Manager");

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  input_handler->CreatePIDResponse(is_mc_analysis);
  mgr->SetInputEventHandler(input_handler);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  if (data_year >= 2015) {
    gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
    AliMultSelectionTask * mult_task = AddTaskMultSelection();
    mult_task->SetSelectedTriggerClass(collision_trigger);
  }

  subdir = TString::Format("%06d", date.GetTime());
  // subdir = "220409";

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  mgr->SetInputEventHandler(input_handler);

  // if (is_run2_data) {
  //   gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
  //   AddTaskMultSelection()->SetSelectedTriggerClass(collision_trigger);
  // }
  // AliMultSelectionTask *mult_task = AddTaskMultSelection(kFALSE);
  // mult_task->SetSelectedTriggerClass(collision_trigger);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  // gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  // AddTaskVZEROEPSelection();

  const TString macro_filename =          "ConfigFemtoAnalysisDeta.C";

  // Create the AliFemto task using configuration from ConfigFemtoAnalysis.C
  AliAnalysisTaskFemto *pipitask = new AliAnalysisTaskFemto(
    "PiPiTask",
    macro_filename,
    macro_config,
    kFALSE
  );

  pipitask->SelectCollisionCandidates(collision_trigger);

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


  TChain *input_files = load_sim_LHC15k1a1(); //  load_sim_LHC16g1(); //(data_year == 2015) ? (is_mc_analysis ? load_2015_sim() : load_2015_data())
                                              // :  load_file_set();
    //load_files(new TChain("aodTree"));

  if (!mgr->InitAnalysis()) {
    cerr << "Error Initting Analysis. Exiting.\n";
    exit(1);
  }

  mgr->PrintStatus();
  mgr->StartAnalysis("local", input_files);

  timer.Stop();
  timer.Print();
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


TChain*
load_2015_data(TChain *input_files=NULL)
{
  if (!input_files) {
    input_files = new TChain("aodTree");
  }

  input_files->Add("/alice/data/2015/LHC15o/000246001/pass1/AOD/001/AliAOD.root");
  input_files->Add("/alice/data/2015/LHC15o/000246001/pass1/AOD/002/AliAOD.root");
  input_files->Add("/alice/data/2015/LHC15o/000246001/pass1/AOD/003/AliAOD.root");

  // input_files->Add("/alice/data/2015/LHC15o/000246390/pass2_lowIR/AOD/001/AliAOD.root");

  // input_files->Add("/alice/data/2015/LHC15o/000246984/pass1/AOD/001/AliAOD.root");
  // input_files->Add("/alice/data/2015/LHC15o/000244918/pass1/AOD/041/AliAOD.root");
  return input_files;
}

TChain*
load_2015_sim(TChain *input_files=NULL)
{
  if (!input_files) {
    input_files = new TChain("aodTree");
  }

  input_files->Add("/alice/sim/2015/LHC15k1a1/244975/001/AliAOD.root");
  input_files->Add("/alice/sim/2015/LHC15k1a1/244975/002/AliAOD.root");
  input_files->Add("/alice/sim/2015/LHC15k1a1/244975/029/AliAOD.root");
  return input_files;
}


TChain*
load_sim_LHC16k3b2(TChain *input_files=NULL)
{
    if (!input_files) {
    input_files = new TChain("aodTree");
  }

  // std::vector<int> numbers = {1, 2, 3, 4, 5, 6, 999};
  // for (int number : numbers) {

  int numbers[] =  {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 24, 999, 17149, 0};
  for (int *num_ptr = numbers, number = *num_ptr; number > 0; number = *++num_ptr) {
    const TString filename = TString::Format("/alice/sim/2016/LHC16k3b2/246751/%03d/AliAOD.root", number);
    std::cout << " Adding: " << filename << "\n";
    input_files->Add(filename);
  }

  return input_files;

}

TChain*
load_sim_LHC16g1(TChain *input_files=NULL)
{
    if (!input_files) {
    input_files = new TChain("aodTree");
  }

  // std::vector<int> numbers =  {1, 2, 3, 4, 5};
  // for (int number : numbers) {

  int numbers[] =  {1, 2, 3, 4, 5, 11, 20, 29, 33, 38, 45, 49, 70, 0};
  // int numbers[] =  {1, 2, 3, 4, 5, 0};
  for (int *num_ptr = numbers, number = *num_ptr; number > 0; number = *++num_ptr) {
    const TString filename = TString::Format("/alice/sim/2016/LHC16g1/245505/AOD/%03d/AliAOD.root", number);
    std::cout << " Adding: " << filename << "\n";
    input_files->Add(filename);
  }

  return input_files;
}


TChain*
load_sim_LHC15k1a1(TChain *input_files=NULL)
{
  if (!input_files) {
     input_files = new TChain("aodTree");
  }

  int numbers[] = {11, 800, 0};
  for (int *num_ptr = numbers, number = *num_ptr; number > 0; number = *++num_ptr) {
    const TString filename = TString::Format("/alice/sim/2015/LHC15k1a1/245064/AOD/%03d/AliAOD.root", number);
    std::cout << " Adding: " << filename << "\n";
    input_files->Add(filename);
  }

  return input_files;
}
