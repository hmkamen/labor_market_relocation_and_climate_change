********************************************************************************
********************* MCFADDEN-TYPE CONDITIONAL LOGIT **************************
********************************************************************************
cd "/Users/hannahkamen/Documents/population-migration2"

clear all
set more off
set matsize 10000
set maxvar 20000

// age 1
forval i = 1/11{
import excel using "results/1st_stage_28_age`i'", clear firstrow
local j = 21 + (`i' - 1) * 5
local k = 25 + (`i' - 1) * 5
display "`j'-`k'"
replace age = "`j'-`k'"
save "results/1st_stage_28_age`i'", replace
}

// age 11
import excel using "results/1st_stage_28_age11", clear firstrow
replace age = "71-"
save "results/1st_stage_28_age11", replace

// append
use "results/1st_stage_28_age1", clear
forval i = 1/11{
append using "results/1st_stage_28_age`i'"
save "results/1st_stage_28_acs", replace
}

tab age

export delimited using "results/1st_stage_28_acs", replace
