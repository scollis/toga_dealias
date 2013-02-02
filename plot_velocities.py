#!/usr/bin/python
import matplotlib
matplotlib.use('agg')
import netCDF4
import sys
import os
import matplotlib as mpl
mpl.use('Agg')

pyart_dir=os.environ.get('PYART_DIR',os.environ['HOME']+'/python')
sys.path.append(pyart_dir)
from pyart.graph import rayplot, radar_display
from pyart.io import radar, py4dd, py_mdv
from pylab import *
import copy

if __name__ == "__main__":
	filename=sys.argv[1]
	outdir=sys.argv[2]
	print "plotting ", filename, " to ", outdir
	if ".mdv" in filename:
		my_object=py_mdv.read_mdv(filename, debug=True)
		myradar=radar.Radar(my_object)
	elif ".nc" in filename:
		my_object=netCDF4.Dataset(filename)
		myradar=radar.Radar(my_object)
		my_object.close()
	else:
		py4dd.RSL_radar_verbose_on()
		my_object = py4dd.RSL_anyformat_to_radar(filename)
	my_display=radar_display.radar_display(myradar)
	f=figure(figsize=[15,5])
	subplot(1,2,1)
	tilt=int(sys.argv[3])
	nyq=myradar.inst_params['nyquist_velocity']['data'][0]
	myradar.time.update({'calendar':'gregorian'})
	my_display.plot_ppi('mean_doppler_velocity', tilt, vmin=-nyq, vmax=nyq)
	my_display.append_x()
	my_display.append_y()
	gca().set_title(my_display.generate_title('mean_doppler_velocity', tilt))
	my_display.add_cb()
	subplot(1,2,2)
	my_display.plot_ppi('corrected_mean_doppler_velocity', tilt, vmin=-30, vmax=30)
	gca().set_title(my_display.generate_title('corrected_mean_doppler_velocity', tilt))
	my_display.append_x()
	my_display.add_cb()
	figname=my_display.generate_filename('dealias_', tilt)
	savefig(outdir+'/'+figname.replace(' ','_'))
	close(f)


