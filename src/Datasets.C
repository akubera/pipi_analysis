 ///
/// \file src/Datasets.C
///


#include <map>
#include <set>
#include <vector>
#include <string>
#include <cassert>
#include <iostream>
#include <TChain.h>
#include <TSystem.h>
#include <TString.h>
#include "../.alice/sw/ubuntu1604_x86-64/AliRoot/latest/include/AliAnalysisAlien.h"

// const std::map<std::string, std::vector<int> > DATASETS 
// {{ {"foo", {1,2} }}};

// {
//   // Pb-Pb, 5.02 TeV - Hijing+injected Xi high pt 0-10% cent (LHC15o), ALIROOT-7082
//   {"LHC17a1a",
//   { 244918, 244975, 244980, 244982, 244983, 245061, 245064, 245066, 245068, 245145, 245146, 245148,
//     245151, 245152, 245231, 245232, 245259, 245343, 245345, 245346, 245347, 245349, 245353, 245396,
//     245397, 245401, 245407, 245409, 245410, 245411, 245439, 245441, 245446, 245450, 245452, 245454,
//     245496, 245497, 245501, 245504, 245505, 245507, 245535, 245540, 245542, 245543, 245544, 245545,
//     245554, 245683, 245692, 245700, 245702, 245705, 245729, 245731, 245738, 245752, 245759, 245766,
//     245775, 245785, 245793, 245829, 245831, 245833, 245923, 245949, 245952, 245954, 246001, 246003,
//     246012, 246036, 246037, 246042, 246048, 246049,
//     // 246052, 246053, 246087, 246089, 246113, 246115, 246151, 246152, 246153, 246178, 246180, 246181,
//     // 246182, 246185, 246217, 246222, 246225, 246271, 246272, 246275, 246276, 246390, 246391, 246392,
//     // 246424, 246428, 246431, 246434, 246487, 246488, 246493, 246495, 246553, 246575, 246583, 246648,
//     // 246675, 246676, 246750, 246751, 246757, 246758, 246759, 246760, 246763, 246765, 246766, 246804,
//     // 246805, 246807, 246808, 246809, 246810, 246844, 246845, 246846, 246847, 246851, 246865, 246867,
//     // 246870, 246871, 246928, 246945, 246948,
//     246980, 246982, 246984, 246989, 246991, 246994
//   }},
// 
//   {"LHC16k3b",
//   { 167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108, 168115, 168310,
//     168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458, 168460, 168464, 168467, 168511,
//     168512, 168514, 168777, 168826, 168988, 168992, 169035, 169040, 169044, 169045, 169091, 169094,
//     169099, 169138, 169144, 169145, 169148, 169156, 169160, 169167, 169238, 169411, 169415, 169417,
//     169418, 169419, 169420, 169475, 169498, 169504, 169506, 169512, 169515, 169550, 169553, 169554,
//     169555, 169557, 169586, 169587, 169588, 169590, 169591, 169835, 169837, 169838, 169846, 169855,
//     169858, 169859, 169923, 169965, 170027, 170040, 170081, 170083, 170084, 170085, 170088, 170089,
//     170091, 170155, 170159, 170163, 170193, 170203, 170204, 170207, 170228, 170230, 170268, 170269,
//     170270, 170306, 170308, 170309, 170311, 170312, 170313, 170315, 170387, 170388, 170572, 170593
//   }},
// 
//   {"LHC15o_pass1_pidfix",
//   // { 245540, 245542, 245543, 245544, 245545, 245554 },
//   { 245145, 245146, 245148, 245151, 245152, 245231, 245232, 245233,
//     245259, 245343, 245345, 245346, 245347, 245349, 245353
//   }},
// 
//   {"LHC12a17a_fix",
//   { 168777, 0
//   }}
//   
// };

// extern int data_year;
 bool is_run2_analysis;


