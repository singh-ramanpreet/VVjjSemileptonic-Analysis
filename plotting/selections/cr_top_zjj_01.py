import numpy as np

apply_btag0Wgt = False

def e_channel(df):
     return (
        (df["lept_channel"] == 1) &
        (np.abs(df["lept1_eta"]) < 2.5) &
        ~(
            (np.abs(df["lept1_eta"]) > 1.4442) &
            (np.abs(df["lept1_eta"]) < 1.566)
        )
    )

def e_channel2(df):
     return (
        (np.abs(df["lept2_eta"]) < 2.5) &
        ~(
            (np.abs(df["lept2_eta"]) > 1.4442) &
            (np.abs(df["lept2_eta"]) < 1.566)
        )
    )

def m_channel(df):
    return (
        (df["lept_channel"] == 0) &
        (np.abs(df["lept1_eta"]) < 2.4)
    )

def m_channel2(df):
    return (np.abs(df["lept2_eta"]) < 2.4)

def region_(df, lepton):
    
    if lepton == "m":
        lept1_pt_cut = 35
        lept2_pt_cut = 20
    
    if lepton == "e":
        lept1_pt_cut = 40
        lept2_pt_cut = 20

    return (
        (df["lept1_pt"] > lept1_pt_cut) &
        (df["lept2_pt"] > lept2_pt_cut) &
        (df["lept1_q"] * df["lept2_q"] < 0) &
        (df["v_m"] > 75) &
        (df["v_m"] < 105) &
        (df["nBTagJet_loose"] > 0) &
        (df["vbf_jj_m"] > 500) &
        (df["vbf_j1_pt"] > 50) &
        (df["vbf_j2_pt"] > 50) &
        (df["vbf_jj_Deta"] > 2.5) &
        (df["dijet_j1_pt"] > 30) &
        (df["dijet_j2_pt"] > 30) &
        (df["dijet_pt"] > 0) &
        (df["dijet_m"] > 65) &
        (df["dijet_m"] < 105)
    )
