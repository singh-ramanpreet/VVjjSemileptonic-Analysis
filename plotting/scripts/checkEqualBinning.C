//https://github.com/GuillelmoGomezCeballos/MitAnalysisRunII/blob/master/panda/macros/9x/checkEqualBinning.C

#include <TROOT.h>
#include <TFile.h>
#include <TTree.h>
#include <TSystem.h>
#include <TString.h>
#include <TH1D.h>
#include <TMath.h>
#include <iostream>
#include <fstream>
#include <TStyle.h>

void checkEqualBinning(TString fileName = "", int numberOfBins = 8, bool debug = false, TString histoName = "VBS_EWK_mva_score"){
  TFile *the_input_file = TFile::Open(fileName.Data());
  if(!the_input_file) return;
  TH1D* theHisto = (TH1D*)the_input_file->Get(histoName.Data());
  if(!theHisto) return;

  const int nBinBDT = numberOfBins; Float_t theInterval[nBinBDT];
  for(int i=0; i<=nBinBDT; i++) theInterval[i] = (i+1.)/numberOfBins;
  theInterval[nBinBDT-1] = 1.001;
  double sum = 0;
  double toKeep[nBinBDT];
  bool theCall[nBinBDT];
  for(int i=0; i<nBinBDT; i++) theCall[i] = false;

  const double numberOfHistoBins = theHisto->GetNbinsX()/2.0;

  for(int nb=1; nb<=theHisto->GetNbinsX(); nb++){
    sum = sum +  theHisto->GetBinContent(nb) / theHisto->GetSumOfWeights();
    if(debug) printf("%5.3f\n",sum);
    for(int i=0; i<nBinBDT; i++) {
      if(theCall[i] == false && sum > theInterval[i]){
        double binHighEdge = theHisto->GetBinLowEdge(nb)+2*(theHisto->GetBinCenter(nb)-theHisto->GetBinLowEdge(nb));
        printf("%3d %5.2f %5.3f %d\n",nb,binHighEdge,sum,i);
        theCall[i] = true;
        toKeep[i] = binHighEdge;
        break;
      }
    }
  }

  for(int i=0; i<nBinBDT; i++) {
   if(theCall[i] == true) printf(",%6.3f",toKeep[i]);
  }
  printf("\n");
}