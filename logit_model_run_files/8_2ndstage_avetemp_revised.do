************************************************************************
********************* SECOND-STAGE REGRESSION **************************
************************************************************************

// This file runs the specifications as below
// ccdb_2007
// age groups: 1-11
// regional FE: CZ

cd "/Users/hannahkamen/Documents/population-migration2"

// log file
capture log close
log using "log/log_8_2ndstage_avgtemp.log", text replace

// from the file "beta_H" in folder "results"
import excel using "results/beta_H", firstrow clear
// j indexes extreme temp (28)
// i indexes age
local k = 1
forvalues a = 1/11{
	scalar beta_H_28_age`a' = beta_H[`k']
	display `k'
	display beta_H_28_age`a'
	local k = `k' + 1
}


// i indexes age
forvalues i = 1/11{
	
	// load regional fixed effects
	import excel "dta/regionfe_bpl_28_age`i'.xlsx", ///
	sheet("Sheet1") cellrange(A1:B261) first clear

	// merge "lnrho"
	merge 1:1 msa using "dta/merge_msa_age`i'"
	drop _merge
    drop if metarea == ""

	// merge climate variables
	replace metarea = lower(metarea)
	merge 1:1 metarea using "dta/climate.dta"
	drop if _merge != 3
	drop _merge

	// merge county-level covariates


	merge m:1 metarea using "dta/new_ccdb.dta"
	drop if _merge != 3
	drop _merge

	

	// construct climate variables
	*egen extcold30 = rowtotal(wa_bin1-wa_bin41)	// -30C
	*egen extcold25 = rowtotal(wa_bin1-wa_bin51)	// -25C
	*egen extcold20 = rowtotal(wa_bin1-wa_bin61)    // -20C 
	egen extcold0 = rowtotal(wa_bin1-wa_bin101)	    // 0C

	*egen exthot25 = rowtotal(wa_bin152-wa_bin222)
	egen exthot26 = rowtotal(wa_bin154-wa_bin222)
	egen exthot28 = rowtotal(wa_bin158-wa_bin222)
	egen exthot30 = rowtotal(wa_bin162-wa_bin222)	
	*egen exthot35 = rowtotal(wa_bin172-wa_bin222)	
	*egen exthot40 = rowtotal(wa_bin182-wa_bin222)

	// rename hot and cold variables
	gen hot = exthot28
	gen cold = extcold0
	
	// add annual temp average as control
	egen avgtemp = rowmean(wa_Temp1-wa_Temp12)

	egen precip = rowtotal(wa_Precip1-wa_Precip12)
	egen dewpt = rowmean(wa_DewPt1-wa_DewPt12)
	egen relhum = rowmean(wa_RelHum1-wa_RelHum12)
	egen sun = rowmean(wa_Sunall1-wa_Sunall12)
	
// den hsgrad coll grad age hisp black	
	// take log
	foreach x in sea sea2 lake lake2 slope {
		gen ln`x' = ln(wa_`x')
	}
	

	gen lnprec = ln(precip)
	gen lndewpt = ln(dewpt)
	gen lnrelhum = ln(relhum)
	gen lnsun = ln(sun)
	gen lnavgtemp = ln(avgtemp)

	replace population = population / 10^6 // unit is million now
	gen lnpop = ln(population)
	gen lnmanu = ln(manuf_est)
	gen lngvt = ln(gvtexpend)
// 	gen lnpropt = ln(proptax)
	gen lnincome = ln(median_income)
	gen lnwhite = ln(prop_white)
	gen lncrime = ln(pccrime)		
	gen lnhdd = ln(wa_HDD)
	gen lncdd = ln(wa_CDD)

	// REGIONAL DUMMIES
	// 9 census region
	gen rd_r1 = 0
	replace rd_r1 = 1 if ///
			statefip == 9 | statefip == 23 | statefip == 25 | ///
			statefip == 33 | statefip == 44 | statefip == 50
	replace rd_r1 = 2 if ///
			statefip == 34 | statefip == 36 | statefip == 42
	replace rd_r1 = 3 if ///
			statefip == 17 | statefip == 18 | statefip == 26 | ///
			statefip == 39 | statefip == 55
	replace rd_r1 = 4 if ///
			statefip == 19 | statefip == 20 | statefip == 27 | ///
			statefip == 29 | statefip == 31 | statefip == 46 | statefip == 38
	replace rd_r1 = 5 if ///
			statefip == 10 | statefip == 11 | statefip == 12 | ///
			statefip == 13 | statefip == 24 | statefip == 37 | ///
			statefip == 45 | statefip == 51 | statefip == 54
	replace rd_r1 = 6 if ///
			statefip == 1 | statefip == 21 | statefip == 28 | statefip == 47
	replace rd_r1 = 7 if ///
			statefip == 5 | statefip == 22 | statefip == 40 | statefip == 48
	replace rd_r1 = 8 if ///
			statefip == 4 | statefip == 8 | statefip == 16 | ///
			statefip == 30 | statefip == 32 | statefip == 35 | ///
			statefip == 49 | statefip == 56
	replace rd_r1 = 9 if ///
			statefip == 2 | statefip == 6 | statefip == 15 | ///
			statefip == 41 | statefip == 53

	// macro region (not used in the final version)
	gen rd_r2 = 0  
	replace rd_r2 = 1 if rd_r1 == 1 | rd_r1 == 2
	replace rd_r2 = 2 if rd_r1 == 3 | rd_r1 == 4
	replace rd_r2 = 3 if rd_r1 == 5 | rd_r1 == 6 | rd_r1 == 7
	replace rd_r2 = 4 if rd_r1 == 8 | rd_r1 == 9

	// USDA region, cliamte zone
	gen rd_r3 = 1    													  //south
	replace rd_r3 = 2 if statefip == 6 									  //CA
	replace rd_r3 = 3 if statefip == 53	| statefip == 41 | statefip == 16 ///
					| statefip == 32	| statefip ==  4 | statefip == 49 ///	
					| statefip == 8	| statefip ==  35| statefip == 29 	  //weat
	replace rd_r3 = 4 if statefip == 30	| statefip == 56 | statefip == 31 ///
					| statefip == 46	| statefip == 38 | statefip == 27 ///	
					| statefip == 19	| statefip == 20 | statefip == 28 ///	 
					| statefip == 17	| statefip == 55 | statefip == 26 ///	 	
					| statefip == 39	| statefip == 18 | statefip == 21 //mid west
	replace rd_r3 = 5 if statefip == 34	| statefip == 36 | statefip == 42 ///
					 |statefip == 33	| statefip == 23 | statefip == 25 ///	
					 |statefip == 9	| statefip == 44 | statefip == 50     //north east
	 
	// RHS variable
	// regionfe + beta_H * lnrho
	// beta_H = beta_I * rho * H /I
	gen y = regionfe +  beta_H_28_age`i'* lnrho	

	// label variables
	label var lnavgtemp 	"Avg. temp."
	label var hot 			"Hot days"
	label var cold 		    "Cold days"
	label var lnprec 		"Precipitation"
	label var lnrelhum 		"Relative humidity"
	label var lnsun			"Sunshine"
	label var lnsea 		"Inv. dist. from sea"
	label var lnsea2 		"Inv. dist. from sea (sqd)"
	label var lnlake 		"Inv. dist. from lake"
	label var lnlake2 		"Inv. dist. from lake (sqd)" 	
	label var lnslope		"Slope"
// 	label var lnden 		"Population density"
// 	label var lnhsgrad		"Percentage of highschool graduates"
// 	label var lncoll		"Percentage of college graduates"
// 	label var lngrad 		"Percentage of grad school"
// 	label var lnage 		"Average age"
// 	label var lnhisp		"Percentage of Hispanic"
// 	label var lnblack		"Percentage of Black"
	label var lnpop 		"Population"
	label var lnmanu 		"Manufacturing est."
	label var lngvt 		"Gvt. expenditure"
// 	label var lnpropt 		"Property tax rates"
	label var lnincome 		"Income"
	label var lnwhite 		"Percentage of White"
	label var lncrime 		"Crime rates"
	
	save "dta/albuoy_new.dta", replace

	//climate zone FE, CZ
	reg y hot cold lnprec lnrelhum ///
		lnavgtemp lnsun lnsea  lnsea2 lnlake  lnlake2 lnslope ///
		lnpop lnmanu lngvt  lnincome ///
		lnwhite lncrime i.rd_r3 ///
// 		lnpropt 

	*outreg2 using "results/2nd_stage_avg.xls", append nocon excel bdec(4) ///
	* keep(hot cold lnprec lnrelhum ///
	*	lnavgtemp lnsun lnsea lnsea2 lnlake lnlake2 lnslope ///
	*	lnpop lnmanu lngvt lnpropt lnincome ///
	*	lnwhite lncrime) ///
	*	addtext(Age, --age`i', Sample, 80k, Htemp, Avg 28C, Region FE, CZ)	
	
	regsave hot cold lnprec lnrelhum lnsun lnsea  lnlake ///
			 lnavgtemp lnslope lnpop lnmanu lngvt  lnincome /// lnpropt
			lnwhite lncrime using "results/temp/2nd_stage_avg_age`i'", ///
			tstat pval addlabel(string) table() replace
}


//lnsea2 lnlake2 


