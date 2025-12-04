********************************************************************************
********************* MCFADDEN-TYPE CONDITIONAL LOGIT **************************
********************************************************************************

clear all
set more off
set matsize 10000
set maxvar 20000
cd "/Users/hannahkamen/Documents/population-migration2"

// log file
capture log close
log using "log/log_5_prep_clogit_2.log", text replace

*	CREAT NEW DATA SET
forvalues k = 1/11{
clear
set obs 21600000 // 270 (msa) * 80,000 = 21,600,000
gen a = 0
egen id = seq(), f(1) t(80000)
drop a
egen msa = seq(), f(1) t(270) b(80000) //for each msa, there are 80,000 obs

*	1. MERGE

merge m:1 id using "dta/merge_id_age`k'.dta"  
drop _merge
//This data set contians some demographic info
//This is produced by do_msa_4prepclogit

merge m:1 msa using "dta/merge_msa_age`k'.dta"
drop if _merge != 3
drop _merge
//lnrho by msa

merge m:1 id msa using "dta/merge_idmsa_age`k'.dta"
rename chosen chosen_orig
gen chosen = 0
replace chosen = 1 if chosen_orig == 1
drop _merge chosen_orig

/////make lowercase metarea 

replace metarea = lower(metarea)

merge m:1 metarea using "dta/climate_hetero.dta"
drop if _merge == 2
drop _merge


*	2. HETEROGENOUS PREFERENCE FOR CLIMATE
***		2.1 USDA PLANT HARDINESS ZONE (ALLEN'S PAPER)
*****		http://pages.uoregon.edu/cameron/WEAI-AERE-2012/Fan_paper.pdf (p.27)
gen clizone = 1	// South
replace clizone = 2 if bpl == 6 // CA
replace clizone = 3 if bpl == 53 | bpl == 41 | bpl == 16 | bpl == 32 ///
					| bpl == 4 | bpl == 49 | bpl == 8 | bpl == 35 ///
					| bpl == 29 // West
replace clizone = 4 if bpl == 30 | bpl == 56 | bpl == 31 | bpl == 46 ///
					| bpl == 38 | bpl == 27 | bpl == 19 | bpl == 20 ///
					| bpl == 28 | bpl == 17 | bpl == 55 | bpl == 26 ///
					| bpl == 39 | bpl == 18 | bpl == 21  // Mid West
replace clizone = 5 if bpl == 34| bpl == 36 | bpl == 42 | bpl == 33 ///
					| bpl == 23 | bpl == 25 | bpl == 9 | bpl == 44 ///
					| bpl == 50 // North East

***		2.2 NOAA CLIMATE ZONE
*****		https://www.ncdc.noaa.gov/monitoring-references/maps/us-climate-regions.php
gen clinoaa = 1						// S
replace clinoaa = 2 if bpl == 6	| bpl == 32		// W
replace clinoaa = 3 if bpl == 53| bpl == 41 | bpl ==16	// NW
replace clinoaa = 4 if bpl == 4 | bpl == 8  | bpl ==35 | bpl ==49			//SW
replace clinoaa = 5 if bpl == 30| bpl == 31 | bpl ==38 | bpl ==46 | bpl == 56		//NRP
replace clinoaa = 6 if bpl == 9 | bpl == 10 | bpl ==23 | bpl ==24 | bpl == 25 | bpl == 33 | bpl == 34 | bpl == 36 | bpl == 42 | bpl == 44 | bpl == 50			//NE
replace clinoaa = 7 if bpl == 19| bpl == 26 | bpl ==27 | bpl ==55			//UMW
replace clinoaa = 8 if bpl == 17| bpl == 18 | bpl ==21 | bpl ==29 | bpl == 39 | bpl ==47 | bpl ==54	//OV
replace clinoaa = 9 if bpl == 1 | bpl == 12 | bpl ==13 | bpl ==37 | bpl == 45 | bpl ==51		//SE

/*
Northwest	WA OR ID
West		CA NV
Southwest	UT CO AZ NM
Northern Rockies and Plains	MT WY ND SD NE
South	KS OK TX AR LA MS
Upper Midwest	IA MI MN WI
ohio Valley		IL IN KY MO OH TN WV
Southeast	AL FL GA NC SC VA
Northeast	CT DE ME MD MA NH NJ NY PA RI VT
*/

*	3. MOVING COSTS
***		3.1 CENSUS REGION (http://www2.census.gov/geo/docs/maps-data/maps/reg_div.txt)
*****			3.1.1 RESIDENCE REGION
gen rd_r1 = 0
replace rd_r1 = 1 if statefip == 9  | statefip == 23 | statefip == 25 | statefip == 33 | ///
			statefip == 44 | statefip == 50
replace rd_r1 = 2 if statefip == 34 | statefip == 36 | statefip == 42
replace rd_r1 = 3 if statefip == 17 | statefip == 18 | statefip == 26 | ///
			statefip == 39 | statefip == 55
replace rd_r1 = 4 if statefip == 19 | statefip == 20 | statefip == 27 | statefip == 29 | ///
			statefip == 31 | statefip == 46 | statefip == 38
replace rd_r1 = 5 if statefip == 10 | statefip == 11 | statefip == 12 | statefip == 13 | ///
			statefip == 24 | statefip == 37 | statefip == 45 | statefip == 51 | statefip == 54
replace rd_r1 = 6 if statefip == 1  | statefip == 21 | statefip == 28 | statefip == 47
replace rd_r1 = 7 if statefip == 5  | statefip == 22 | statefip == 40 | statefip == 48
replace rd_r1 = 8 if statefip == 4  | statefip == 8 | statefip == 16 | statefip == 30 | ///
			statefip == 32 | statefip == 35 | statefip == 49 | statefip == 56
replace rd_r1 = 9 if statefip == 2  | statefip == 6 | statefip == 15 | statefip == 41 | statefip == 53

*****			3.1.3 BIRTH LOCATION
gen bp_r1 = 0
replace bp_r1 = 1 if bpl == 9  | bpl == 23 | bpl == 25 | bpl == 33 | ///
			bpl == 44 | bpl == 50
replace bp_r1 = 2 if bpl == 34 | bpl == 36 | bpl == 42
replace bp_r1 = 3 if bpl == 17 | bpl == 18 | bpl == 26 | ///
			bpl == 39 | bpl == 55
replace bp_r1 = 4 if bpl == 19 | bpl == 20 | bpl == 27 | bpl == 29 | ///
			bpl == 31 | bpl == 46 | bpl == 38
replace bp_r1 = 5 if bpl == 10 | bpl == 11 | bpl == 12 | bpl == 13 | ///
			bpl == 24 | bpl == 37 | bpl == 45 | bpl == 51 | bpl == 54
replace bp_r1 = 6 if bpl == 1  | bpl == 21 | bpl == 28 | bpl == 47
replace bp_r1 = 7 if bpl == 5  | bpl == 22 | bpl == 40 | bpl == 48
replace bp_r1 = 8 if bpl == 4  | bpl == 8 | bpl == 16 | bpl == 30 | ///
			bpl == 32 | bpl == 35 | bpl == 49 | bpl == 56
replace bp_r1 = 9 if bpl == 2  | bpl == 6 | bpl == 15 | bpl == 41 | bpl == 53

***		3.2 MACRO REGION
*****			3.2.1 RESIDENCE OF MACRO REGION
gen rd_r2 = 0
replace rd_r2 = 1 if rd_r1 == 1 | rd_r1 == 2
replace rd_r2 = 2 if rd_r1 == 3 | rd_r1 == 4
replace rd_r2 = 3 if rd_r1 == 5 | rd_r1 == 6 | rd_r1 == 7 
replace rd_r2 = 4 if rd_r1 == 8 | rd_r1 == 9

*****			3.2.3 MACRO-REGION (BPL)
gen bp_r2 = 0
replace bp_r2 = 1 if bp_r1 == 1 | bp_r1 == 2
replace bp_r2 = 2 if bp_r1 == 3 | bp_r1 == 4
replace bp_r2 = 3 if bp_r1 == 5 | bp_r1 == 6 | bp_r1 == 7 
replace bp_r2 = 4 if bp_r1 == 8 | bp_r1 == 9

***		3.3 MOVING COSTS
gen d_s = 0
gen d_r1 = 0
gen d_r2 = 0

replace d_s = 1 if bpl != statefip
replace d_r1 = 1 if bp_r1 != rd_r1
replace d_r2 = 1 if bp_r2 != rd_r2

*	4. MERGE \HAT{W}
merge 1:1 id msa using "dta/inchat_final_age`k'.dta"
drop if _merge != 3
drop _merge

*	5. CREATE VARIABLES FOR HETEROGENOUS PREFERENCE
sort id msa
gen coll = 0
replace coll = 1 if somecoll == 1 | collgrad == 1

gen usda_ca = 0
gen usda_w = 0
gen usda_mw = 0
gen usda_ne = 0

replace usda_ca = 1 if clizone == 2
replace usda_w = 1 if clizone == 3
replace usda_mw = 1 if clizone == 4
replace usda_ne = 1 if clizone == 5

gen noaa_w = 0
gen noaa_nw = 0
gen noaa_sw = 0
gen noaa_nrp = 0 
gen noaa_ne = 0
gen noaa_umw = 0
gen noaa_ov = 0
gen noaa_se = 0

replace noaa_w = 1 if clinoaa == 2
replace noaa_nw = 1 if clinoaa == 3
replace noaa_sw = 1 if clinoaa == 4
replace noaa_nrp = 1 if clinoaa == 5
replace noaa_ne = 1 if clinoaa == 6
replace noaa_umw = 1 if clinoaa == 7
replace noaa_ov = 1 if clinoaa == 8
replace noaa_se = 1 if clinoaa == 9

*replace exthot_25 = 10^-9 if exthot_25 == 0
replace exthot_26 = 10^-9 if exthot_26 == 0
*replace exthot_27 = 10^-9 if exthot_27 == 0
replace exthot_28 = 10^-9 if exthot_28 == 0
*replace exthot_29 = 10^-9 if exthot_29 == 0
replace exthot_30 = 10^-9 if exthot_30 == 0
replace extcold = 10^-9 if extcold == 0

//Use USDA for regional heterogeneity instead of NOAA
foreach x in ca w mw ne {
	gen hot_26C_`x' = usda_`x' * exthot_26
	gen hot_28C_`x' = usda_`x' * exthot_28
	gen hot_30C_`x' = usda_`x' * exthot_30
	gen cold_0C_`x' = usda_`x' * extcold
}
//

//education heterogeneity
gen cold_0C_coll = coll * extcold
foreach x in 26 28 30{
	gen hot_`x'C_coll = coll * exthot_`x'
}
//

gen kid = 0
replace kid = 1 if nchild != 0
gen d_s_kid = d_s * kid
gen d_r1_kid = d_r1 * kid
gen d_r2_kid = d_r2 * kid

/*
gen d_5s_kid = d_5s * kid
gen d_51_kid = d_51 * kid
gen d_52_kid = d_52 * kid
*/

sort id msa

keep chosen inc_hat hot_28C* cold_0C* d_s d_r1 d_r2 d_s_kid d_r1_kid d_r2_kid id msa

save "dta/logit-ready_full_age`k'.dta", replace
}

