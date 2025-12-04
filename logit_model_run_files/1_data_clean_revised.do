
clear all
set more off
set matsize 10000

*****************************************************************
*************************DATA CLEARING***************************
*****************************************************************

// the logit processing code used for this work has been adapted from the analysis done in Carbone, Lee, and Shen 2021, entitled
// "U.S. HOUSEHOLD PREFERENCES FOR CLIMATE AMENITIES: DEMOGRAPHIC ANALYSIS AND ROBUSTNESS TESTING"
// this file cleans the 5 year ACS micro-datafile datafile
// and creates sample datasets for use in logit regression

clear all
set more off

cd "/Users/hannahkamen/Documents/population-migration2"

// log file
capture log close
log using "log/log_1_data_clean.log", text replace

// load acs data
use "dta/acs5yr2019.dta", clear

drop if multyear == .

rename met2013 metarea



// collapse race, by(metarea) 
// save "dta/msa_2007_lookup.dta", replace
//
// exit

// keep if respondent is household head
tabulate relate
keep if relate == 1

// keep if born in US
keep if bpl <= 56

// match PUMA id with Albouy 2010 data
sort statefip puma
tostring puma, gen(str_puma)
tostring statefip, gen(str_statefip)
order str_statefip, a(statefip)
order str_puma, a(str_statefip) 
gen str_PumaID = "na"
order str_PumaID, a(str_puma)
replace str_PumaID = str_statefip + "00" + str_puma if puma < 1000
replace str_PumaID = str_statefip + "0" + str_puma if puma >= 1000
destring str_PumaID, gen(PumaID)
su PumaID

// aggregate occupation							
gen occup = 0
//see the ACS occupation codes (OCC) for detial:
//https://usa.ipums.org/usa/volii/occ_acs.shtml
//occ is changed from a 3-digit variable to 4-digit variable
replace occup = 1 if occ >= 10 & occ <= 430		// Management, Business, Science, and Arts
replace occup = 2 if occ >= 500 & occ <= 740	// Business operations
replace occup = 3 if occ >= 800 & occ <= 950	// Financial specialists
replace occup = 4 if occ >= 1000 & occ <= 1240	// Computer and mathematical 
replace occup = 5 if occ >= 1300 & occ <= 1560	// Architecture and engineering
replace occup = 6 if occ >= 1600 & occ <= 1965	// Life, physical, and social science
replace occup = 7 if occ >= 2000 & occ <= 2060	// Community and social services
replace occup = 8 if occ >= 2100 & occ <= 2160	// Legal
replace occup = 9 if occ >= 2200 & occ <= 2550	// Education, training, and library
replace occup = 10 if occ >= 2600 & occ <= 2960	// Arts, design, entertainment, sports, and media
replace occup = 11 if occ >= 3000 & occ <= 3540	// Healthcare practitioners and technical
replace occup = 12 if occ >= 3600 & occ <= 3655	// Healthcare support
replace occup = 13 if occ >= 3700 & occ <= 3955	// Protective service
replace occup = 14 if occ >= 4000 & occ <= 4150	// Food preparation and serving
replace occup = 15 if occ >= 4200 & occ <= 4250	// Building and grounds cleaning and maintenance
replace occup = 16 if occ >= 4300 & occ <= 4650	// Personal care and service
replace occup = 17 if occ >= 4700 & occ <= 4965	// Sales
replace occup = 18 if occ >= 5000 & occ <= 5940	// Office and administrative support
replace occup = 19 if occ >= 6000 & occ <= 6130	// Farming, fishing, and forestry
replace occup = 20 if occ >= 6200 & occ <= 6765	// Construction and Extraction
replace occup = 21 if occ >= 6800 & occ <= 6940	// Extraction workers
replace occup = 22 if occ >= 7000 & occ <= 7610	// Installation, maintenance, and repair workers
//"Solar photovoltaic installers" is a part of both "construction and extraction"
//and "installation, maintenance, and repaire workers". Here, they are counted
//as the former.
replace occup = 23 if occ >= 7700 & occ <= 8965	// Production
replace occup = 24 if occ >= 9000 & occ <= 9750	// Transportation and material moving
replace occup = 25 if occ >= 9800 & occ <= 9830 // Military specific
replace occup = 27 if occ == 9920 				// Unemployed
// drop certain occupations
drop if  occup == 0 | occup == 21 | occup == 25 | occup == 27
//0: Not identified
//21: Extraction 						
//25: military specific
//27: unemployed

// drop if live and/or born in Hawaii and Alaska
drop if statefip == 2 | statefip == 15	// 2: HI, 15: AL
drop if bpl == 2 | bpl == 15

// ADDITIONAL CLEARING
drop year       

count
// 3,852,243
count if metarea == 0
// 1,132,974
// For metarea, 0 means "Not identifiable or not in an MSA"
// drop metarea == 0 will drop all of the households in 
// the states listed below: Vermont, West Virginia, Wyoming

// we want to keep all of the states other than HI and AK.
// create virtual MSA for the below states: 
// Vermont, West Virginia, Wyoming

// ...and New Hampshire 
// New Hampshire will be in the data after dropping obs with
// 0 metarea, but it will be dropped later for other reasons...
// So, fix it here...

// replace all the MSAs in New Hampshire with
// "new hampshire msa" and code "996"
save "dta/data_clean_step1", replace
use "dta/data_clean_step1", clear
// count if statefip == 33  //New Hampshire: 19,586
// replace metarea = 996  if statefip == 33
// count if metarea == 996  //19,586

