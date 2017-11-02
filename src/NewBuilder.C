///
/// \file NewBuilder.C
///

#include <cassert>

#include <TString.h>
#include <AliAnalysisManager.h>


enum class RunMode {
  FULL,
  TERMINATE,
};


template <typename T, typename U>
struct Builder {
  using Map_t = std::map<T, U*>;
};

class AlienHandlerBuilder;




struct AlienHandlerBuilder : public Builder<AlienHandlerBuilder, AliAnalysisAlien> {
  static Map_t fyResults;
//   TString dataset;
  std::tuple<TString  // 0 - dataset
            , RunMode // 1 - runmode
            , TString // 2 - AliPhysicsVersion
            > data

            // defaults
            { "lhc11"       // dataset
            , RunMode::FULL // runmode
            , "vAN-2017025" // physics-version
            };


  // defaults
  // AlienHandlerBuilder()
  // : data() {}

//   bool operator<(const AlienHandlerBuilder&r) const {
//     if (dataset == r.dataset) {
//       return false;
//     } else {
//       return dataset < r.dataset;
//     }
//   }


  operator AliAnalysisAlien*() const {
    auto found = fyResults.find(*this);
    if (found != fyResults.end()) {
      return found->second;
    }

    auto alienHandler = new AliAnalysisAlien();
    alienHandler->SetOverwriteMode();
    auto runmode = std::get<1>(data);
    switch (runmode) {
      case RunMode::FULL:
        alienHandler->SetRunMode("full");
        break;
      case RunMode::TERMINATE:
        alienHandler->SetRunMode("terminate");
        break;
    }
    alienHandler->SetAPIVersion("V1.1x");
    alienHandler->SetAliPhysicsVersion(std::get<2>(data));

    alienHandler->SetCheckCopy(kFALSE);

    alienHandler->SetMergeViaJDL(kTRUE);

    alienHandler->SetMaxMergeFiles(30);
    alienHandler->SetMaxMergeStages(3);
    alienHandler->SetSplitMaxInputFileNumber(18);

    return fyResults[*this] = alienHandler;
  }

  // operator AliAnalysisAlien*() const;
    // AliAnalysisAlien *handler = new AliAnalysisAlien();
//     if (!alienHandler) {

//     }

//   }
// protected:
//   static std::map<AliManagerBuilder, AliAnalysisManager*> fyResults;
};

// template<>
// std::map<AlienHandlerBuilder, AliAnalysisAlien*> Builder<AlienHandlerBuilder, AliAnalysisAlien>::fyResults;
AlienHandlerBuilder::Map_t
// Builder<AlienHandlerBuilder, AliAnalysisAlien>::fyResults;
AlienHandlerBuilder::fyResults;


/*
struct AliManagerBuilder {
  TString name; 
  TString title;

  AliManagerBuilder(): name("mgr"), title("") {}

  AliManagerBuilder WithName(const TString &name) const {
    AliManagerBuilder result(*this);
    result.name = name;
    return result;
  }

  AliManagerBuilder WithTitle(const TString &title) const {
    AliManagerBuilder result(*this);
    result.title = title;
    return result;
  }

  bool operator<(const AliManagerBuilder &r) const {
    if (name == r.name) {
      return title < r.title;
    } else {
      return name < r.name;
    }
  }

  operator AliAnalysisManager*() const {
    auto it = fyResults.find(*this);
    if (it != fyResults.end()) {
      return it->second;
    }

    auto result = new AliAnalysisManager(name, title);
    fyResults[*this] = result;
    return result;
  }

protected:
  static std::map<AliManagerBuilder, AliAnalysisManager*> fyResults;
};
*/





class AliManagerBuilder {
  std::tuple<TString, TString> data;

public:
  AliManagerBuilder(): data({"mgr", ""}) {}

  AliManagerBuilder WithName(const TString &name) const {
    AliManagerBuilder result(*this);
    std::get<0>(result.data) = name;
    return result;
  }

  AliManagerBuilder WithTitle(const TString &title) const {
    AliManagerBuilder result(*this);
    std::get<1>(result.data) = title;
    return result;
  }

  bool operator<(const AliManagerBuilder &r) const {
    return data < r.data;
  }

  operator AliAnalysisManager*() const {
    auto it = fyResults.find(*this);
    if (it != fyResults.end()) {
      return it->second;
    }

    TString name, title;
    std::tie(name, title) = data;

    auto result = new AliAnalysisManager(name, title);
    fyResults[*this] = result;
    return result;
  }

protected:
  static std::map<AliManagerBuilder, AliAnalysisManager*> fyResults;
};


std::map<AliManagerBuilder, AliAnalysisManager*> AliManagerBuilder::fyResults;



void
NewBuilder()
{
  auto builder = AliManagerBuilder().WithTitle("My Manager");
  AliAnalysisManager *mgr = builder;
  AliAnalysisManager *mgr2 = builder;

  assert(mgr == mgr2);

}
