readme for Heidiplot v0.13

about:
Heidiplot is a python 2.7 based program, which was developed to visualize data taken at a 4 circle single crystal diffractometer, namely HEidi the Hot Single Crystal Diffractometer at the nuclear reactor FRM II near by Munich.

Heidiplot is based on pythonmodules like wx, matplotlib and numpy, which are necessary for it to run properly.

For further questions feel free to contact: j.reim@fz-juelich.de

manual:
1. in order to start the program change to the directory you have unzipped to program to and open a terminal
2. run the command: python Heidiplot.py (on mac choose grpython instead of python as the compiler)
3. after loading the program the main screen should be active, there you have to follow the steps in order to generate a plot
4. first insert the crystal structure manually or you can choose "from file" if you created a config-file for the crystal in a session before. 
	4a. Please note that the values you insert should be reciprocal Angstrom for the lengths and degree for the angles and the orientation matrix should the inserted the way, that the columns are a*, b* and c*, if you inserted everything you can save this config to a file and press okay, otherwise just close
	4b. If you inserted the structure from a file, you can still change the values by clicking on "manual/edit" and correct the values shown in the new screen
5. now you can load the taken data into the program with a click on "load", following step 2. The data has to be provided in gnuplot-format, which you will usually recieve after finishing your measurement at HEiDi, otherwise please contact the instrument responsible (f.e. martin.meven@frm2.tum.de). You can load as many gnuplot files as you like and if you loaded a file unintentionally, xou can unload it using the unload button next to it
6. for step 3 you insert the desired boundaries in values for hkl (regarding to the crystal structure you inserted) and temperature, if you keep fields empty the boundary will be adjusted automatically. Please note, that the amount of datapoints will reduce the rotationspeed of the diagramm. Single layers (lmin=lmax) are most convenient to investigate.
7. the data is now ready to be plotted, but some additional options can be choosen: if you would like to show either magnetic or nuclear peaks, or the brillouinzone and you can scale the plotted pointsize then click on "generate plot". If it succeeds and your fine with your plot, via the menu you can save (Ctrl+S) the complete config for this plot. This can also be loaded via the load entry within the menu (Ctrl+L).
8. the shown plot is created by matplotlib, you can rotate the plot by dragging the plot with the left mouse. For further information please attend the tutorials for matplotlib
9. at last the converted data from angles to Q can be also saved to a gnuplotfile, which will create plots similar to the ones created by the loaded gnuplot-file, but now intensity versus |Q|.

Example data:
with the program some example data is provided, with which you can try out this program
only nuclear peaks:
	crystal structure config file (structural cell): cabaco2fe2o7_nucCell.scfg
	gnuplot files: cbcfoI190K_nucCell.gpl
nuclear and magnetic peaks:
	crystal structure config file (magnetic cell): cabaco2fe2o7_magCell.scfg
	gnuplot files: cbcfoI.gpl, cbcfoI2k5_30LC.gpl
	saved plot config: CaBaCo2Fe2O7_magCell.pcfg
good boundaries: h and k can be kept empty, l should be confined f.e. to (lmin,lmax): (0,0), (1,1), (2,2) or (0,1)

Thank you a lot for using this program, and I hope it will be useful for you.
I welcome any propositions or bug reports, please send them to j.reim@fz-juelich.de