// fix Vermont(50), West Virginia(54), Wyoming(56)
count if statefip == 50 | statefip == 54 | statefip == 56 //  42,311
count if metarea == 0  //1,115,955
// count if metarea == 0 & statefip == 50  // 9,738
// count if metarea == 0 & statefip == 54  // 24,079
count if metarea == 0 & statefip == 56  // 8,494
// replace metarea of the three states with 997, 998, and 999
// replace metarea = 997  if statefip == 50
// replace metarea = 998  if statefip == 54
replace metarea = 999  if statefip == 56


// fix North Dakota(38), South Dakota(46), Montana(30)

count if statefip == 38 | statefip == 46 | statefip == 30 //  42,311

// count if metarea == 0 & statefip == 38
count if metarea == 0 & statefip == 46 
count if metarea == 0 & statefip == 30  

// replace metarea of the three states with 1000, 1001, and 1002
// replace metarea =1000  if statefip == 38
replace metarea = 1001 if statefip == 46
replace metarea =  1002  if statefip == 30 
count if metarea == 0 //1,073,644


//re-define labels for virtual msas

label define met2013_lbl 999 "wy virtual msa, wy" 1001 "sd virtual msa, sd" 1002  "mt virtual msa, mt", add

// new added metarea
// MSA name					MSA code
// "new hampshire msa"		996
// "vermont msa"			997
// "west virginia msa"		998
// "wyoming	msa"			999
// "north dakota msa"		1000
// "south dakota msa"		1001
// "montana	msa"			1002

drop if metarea == 0

// MATCH WITH CCDB - CCDB DOESN'T CONTAIN ALL MSAs.  
// used in the 2nd stage regression to control for 
// regional specific characteristics
// make sure the new MSAs are created in the ccdb file.

////////////////////////////////////////
////////////////////////////////////////
////////////////////////////////////////

//Join on new ccdb variables

rename metarea metarea19_encoded
decode metarea19_encoded,gen(metarea)

replace metarea = lower(metarea)


merge m:1 metarea using "dta/new_ccdb.dta"

drop _merge


// merge m:1 metareanum using "dta/old_ccdb_lm.dta"

// tabulate metarea if _merge != 3					
// drop if _merge != 3
//The command above drops all of the obs with 0 metarea.
// drop _merge											

// create msa id 
egen msa = group(metarea)

// demographics
gen white = 0
replace white = 1 if race == 1
gen male = 0
replace male = 1 if sex == 1
gen old = 0
replace old = 1 if age > 60
gen hsdrop = 0
replace hsdrop = 1 if educd < 62
gen hsgrad = 0
replace hsgrad = 1 if educd == 62
gen somecoll = 0
replace somecoll = 1 if educd > 62 & educd <= 81
gen collgrad = 0
replace collgrad = 1 if educd > 81

// chosen MSA
gen chosen = 1

// income variable
sum hhincome inctot ftotinc incwage
drop if inctot <= 0
drop if inctot == 999999


// create age groups
tab age
count if age >= 21 & age <= 25	    //21-25		ageid = 1
count if age >= 26 & age <= 30	    //26-30		ageid = 2
count if age >= 31 & age <= 35		//31-35		ageid = 3
count if age >= 36 & age <= 40		//36-40		ageid = 4
count if age >= 41 & age <= 45		//41-45		ageid = 5
count if age >= 46 & age <= 50		//46-50		ageid = 6
count if age >= 51 & age <= 55		//51-55		ageid = 7
count if age >= 56 & age <= 60		//56-60		ageid = 8
count if age >= 61 & age <= 65		//61-65		ageid = 9
count if age >= 66 & age <= 70		//66-70		ageid = 10
count if age >= 71           		//71-		ageid = 11

gen ageid = 0
replace ageid = 1 if age >= 21 & age <= 25		//21-25
replace ageid = 2 if age >= 26 & age <= 30		//26-30
replace ageid = 3 if age >= 31 & age <= 35		//31-35
replace ageid = 4 if age >= 36 & age <= 40		//36-40
replace ageid = 5 if age >= 41 & age <= 45		//41-45
replace ageid = 6 if age >= 46 & age <= 50		//46-50
replace ageid = 7 if age >= 51 & age <= 55		//51-55
replace ageid = 8 if age >= 56 & age <= 60		//56-60
replace ageid = 9 if age >= 61 & age <= 65		//61-65
replace ageid = 10 if age >= 66 & age <= 70		//66-70
replace ageid = 11 if age >= 71          		//71-

// save cleaned data
save "dta/acs5yr_1519_clr.dta", replace

// save msa identifier
keep msa metarea
collapse msa, by(metarea)
save "dta/msa_identifier.dta", replace


*****************************************************************
*****************************************************************
// create a random subsample to reduce the size of the data
use "dta/acs5yr_1519_clr.dta", clear
set seed 1000
gen random = runiform()
sort random
keep in 1/150000					
unique PumaID					
unique metarea
unique serial		
drop random

// save
save "dta/acs5yr_1519_clr_shrink_all.dta", replace


*****************************************************************
*****************************************************************
// create random subsamples by age group
forvalues i = 1/11 {
	display "ageid = " `i'
	use "dta/acs5yr_1519_clr.dta", clear
	keep if ageid == `i'
	set seed 1000
	gen random = runiform()
	sort random
	keep in 1/110000
	drop random
	save "dta/acs5yr_1519_clr_shrink_age`i'.dta", replace
}
//

capture log close
exit
