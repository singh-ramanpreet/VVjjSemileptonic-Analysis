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
        "title_y": "",
        "units": "",
        "axis_max_digits": 4,
        "scale_y_axis": 1.8,
        "canvas_log_y": False,
        "draw_with_ratio": True,
        "make_cms_text": True,
        "ndivisions_x": 510,
        "upper_pad_min_y": "auto",
        "lower_graph_draw_opt": "p",
        "lower_graph_max_y": 2.0,
        "lower_graph_min_y": 0.0,
        "lower_graph_ndivisions_y": 404,
        "lower_graph_title_y": "#frac{Data}{MC}",
        "legend_position": [0.42, 0.75, 0.95, 0.9],
        "legend_columns": 2,
        "legend_fill_style": 0,
        "legend_border_size": 0,
        "legend_text_font": 42,
        "sys": args.sys,
        "stacks": {
            "VBS_QCD": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "VBS QCD (#INTEGRAL#)",
                "legend_style": "f",
                "fill_color": ROOT.TColor.GetColor(248, 206, 104),
                "line_color": ROOT.TColor.GetColor(248, 206, 104),
                "fill_style": 1001,
                "sys": args.sys,
                "sys_name": f"{args.sub_dir}_#SYS#/#NAME#_{variable}",
            },
            "Top": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "Top (#INTEGRAL#)",
                "legend_style": "f",
                "fill_color": ROOT.TColor.GetColor(155, 152, 204),
                "line_color": ROOT.TColor.GetColor(155, 152, 204),
                "fill_style": 1001,
                "sys": args.sys,
                "sys_name": f"{args.sub_dir}_#SYS#/#NAME#_{variable}",
            },
            "DYJets_HT": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "DY Jets (#INTEGRAL#)",
                "legend_style": "f",
                "fill_color": ROOT.TColor.GetColor(200, 90, 106),
                "line_color": ROOT.TColor.GetColor(200, 90, 106),
                "fill_style": 1001,
                "sys": args.sys,
                "sys_name": f"{args.sub_dir}_#SYS#/#NAME#_{variable}",
            },
            "DYJets_HT_b1": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "DY Jets - b1 (#INTEGRAL#)",
                "legend_style": "f",
                "fill_color": ROOT.TColor.GetColor(200, 90, 106),
                "line_color": ROOT.TColor.GetColor(200, 90, 106),
                "fill_style": 1001,
                "sys": args.sys,
                "sys_name": f"{args.sub_dir}_#SYS#/#NAME#_{variable}",
            }
        },
        "overlays": {
            "VBS_EWK": {
                "name": f"{args.sub_dir}/#NAME#_{variable}",
                "legend": "VBS EWK #SCALE# (#INTEGRAL#)",
                "scale": 20,
                "legend_style": "l",
                "line_color": ROOT.kBlack,
                "line_style": ROOT.kDashed
            }
        },
        "data": {
            "name": f"{args.sub_dir}/data_obs_{variable}",
            "legend": "Data (#INTEGRAL#)",
            "legend_style": "pe",
            "marker_style": 20,
            "marker_color": ROOT.kBlack,
            "marker_size": 0.8,
            "blind": args.blind,
            "blind_range": (),
        },
        "postfit": {
            "name": f"{args.sub_dir}/Total_Bkg_{variable}"
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
        self.stacks = config["stacks"]
        self.overlays = config["overlays"]
        self.data = config["data"]
        self.postfit_data = config["postfit"]

        self.postfit = False

        # make stacked hist
        if self.config["units"] != "":
            self.config["title_x"] = f"{self.config['title_x']} ({self.config['units']})"

        self.stacked_obj = ROOT.THStack("stacked", f";{self.config['title_x']};#TITLE_Y#")
        self.stacked_obj_sysUp = ROOT.THStack("stacked_sysUp", "")
        self.stacked_obj_sysDown = ROOT.THStack("stacked_sysDown", "")

        self.stacked_sum = None
        self.stacked_sum_sysUp = None
        self.stacked_sum_sysDown = None

        self.stacked_obj_errors = None
        self.stacked_obj_errors_ratio = None

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

        self.stacked_sum = self.hist_file.Get(self.postfit_data["name"])
        if type(self.stacked_sum) == ROOT.TObject:
            self.postfit = False

        self.data["obj"] = self.hist_file.Get(self.data["name"])
        if self.data["obj"].GetEntries() != 0.0:
            self.data["legend"] = self.data["legend"] if not self.postfit else self.data["legend"].replace("Data", "Asimov Data")

        data_integral = self.data['obj'].Integral()
        if self.data["blind"]:
            if len(self.data["blind_range"]) != 0:
                binA = self.data["obj"].FindBin(self.data["blind_range"][0])
                binB = self.data["obj"].FindBin(self.data["blind_range"][1])
                for i in range(binA, binB + 1):
                    data_integral -= self.data["obj"].GetBinContent(i)
                    self.data["obj"].SetBinContent(i, 0.0)
                    self.data["obj"].SetBinError(i, 0.01)
            else:
                for i in range(1, self.data["obj"].GetNbinsX() + 1):
                    data_integral -= self.data["obj"].GetBinContent(i)
                    self.data["obj"].SetBinContent(i, 0.0)
                    self.data["obj"].SetBinError(i, 0.01)

        self.legend.AddEntry(self.data["obj"],
                             self.data["legend"].replace("#INTEGRAL#", f"{data_integral:.2f}"),
                             self.data["legend_style"])

        for h in self.stacks:
            self.stacks[h]["obj"] = self.hist_file.Get(self.stacks[h]["name"].replace("#NAME#", h))

            if type(self.stacks[h]["obj"]) == ROOT.TObject:
                continue

            if self.stacks[h]["obj"].Integral() == 0.0:
                continue

            if "fill_color" in self.stacks[h]: self.stacks[h]["obj"].SetFillColor(self.stacks[h]["fill_color"])
            if "line_color" in self.stacks[h]: self.stacks[h]["obj"].SetLineColor(self.stacks[h]["line_color"])
            if "fill_style" in self.stacks[h]: self.stacks[h]["obj"].SetFillStyle(self.stacks[h]["fill_style"])

            self.stacks[h]["obj_sysUp"] = self.stacks[h]["obj"].Clone(f"sysUp")
            self.stacks[h]["obj_sysDown"] = self.stacks[h]["obj"].Clone(f"sysDown")
            
            for i in range(1, self.stacks[h]["obj"].GetNbinsX() + 1):
                sysUp = 0.0
                sysDown = 0.0
                for sys in self.config["sys"]:
                    htemp_Up = self.hist_file.Get(self.stacks[h]["sys_name"].replace("#SYS#", f"{sys}Up").replace("#NAME#", h))
                    htemp_Down = self.hist_file.Get(self.stacks[h]["sys_name"].replace("#SYS#", f"{sys}Down").replace("#NAME#", h))
                    if type(htemp_Up) == ROOT.TObject: continue

                    sysUp = add_errors(sysUp, abs(self.stacks[h]["obj_sysUp"].GetBinContent(i) - htemp_Up.GetBinContent(i)))
                    sysDown = add_errors(sysDown, abs(self.stacks[h]["obj_sysDown"].GetBinContent(i) - htemp_Down.GetBinContent(i)))
                self.stacks[h]["obj_sysUp"].SetBinContent(i, self.stacks[h]["obj"].GetBinContent(i) + sysUp)
                self.stacks[h]["obj_sysDown"].SetBinContent(i, self.stacks[h]["obj"].GetBinContent(i) - sysDown)

            if self.stacks[h]["obj"].GetEntries() != 0.0:
                self.legend.AddEntry(self.stacks[h]["obj"],
                                self.stacks[h]["legend"].replace("#INTEGRAL#", f"{self.stacks[h]['obj'].Integral():.2f}"),
                                self.stacks[h]["legend_style"])
                self.stacked_obj.Add(self.stacks[h]["obj"])
                self.stacked_obj_sysUp.Add(self.stacks[h]["obj_sysUp"])
                self.stacked_obj_sysDown.Add(self.stacks[h]["obj_sysDown"])

        if not self.postfit:
            self.stacked_sum = self.stacked_obj.GetStack().Last()
            self.stacked_sum_sysUp = self.stacked_obj_sysUp.GetStack().Last()
            self.stacked_sum_sysDown = self.stacked_obj_sysDown.GetStack().Last()

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

            if self.overlays[h]["scale"] == 1:
                self.overlays[h]["legend"] = self.overlays[h]["legend"].replace(" #SCALE#", "")
            else:
                self.overlays[h]["legend"] = self.overlays[h]["legend"].replace(" #SCALE#", f" x{self.overlays[h]['scale']}")

            if self.overlays[h]["obj"].GetEntries() != 0.0:
                self.legend.AddEntry(self.overlays[h]["obj"],
                                self.overlays[h]["legend"].replace("#INTEGRAL#", f"{self.overlays[h]['obj'].Integral():.2f}"),
                                self.overlays[h]["legend_style"])

            if self.overlays[h]["scale"] != 1:
                self.overlays[h]["obj"].Scale(self.overlays[h]["scale"])

        self.stacked_obj_errors = ROOT.TGraphAsymmErrors(self.stacked_sum.Clone("sum_errors"))
        self.stacked_obj_errors.SetFillStyle(3145)
        self.stacked_obj_errors.SetMarkerStyle(0)
        self.stacked_obj_errors.SetFillColor(1)
        self.stacked_obj_errors.SetLineColor(1)

        self.stacked_obj_errors_ratio = self.stacked_obj_errors.Clone("sum_errors_ratio")
        self.stacked_obj_errors_ratio.SetFillStyle(1001)
        self.stacked_obj_errors_ratio.SetMarkerStyle(0)
        self.stacked_obj_errors_ratio.SetFillColor(ROOT.kGray)

        self.legend.AddEntry(ROOT.nullptr, f"Total MC ({self.stacked_sum.Integral():.2f})", "f")
        self.legend.AddEntry(self.stacked_obj_errors, "PostFit Unc." if self.postfit else "Stat + Sys Unc.", "f")

        for i in range(self.stacked_sum.GetNbinsX()):
            if self.postfit:
                d_ey_Up = 0.0
                d_ey_Down = 0.0
            else:
                d_ey_Up = abs(self.stacked_sum_sysUp.GetBinContent(i + 1) - self.stacked_sum.GetBinContent(i + 1))
                d_ey_Down = abs(self.stacked_sum_sysDown.GetBinContent(i + 1) - self.stacked_sum.GetBinContent(i + 1))

            ey_Up = add_errors(self.stacked_obj_errors.GetErrorYhigh(i), d_ey_Up)
            self.stacked_obj_errors.SetPointEYhigh(i, ey_Up)
            ey_Down = add_errors(self.stacked_obj_errors.GetErrorYlow(i), d_ey_Down)
            self.stacked_obj_errors.SetPointEYlow(i, ey_Down)

            self.stacked_obj_errors_ratio.SetPointY(i, 1.0)
            if self.stacked_obj_errors.GetPointY(i) != 0.0:
                self.stacked_obj_errors_ratio.SetPointEYhigh(i, ey_Up/self.stacked_obj_errors.GetPointY(i))
                self.stacked_obj_errors_ratio.SetPointEYlow(i, ey_Down/self.stacked_obj_errors.GetPointY(i))
            else:
                self.stacked_obj_errors_ratio.SetPointEYhigh(i, 0.0)
                self.stacked_obj_errors_ratio.SetPointEYlow(i, 0.0)

        maxY = max(self.data["obj"].GetMaximum(), self.stacked_sum.GetMaximum())
        minY = min(self.data["obj"].GetMinimum(), self.stacked_sum.GetMinimum())
        self.stacked_sum.SetMaximum(maxY * self.config["scale_y_axis"])

        if self.config["upper_pad_min_y"] != "auto":
            self.stacked_obj.SetMinimum(self.config["upper_pad_min_y"])

        if self.config["title_y"] == "":
            self.stacked_obj.SetTitle(self.stacked_obj.GetTitle().
                                      replace("#TITLE_Y#",
                                              f"Events / {self.stacked_sum.GetBinWidth(1):.2f} {self.config['units']}"))

    def draw(self):
        self.get_hists()
        canvas = ROOT.TCanvas()
        if self.config["canvas_log_y"]:
            canvas.SetLogy()

        if not self.config["draw_with_ratio"]:

            self.stacked_obj.Draw("hist")
            self.data["obj"].Draw("x0 e1 same")
            for h in self.overlays:
                self.overlays[h]["obj"].Draw("hist same")
            self.stacked_obj_errors.Draw("2")

            self.legend.Draw()

            if self.config["make_cms_text"]:
                if self.config["year"] == "2016":
                    self.config["lumi_text"] = "#scale[1.0]{35.9 fb^{-1} (13 TeV)}"
                if self.config["year"] == "2017":
                    self.config["lumi_text"] = "#scale[1.0]{41.5 fb^{-1} (13 TeV)}"
                if self.config["year"] == "2018":
                    self.config["lumi_text"] = "#scale[1.0]{59.74 fb^{-1} (13 TeV)}"
                if self.config["year"] == "run2":
                    self.config["lumi_text"] = "#scale[1.0]{137 fb^{-1} (13 TeV)}"
                CMS_text(
                    canvas,
                    cms_text_location="inside left",
                    cms_pos_y_scale=0.9,
                    draw_extra_text=True,
                    extra_text_location="inside left below",
                    extra_text="#scale[1.0]{Work in Progress}",
                    extra_text_pos_y_scale=0.95,
                    draw_lumi_text=True,
                    lumi_text=self.config["lumi_text"]
                )

        if self.config["draw_with_ratio"]:

            data_clone = self.data["obj"].Clone("data_clone")
            stacked_clone = self.stacked_sum.Clone("stacked_clone")

            if self.data["obj"].Integral() == 0.0:
                # this for blinded plots
                ratio = ROOT.TRatioPlot(stacked_clone, stacked_clone)
                self.config["lower_graph_title_y"] = ""
            else:
                ratio = ROOT.TRatioPlot(data_clone, stacked_clone)

            ratio.SetGraphDrawOpt(self.config["lower_graph_draw_opt"])

            ratio.SetSeparationMargin(0)
            ratio.SetLeftMargin(canvas.GetLeftMargin())
            ratio.SetRightMargin(canvas.GetRightMargin())
            ratio.SetUpTopMargin(0.075)
            ratio.SetLowBottomMargin(0.40)

            ratio.Draw("grid hideup")

            ratio.GetLowYaxis().SetNdivisions(self.config["lower_graph_ndivisions_y"])
            ratio.GetXaxis().SetNdivisions(self.config["ndivisions_x"])
            if self.config["canvas_log_y"]:
                ratio.GetXaxis().SetRange(2, 2) # brute force

            gridlines = ROOT.std.vector("double")()
            gridlines.push_back(0.5)
            gridlines.push_back(1.0)
            gridlines.push_back(1.5)
            ratio.SetGridlines(gridlines)
            ratio.GetLowerRefYaxis().CenterTitle()
            ratio.GetLowerRefYaxis().SetTitleSize(0.04)
            ratio.GetLowerRefYaxis().SetTitleOffset(1.8)
            ratio.GetLowerRefYaxis().SetLabelSize(0.035)
            ratio.GetLowerRefYaxis().SetTitle(self.config["lower_graph_title_y"])
            ratio.GetLowerRefGraph().SetMinimum(self.config["lower_graph_min_y"])
            ratio.GetLowerRefGraph().SetMaximum(self.config["lower_graph_max_y"])
            ratio.GetLowerRefGraph().SetMarkerStyle(20)
            ratio.GetLowerRefGraph().SetMarkerSize(0.8)

            lower_pad = ratio.GetLowerPad()
            lower_pad.cd()
            self.stacked_obj_errors_ratio.Draw("2")
            # draw again, hack
            ratio.GetLowerRefGraph().Draw(f"same {self.config['lower_graph_draw_opt']}")

            if self.data["obj"].Integral() == 0.0:
                ratio.GetLowerRefGraph().SetMarkerSize(0.0)
                for i in range(ratio.GetLowerRefGraph().GetN()):
                    ratio.GetLowerRefGraph().SetPointError(i, 0, 0, 0, 0)

            upper_pad = ratio.GetUpperPad()
            upper_pad.cd()

            stacked_clone.Reset()
            data_clone.Reset()
            self.stacked_obj.Draw("ah hist")
            self.stacked_obj_errors.Draw("2")
            self.data["obj"].Draw("x0 e1 same")
            for h in self.overlays:
                self.overlays[h]["obj"].Draw("hist same")

            self.legend.SetY1(self.legend.GetY2() - 0.05 * self.legend.GetNRows())
            self.legend.Draw()

            if self.config["make_cms_text"]:
                if self.config["year"] == "2016":
                    self.config["lumi_text"] = "#scale[1.0]{35.9 fb^{-1} (13 TeV)}"
                if self.config["year"] == "2017":
                    self.config["lumi_text"] = "#scale[1.0]{41.5 fb^{-1} (13 TeV)}"
                if self.config["year"] == "2018":
                    self.config["lumi_text"] = "#scale[1.0]{59.74 fb^{-1} (13 TeV)}"
                if self.config["year"] == "run2":
                    self.config["lumi_text"] = "#scale[1.0]{137 fb^{-1} (13 TeV)}"
                CMS_text(
                    upper_pad,
                    cms_text_scale=1.2,
                    cms_text_location="inside left",
                    cms_pos_y_scale=0.95,
                    draw_extra_text=True,
                    extra_text_location="inside left below",
                    extra_text="#scale[1.2]{Work in Progress}",
                    extra_text_pos_x_scale=1.0,
                    extra_text_pos_y_scale=1.0,
                    draw_lumi_text=True,
                    lumi_text=self.config["lumi_text"]
                )

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
            if i.GetClassName() == "TH1D":
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
            title_x="p^{T}_{Z}"
            units="GeV"
            do_log = True
            upper_pad_min_y = 0.01

        if "mva_score" in var:
            title_x="BDT Score"
            do_log = True
            upper_pad_min_y = 0.1

        print(f"=> {args.rootfile} --- {args.sub_dir} --- {var}")
        config = make_config(args, variable=var, title_x=title_x, units=units, title_y=title_y, plot_filename=plot_filename)
        if args.mva_type == "zv":
            config["overlays"]["VBS_EWK"]["scale"] = 30
        if args.mva_type == "zjj":
            config["overlays"]["VBS_EWK"]["scale"] = 100
        plot(config).draw()
        if do_log:
            config = make_config(args, variable=var, title_x=title_x, units=units, title_y=title_y, plot_filename=plot_filename)
            config["canvas_log_y"] = True
            config["overlays"]["VBS_EWK"]["scale"] = 1
            config["scale_y_axis"] = 50
            config["upper_pad_min_y"] = upper_pad_min_y
            plot(config).draw()
