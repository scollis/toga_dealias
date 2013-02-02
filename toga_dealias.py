#!/usr/bin/python
# Generate and Save a Corrected Moments in Antenna Coordinates file
# usage : process_and_save_csapr_params.py csapr_file.mdv outdir param_file

import sys
import copy
import os
basedir=os.getenv('PYART_DIR')
sys.path.append(basedir)

import numpy as np
import netCDF4
import scipy.interpolate
from pyart.io import py4dd, radar, nc_utils
from pyart.correct import dealias


def dt_to_dict(dt, **kwargs):
        pref = kwargs.get('pref', '')
        return dict([(pref+key, getattr(dt, key)) for key in
                    ['year', 'month', 'day', 'hour', 'minute', 'second']])




if __name__ == "__main__":
    filename = sys.argv[1]
    outdir = sys.argv[2]
    first_start=14
    sonde_text = np.loadtxt(sys.argv[3], skiprows=14)
    alt=np.array([ar[-1] for ar in sonde_text])
    spd=np.array([ar[10] for ar in sonde_text])
    dir=np.array([ar[11] for ar in sonde_text])
    levs=np.linspace(50,alt.max()-1000.0,900)
    good=np.where(alt > 20.0)	
    alt_qc=alt[good]; spd_qc=spd[good]; dir_qc=dir[good]
    spd_i=scipy.interpolate.interp1d(alt_qc, spd_qc)(levs)
    dir_i= scipy.interpolate.interp1d(alt_qc, dir_qc)(levs)
    if filename[-3::]==".nc":
        myradar=radar.Radar(netCDF4.Dataset(filename, 'r'))
        myradar.time.update({'calendar':'gregorian'})
    else:
        rslobj=py4dd.RSL_anyformat_to_radar(filename)
        myradar = radar.Radar(rslobj)
        rsl=True
    #myheight, myspeed, mydirection = dealias.find_time_in_interp_sonde(
    #interp_sonde, target)
    
    target = netCDF4.num2date(myradar.time['data'][0], myradar.time['units'])
    if rslobj:
        deal_obj = dealias.dealiaser(myradar, levs[2::], spd_i[2::],
                                     dir_i[2::]   , target, refl='CZ', vel='VR', rsl_radar=rslobj)
    else:
        deal_obj = dealias.dealiaser(myradar, levs[2::], spd_i[2::],
                                     dir_i[2::], target, refl='CZ', vel='VR')

    my_new_field = deal_obj(filt=0, low_dbz=0)
    myradar.fields.update({'corrected_mean_doppler_velocity': my_new_field})

    mydatetime = netCDF4.num2date(myradar.time['data'][0],
                                  myradar.time['units'],
                                  calendar=myradar.time['calendar'])
    mydict = dt_to_dict(mydatetime)
    mydict.update({'scanmode': myradar.sweep_mode[0]})
    ofilename = outdir + '%(scanmode)scmacs.c0.%(year)04d%(month)02d%(day)02d.%(hour)02d%(minute)02d%(second)02d.nc' % mydict
    netcdf_obj = netCDF4.Dataset(ofilename, 'w', format='NETCDF4')
    nc_utils.write_radar4(netcdf_obj, myradar)
    netcdf_obj.close()

#indir='/net/shasta/data2/liz/TOGA/PUF/1124/PPI'