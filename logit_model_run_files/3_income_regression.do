****************************************************************
******************** INCOME REGRESSIONS ************************
****************************************************************
clear all
set more off
set maxvar 32000
set matsize 10000

cd "/Users/hannahkamen/Documents/population-migration2"

// log file
capture log close
log using "log/log_3_income_regression.log", text replace


//age1-age7
forvalues a = 1/11 {
display `ageid'

clear
use "dta/acs5yr_1519_clr.dta", clear

// keep one age group
keep if ageid == `a'

// MSA
egen msa_inc = group(metarea)
merge m:1 metarea using "dta/msa_identifier.dta"
tabulate msa_inc if _merge == 1
drop if _merge != 3
drop _merge

unique metarea


// log income
gen lnincome = log(inctot)

// keep the necessary variables
keep lnincome white male old hsdrop hsgrad somecoll collgrad occup serial hhwt bpl ///
		msa metarea ftotinc hhincome inctot incwage statefip
		
// 9 census regions, current place
gen rd_r1 = 0
replace rd_r1 = 1 if statefip == 9 | statefip == 23 | statefip == 25 | statefip == 33 | ///
					statefip == 44 | statefip == 50
replace rd_r1 = 2 if statefip == 34 | statefip == 36 | statefip == 42
replace rd_r1 = 3 if statefip == 17 | statefip == 18 | statefip == 26 | ///
					statefip == 39 | statefip == 55
replace rd_r1 = 4 if statefip == 19 | statefip == 20 | statefip == 27 | statefip == 29 | ///
					statefip == 31 | statefip == 46 | statefip == 38
replace rd_r1 = 5 if statefip == 10 | statefip == 11 | statefip == 12 | statefip == 13 | ///
					statefip == 24 | statefip == 37 | statefip == 45 | statefip == 51 | statefip == 54
replace rd_r1 = 6 if statefip == 1 | statefip == 21 | statefip == 28 | statefip == 47
replace rd_r1 = 7 if statefip == 5 | statefip == 22 | statefip == 40 | statefip == 48
replace rd_r1 = 8 if statefip == 4 | statefip == 8 | statefip == 16 | statefip == 30 | ///
					statefip == 32 | statefip == 35 | statefip == 49 | statefip == 56
replace rd_r1 = 9 if statefip == 2 | statefip == 6 | statefip == 15 | statefip == 41 | statefip == 53

// 9 census regions, birth place
gen bp_r1 = 0
replace bp_r1 = 1 if bpl == 9 | bpl == 23 | bpl == 25 | bpl == 33 | ///
					bpl == 44 | bpl == 50
replace bp_r1 = 2 if bpl == 34 | bpl == 36 | bpl == 42
replace bp_r1 = 3 if bpl == 17 | bpl == 18 | bpl == 26 | ///
					bpl == 39 | bpl == 55
replace bp_r1 = 4 if bpl == 19 | bpl == 20 | bpl == 27 | bpl == 29 | ///
					bpl == 31 | bpl == 46 | bpl == 38
replace bp_r1 = 5 if bpl == 10 | bpl == 11 | bpl == 12 | bpl == 13 | ///
					bpl == 24 | bpl == 37 | bpl == 45 | bpl == 51 | bpl == 54
replace bp_r1 = 6 if bpl == 1 | bpl == 21 | bpl == 28 | bpl == 47
replace bp_r1 = 7 if bpl == 5 | bpl == 22 | bpl == 40 | bpl == 48
replace bp_r1 = 8 if bpl == 4 | bpl == 8 | bpl == 16 | bpl == 30 | ///
					bpl == 32 | bpl == 35 | bpl == 49 | bpl == 56
replace bp_r1 = 9 if bpl == 2 | bpl == 6 | bpl == 15 | bpl == 41 | bpl == 53

save "dta/data_roysorting_age`a'.dta", replace

// construct the Roy sorting term
//
// for all the high school dropouts who live in region i currently, 
// count the frequency of their birth places.
// conduct the process for all catagories of education.

net install carryforward.pkg, from(http://fmwww.bc.edu/RePEc/bocode/c/)
putexcel set "dta/roy_sorting_age`a'", sheet("ROY") replace
putexcel A1=("HSDROP")

local i 1
forval x = 2/10{
	putexcel A`x' = (`i')
	local i = `i' + 1
}
//

putexcel B1 = ("rd_r1")
putexcel C1 = ("rd_r2")
putexcel D1 = ("rd_r3")
putexcel E1 = ("rd_r4")
putexcel F1 = ("rd_r5")
putexcel G1 = ("rd_r6")
putexcel H1 = ("rd_r7")
putexcel I1 = ("rd_r8")
putexcel J1 = ("rd_r9")

/*
local j 2
excelcol `j'
local col `r(column)'

forval x = 1/9{
	putexcel `col'1 = ("rd_r`x'")
	local j = `j' + 1
	excelcol `j'
	local col `r(column)'
}
*/

local i 2
* local j 2
local count r(N)
* excelcol `j'
local col `r(column)'

forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 1 & bp_r1 == `y'
		putexcel B`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 2 & bp_r1 == `y'
		putexcel C`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 3 & bp_r1 == `y'
		putexcel D`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 4 & bp_r1 == `y'
		putexcel E`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 5 & bp_r1 == `y'
		putexcel F`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 6 & bp_r1 == `y'
		putexcel G`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 7 & bp_r1 == `y'
		putexcel H`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 8 & bp_r1 == `y'
		putexcel I`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 2
forval y = 1/9{
		count if hsdrop == 1 & rd_r1 == 9 & bp_r1 == `y'
		putexcel J`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}



********************************************************************************

putexcel A12=("HSGRAD")
local i 13
local k 1
forval x = 13/21{
	putexcel A`x' = (`k')
	local i = `i' + 1
	local k = `k' + 1
}

putexcel B12 = ("rd_r1")
putexcel C12 = ("rd_r2")
putexcel D12 = ("rd_r3")
putexcel E12 = ("rd_r4")
putexcel F12 = ("rd_r5")
putexcel G12 = ("rd_r6")
putexcel H12 = ("rd_r7")
putexcel I12 = ("rd_r8")
putexcel J12 = ("rd_r9")

/*
local j 2
excelcol `j'
local col `r(column)'

forval x = 1/9{
	putexcel `col'12 = ("rd_r`x'")
	local j = `j' + 1
	excelcol `j'
	local col `r(column)'
}
*/

local i 13
* local j 2
local count r(N)
* excelcol `j'
local col `r(column)'


forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 1 & bp_r1 == `y'
		putexcel B`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 2 & bp_r1 == `y'
		putexcel C`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 3 & bp_r1 == `y'
		putexcel D`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 4 & bp_r1 == `y'
		putexcel E`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 5 & bp_r1 == `y'
		putexcel F`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 6 & bp_r1 == `y'
		putexcel G`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 7 & bp_r1 == `y'
		putexcel H`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 8 & bp_r1 == `y'
		putexcel I`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 13
forval y = 1/9{
*	forval z = 1/9{
		count if hsgrad == 1 & rd_r1 == 9 & bp_r1 == `y'
		putexcel J`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


********************************************************************************
putexcel A23=("SOMECOLL")

local i 24
local k 1
forval x = 24/32{
	putexcel A`x' = (`k')
	local i = `i' + 1
	local k = `k' + 1
}

putexcel B23 = ("rd_r1")
putexcel C23 = ("rd_r2")
putexcel D23 = ("rd_r3")
putexcel E23 = ("rd_r4")
putexcel F23 = ("rd_r5")
putexcel G23 = ("rd_r6")
putexcel H23 = ("rd_r7")
putexcel I23 = ("rd_r8")
putexcel J23 = ("rd_r9")
/*
local j 2
excelcol `j'
local col `r(column)'

forval x = 1/9{
	putexcel `col'23 = ("rd_r`x'")
	local j = `j' + 1
	excelcol `j'
	local col `r(column)'
}
*/

local i 24
* local j 2
local count r(N)
* excelcol `j'
local col `r(column)'

forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 1 & bp_r1 == `y'
		putexcel B`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 2 & bp_r1 == `y'
		putexcel C`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 3 & bp_r1 == `y'
		putexcel D`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 4 & bp_r1 == `y'
		putexcel E`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 5 & bp_r1 == `y'
		putexcel F`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 6 & bp_r1 == `y'
		putexcel G`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 7 & bp_r1 == `y'
		putexcel H`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 8 & bp_r1 == `y'
		putexcel I`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 24
forval y = 1/9{
*	forval z = 1/9{
		count if somecoll == 1 & rd_r1 == 9 & bp_r1 == `y'
		putexcel J`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


*******************************************************************************

putexcel A34=("COLLGRAD")

local i 35
local k 1
forval x = 35/43{
	putexcel A`x' = (`k')
	local i = `i' + 1
	local k = `k' + 1
}

putexcel B34 = ("rd_r1")
putexcel C34 = ("rd_r2")
putexcel D34 = ("rd_r3")
putexcel E34 = ("rd_r4")
putexcel F34 = ("rd_r5")
putexcel G34 = ("rd_r6")
putexcel H34 = ("rd_r7")
putexcel I34 = ("rd_r8")
putexcel J34 = ("rd_r9")
/*
local j 2
excelcol `j'
local col `r(column)'

forval x = 1/9{
	putexcel `col'34 = ("rd_r`x'")
	local j = `j' + 1
	excelcol `j'
	local col `r(column)'
}
*/

local i 35
*local j 2
local count r(N)
*excelcol `j'
local col `r(column)'

forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 1 & bp_r1 == `y'
		putexcel B`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 2 & bp_r1 == `y'
		putexcel C`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}


local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 3 & bp_r1 == `y'
		putexcel D`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 4 & bp_r1 == `y'
		putexcel E`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 5 & bp_r1 == `y'
		putexcel F`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 6 & bp_r1 == `y'
		putexcel G`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 7 & bp_r1 == `y'
		putexcel H`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 8 & bp_r1 == `y'
		putexcel I`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

local i 35
forval y = 1/9{
*	forval z = 1/9{
		count if collgrad == 1 & rd_r1 == 9 & bp_r1 == `y'
		putexcel J`i' = (`count')
		local i = `i' + 1
*		}
*	local j = `j' + 1
*	excelcol `j'
*	local col `r(column)'
*	local i = `i' - 9
}

***********************************************************************

* HSDROP
import excel "dta/roy_sorting_age`a'.xlsx", sheet("ROY") cellrange(A1:J10) firstrow clear

// sum up households by birth place and years of schooling.
egen rowsum = rowtotal(rd_r1-rd_r9)
su rowsum
return list

// calculate the Roy sorting term. 
// the denominator is the total number of high school dropouts.
// the numerator is the number of people who were born in location i 
// and live in location j currently.
forval x = 1/9{
	rename rd_r`x' rd_`x'_orig
	gen rd_`x' = rd_`x'_orig / r(sum)
}
//
drop *_orig

// transform the matrix to a vector
forval x = 1/9{
	forval y = 1/9{
		gen roy_hsdrop`x'`y' = .
		replace roy_hsdrop`x'`y' = rd_`y' in `x'
		carryforward roy_hsdrop`x'`y', replace
		gsort -HSDROP
		carryforward roy_hsdrop`x'`y', replace
		sort HSDROP
	}
}		

drop rd_* HSDROP rowsum
gen roy_identifier = 1
save "dta/roy_sorting_hsdrop_age`a'.dta", replace

* HSGRAD
import excel "dta/roy_sorting_age`a'.xlsx", sheet("ROY") cellrange(A12:J21) firstrow clear

egen rowsum = rowtotal(rd_r1-rd_r9)
su rowsum
return list

forval x = 1/9{
	rename rd_r`x' rd_`x'_orig
	gen rd_`x' = rd_`x'_orig / r(sum)
}

drop *_orig

forval x = 1/9{
	forval y = 1/9{
		gen roy_hsgrad`x'`y' = .
		replace roy_hsgrad`x'`y' = rd_`y' in `x'
		carryforward roy_hsgrad`x'`y', replace
		gsort -HSGRAD
		carryforward roy_hsgrad`x'`y', replace
		sort HSGRAD
	}
}		

drop rd_* HSGRAD rowsum
gen roy_identifier = 1
save "dta/roy_sorting_hsgrad_age`a'.dta", replace

* SOMECOLL
import excel "dta/roy_sorting_age`a'.xlsx", sheet("ROY") cellrange(A23:J32) firstrow clear

egen rowsum = rowtotal(rd_r1-rd_r9)
su rowsum
return list

forval x = 1/9{
	rename rd_r`x' rd_`x'_orig
	gen rd_`x' = rd_`x'_orig / r(sum)
}

drop *_orig


forval x = 1/9{
	forval y = 1/9{
		gen roy_somecoll`x'`y' = .
		replace roy_somecoll`x'`y' = rd_`y' in `x'
		carryforward roy_somecoll`x'`y', replace
		gsort -SOMECOLL
		carryforward roy_somecoll`x'`y', replace
		sort SOMECOLL
	}
}		

drop rd_* SOMECOLL rowsum
gen roy_identifier = 1
save "dta/roy_sorting_somecoll_age`a'.dta", replace


* COLLGRAD
import excel "dta/roy_sorting_age`a'.xlsx", sheet("ROY") cellrange(A34:J43) firstrow clear

egen rowsum = rowtotal(rd_r1-rd_r9)
su rowsum
return list

forval x = 1/9{
	rename rd_r`x' rd_`x'_orig
	gen rd_`x' = rd_`x'_orig / r(sum)
}

drop *_orig


forval x = 1/9{
	forval y = 1/9{
		gen roy_collgrad`x'`y' = .
		replace roy_collgrad`x'`y' = rd_`y' in `x'
		carryforward roy_collgrad`x'`y', replace
		gsort -COLLGRAD
		carryforward roy_collgrad`x'`y', replace
		sort COLLGRAD
	}
}		

drop rd_* COLLGRAD rowsum
gen roy_identifier = 1
save "dta/roy_sorting_collgrad_age`a'.dta", replace

// merge
use "dta/roy_sorting_hsdrop_age`a'.dta", clear
merge m:m roy_identifier using "dta/roy_sorting_hsgrad_age`a'.dta"
drop _merge
merge m:m roy_identifier using "dta/roy_sorting_somecoll_age`a'.dta"
drop _merge
merge m:m roy_identifier using "dta/roy_sorting_collgrad_age`a'.dta"
drop _merge
keep in 1
save "dta/roy_sorting_all_age`a'.dta", replace

// again, roy_z_x_y menas the ratio of z-type people born in x and live y.
// A indexes the type of schooling of the HH head.
// this creates 9*9*3=243 indicators.

use "dta/data_roysorting_age`a'.dta", clear

gen roy_identifier = 1
merge m:1 roy_identifier using "dta/roy_sorting_all_age`a'.dta"

gen roy = 0

forval x = 1/9{
	forval y = 1/9{
		foreach z of varlist hsdrop hsgrad somecoll collgrad{
			replace roy = roy_`z'`x'`y' if bp_r1 == `x' & rd_r1 == `y' & `z' == 1
		}
	}
}
//
// the process above assgins one of the 243 indicators to 
// an household head based on their type of schooling, 
// birth place and current place.

gen roy2 = roy^2
drop roy_*

tab occup, gen(Ioccup)
*xi i.occup, noomit
// use "tab, gen()" instead of "xi i." since the latter 
// generates the dummies based on the value of occup, 
// however there is no occup=21 as we dropped it in the 
// data cleaning process..this will make the program 
// "gen b_occ_`x'_`y' = _b[_Ioccup_`y']" problematic.

save "dta/income_reg_age`a'.dta", replace

drop if msa == .
drop if occup == .

// run income regression for each MSA
unique msa //259
return list
scalar numb_msa = r(unique)

unique occup //23
return list
scalar numb_occup = r(unique)


forval x = 1/`=numb_msa'{
	use "dta/income_reg_age`a'.dta", clear
	reg lnincome white male old hsdrop hsgrad somecoll collgrad Ioccup* roy roy2 ///
		[pweight = hhwt] if msa == `x', noconst
		gen b_whi_`x' = _b[white]
		gen b_mal_`x' = _b[male]
		gen b_hsd_`x' = _b[hsdrop]
		gen b_hsg_`x' = _b[hsgrad]
		gen b_som_`x' = _b[somecoll]
		gen b_col_`x' = _b[collgrad]

	forval y = 1/`=numb_occup'{
		gen b_occ_`x'_`y' = _b[Ioccup`y']
		}
	keep msa metarea b_*
	keep in 1/`=numb_msa'
	save "dta/income_reg/coeff_msa`x'_age`a'.dta", replace
}
//

forval x = 1/`=numb_msa'{
	use "dta/income_reg/coeff_msa`x'_age`a'.dta", clear
	rename msa msa_orig
	egen msa = seq(), f(1) t(`=numb_msa')
	save "dta/income_reg/coeff_msa`x'_age`a'.dta", replace
}
//

use "dta/income_reg/coeff_msa1_age`a'.dta", clear
forval x = 2/`=numb_msa'{
	merge 1:1 msa using "dta/income_reg/coeff_msa`x'_age`a'"
	drop _merge
}
//


drop msa_orig metarea
save "dta/inchat_age`a'.dta", replace

foreach x in whi mal hsd hsg som col{
	gen b`x' = 0
	forval y = 1/`=numb_msa' {
		replace b`x' = b_`x'_`y' in `y'
	}
}
//

tabstat bwhi bmal bhsd bhsg bsom bcol, s(mean sd)

forval x = 1/`=numb_occup'{
	gen bocc`x' = 0
	foreach y of numlist 1/`=numb_msa'{
	replace bocc`x' = b_occ_`y'_`x' in `y'
	}
}

tabstat bocc*, s(mean sd)

label var bwhi "White"
tabstat bwhi bmal bhsd bhsg bsom bcol, s(mean sd) // f(%9.4f) 
tabstat bocc1-bocc23, s(mean sd)   // f(%9.4f)
save "dta/inchat_stat_age`a'.dta", replace

}
//


capture log close
exit
