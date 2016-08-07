/**
 * CommonConfig.C
 *
 * A ROOT macro to ensure common configuration between local and grid runs.
 */


void
CommonConfig()
{
  macro_config = ""
  "\""
    "+p; "
    "{0:10:50}; "

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
    "$pion_1_max_tpc_chi_ndof = 3.010; "
    "$pion_1_max_its_chi_ndof = 3.010;"
  "\""
    ;

  is_mc_analysis = false;
  is_2015_data = true;
  collision_trigger = AliVEvent::kINT7;
}
