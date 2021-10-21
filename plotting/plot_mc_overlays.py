#!/usr/bin/env python3

import ROOT
ROOT.gROOT.SetBatch()
ROOT.PyConfig.IgnoreCommandLineOptions = True
import os
import argparse
from pyroot_cms_scripts import CMS_style, CMS_text
ROOT.gErrorIgnoreLevel = ROOT.kError

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--rootfile", type=str, default="test.root")
parser.add_argument("-b", "--blind", action="store_true")
parser.add_argument("-y", "--year", type=str, default="2016")
parser.add_argument("-s", "--sub-dir", dest="sub_dir", type=str, default="/")
parser.add_argument("-m", "--mva-type", dest="mva_type", type=str, default="wjj")
parser.add_argument("-B", "--boson", type=str, default="W")
parser.add_argument("-v", "--var", action="append", default=[])
parser.add_argument("-S", "--sys", action="append", default=[])


def add_errors(x1, x2):
    return (x1**2 + x2**2)**0.5

def make_config(args, variable="lep1_pt", **kwargs):
    config = {
        "hist_filename": args.rootfile,
        "plot_filename": "",
        "year": args.year,
        "title_x": "",
        "title_y": "a.u.",
        "units": "",
        "axis_max_digits": 4,
        "scale_y_axis": 1.8,
        "canvas_log_y": False,
        "ndivisions_x": 510,
        "legend_position": [0.42, 0.75, 0.95, 0.9],
        "legend_columns": 2,
        "legend_fill_style": 0,
        "legend_border_size": 0,
        "legend_text_font": 42,
        "overlays": {
            "VBS_QCD": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "VBS QCD (#INTEGRAL#)",
                "legend_style": "f",
                "line_color": ROOT.TColor.GetColor(248, 206, 104),
                "line_style": ROOT.kSolid,
                "line_width": 2
            },
            "Top": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "Top (#INTEGRAL#)",
                "legend_style": "f",
                "line_color": ROOT.TColor.GetColor(155, 152, 204),
                "line_style": ROOT.kSolid,
                "line_width": 2
            },
            "DYJets_HT": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "DY Jets (#INTEGRAL#)",
                "legend_style": "f",
                "line_color": ROOT.TColor.GetColor(200, 90, 106),
                "line_style": ROOT.kSolid,
                "line_width": 2
            },
            "VBS_EWK": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "VBS EWK (#INTEGRAL#)",
                "legend_style": "f",
                "line_color": ROOT.kBlack,
                "line_style": ROOT.kSolid,
                "line_width": 2
            }
        }
    }
    for k in kwargs:
        config[k] = kwargs[k]

    return config


