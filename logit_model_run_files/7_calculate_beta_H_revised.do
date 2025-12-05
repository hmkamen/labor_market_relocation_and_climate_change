// calculate_beta_H

clear all
set more off
set matsize 10000

cd "/Users/hannahkamen/Documents/population-migration2"

capture log close
log using "log/log_7_beta_H.log", text replace

forval i = 1/11{
use "results/1st_stage_28_age`i'",clear
keep if variable == "inc_hat" 
keep if type == "point estimate"
summ value
scalar alpha_28_age`i' = r(sum)
display alpha_28_age`i'
}



// load cleaned data
use "dta/acs5yr_1519_clr.dta", clear

drop if msa == .

// get rid of no cash renters
count if rent == 0 & valueh == 9999999
tabulate ownershpd
drop if rent == 0 & valueh == 9999999
drop if ftotinc <= 0

// drop unused variables
drop str_PumaID county city citypop puma ///
	cpuma0010 gq marst migpuma movedin pwstate2 trantime

// estimate "prices of housing services" at each location
// annualized housing price for home owners	
gen annualp = valueh * (0.04 + 0.02) / (1 + 0.04)
*	A = V * (r+d) / (1+r) where
*		A: annualized value of house
*		V: sale price of the home
*		r: annual interest rate (4% assumed)
*		d: annual depreciation rate (2% assumed)

// combine value of house (for owners) and rental payments (for renters)
gen phouse = 0
replace phouse = annualp if ownershp == 1
replace phouse = rent * 12 if ownershp == 2
count if phouse == 0

// add utility, insurance, and tax costs
foreach x of varlist costelec costwatr costfuel costgas{
replace `x' = 0 if `x' == 9993 | `x' == 9997
}
replace phouse = phouse + costelec + costgas + costwatr + costfuel + propinsr + proptx99

*tabstat phouse, by(ownershp) s(n mean sd min max)

// take logarithm 
gen lphouse = log(phouse)

// ownership dummy
gen homeown = 0
replace homeown = 1 if ownershp == 1

// righthand side variables of the housing regression
/* // these variables are n.a. in the acs data
tab acreprop, nolabel			
tab acreprop
gen acre1_9 = 0
replace acre1_9 = 1 if acreprop == 7
gen acre10 = 0
replace acre10 = 1 if acreprop == 8
*/

tab kitchen
tab kitchen, nolab
gen nokitch = 0
replace nokitch = 1 if kitchen == 1

tab plumbing
tab plumbing, nolab
gen noplumb = 0
replace noplumb = 1 if plumbing == 10

tab unitsstr
tab unitsstr, nolab
foreach x of numlist 1/10{
gen units`x' = 0
replace units`x' = 1 if unitsstr == `x'

}


// clean rooms variable
replace rooms = 9 if rooms >= 9

// clean bedrooms variable

replace bedrooms = 6 if bedrooms >= 6


// clean builtyr 

replace builtyr = 10 if builtyr >=10

// create dummies
xi i.msa i.rooms i.bedrooms i.builtyr, noomit

// number of MSAs
unique msa //270
return list
scalar numb_msa = r(unique)

foreach x of numlist 1/`=numb_msa' {
gen omega`x' = _Imsa_`x' * homeown
}

// housing regression
reg lphouse _Imsa_2-_Imsa_`=numb_msa' _Irooms_2-_Irooms_9 ///
			_Ibedrooms_2-_Ibedrooms_6 _Ibuiltyr2_2-_Ibuiltyr2_10 ///
			nokitch noplumb units2-units10 ///
			omega1-omega`=numb_msa'

*su _Irooms* _Ibedrooms* _Ibuiltyr* acre1_9 acre10 units* incwage inctot
*di sum(_b[omega1]-_b[omega`=numb_msa']) / `=numb_msa'

// prices of housing services of MSAs relative to MSA 1	
gen lnrho = 0								
foreach x of numlist 2/`=numb_msa' {
replace lnrho = _b[_Imsa_`x'] if msa == `x' 
}

*su lnrho

predictnl housingsvc = _b[_cons] + _b[_Irooms_2] * _Irooms_2 + ///
					   _b[_Irooms_3] * _Irooms_3 + _b[_Irooms_4] * _Irooms_4 + ///
					   _b[_Irooms_5] * _Irooms_5 + _b[_Irooms_6] * _Irooms_6 + ///
					   _b[_Irooms_7] * _Irooms_7 + _b[_Irooms_8] * _Irooms_8 + ///
					   _b[_Irooms_9] * _Irooms_9 + ///
					   _b[_Ibedrooms_2] * _Ibedrooms_2 + ///
					   _b[_Ibedrooms_3] * _Ibedrooms_3 + _b[_Ibedrooms_4] * _Ibedrooms_4 + ///
					   _b[_Ibedrooms_5] * _Ibedrooms_5 + _b[_Ibedrooms_6] * _Ibedrooms_6 + ///
					   _b[_Ibuiltyr2_1] * _Ibuiltyr2_1 + _b[_Ibuiltyr2_2] * _Ibuiltyr2_2 + ///
					   _b[_Ibuiltyr2_3] * _Ibuiltyr2_3 + _b[_Ibuiltyr2_4] * _Ibuiltyr2_4 + ///
					   _b[_Ibuiltyr2_5] * _Ibuiltyr2_5 + _b[_Ibuiltyr2_6] * _Ibuiltyr2_6 + ///
					   _b[_Ibuiltyr2_7] * _Ibuiltyr2_7 + ///
					   _b[nokitch] * nokitch + _b[noplumb] * noplumb + ///
					   _b[units2] * units2 + ///
					   _b[units3] * units3 + _b[units4] * units4 + ///
					   _b[units5] * units5 + _b[units6] * units6 + ///
					   _b[units7] * units7 + _b[units8] * units8 + ///
					   _b[units9] * units9 + _b[units10] * units10
					   
// calculate beta_H, see footnote 5 on page 7, version Oct 2019.
// beta_h = alpha * exp(lnrho) * exp(housingsvc) / incwage	

// the values of alpha are from the results of the 
// conditional logit regressions,
// i.e. the coefficients on inc_hat


// scalar alpha_28_age1 = 0.02028184
// scalar alpha_28_age2 = 0.219844529
// scalar alpha_28_age3 = 0.229766126
// scalar alpha_28_age4 = 0.275639098
// scalar alpha_28_age1 = 0.020165205
// scalar alpha_28_age2 = 0.220051701
// scalar alpha_28_age3 = 0.229534487
// scalar alpha_28_age4 = 0.274741512
// scalar alpha_28_age5 = 0.176121344  
// scalar alpha_28_age6 = 0.204659023 
// scalar alpha_28_age7 = 0.157808511  
// scalar alpha_28_age8 = 0.172062392 
// scalar alpha_28_age9 = 0.106606917
// scalar alpha_28_age10 = 0.108444633 
// scalar alpha_28_age11 = 0.090703422  



// calculate and save the values of beta_H to "results"
putexcel set "results/beta_H", replace
putexcel A1 = ("htem")
putexcel B1 = ("age")	
putexcel C1 = ("beta_H")  	


// 28
forval a = 1/11{ // age loop
	local i = `a' + 1
	putexcel A`i' = ("28")
	putexcel B`i' = ("age`a'")
	capture drop beta_h
	gen beta_h =  alpha_28_age`a' * exp(lnrho) * exp(housingsvc) / incwage	
	// we use median value of beta_h
	tabstat beta_h, s(median) save
	matrix median = r(StatTotal)
	putexcel C`i' = matrix(median)
}


// load these values to the do files that run the second stage regression

capture log close
exit