void SetupAlienPaths(AliAnalysisAlien &alien, const TString &name)
{
  TString data_dir, data_pattern;

  int data_year = 2000 + name(3, 2).String().Atoi();

  if (name == "LHC15k2b") {
    data_dir = "/alice/sim/2015/LHC15k2b";
    data_pattern = "*/AOD/*/AliAOD.root";
  }
  else if (name == "LHC16a0a") {
    data_dir = "/alice/sim/2016/LHC16a0a";
    data_pattern = "*/AOD/*/AliAOD.root";
  }
  else if (name == "LHC14o_pass0") {
    data_dir = "/alice/data/2014/LHC14o";
    data_pattern = "*pass0/AOD/*/AliAOD.root";
  }
  else if (name == "LHC14o_pass0_pidfix") {
    data_dir = "/alice/data/2014/LHC14o";
    data_pattern = "*/pass0_pidfix/AOD/*/AliAOD.root";
  } 
  
  else if (name == "LHC15o_pass1-1") {
    data_dir = "/alice/data/2015/LHC15o";
    data_pattern = "*/pass1/AOD/*/AliAOD.root";
  }

  else if (name == "LHC15o_pass1_pidfix") {
    data_dir = "/alice/data/2015/LHC15o";
    data_pattern = "*/pass1_pidfix/AOD/*/AliAOD.root";
  }
  else if (name == "LHC15o_pass2_lowIR") {
    data_dir = "/alice/data/2015/LHC15o";
    data_pattern = "*/pass2_lowIR/AOD/*/AliAOD.root";
  } else if (name.BeginsWith("LHC11h_AOD145")) { // (name == "LHC11h_AOD145-FemtoMinus") {
    data_dir = "/alice/data/2011/LHC11h_2";
    data_pattern = "*/ESDs/pass2/AOD145/*/AliAOD.root";
  }
  else if (data_year == 2014) {
    // 2014
       // data_pattern = "*/pass_lowint_firstphys/AOD/*/AliAOD.root";
    data_dir = "/alice/sim/2014/LHC14k0a0";
    data_pattern = "*/AOD/*/AliAOD.root";
  }
  else if (data_year == 2010) {
    // 2010
    data_dir = "/alice/data/2010/LHC10h_1";
    data_pattern = "*ESDs/pass1/AOD144/*/AliAOD.root";
  }
  else if (data_year == 2011) {
    data_dir = "/alice/sim/2011/LHC11a16a_fix";
    data_pattern = "*/AOD148/*/AliAOD.root";
  }
  else if (data_year == 2009) {
    data_dir = "/alice/data/2009/LHC9h";
    data_pattern = "*ESDs/pass1/AOD72/*/AliAOD.root";
  }
  else {
    std::cerr << "[ConfigAlienHandler] Unknown dataset name '" << name << "'. Aborting.\n";
    gSystem->Exit(1);
  }

  alien.SetGridDataDir(data_dir);
  alien.SetDataPattern(data_pattern);
}

std::set<int> runs_from_dataset_name(const TString &name)
{
  std::set<int> runs;
  if (name == "LHC11h_AOD145-FemtoMinus") {
    runs = {167915, 167920, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108,
	    168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458,
	    168460, 168464, 168467, 168511, 168512, 168514, 168777, 168826, 168988, 168992,
	    169035, 169040, 169044, 169045, 169091, 169094, 169099, 169138, 169144, 169145,
	    169148, 169156, 169160, 169167, 169238, 169411, 169415, 169417, 169418, 169419,
	    169420, 169475, 169498, 169504, 169506, 169512, 169515, 169550, 169553, 169554,
	    169555, 169557, 169586, 169587, 169588, 169590, 169591 };
  } else if (name == "LHC11h_AOD145-FemtoMinus-1") {
    runs = {167915, 167920};
    	  //, 167985, 167987, 167988, 168069, 168076, 168105, 168107, 168108,
	   // 168115, 168310, 168311, 168322, 168325, 168341, 168342, 168361, 168362, 168458};
  } else if (name == "LHC11h_AOD145-FemtoMinus-2") {
    runs = {168460, 168464, 168467, 168511, 168512, 168514, 168777, 168826, 168988, 168992,
	    169035, 169040, 169044, 169045, 169091, 169094, 169099, 169138, 169144, 169145};
  } else if (name == "LHC11h_AOD145-FemtoMinus-3") {
    runs = {169148, 169156, 169160, 169167, 169238, 169411, 169415, 169417, 169418, 169419,
	    169420, 169475, 169498, 169504, 169506, 169512, 169515, 169550, 169553, 169554,
	    169555, 169557, 169586, 169587, 169588, 169590, 169591 };
  }
 
  else if (name == "LHC11h_AOD145-FemtoPlus") {
    runs = {169835, 169837, 169838, 169846, 169855, 169858, 169859, 169923, 169965, 170027,
	    170040, 170081, 170083, 170084, 170085, 170088, 170089, 170091, 170155, 170159,
	    170163, 170193, 170203, 170204, 170207, 170228, 170230, 170268, 170269, 170270,
	    170306, 170308, 170309, 170311, 170312, 170313, 170315, 170387, 170388, 170572,
	    170593};
  } else if (name == "LHC11h_AOD145-FemtoPlus-1") {
    runs = {169835, 169837, 169838, 169846, 169855, 169858, 169859, 169923, 169965, 170027,
	    170040, 170081, 170083, 170084, 170085, 170088, 170089, 170091, 170155, 170159};
  } else if (name == "LHC11h_AOD145-FemtoPlus-2") {
    runs = {170163, 170193, 170203, 170204, 170207, 170228, 170230, 170268, 170269, 170270,
	    170306, 170308, 170309, 170311, 170312, 170313, 170315, 170387, 170388, 170572,
	    170593};
  }
  
  else if (name == "LHC15o_pass2_lowIR") {
    runs = {244917, 244918, 244975, 244980, 244982, 244983, 245061, 245064, 
	    245066, 245068, 246390, 246391, 246392};
  }
  
  else if (name == "LHC15o_pass1-1") {
    runs = {245683, 245692, 245700, 245702};  // , 245705, 245729, 245731, 245738};
    //, 245752, 245759,
    // 245766, 245775, 245785, 245793, 245829, 245831, 245833, 245923, 245949, 245952, 245954, 245963, 
    
  }
 
  else if (name == "LHC15o_pass1_pidfix") {
    runs = {245540, 245542, 245543, 245544, 245545, 245554,
            245145, 245146, 245148, 245151, 245152, 245231, 245232, 245233,
            245259, 245343, 245345, 245346, 245347, 245349, 245353};
  }
 
  else {
    return std::set<int>();
  }

  return runs;
}

