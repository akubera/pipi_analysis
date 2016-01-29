/**
 * RunMe.C
 *
 * My ROOT macro entry point
 */

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

void process_arguments();

// std::vector<int> runs;
std::set<int> runs;
std::vector<int>* gBitmap;

TString output_filename = "",
         macro_filename =
          //  "$ALICE_PHYSICS/PWGCF/FEMTOSCOPY/macros/Train/PionPionFemto/ConfigFemtoAnalysis.C";
         "ConfigFemtoAnalysis.C";

// Global Configuration - set by CommonConfig.C
bool is_mc_analysis;
bool is_2015_data;
TString macro_config;
Int_t collision_trigger;


void
RunLocal()
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

  // Create Analysis Manager
  AliAnalysisManager *mgr = new AliAnalysisManager("mgr", "My Analysis Manager");

  // Create AOD input event handler
  AliInputEventHandler *input_handler = new AliAODInputHandler();
  input_handler->CreatePIDResponse(is_mc_analysis);
  mgr->SetInputEventHandler(input_handler);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskPIDResponse.C");
  AddTaskPIDResponse(is_mc_analysis);

  gROOT->LoadMacro("$ALICE_PHYSICS/OADB/COMMON/MULTIPLICITY/macros/AddTaskMultSelection.C");
  AliMultSelectionTask *mult_task = AddTaskMultSelection();
  mult_task->SetSelectedTriggerClass(collision_trigger);

  gROOT->LoadMacro("$ALICE_ROOT/ANALYSIS/macros/AddTaskVZEROEPSelection.C");
  AddTaskVZEROEPSelection();

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
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/002/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/003/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/004/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/005/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/006/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/007/AliAOD.root");

       // group 2
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/008/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/010/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/009/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/011/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/012/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/013/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/014/AliAOD.root");

        // group 3
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/015/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/016/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/017/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/018/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/019/AliAOD.root");
      //  input_files->Add("/alice/data/2015/LHC15o/000245145/pass1/AOD/020/AliAOD.root");

    }
  return input_files;
}

TChain*
load_file_set(TChain *input_files = NULL)
{
  if (!input_files) {
    input_files = new TChain("aodTree");
  }

  char **argv = gApplication->Argv();
  int argc = gApplication->Argc();

  Int_t id = TString(argv[argc-1]).Atoi();
  if (id == 0) {
    cout << "Error, bad id num '" << argv[argc-1] << "'. Aborting.\n";
    exit(1);
  }

  const width = 3;

  const char fmt[] = "/alice/data/2015/LHC15o/000244918/pass1/AOD/%03d/AliAOD.root";
  int start = width * (id - 1) + 1,
       stop = width * id + 1;

  cout << "ID: " << id << ": " << start << " -- " << stop << "\n";
  for (int i = start; i < stop; ++i) {
    cout << TString::Format(fmt, i) << "\n";
    input_files->Add(TString::Format(fmt, i));
  }

  return input_files;
}
