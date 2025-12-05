#!/bin/bash


#for i in $(seq .6 .1 2.5); do gams staticmodel_d2_v3.gms --esub_l=$i   o=lst/staticmodel_d2_v2_${i}.lst; done

#for i in $(seq 1.8 .1 3); do gams staticmodel_d2_v3.gms --esub_nat=$i   o=lst/staticmodel_d2_v2_${i}.lst; done

#for i in $(seq .5 .2 1.5); do gams staticmodel_d2_v3.gms --esub_c=$i   o=lst/staticmodel_d2_v2_${i}.lst; done

# Now merge the individual GDX files using gdxmerge.

## Delete any old results.
rm merged.gdx

## And merge new files
gdxmerge staticmodel_d2_v2*.gdx
## Now write the merge GDX file out to CSV.                                                                                                                                                                                                                                                                
gdxdump merged.gdx output=csv_d2_v2/le0_d_rpt00.csv symb=le0_d_rpt00 format=csv  header= "file,region,household,skill,benchmark_le0"
gdxdump merged.gdx output=csv_d2_v2/le0_d_rpt.csv symb=le0_d_rpt format=csv  header= "file,region,household,skill,benchmark_le0"
gdxdump merged.gdx output=csv_d2_v2/cons0_rpt.csv symb=cons0_rpt format=csv  header= "file,region,household,skill,benchmark_cons"
gdxdump merged.gdx output=csv_d2_v2/ld0_d_rpt.csv symb=ld0_d_rpt format=csv  header= "file,sector,skill,benchmark_ld0"
gdxdump merged.gdx output=csv_d2_v2/c0_h_d_rpt.csv symb=c0_h_d_rpt  format=csv  header= "file,region,good,household,skill,benchmark_demand"
gdxdump merged.gdx output=csv_d2_v2/cd0_h_d_rpt.csv symb=cd0_h_d_rpt  format=csv  header= "file,region,good,household,skill,benchmark_disagg_cons"
gdxdump merged.gdx output=csv_d2_v2/kd0_rpt.csv symb=kd0_rpt  format=csv  header= "file,region,sector,benchmark_capital_demand"
gdxdump merged.gdx output=csv_d2_v2/SAVRATE_rpt.csv symb=SAVRATE_rpt  format=csv  header= "file,SAVRATE"
gdxdump merged.gdx output=csv_d2_v2/TAXRATE_rpt.csv  symb=TAXRATE_rpt  format=csv  header= "file,TAXRATE"

gdxdump merged.gdx output=csv_d2_v2/hhtrn0_d_rpt.csv symb=hhtrn0_d_rpt format=csv  header= "file,r,h,sk,trn,benchmark_transfers"

gdxdump merged.gdx output=csv_d2_v2/hhtrn0_ds_rpt.csv symb=hhtrn0_ds_rpt format=csv  header= "file,region,household,skill,benchmark_transfers"
gdxdump merged.gdx output=csv_d2_v2/id0_rpt.csv symb=id0_rpt format=csv  header= "file,region,good,sector,benchmark_int_dmd"
gdxdump merged.gdx output=csv_d2_v2/sav0_d_rpt.csv symb=sav0_d_rpt  format=csv  header= "file,good,household,skill,benchmark_savings"
gdxdump merged.gdx output=csv_d2_v2/ke0_d_rpt.csv symb=ke0_d_rpt format=csv  header= "file,region,household,skill,benchmark_k"
gdxdump merged.gdx output=csv_d2_v2/tl0_d_rpt.csv symb=tl0_d_rpt format=csv  header= "file,region,household,skill,benchmark_tl"
gdxdump merged.gdx output=csv_d2_v2/ys0_rpt.csv symb=ys0_rpt format=csv  header= "file,region,sector,good,benchmark_supply"

#for i in 0; do gdxdump merged.gdx output=csv/le0_d_rpt${i}.csv symb=le0_d_rpt${i} format=csv  header= "file,region,household,skill,le0_shock${i}";done                                                                                                                                                    
gdxdump merged.gdx output=csv_d2_v2/le0_d_rpt0.csv symb=le0_d_rpt0 format=csv  header= "file,region,household,skill,le0_shock0"
gdxdump merged.gdx output=csv_d2_v2/y_rpt0.csv symb=y_rpt0 format=csv  header= "file,region,sector,output_shock0"
gdxdump merged.gdx output=csv_d2_v2/c_rpt0.csv symb=c_rpt0 format=csv  header= "file,region,household,skill,cons_shock0"
gdxdump merged.gdx output=csv_d2_v2/pl_rpt0.csv symb=pl_rpt0 format=csv  header= "file,region,skill,pl_shock0"
gdxdump merged.gdx output=csv_d2_v2/pc_rpt0.csv symb=pc_rpt0 format=csv  header= "file,region,household,skill,pc_shock0"
gdxdump merged.gdx output=csv_d2_v2/w_rpt0.csv symb=w_rpt0 format=csv  header= "file,region,household,skill,welfare_shock0"
gdxdump merged.gdx output=csv_d2_v2/npl_rpt0.csv symb=npl_rpt0 format=csv  header= "file,region,skill,npl_shock0"
gdxdump merged.gdx output=csv_d2_v2/phou_rpt0.csv symb=phou_rpt0 format=csv  header= "file,region,sector,ph_shock0"
gdxdump merged.gdx output=csv_d2_v2/ra_rpt0.csv symb=ra_rpt0 format=csv  header= "file,region,household,skill,ra_shock0"
gdxdump merged.gdx output=csv_d2_v2/pfx_rpt0.csv symb=pfx_rpt0 format=csv  header= "file,pfx0"
gdxdump merged.gdx output=csv_d2_v2/pk_rpt0.csv symb=pk_rpt0 format=csv  header= "file,pk0"
gdxdump merged.gdx output=csv_d2_v2/pn_rpt0.csv symb=pn_rpt0 format=csv  header= "file,good,pn0"
gdxdump merged.gdx output=csv_d2_v2/pm_rpt0.csv symb=pm_rpt0 format=csv  header= "file,region,margin,pm0"
gdxdump merged.gdx output=csv_d2_v2/pa_rpt0.csv symb=pa_rpt0 format=csv  header= "file,region,good,pa0"
gdxdump merged.gdx output=csv_d2_v2/py_rpt0.csv symb=py_rpt0 format=csv  header= "file,region,good,py0"
gdxdump merged.gdx output=csv_d2_v2/pd_rpt0.csv symb=pd_rpt0 format=csv  header= "file,region,good,pd0"
gdxdump merged.gdx output=csv_d2_v2/rk_rpt0.csv symb=rk_rpt0 format=csv  header= "file,region,s,rk0"
gdxdump merged.gdx output=csv_d2_v2/a_rpt0.csv symb=a_rpt0 format=csv  header= "file,region,good,a0"
