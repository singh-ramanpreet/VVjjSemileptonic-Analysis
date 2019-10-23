#!/bin/bash

../plot_variable.py --hist_file hists.root\
 --variable lept_pt1\
 --units GeV \
 --title_x 'lept_{1} p_{T}'\
 --show_bw\
 --draw_with_ratio\
 --batch_mode

../plot_variable.py --hist_file hists.root\
 --variable lept_pt2\
 --units GeV \
 --title_x 'lept_{2} p_{T}'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --batch_mode
 
 ../plot_variable.py --hist_file hists.root\
 --variable lept_eta1\
 --units '' \
 --title_x 'lept_{1} #eta'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --scale_y_axis 1.4\
 --batch_mode
 
  ../plot_variable.py --hist_file hists.root\
 --variable lept_eta2\
 --units '' \
 --title_x 'lept_{2} #eta'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --scale_y_axis 1.4\
 --batch_mode
 
  ../plot_variable.py --hist_file hists.root\
 --variable lept_phi1\
 --units '' \
 --title_x 'lept_{1} #phi'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --scale_y_axis 1.4\
 --batch_mode

 
  ../plot_variable.py --hist_file hists.root\
 --variable lept_phi2\
 --units '' \
 --title_x 'lept_{2} #phi'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --scale_y_axis 1.4\
 --batch_mode
 
 
  ../plot_variable.py --hist_file hists.root\
 --variable mass_WV\
 --units GeV \
 --title_x 'm_{WV}'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --axis_max_digits 4\
 --scale_y_axis 1.4\
 --log_y_axis\
 --batch_mode
 
   ../plot_variable.py --hist_file hists.root\
 --variable mass_ZV\
 --units GeV \
 --title_x 'm_{ZV}'\
 --show_bw\
 --leg_pos 0.55 0.65 0.95 0.9\
 --draw_with_ratio\
 --axis_max_digits 4\
 --scale_y_axis 1.4\
 --log_y_axis\
 --batch_mode