void load_runs(AliAnalysisAlien &alien, const TString &name)
{
  std::cout << "\n\nLoading Runs!\n";
  std::set<int> runs = runs_from_dataset_name(name);
  //for (auto i : runs) {
  for (std::set<int>::iterator it = runs.begin(); it != runs.end(); ++it) {
    int i = *it;
    std::cout << "Adding run " << i <<"\n";
    alien.AddRunNumber(i);
  }
  alien.SetNrunsPerMaster((int)runs.size());
}



TChain* load_local_data(const TString &name)
{
  TChain *result = new TChain("aodTree");

  std::vector<int> numbers;
  TString format;
  bool is_mc = false;

  int data_year = 2000 + name(3, 2).String().Atoi();
  if (name  == "LHC15o") {
    format = "/alice/data/2015/LHC15o/000246001/pass1/AOD/%03d/AliAOD.root";
    numbers = {1, 2, 3};
  }
  else if (name  == "LHC15o-1") {
    format = "/alice/data/2015/LHC15o/000244918/pass1/AOD/%03d/AliAOD.root";
    numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17 //};
    , 18, 19, 20, 21, 22, 23, 24, 25, 26,27,28};
  }
  else if (name == "LHC16g1") {
    numbers = {1, 2, 3, 4, 5, 11, 20, 29, 33, 38, 45, 49, 70, 0};
    format = "/alice/sim/2016/LHC16g1/245505/AOD/%03d/AliAOD.root";
    is_mc = true;
    assert(data_year == 2016);
  }
  else if (name == "LHC16k3b2") {
    numbers =  {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 24, 999, 17149, 0};
    format = "/alice/sim/2016/LHC16k3b2/246751/%03d/AliAOD.root";
    is_mc = true;
  }
  else if (name == "LHC15k1a1") {
    // numbers = {1, 2, 29};
    // format = "/alice/sim/2015/LHC15k1a1/244975/%03d/AliAOD.root";
    numbers = {11, 800};
    format = "/alice/sim/2015/LHC15k1a1/245064/AOD/%03d/AliAOD.root";
    is_mc = true;
  }
  else if (name.BeginsWith("LHC11h_AOD145")) {  //(name == "LHC11h_2") {
    numbers = {27, 186, 652, 1062, 1168, 1200};
    format = "/alice/data/2011/LHC11h_2/000168511/ESDs/pass2/AOD145/%04d//AliAOD.root";
    data_year = 2011;
  }
  else {
    std::cerr << "Unknown dataset name '" << name << "'. Aborting.\n";
    gSystem->Exit(1);
  }

  if (data_year >= 2015) {
    is_run2_analysis = true;
  }

  for (int number : numbers) {
    const TString filename = TString::Format(format, number);
    std::cout << " Adding: " << filename << "\n";
    result->Add(filename);
  }

  return result;
}
