clear all
set more off

cd "/Users/hannahkamen/Documents/population-migration2"

clear matrix
clear mata
set matsize 10000
set maxvar 20000

capture log close
log using "log/5_climate.log", text replace


use "dta/albuoy_all_weighted_v2.dta", clear


unique metarea

forval x = 1/222 {
// 	gen bin`x' = bin`x'
// 	gen Tbin`x' = Tbin`x'
	gen fbin`x' = DeltaA2Ensemble30Year_bin`x'
}

// forval x = 1/102 {
// 	gen popXPbin`x' = Population * Pbin`x'
// }

forval x = 1/12 {
// 	gen Precip`x' = Precip`x'
// 	gen DewPt`x' = DewPt`x'
// 	gen Temp`x' = Temp`x'
// 	gen RelHum`x' = RelHum`x'
// 	gen Sunall`x' = Sun`x'
// 	gen Sun4S`x' = Sun4S`x'
	gen fPrecip`x' = DeltaA2Ensemble30YearPrecipT`x'
	gen fRelHum`x' = DeltaA2Ensemble30YearRelHum`x'
	rename Sun`x' Sunall`x'
}

// forval x = 1/10 {
// 	gen popXRHbin`x' = Population * RHbin`x'
// 	gen popXDPbin`x' = Population * DPbin`x'
// }

gen HDD = HDD_Pres
gen CDD = CDD_Pres

unique statefip
sort metarea statefip


count if metarea == ""


order metarea, a(msa)
drop if metarea == ""



* Squared slope
rename slope_pct Slope

gen slope = Slope

* Demographic controls
// gen LogWeightedDensity = log(PopDens_Weighted)
// gen LogDensity = log(PopDens)
// gen Pct_HSEd = 1 - sch_hsdo
// gen Pct_BSEd = sch_cdeg
// gen Pct_GradEd = sch_post
// sum Pct*
// gen Age = age
// drop age
// gen PctHisp = min_hisp
// gen PctBlack = min_blac
// drop min_*
//
// gen popXden = Population * LogWeightedDensity
// gen popXhsgrad = Population * Pct_HSEd
// gen popXcoll = Population * Pct_BSEd
// gen popXgrad = Population * Pct_GradEd
// gen popXage = Population * Age
// gen popXhisp = Population * PctHisp
// gen popXblack = Population * PctBlack


// get weighted sum of climate variables based on puma weights
// collapse (sum) popXbin* popXTbin* popXfbin* popXPbin* popXPrecip* popXDewPt* ///
// 				popXTemp* popXRelHum* popXSunall* popXSun4S* popXRHbin* popXDPbin* ///
// 				popXHDD popXCDD popXsea popXsea2 popXlake popXlake2 popXfPrecip* popXfRelHum* ///
// 				popXslope popXden popXhsgrad popXcoll popXgrad popXage popXhisp popXblack ///
//





				
collapse (sum)  bin* Tbin* fbin* Pbin* Precip* DewPt* ///
				Temp* RelHum* Sunall* Sun4S* RHbin* DPbin* ///
				HDD CDD fPrecip* fRelHum* ///
				slope  ///
 				 HDD_Pres CDD_Pres mean_sea mean_lake sea sea2 lake lake2,  by(metarea)		


// * Get inverse distances to coast, and powers thereof
// replace mean_sea = 1 if mean_sea<1
// replace mean_lake = 1 if mean_lake<1
// gen SeaDistInv = 1 / mean_sea
// gen SeaDistInv2 = SeaDistInv^2
//
// gen LakeDistInv = 1 / mean_lake
// gen LakeDistInv2 = LakeDistInv^2 
//
//
// gen sea = SeaDistInv
// gen sea2 = SeaDistInv2
// gen lake = LakeDistInv
// gen lake2 = LakeDistInv2

//bin* Tbin* Pbin* Precip* DewPt*  Temp* RelHum* Sunall* Sun4S* RHbin* DPbin*
//sea sea2 lake lake2				
		
// 		(mean) bin* Tbin* Pbin* Precip* DewPt* Temp* RelHum* Sunall* Sun4S* ///
// 				RHbin* DPbin* HDD_Pres CDD_Pres, by(metarea)
		
// foreach x in bin Tbin fbin{
// 	forval y = 1/222{
// 		gen wa_`x'`y' = popX`x'`y' / Population
// 	}
// }
//
// forval x = 1/102 {
// 	gen wa_Pbin`x' = popXPbin`x' / Population
// }
//
// foreach x in Precip DewPt Temp RelHum Sunall Sun4S fPrecip fRelHum {
// 	forval y = 1/12 {
// 		gen wa_`x'`y' = popX`x'`y' / Population
// 	}
// }
//
// foreach x in RHbin DPbin {
// 	forval y = 1/10 {
// 		gen wa_`x'`y' = popX`x'`y' / Population
// 	}
// }
//	
// foreach x in sea sea2 lake lake2 slope den hsgrad coll grad age hisp black {
// 	gen wa_`x' = popX`x' / Population
// }
//
// gen wa_HDD = popXHDD / Population
// gen wa_CDD = popXCDD / Population
//	
// drop popX*
// keep wa_* metarea




foreach x in bin Tbin fbin{
	forval y = 1/222{
		gen wa_`x'`y' = `x'`y'
	}
}

forval x = 1/102 {
	gen wa_Pbin`x' = Pbin`x'
}

foreach x in Precip DewPt Temp RelHum Sunall Sun4S fPrecip fRelHum {
	forval y = 1/12 {
		gen wa_`x'`y' = `x'`y'
	}
}

foreach x in RHbin DPbin {
	forval y = 1/10 {
		gen wa_`x'`y' = `x'`y' 
	}
}
	
foreach x in sea sea2 lake lake2 slope {
	gen wa_`x' = `x'
}

//den hsgrad coll grad age hisp black 

gen wa_HDD = HDD
gen wa_CDD = CDD

// drop popX*

/*
merge 1:1 metarea using "dta/climate_minmax_shrink.dta"
drop _merge
*/
saveold "dta/climate.dta", replace

* ALLEN-TYPE HETEROGENEITY
use "dta/climate.dta", clear
egen extcold = rowtotal(wa_bin1-wa_bin101)	// Daily avg temperature below 0C
egen exthot_25 = rowtotal(wa_bin152-wa_bin222)	// Daily avg temperature above 25C
egen exthot_26 = rowtotal(wa_bin154-wa_bin222)
egen exthot_27 = rowtotal(wa_bin156-wa_bin222)		// Daily avg temperature above 27C
egen exthot_28 = rowtotal(wa_bin158-wa_bin222)
egen exthot_29 = rowtotal(wa_bin160-wa_bin222)
egen exthot_30 = rowtotal(wa_bin162-wa_bin222)

egen summer = rowmean(wa_Temp6-wa_Temp8)
egen winter = rowmean(wa_Temp12 wa_Temp1 wa_Temp2)
egen avgtemp = rowmean(wa_Temp1-wa_Temp12)

keep metarea extcold exthot* summer winter avgtemp 
//wa_hot90 wa_col32

saveold "dta/climate_hetero.dta", replace

exit
