import numpy as np

apply_btag0Wgt = True

def e_channel(df):
     return (
        (df["type"] == 1) &
        (np.abs(df["l_eta1"]) < 2.5) &
        ~(
            (np.abs(df["l_eta1"]) > 1.4442) &
            (np.abs(df["l_eta1"]) < 1.566)
        )
    )

def m_channel(df):
    return (
        (df["type"] == 0) &
        (np.abs(df["l_eta1"]) < 2.4)
    )

def region_(df, lepton):
    
    if lepton == "m":
        l_pt1_cut = 50
        pfmet_cut = 50
    
    if lepton == "e":
        l_pt1_cut = 50
        pfmet_cut = 80

    return (
        (df["isResolved"] == False) &
        (df["l_pt1"] > l_pt1_cut) &
        (df["l_pt2"] < 0) &
        (df["pfMET_Corr"] > pfmet_cut) &
        (df["nBTagJet_loose"] == 0) &
        (df["vbf_maxpt_jj_m"] > 800) &
        (df["vbf_maxpt_j1_pt"] > 30) &
        (df["vbf_maxpt_j2_pt"] > 30) &
        (df["vbf_maxpt_jj_Deta"] > 4.0) &
        (df["ungroomed_PuppiAK8_jet_pt"] > 200 ) &
        (np.abs(df["ungroomed_PuppiAK8_jet_eta"]) < 2.4 ) &
        (df["PuppiAK8_jet_tau2tau1"] < 0.55) &
        (df["PuppiAK8_jet_mass_so_corr"] > 65) &
        (df["PuppiAK8_jet_mass_so_corr"] < 105) &
        (df["mass_lvj_type0_PuppiAK8"] > 600) &
        (df["BosonCentrality_type0"] > 1.0) &
        (np.abs((df["ZeppenfeldWL_type0"])/(df["vbf_maxpt_jj_Deta"])) < 0.3) &
        (np.abs((df["ZeppenfeldWH"])/(df["vbf_maxpt_jj_Deta"])) < 0.3)
    )