class plot:
    def __init__(self, config):
        self.config = config

        # Force CMS_style
        # ==============
        ROOT.TGaxis().SetMaxDigits(config["axis_max_digits"])
        CMS_style.SetLabelSize(0.042, "XYZ")
        CMS_style.SetTitleSize(0.055, "XYZ")
        CMS_style.SetHatchesLineWidth(1)
        CMS_style.SetHatchesSpacing(2.5)
        CMS_style.cd()
        ROOT.gROOT.ForceStyle()
        
        # make global properties and objects
        self.hist_file = ROOT.TFile.Open(config["hist_filename"])
        self.overlays = config["overlays"]

        # make stacked hist
        if self.config["units"] != "":
            self.config["title_x"] = f"{self.config['title_x']} ({self.config['units']})"

        # make legend
        self.legend = ROOT.TLegend(
            config["legend_position"][0], config["legend_position"][1],
            config["legend_position"][2], config["legend_position"][3]
        )
        self.legend.SetFillStyle(config["legend_fill_style"])
        self.legend.SetBorderSize(config["legend_border_size"])
        self.legend.SetTextFont(config["legend_text_font"])
        self.legend.SetNColumns(config["legend_columns"])

    def get_hists(self):

        for h in self.overlays:
            self.overlays[h]["obj"] = self.hist_file.Get(self.overlays[h]["name"].replace("#NAME#", h))

            if type(self.overlays[h]["obj"]) == ROOT.TObject:
                continue

            if self.overlays[h]["obj"].Integral() == 0.0:
                continue

            if "marker_style" in self.overlays[h]: self.overlays[h]["obj"].SetMarkerStyle(self.overlays[h]["marker_style"])
            if "marker_color" in self.overlays[h]: self.overlays[h]["obj"].SetMarkerColor(self.overlays[h]["marker_color"])
            if "marker_size" in self.overlays[h]: self.overlays[h]["obj"].SetMarkerSize(self.overlays[h]["marker_size"])
            if "fill_color" in self.overlays[h]: self.overlays[h]["obj"].SetFillColor(self.overlays[h]["fill_color"])
            if "line_color" in self.overlays[h]: self.overlays[h]["obj"].SetLineColor(self.overlays[h]["line_color"])
            if "fill_style" in self.overlays[h]: self.overlays[h]["obj"].SetFillStyle(self.overlays[h]["fill_style"])
            if "line_style" in self.overlays[h]: self.overlays[h]["obj"].SetLineStyle(self.overlays[h]["line_style"])
            if "line_width" in self.overlays[h]: self.overlays[h]["obj"].SetLineWidth(self.overlays[h]["line_width"])

            self.overlays[h]["legend"] = self.overlays[h]["legend"].replace(" #SCALE#", "")

            if self.overlays[h]["obj"].GetEntries() != 0.0:
                self.legend.AddEntry(self.overlays[h]["obj"],
                                self.overlays[h]["legend"].replace("#INTEGRAL#", f"{self.overlays[h]['obj'].Integral():.2f}"),
                                self.overlays[h]["legend_style"])


    def draw(self):
        self.get_hists()
        canvas = ROOT.TCanvas()
        if self.config["canvas_log_y"]:
            canvas.SetLogy()

        maxY = 0
        for h in self.overlays:
            if self.overlays[h]["obj"] != ROOT.TObject:
                sum_ = self.overlays[h]["obj"].GetSumOfWeights()
                self.overlays[h]["obj"].Scale(1.0/sum_)
                maxY_ = self.overlays[h]["obj"].GetMaximum()
                if maxY_ >= maxY:
                    maxY = maxY_
                    self.overlays[h]["obj"].SetMaximum(3*maxY)
                self.overlays[h]["obj"].Draw("hist same")                
        self.legend.Draw()

        canvas.Draw()
        extra_tag = ""

        if self.config["canvas_log_y"]:
            self.config["plot_filename"] += "_log"

        canvas.SaveAs(f"{self.config['plot_filename']}.pdf")
        os.popen(f"convert -density 150 -antialias {self.config['plot_filename']}.pdf \
                 -trim {self.config['plot_filename']}.png 2> /dev/null").read()


if __name__ == "__main__":

    args = parser.parse_args()

    out_dir  = f"{args.rootfile.replace('.root', '')}/{args.sub_dir}"
    os.makedirs(out_dir, exist_ok=True)

    if (len(args.var) == 0):
        f = ROOT.TFile.Open(args.rootfile)
        d = f.Get(args.sub_dir)
        l = d.GetListOfKeys()
        variables = []
        for i in l:
            name_ = i.GetName()
            if "data_obs_" in name_:
                variables.append(name_.replace("data_obs_", ""))
    else:
        variables = args.var

    for var in variables:
        plot_filename = f"{out_dir}/{var}"
        title_x = var
        units = ""
        title_y = ""
        do_log = False

        if args.boson == "Z":
            if "boson_cent" in var: continue
            if "MET" in var: continue

            if args.mva_type == "zv":
                if "dijet_" in var: continue
                if "mva_score" in var and "zv" not in var: continue
            if args.mva_type == "zjj":
                if "fatjet_" in var: continue
                if "mva_score" in var and "zjj" not in var: continue

        if var == "v_lep_pt":
            title_x="p^{T}_{lep1}"
            units="GeV"
            do_log = True
            upper_pad_min_y = 0.01

        print(f"=> {args.rootfile} --- {args.sub_dir} --- {var}")
        config = make_config(args, variable=var, title_x=title_x, units=units, title_y=title_y, plot_filename=plot_filename)
        plot(config).draw()
