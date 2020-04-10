import numpy as np

apply_btag0Wgt = True

# blind data histograms
# name x_low, x_high
blind_data = [
    ("mva_score", 0.0, 1.0)
]

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
        lept1_pt_cut = 35
        pf_met_cut = 40
    
    if lepton == "e":
        lept1_pt_cut = 40
        pf_met_cut = 40

    return (
        (df["lept1_pt"] > lept1_pt_cut) &
        (df["lept2_pt"] < 0) &
        (df["pf_met_corr"] > pf_met_cut) &
        (df["nBTagJet_loose"] == 0) &
        (df["vbf_jj_m"] > 500) &
        (df["vbf_j1_pt"] > 50) &
        (df["vbf_j2_pt"] > 50) &
        (df["vbf_jj_Deta"] > 2.5) &
        (df["fatjet_pt"] > 200) &
        (np.abs(df["fatjet_eta"]) < 2.4) &
        (df["fatjet_m"] > 65) &
        (df["fatjet_m"] < 105) &
        (df["fatjet_tau21"] < 0.55) &
        (df["boson_centrality"] > 0.0) &
        (np.abs(df["zeppenfeld_w_Deta"]) < 1.0) &
        (np.abs(df["zeppenfeld_v_Deta"]) < 1.0)
    )
