/**
 * CommonConfig.C
 *
 * A ROOT macro to ensure common configuration between local and grid runs.
 */


void
CommonConfig()
{
  is_mc_analysis = false;

  macro_config = ""
  "\""
    "+p;"
    "{0:10}; "
    //"{0:10:20}; "
    // "{0:5:10:20:30,0:10}; "

    "@verbose = false; "
    "~do_avg_sep_cf = false; "
    "~do_q3d_cf = false; "
    "~do_kt_q3d = false; "

    "~do_trueq_cf = false; "

    "~do_deltaeta_deltaphi_cf = true; "
    "~delta_eta_bin_count = 75; "
    "~delta_phi_bin_count = 75; "

    // "$pair_delta_eta_min = 0.006; "
    // "$pair_delta_phi_min = 0.015; "

    "~do_kt_qinv=true; "
    "~qinv_bin_size_MeV=2.5; "

    "@enable_pair_monitors = true;"
    "@min_coll_size = 100; "
    "@num_events_to_mix = 3; "
    "@mult_max = 500; "
    "@mult_bins = 25; "
    "@is_mc_analysis = " + TString::Format("%d", is_mc_analysis) + "; "

    // "$event_VertexZMin = 0; "
    "$event_VertexZMin = -8; "
    "$event_VertexZMax = 8; "

  //  "$pion_1_EtaMin = 0; "


    "$pair_delta_eta_min = 0.0; "
    "$pair_delta_phi_min = 0.0; "
//     "$pair_delta_eta_min = 0.01; "
//     "$pair_delta_phi_min = 0.016; "

    "$pion_1_PtMin = 0.14; "
    "$pion_1_PtMax = 2.0; "
    "$pion_1_max_impact_z = 2.4; "
    "$pion_1_max_impact_xy = 3.20; "

    "$pion_1_max_tpc_chi_ndof = 3.010; "
    "$pion_1_max_its_chi_ndof = 3.010;"
  "\""
    ;

//   collision_trigger = AliVEvent::kCentral | AliVEvent::kMB  | AliVEvent::kSemiCentral;
  // collision_trigger = AliVEvent::kMB;
  collision_trigger = AliVEvent::kINT7;
//   collision_trigger = AliVEvent::kAny;
}
