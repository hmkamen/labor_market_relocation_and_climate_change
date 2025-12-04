********************************************************************************
********************* MCFADDEN-TYPE CONDITIONAL LOGIT **************************
********************************************************************************
cd "/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610"

clear all
set more off
set matsize 10000
set maxvar 20000

// log file
capture log close
log using "log/9_projections.log", text replace


********************************************************************
// 28c
// load data



*************************************************************
*********get first stage coefficients************************
*************************************************************
*i indexes age
forvalues i = 2/2{
	
	import excel using "results/1st_stage_28_age`i'.xlsx", firstrow clear
	keep if type == "p-value"
	keep if value <=.1
	gen p_value = value
	drop value
	save "results/1st_stage_28_age`i'_sig_list.dta",replace

	
	import excel using "results/1st_stage_28_age`i'.xlsx", firstrow clear
	
	keep if type == "point estimate"
	
	merge 1:1 variable using "results/1st_stage_28_age`i'_sig_list.dta"
	
	drop if _merge == 1


	keep if type == "point estimate"
	
	drop type age sample htemp data p_value _merge

	sort value
	
	by value: gen newid = _n
	
	reshape wide value, i(newid) j(variable) string

   foreach var of varlist * {
	   local newname : subinstr local var "value" ""
	   rename `var' `newname'
       
    }
	
	foreach x of varlist *{
    gen _b_`x' = `x'
	}
	
	keep _b*
	
	save results/1st_stage_28_age`i'_sig.dta,replace
	
	
	
//
// 	foreach x in "inc_hat" "Hot_CA" "Hot_West" "Hot_Midwest" "Hot_Northeast" "Hot_College" "Cold_CA" "Cold_West" "Cold_Midwest" "Cold_Northeast" "Cold_College" "d_s" "d_r1" "d_r2" "d_s_kid" "d_r1_kid" "d_r2_kid"{
//      scalar _b_`x' = value`x'
// 	}
	
	
  		
*******************get fixed effect coefficients****************************	
	
	use "results/temp/2nd_stage_avg_age`i'.dta", clear
	
	drop if pval > .1

	keep var coef

	sort coef
	
	by coef: gen newid = _n
	
	reshape wide coef, i(newid) j(var) string	
	
   foreach var of varlist * {
	   local newname : subinstr local var "coef" ""
	   rename `var' `newname'
       
    }
	
	
	foreach x of varlist *{
		gen _b_`x' = `x'
	}
	
	keep _b*
	
	save results/2nd_stage_28_age`i'_sig.dta,replace
	

*******************get betah***********************************************

// from the file "beta_H" in folder "results"
	import excel using "results/beta_H", firstrow clear

	local k = 1
    keep if htem == "28"
	keep if age == "age`i'"
	
	gen _b_newid = 1
	
	merge 1:1 _b_newid using "results/1st_stage_28_age`i'_sig.dta"
	
	drop _merge
	
	merge 1:1 _b_newid using "results/2nd_stage_28_age`i'_sig.dta"
	
	drop _merge
	
	
	
	
	rename _all, lower
	rename beta_h _b_lnrho
	rename _b_cold_college _b_cold_coll
	rename _b_hot_college _b_hot_coll
	
	foreach var of varlist * {
		local newname : subinstr local var "midwest" "mw"
		rename `var' `newname'
       
    }
	
	foreach var of varlist * {
		local newname : subinstr local var "northeast" "ne"
		rename `var' `newname'
       
    }
	
	foreach var of varlist * {
	local newname : subinstr local var "west" "w"
	rename `var' `newname'
   
	}
	save "results/age`i'_sig_coefs.dta", replace
	
	
**************************************************************************
**************************************************************************
**************************************************************************	
**************************************************************************
*****************Begin Skill Loop*****************************************
**************************************************************************
**************************************************************************
**************************************************************************
**************************************************************************
	
	forvalues j = 0/1{
		use chosen inc_hat  hot_28* cold_0* d_s d_r1 d_r2 d_s_kid ///
		d_r1_kid d_r2_kid id msa bpl coll using "dta/logit-ready_full_age`i'.dta", clear
		
		



		
		gen _b_newid = 1
		
		merge m:1 _b_newid using "results/age`i'_sig_coefs.dta"
		
		drop _merge

		// drop MSA 111
		
		if `i' == 2 drop if msa ==111

		keep if coll == `j'

		************prepare betas from previous regressions*********************************

		merge m:1 msa using "dta/second_stage_dataset_cl.dta"
		drop _merge
		
		
		**get chicago back in there, replace lncrime with estimate of crime rate
		
		replace lncrime = -3.21 if msa == 46
		

		*****re-make usda regional variables

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
						
		gen usda_ca = 0
		gen usda_w = 0
		gen usda_mw = 0
		gen usda_ne = 0
	
		replace usda_ca = 1 if clizone == 2
		replace usda_w = 1 if clizone == 3
		replace usda_mw = 1 if clizone == 4
		replace usda_ne = 1 if clizone == 5
	
	// 	*************************create future hot/cold vars********************
		egen fexthot_28 = rowtotal(wa_fbin158-wa_fbin222)
		egen fextcold = rowtotal(wa_fbin1-wa_fbin101)
	
		drop wa_*
	
		*****regional heterogenaity
	
		gen fhot = (fexthot_28 + hot)
		gen fcold = (fextcold + cold)
	
	
		foreach x in ca w mw ne {
			gen fhot_`x' = usda_`x' * (fhot)
			gen fcold_`x' = usda_`x' * (fcold)
		}

		*************education heterogeneity
		gen fcold_coll = coll * fcold
		gen fhot_coll = coll * fhot
		
		

		drop usda* 
		
		****rename to match coefficienct columns
		
		
	   foreach var of varlist hot* {
		   local newname : subinstr local var "_28C" ""
		   rename `var' `newname'
       
		}
	
	
	   foreach var of varlist cold* {
		   local newname : subinstr local var "_0C" ""
		   rename `var' `newname'
       
		}

		*get projections by age and skill
		
		drop _b_newid
		
		gen non_exp_num = 0
		foreach var of varlist _b_* {

			local newname : subinstr local var "_b_" ""
            replace non_exp_num = non_exp_num + `var'*`newname'
       
		}
		
		
		gen probability_b = exp(non_exp_num)
		
		sort id
		
		by id: egen total_probability_b = total(probability_b)
		
		gen shareb = probability/total_probability
		
		by id: egen sum_id_share = total(shareb)
		
		drop non_exp_num sum_id_share total_probability_b probability_b
		
		save "dta/projection_data_age`i'_`j'_wbmk_v2.dta", replace
		
				

			
	}	
} 



capture close log
exit		
