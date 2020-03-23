import numpy as np

apply_btag0Wgt = True

def e_channel(df):
     return (
        (df["lept_channel"] == 1) &
        (np.abs(df["lept1_eta"]) < 2.5) &
        ~(
            (np.abs(df["lept1_eta"]) > 1.4442) &
            (np.abs(df["lept1_eta"]) < 1.566)
        )
    )

def m_channel(df):
    return (
        (df["lept_channel"] == 0) &
        (np.abs(df["lept1_eta"]) < 2.4)
    )

def region_(df, lepton):
    
    if lepton == "m":
        lept1_pt_cut = 50
        pf_met_cut = 50
    
    if lepton == "e":
        lept1_pt_cut = 50
        pf_met_cut = 80

    return (
        (df["isResolved"] == False) &
        (df["lept1_pt"] > lept1_pt_cut) &
        (df["lept2_pt"] < 0) &
        (df["pf_met_corr"] > pf_met_cut) &
        (df["nBTagJet_loose"] == 0) &
        (df["vbf_jj_m"] > 800) &
        (df["vbf_j1_pt"] > 30) &
        (df["vbf_j2_pt"] > 30) &
        (df["vbf_jj_Deta"] > 4.0) &
        (df["fatjet_pt"] > 200 ) &
        (np.abs(df["fatjet_eta"]) < 2.4 ) &
        (df["fatjet_tau21"] < 0.55) &
        (df["fatjet_m"] > 65) &
        (df["fatjet_m"] < 105) &
        (df["wv_m"] > 600) &
        (df["boson_centrality"] > 1.0) &
        (np.abs(df["zeppenfeld_w_Deta"]) < 0.3) &
        (np.abs(df["zeppenfeld_v_Deta"]) < 0.3)
    )
