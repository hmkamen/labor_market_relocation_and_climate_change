*******************************************************************************
******************************** HOUSING PRICE ********************************
*******************************************************************************
clear all
set more off
set matsize 10000

cd "/Users/hannahkamen/Documents/population-migration2"

capture log close
log using "log/log_2_housing_regression.log", text replace

// load cleaned data
use "dta/acs5yr_1519_clr.dta", clear



// get rid of no cash renters
count if rent == 0 & valueh == 9999999
tabulate ownershpd
tab rent
drop if rent == 0 & valueh == 9999999
drop if ftotinc <= 0


drop if missing(msa)

// drop unused variables
drop  str_PumaID county city citypop puma  ///
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
// these variables are n.a. in the acs data
// tab acreprop, nolabel			
// tab acreprop
// gen acre1_9 = 0
// replace acre1_9 = 1 if acreprop == 7
// gen acre10 = 0
// replace acre10 = 1 if acreprop == 8


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


tab rooms, nolab
tab rooms
tab bedrooms, nolab
tab bedrooms
tab builtyr2,nolab
tab builtyr2


// clean rooms variable
replace rooms = 9 if rooms >= 9

// clean bedrooms variable

replace bedrooms = 6 if bedrooms >= 6


// clean builtyr 

replace builtyr = 10 if builtyr >=10




tab rooms, nolab //1-9 
tab rooms
tab bedrooms, nolab //1-6
tab builtyr, nolab //1-10
// tab units, nolab //1-10


// create dummies
xi i.msa i.rooms i.bedrooms i.builtyr, noomit



// number of MSAs
unique msa //261
return list
scalar numb_msa = r(unique)

foreach x of numlist 1/`=numb_msa' {
gen omega`x' = _Imsa_`x' * homeown
}


reg lphouse _Imsa_2-_Imsa_`=numb_msa' _Irooms_2-_Irooms_9 ///
			_Ibedrooms_2-_Ibedrooms_6 _Ibuiltyr2_2-_Ibuiltyr2_10 ///
			nokitch noplumb units2-units10 ///
			omega1-omega`=numb_msa'
			
			


// export results, latex format
*outreg2 using "results/table3_housing_price.tex", replace tex(frag) bdec(3) ///
*		keep(_Irooms* _Ibedrooms* _Ibuiltyr2* units2-units10 nokitch noplumb ) ///
*		label ctitle ($ p_j $)

// export results, Excel format	
outreg2 using "results/table3_housing_price.xls", replace ///
		keep(_Irooms* _Ibedrooms* _Ibuiltyr2* units2-units10 nokitch noplumb )

*su _Irooms* _Ibedrooms* _Ibuiltyr* acre1_9 acre10 units* incwage inctot
*di sum(_b[omega1]-_b[omega`=numb_msa']) / `=numb_msa'

// prices of housing services of MSAs relative to MSA 1	
gen lnrho = 0								
foreach x of numlist 2/`=numb_msa' {
replace lnrho = _b[_Imsa_`x'] if msa == `x' 
}
su lnrho

// save
rename msa msa_housing
keep serial pernum lnrho msa metarea
drop if serial == .
save "dta/acs5yr_1519_housing.dta", replace
*export delimited using "results/rank_msa_phousing_acs.csv", replace


********************************************************************************
*****************  MERGE HOUSING RESULT TO REDUCED HH SUBSET	****************
********************************************************************************

// merge household data and housing data
// all age
use "dta/acs5yr_1519_clr_shrink_all", clear
merge 1:1 serial using "dta/acs5yr_1519_housing.dta"
drop if _merge != 3
drop _merge

// further reduce the sample size to 80,000
set seed 1000
gen random = runiform()
sort random
keep in 1/80000	
drop random

// save
save "dta/acs5yr_1519_hss_all.dta", replace

// unique serial
// use "dta/acs5yr_1519_clr_shrink_age1.dta", clear
// exit
// age groups 1-11
forvalues i = 1/11 {
	use "dta/acs5yr_1519_clr_shrink_age`i'.dta", clear
	drop if serial == .
	merge 1:1 serial using "dta/acs5yr_1519_housing.dta"
	drop if _merge != 3
	drop _merge

	set seed 1000
	gen random = runiform()
	sort random
	keep in 1/80000	
	drop random

	save "dta/acs5yr_1519_hss_age`i'.dta", replace
}
//

capture log close
exit
