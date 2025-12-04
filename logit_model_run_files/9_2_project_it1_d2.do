
cd "/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610"

clear all
set more off
set matsize 10000
set maxvar 20000

// log file
capture log close
log using "log/9_projections.log", text replace

forvalues t = 1/1{

*************************************************initial population shock********************

	forvalues i = 2/2{
		
		local tt = `t'-1
		
		use  "dta/projection_data_age`i'_01_wbmk_v2_`tt'.dta", clear
			
		merge m:1 statefip using "dta/gams_dta`t'_v2_d2.dta"
		drop _merge

		
		** lnrho is the percentage housing premium each msa has over yuma, AZ. GAMS data represents the increase relative to each msa's past value. 
		** To preserve the meaning of lnrho, that is the premium of each msa realtive to increase in yuma, must do some algebra
		
		***get AZ inflator as variable
		
		egen AZ_change0 = mean(ph) if abbrev == "AZ"
		egen AZ_change = max(AZ_change0)
		
		****get new premium that each msa has over yuma before considering that msa's change
		
		gen new_premium = ((1+lnrho)/AZ_change) -1
		
		gen lnrho_new = new_premium + (ph-1) + (new_premium*(ph-1))
		
		***rename coefficient to match
		
		gen  _b_lnrho_new = _b_lnrho
		
		**prepare by renaming variables specific to numerator by skilled and unskilled
		
		gen non_exp_num0 = 0
		gen non_exp_num1 = 0
				
			
		gen inc_level0 = exp(inc_hat)*pl_unskl if coll == 0
		gen inc_hat_new0 = ln(inc_level0) if coll == 0
		
		****rename coefficients		
		gen _b_inc_hat_new0 = _b_inc_hat if coll == 0
												
		foreach var of varlist _b_* {
			local newname : subinstr local var "_b_" ""
			replace non_exp_num0 = non_exp_num0+ `var'*`newname' if coll == 0
			}
   
		
			
		replace non_exp_num0 = (non_exp_num0 - (_b_inc_hat*inc_hat)) - (_b_lnrho*lnrho) if coll == 0

		
		**college educated
		
		gen inc_level1 = exp(inc_hat)*pl_skl if coll == 1
		gen inc_hat_new1 = ln(inc_level1) if coll == 1
			
		****rename coefficients
			
		gen _b_inc_hat_new1 = _b_inc_hat if coll == 1			
							
		foreach var of varlist _b_* {
			if `var' != _b_inc_hat_new0 {
				local newname : subinstr local var "_b_" ""
				replace non_exp_num1 = non_exp_num1+ `var'*`newname' if coll == 1
			}

		}
			
		replace non_exp_num1 = (non_exp_num1 - (_b_inc_hat*inc_hat)) - (_b_lnrho*lnrho) if coll == 1

		
		****end college loop
		
		gen non_exp_num = 0
		
		replace  non_exp_num = non_exp_num0 if coll == 0
		replace  non_exp_num = non_exp_num1 if coll == 1
		
		
		gen probability = exp(non_exp_num)
		
		sort id
		
		by id: egen total_probability = total(probability)
		
		gen share`t' = probability/total_probability

		drop probability total_probability non_exp_num inc_hat_new* lnrho_new ph pl_skl pl_unskl new_premium AZ_change*  non_exp_num* _b_inc_hat_new* inc_level* _b_lnrho_new
		
		save "dta/projection_data_age`i'_01_wbmk_v2_`t'_tag.dta", replace

		
		local tt = `t'-1
				
		collapse (rawsum) shareb share0 share`t' (max) fexthot_28 (min) fextcold, by(statefip coll)

		gen state_pct_change`t'_uw = (share`t' - share`tt')/share`tt'
		
		gen age_id = `i'
	
		save "dta/age`i'_le0_shock`t'_v2_uw.dta", replace
			
	}

***prep data for GAMS
**for now just use age2

	cd "/Users/hannahkamen/Downloads/population-migration-master/estimation/1_main_specification/acs5yr0610"

	use "dta/age2_le0_shock`t'_v2_uw.dta", clear

	// forvalues i = 3/7{
	//	
	// 	append using "dta/age`i'_le0_shock0.dta"
	//
	// }
			
	merge m:1 statefip using "dta/state_age_shares_lkup.dta"
	drop _merge


	*for now age group 2 is entire population
	gen state_pct_change`t'_w = state_pct_change`t'_uw*1 if age_id ==2
	// replace state_pct_change`t'_w = state_pct_change`t'_uw*age3_ if age_id ==3
	// replace state_pct_change`t'_w = state_pct_change`t'_uw*age4_ if age_id ==4
	// replace state_pct_change`t'_w = state_pct_change`t'_uw*age5_ if age_id ==5
	// replace state_pct_change`t'_w = state_pct_change`t'_uw*age6_ if age_id ==6
	// replace state_pct_change`t'_w = state_pct_change`t'_uw*age7_ if age_id ==7

	collapse (rawsum) state_pct_change`t'_w (max) fexthot_28 (min) fextcold, by(abbrev coll)
		
		
	rename abbrev r

	gen sk = ""

	replace sk = "unskl" if coll == 0
	replace sk = "skl" if coll == 1


	rename state_pct_change`t'_w skill_shr 

	drop if sk == ""


	cd "/Users/hannahkamen/Downloads"

	***merge in full factorial, change to zero change for workers not living in the place they workers

	merge 1:m r sk using "le0_factorial.dta"
	drop _merge

	sort r q

	// replace skill_shr = 0 if q!=r
	replace skill_shr = 0 if missing(skill_shr)

	outsheet r q h sk skill_shr using "le0_shock1_v2_test2_adj_d2_tag.csv", comma replace			
	

	
	
	
	
		
}
capture close log
exit
