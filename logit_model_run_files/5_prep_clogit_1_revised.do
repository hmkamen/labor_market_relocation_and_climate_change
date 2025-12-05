********************************************************************************
********************* MCFADDEN-TYPE CONDITIONAL LOGIT **************************
********************************************************************************

clear all
set more off
set maxvar 32000
set matsize 10000
cd "/Users/hannahkamen/Documents/population-migration2"

// log file
capture log close
log using "log/log_5_prep_clogit_1.log", text replace

forvalues ageid = 1/11 {
*	1. PREPARE THE DATASET
use "dta/acs5yr_1519_hss_age`ageid'.dta", clear	// 

egen id = group(serial)
order msa, a(serial)
order id, a(serial)
sort serial msa

keep id msa migmet1 serial statefip PumaID metarea bpl lnrho chosen  ///
	white male hsdrop hsgrad somecoll collgrad occup incwage age nchild 
	
save "dta/mergebase_age`ageid'.dta", replace

***		1.1 KEEP VARIABLES MERGED BY ID
use "dta/mergebase_age`ageid'.dta", clear
keep id serial nchild migmet1 bpl white male hsdrop hsgrad somecoll collgrad occup incwage age
save "dta/merge_id_age`ageid'.dta", replace

***		1.2 KEEP VARIABLES MERGED BY MSA
use "dta/mergebase_age`ageid'.dta", clear
keep msa statefip lnrho metarea
tabstat statefip, by(msa) s(sd)


//for msa=4,12... there are more than 1 states...
foreach x of numlist 4 12 38 39 40 42 43 110 136 142 150 156 166 173 179 181 199 224 240 247 250{
tabulate statefip if msa == `x', nolabel
}


* I USE THE LARGEST STATEFIP
replace statefip = 42 if msa == 4
replace statefip = 13 if msa == 12
replace statefip = 37 if msa == 38
replace statefip = 47   if msa == 39
replace statefip = 17 if msa == 40
replace statefip = 39 if msa == 42


replace statefip = 47 if msa == 43
replace statefip = 29 if msa == 110
replace statefip = 47 if msa == 136


replace statefip = 27 if msa == 142
replace statefip = 45 if msa == 150
replace statefip = 36 if msa == 156


replace statefip = 31 if msa == 166
replace statefip = 42 if msa == 173
replace statefip = 41 if msa == 179

replace statefip = 44 if msa == 181
replace statefip = 24 if msa == 199
replace statefip = 29 if msa == 224


replace statefip = 51 if msa == 240
replace statefip = 25 if msa == 247
replace statefip = 39 if msa == 250

collapse statefip lnrho, by(msa metarea)
save "dta/merge_msa_age`ageid'.dta", replace


***		1.3 KEEP VARIABLE MERGED BY ID & MSA
use "dta/mergebase_age`ageid'.dta", clear
keep id msa chosen
save "dta/merge_idmsa_age`ageid'.dta", replace


*	2. INCOME PREDICTION FOR EACH REGION

unique msa //259


return list
scalar numb_msa = r(unique)

forval x = 1/`=numb_msa'{
clear
set obs 80000
gen a = 0
egen id = seq(), f(1) t(80000)
drop a
gen msa = `x'
merge m:1 msa using "dta/inchat_age`ageid'.dta"
drop if _merge != 3
drop _merge
merge m:1 id using "dta/merge_id_age`ageid'.dta"
drop if _merge !=3
drop _merge

tab occup, gen(Ioccup)

gen inc_hat = 0
	
	forval y = 1/23{
		replace inc_hat = b_whi_`x' * white + b_mal_`x' * male ///
			+ b_hsd_`x' * hsdrop + b_hsg_`x' * hsgrad + b_som_`x' * somecoll + b_col_`x' * collgrad ///
			+ b_occ_`x'_`y' if msa == `x' & Ioccup`y' == 1
	}
	
	keep id msa inc_hat
save "dta/income_reg/inchat_`x'_age`ageid'.dta", replace
}

***		2.1 APPEND ALL
use "dta/income_reg/inchat_1_age`ageid'.dta", clear
forval x = 2/`=numb_msa'{
	append using "dta/income_reg/inchat_`x'_age`ageid'.dta"
}
//

sort id msa
save "dta/inchat_final_age`ageid'.dta", replace
}
capture close log
exit


//
