********************************************************************************
********************* MCFADDEN-TYPE CONDITIONAL LOGIT **************************
********************************************************************************
cd "/Users/hannahkamen/Documents/population-migration2/"

clear all
set more off
set matsize 10000
set maxvar 20000

forval a = 10/11{
//28c age 1-11
capture log close  
log using "log/log_6_clogit_28c_age`a'.log", text replace
use "dta/logit-ready_full_age`a'.dta", clear



drop if msa == 111

drop if msa == .

asclogit chosen inc_hat hot_28C* cold_0C* ///
	d_s d_r1 d_r2 d_s_kid d_r1_kid d_r2_kid, case(id) alt(msa)

// save regional fixed effects in a separate file for 2nd stage regression
putexcel set "dta/regionfe_bpl_28_age`a'", replace
putexcel A1 = ("msa")
local i 2

forval x = 1/270{
	if `x' <= 110 putexcel A`i' = (`x') 
	if `x' > 110 putexcel A`i' = (`x'+ 1 ) 
	local i = `i' + 1
}

putexcel B1 = ("regionfe")
putexcel B2 = (0)
matrix B = e(b)'
matrix list B
matrix MAT = B[18..., 1]
matrix list MAT
putexcel B3 = matrix(MAT)

// save results to pivot table
putexcel set "results/1st_stage_28_age`a'", replace
putexcel A1 = ("variable")	// Variable name
putexcel B1 = ("value")   	// Value
putexcel C1 = ("type")    	// point estimate / t-stat / p-value
putexcel D1 = ("age")		// age1 / age2 / age3 / age4 / age5 / age6 / age7
putexcel E1 = ("sample")	// 80k
putexcel F1 = ("htemp")		// 26C / 28C / 30C / min/max / summer/winter
putexcel G1 = ("data")		// 2000 / acs

// coefficients
putexcel A2 = ("inc_hat")
putexcel A3 = ("Hot_CA")
putexcel A4 = ("Hot_West")
putexcel A5 = ("Hot_Midwest")
putexcel A6 = ("Hot_Northeast")
putexcel A7 = ("Hot_College")
putexcel A8 = ("Cold_CA")
putexcel A9 = ("Cold_West")
putexcel A10 = ("Cold_Midwest")
putexcel A11 = ("Cold_Northeast")
putexcel A12 = ("Cold_College")
putexcel A13 = ("d_s")
putexcel A14 = ("d_r1")
putexcel A15 = ("d_r2")
putexcel A16 = ("d_s_kid")
putexcel A17 = ("d_r1_kid")
putexcel A18 = ("d_r2_kid")

matrix D = e(b)'
matrix MA = D[1..17, 1]
putexcel B2 = matrix(MA)

// s.e.
putexcel A19 = ("inc_hat")
putexcel A20 = ("Hot_CA")
putexcel A21 = ("Hot_West")
putexcel A22 = ("Hot_Midwest")
putexcel A23 = ("Hot_Northeast")
putexcel A24 = ("Hot_College")
putexcel A25 = ("Cold_CA")
putexcel A26 = ("Cold_West")
putexcel A27 = ("Cold_Midwest")
putexcel A28 = ("Cold_Northeast")
putexcel A29 = ("Cold_College")
putexcel A30 = ("d_s")
putexcel A31 = ("d_r1")
putexcel A32 = ("d_r2")
putexcel A33 = ("d_s_kid")
putexcel A34 = ("d_r1_kid")
putexcel A35 = ("d_r2_kid")

local i 19
foreach x of varlist inc_hat hot_28C_ca hot_28C_w hot_28C_mw hot_28C_ne hot_28C_coll ///
  cold_0C_ca cold_0C_w cold_0C_mw cold_0C_ne cold_0C_coll d_s d_r1 d_r2 ///
  d_s_kid d_r1_kid d_r2_kid {
  putexcel B`i' = (_se[`x'])
  local i = `i' + 1
}

// p-value
putexcel A36 = ("inc_hat")
putexcel A37 = ("Hot_CA")
putexcel A38 = ("Hot_West")
putexcel A39 = ("Hot_Midwest")
putexcel A40 = ("Hot_Northeast")
putexcel A41 = ("Hot_College")
putexcel A42 = ("Cold_CA")
putexcel A43 = ("Cold_West")
putexcel A44 = ("Cold_Midwest")
putexcel A45 = ("Cold_Northeast")
putexcel A46 = ("Cold_College")
putexcel A47 = ("d_s")
putexcel A48 = ("d_r1")
putexcel A49 = ("d_r2")
putexcel A50 = ("d_s_kid")
putexcel A51 = ("d_r1_kid")
putexcel A52 = ("d_r2_kid")

local i 36
foreach x of varlist inc_hat hot_28C_ca hot_28C_w hot_28C_mw hot_28C_ne hot_28C_coll ///
  cold_0C_ca cold_0C_w cold_0C_mw cold_0C_ne cold_0C_coll d_s d_r1 d_r2 ///
  d_s_kid d_r1_kid d_r2_kid {
  putexcel B`i' = (2 * ttail(21520000, abs(_b[`x'] / _se[`x'])))
  local i = `i' + 1
}

// type
forval x = 2/18 {
  putexcel C`x' = ("point estimate")
}
forval x = 19/35 {
  putexcel C`x' = ("std. err.")
}
forval x = 36/52 {
  putexcel C`x' = ("p-value")
}
forval x = 2/52 {
  putexcel D`x' = ("age`a'")		// age1 / age2 / age3 / age4 / age5 / age6 / age7
}
forval x = 2/52 {
  putexcel E`x' = ("80k")	// 80k
}
forval x = 2/52 {
  putexcel F`x' = ("28C")	// 26C / 28C / 30C / min/max / summer/winter
}
forval x = 2/52 {
  putexcel G`x' = ("acs")	// 2000 / acs
}

} // age loop

capture log close
exit
