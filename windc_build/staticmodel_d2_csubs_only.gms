$title	Read a Dataset and Replicate the Static Equilibrium

* -----------------------------------------------------------------------------
* set options
* -----------------------------------------------------------------------------

* set year of interest
$if not set year $set year 2017

* set elasticity of substitution between labor skill types
$if not set esub_labor $set esub_labor 1.6

* set elasticity of supply to other regions
$if not set e_nu  $set e_nu 2


* set elasticity of supply to other regions
$if not set esub_nat  $set esub_nat 4

* set elasticity of supply to foreign markets
$if not set e_nu_m  $set e_nu_m 4


* set elasticity of substitution in consumption
$if not set esub_cons  $set esub_cons 0

* migration scenario
$if not setglobal pct $setglobal pct .05

* set underlying dataset for recalibration
$if not set hhdata $set hhdata cps

* switch for dynamic calibration (static vs. dynamic)
$if not set invest $set invest static


* set top level elasticity of substitution
$if not set esubp_top  $set esubp_top  1


* migration scenario
$if not setglobal pct $setglobal pct .05

* set underlying dataset for recalibration
$if not set hhdata $set hhdata cps

* switch for dynamic calibration (static vs. dynamic)
$if not set invest $set invest static

* file separator
$set sep %system.dirsep%

*	GDX directory

$set gdxdir gdx%sep%

*	Core data directory:
$if not set core $set core ..%sep%core%sep%

* -----------------------------------------------------------------------------
* read in dataset
* -----------------------------------------------------------------------------

* read in base windc data

$set ds '%core%WiNDCdatabase.gdx'
$include '%core%windc_coredata.gms'


set house(s)    /"hou"/;
alias (r,q,rr), (s,g);


* add capital tax rate
parameter
    tk0(r)    Capital tax rate
    esubland(r);

$gdxin "%gdxdir%capital_taxrate_%year%.gdx"

$loaddc tk0

* convert gross capital payments to net
kd0(r,s) = kd0(r,s) / (1+tk0(r));

* read in household data
$gdxin "%gdxdir%calibrated_hhdata_%hhdata%_%invest%_%year%.gdx"
set
    h     Household categories,
    trn   Transfer types;

set sk labor skill /skl,unskl/;


$load h trn
alias(h,hh),(r,q), (g,gg);


*read in labor endowment shares

SET
col     /skill_shr/
col_lsub /housing_elasticity/;

PARAMETERS
sk_sh_le(r,q,h,sk)
sk_sh_les(r,h,sk);


TABLE  skill_shr_le0(r,q,h,sk,col)
$ondelim
$include le0_shr2.csv
$offdelim
;


**read in region household shares

TABLE  skill_shr_le0s(r,h,sk,col)
$ondelim
$include le0_shr2s.csv
$offdelim
;


**read in region elasticities

TABLE  housing_elasticities(r,col_lsub)
$ondelim
$include elasticity_lookup_final_min.csv
$offdelim
;

esubland(r)=housing_elasticities(r,"housing_elasticity");

sk_sh_le(r,q,h,sk)=skill_shr_le0(r,q,h,sk,"skill_shr");
sk_sh_les(r,h,sk)=skill_shr_le0s(r,h,sk,"skill_shr");


*load original household level parameters 

parameter
    le0(r,q,h)	   Household labor endowment,
    ke0(r,h)	   Household interest payments,
    tl0(r,h)	   Household labor tax rate,
    cd0_h(r,g,h)   Household level expenditures,
    c0_h(r,h)	   Aggregate household level expenditures,
    sav0(r,h)	   Household saving,
    trn0(r,h)	   Household transfer payments,
    hhtrn0(r,h,*)  Disaggregate transfer payments,
    pop(r,h)       Population (households or returns in millions)

    pe0(r,h)       Household property endowments
    esubl(s)       labor substitution between skilled and unskilled
    nu             elasticity of supply to regional markets
    nu_m           elasticity of supply to foreign markets
    esubc          elasticity of substitution in consumption
    esubtop      va elasticity of substitution
    esubnat      transformation in disposition
    pct_land_endow  percent of capital endowmentthan becomes land endowment;

$loaddc le0 ke0 tl0 cd0_h c0_h sav0 trn0 hhtrn0 pop

*split out capital endowment to property
*property endowment is equal to 5% of existing capital endowment

pct_land_endow=.001;

pe0(r,h)= ke0(r,h)*pct_land_endow;

*subtract from capital endowment

ke0(r,h)=ke0(r,h)-(ke0(r,h)*pct_land_endow);

* get subs param from supply elasticity

esubland(r)=(esubland(r)*pct_land_endow)/(1-pct_land_endow);

esubl(s) = %esub_labor%;
nu=%e_nu%;
nu_m=%e_nu_m%;

esubc=%esub_cons%;
esubtop=%esubp_top%;

esubnat=%esub_nat%;

* load disaggregate household level parameters

parameter
    le0_d(r,q,h,sk)          Household labor endowment,

    ke0_d(r,h,sk)       Household interest payments, 
    sav0_d(r,h,sk)      Household saving,
    trn0_d(r,h,sk)      Household transfer payments,
    hhtrn0_d(r,h,sk,*)  Disaggregate transfer payments,

    tl0_d(r,h,sk)       household labor tax rate
    cd0_h_d(r,g,h,sk)        Household level expenditures,
    c0_h_d(r,h,sk)           Aggregate household level expenditures,


    pop_d(r,h,sk)       Population (households or returns in millions)
    tot_wrkers(r,h)     total workers by region and household
    tot_wrkers_sk(r,h,sk)   total workers by region household and skill type

    pe0_d(r,h,sk)         dissagregate property endowment
    pd0(r,s)              benchmark property demand  

;

* breakout hh params at skill level

tl0_d(r,h,sk)=tl0(r,h);

le0_d(r,q,h,sk)=le0(r,q,h)*sk_sh_le(r,q,h,sk);

*----------------------------------------------
*create shares by r,h,s for "at home" variables
*----------------------------------------------

pe0_d(r,h,sk) = pe0(r,h)*sk_sh_les(r,h,sk);

ke0_d(r,h,sk)=ke0(r,h)*sk_sh_les(r,h,sk);

sav0_d(r,h,sk)=sav0(r,h)*sk_sh_les(r,h,sk);

trn0_d(r,h,sk)=trn0(r,h)*sk_sh_les(r,h,sk);

hhtrn0_d(r,h,sk,trn)=hhtrn0(r,h,trn)*sk_sh_les(r,h,sk);

cd0_h_d(r,g,h,sk) =cd0_h(r,g,h)*sk_sh_les(r,h,sk);

c0_h_d(r,h,sk) = c0_h(r,h)*sk_sh_les(r,h,sk);

pop_d(r,h,sk) = pop(r,h)*sk_sh_les(r,h,sk);

*----------------------------------------------
*create shares for property demand from capital demand/endowment
*----------------------------------------------

* breakout property demand for housing market

*set property demand equal to property endowment in each region

pd0(r,"hou")=sum(h,pe0(r,h));

*set capital demand for housing equal to original capital demand less the total value of property endowment in region 

kd0(r,"hou")=kd0(r,"hou")-sum(h,pe0(r,h));



*define sum of skilled and unskilled workforce across households

* reassign steady state parameters as needed
parameter
    ys0_ss(r,s,g)	Steady state output,
    id0_ss(r,g,s)	Steady state intermediate demand,
    dd0_ss(r,g)		Steady state local demand,
    nd0_ss(r,g)		Steady state national demand,
    xd0_ss(r,g)		Steady state local supply,
    xn0_ss(r,g)		Steady state national supply,
    g0_ss(r,g)		Steady state government demand,
    a0_ss(r,g)		Steady state armington supply,
    s0_ss(r,g)		Steady state total supply,
    i0_ss(r,g)		Steady state investment,
    ty0_ss(r,s)         Steady state production tax,
    ta0_ss(r,g)         Steady state commodity tax;

$ifthen.dynamic %invest%=="dynamic"

$gdxin "%gdxdir%dynamic_parameters_%year%.gdx"
$loaddc ys0_ss=ys0 id0_ss=id0 dd0_ss=dd0 nd0_ss=nd0 xd0_ss=xd0 xn0_ss=xn0 
$loaddc a0_ss=a0 s0_ss=s0 i0_ss=i0 g0_ss=g0 ty0_ss=ty0 ta0_ss=ta0
	ys0(r,s,g) = ys0_ss(r,s,g);
	id0(r,g,s) = id0_ss(r,g,s);
	dd0(r,g) = dd0_ss(r,g);
	nd0(r,g) = nd0_ss(r,g);
	xd0(r,g) = xd0_ss(r,g);
	xn0(r,g) = xn0_ss(r,g);
	g0(r,g) = g0_ss(r,g);
	a0(r,g) = a0_ss(r,g);
	s0(r,g) = s0_ss(r,g);
	i0(r,g) = i0_ss(r,g);
	ty0(r,s) = ty0_ss(r,s);
	ta0(r,g) = ta0_ss(r,g);
$endif.dynamic


* define additional aggregate parameters
parameter
    totsav0	Total domestic savings,
    fsav0	Total foreign savings,
    taxrevL(r,sk)  Tax revenue from labor income tax,
    taxrevK     Tax revenue from capital income tax,
    govdef0	Government deficit;

totsav0 = sum((r,h,sk), sav0_d(r,h,sk));

fsav0 = sum((r,g), i0(r,g)) - totsav0;

taxrevL(rr,sk) = sum((r,h),tl0_d(r,h,sk)*le0_d(r,rr,h,sk));

display taxrevL, tl0_d;


taxrevK = sum((r,s),tk0(r)*(kd0(r,s)+pd0(r,s)));

display kd0, pd0;


govdef0 = sum((r,g), g0(r,g)) + sum((r,h,sk), trn0_d(r,h,sk))
	- sum((r,sk), taxrevL(r,sk)) 
	- taxrevK 
	- sum((r,s,g)$y_(r,s), ty0(r,s) * ys0(r,s,g)) 
	- sum((r,g)$a_(r,g),   ta0(r,g)*a0(r,g) + tm0(r,g)*m0(r,g));

* define capital transformation elasticity and policy tax rates
parameter
    etaK	Capital transformation elasticity /4/,
    ta(r,g)	Consumption taxes,
    ty(r,s)	Production taxes
    tm(r,g)	Import taxes,
    tk(r,s)     Capital taxes,
    tl(r,h,sk)	Labor taxes;

ta(r,g) = ta0(r,g);
ty(r,s) = ty0(r,s);
tm(r,g) = tm0(r,g);
tk(r,s) = tk0(r);
tl(r,h,sk) = tl0_d(r,h,sk);

* -----------------------------------------------------------------------------
*    Define new production parameters and labor by skill type
* -----------------------------------------------------------------------------

*read in shares of labor demanded by skill type


PARAMETER
sk_sh_ld(r,s,sk);

TABLE  skill_shr_ld0(r,s,sk,col)
$ondelim
$include ld0_shr2.csv
$offdelim
;


sk_sh_ld(r,s,sk)=skill_shr_ld0(r,s,sk,"skill_shr");


PARAMETER

ld0_d(r,s,sk)     labor demand by skill type
;

*multiply benchmark labor demand (by region, sector) by share to get demadn each sector has for each skill type

ld0_d(r,s,sk)=ld0(r,s)*sk_sh_ld(r,s,sk);


* -----------------------------------------------------------------------------
* static calibration model
* -----------------------------------------------------------------------------

$ontext 
$model:mgemodel

$sectors:
        Y(r,s)$y_(r,s)          !       Production
        X(r,g)$x_(r,g)          !       Disposition
        A(r,g)$a_(r,g)          !       Absorption
	KS			!	Aggregate capital stock
	P(r)                    !       Regional property endowment
        C(r,h,sk)		!       Household consumption
        MS(r,m)                 !       Margin supply

$commodities:
        PA(r,g)$a0(r,g)         !       Regional market (input)
        PY(r,g)$s0(r,g)         !       Regional market (output)
        PD(r,g)$xd0(r,g)        !       Local market price
        RK(r,s)$kd0(r,s)	!       Sectoral rental rate
	RKS			!	Capital stock
        PM(r,m)                 !       Margin price
        PC(r,h,sk)	        !       Consumer price index
        PN(g)                   !       National market price for goods
        PL(r,sk)                !       Regional wage rate
        PP(r)                   !       Price of land
        PK			!     	Aggregate return to capital
        PFX                     !       Foreign exchange

$consumer:
        RA(r,h,sk)		!	Representative agent
	NYSE			!	Aggregate capital owner
	INVEST			!	Aggregate investor
	GOVT			!	Aggregate government
        RLAND(r)                !       Regional land owner
$auxiliary:
	SAVRATE			!	Domestic savings rate
	TAXRATE			!	Budget balance rationing variable
	SSK			!	Steady-state capital stock


$prod:Y(r,s)$y_(r,s)  s:esubland(r)   nf:0 mat(nf):0 va(nf):esubtop lsk(va):esubl(s)

        o:PY(r,g)       q:ys0(r,s,g)       a:GOVT t:ty(r,s)       p:(1-ty0(r,s))
        i:PA(r,g)       q:id0(r,g,s)       mat:
        i:PL(r,sk)      q:ld0_d(r,s,sk)    lsk:
        i:RK(r,s)       q:kd0(r,s)         va:      a:GOVT t:tk(r,s)       p:(1+tk0(r))
	i:PP(r)$house(s)         q:pd0(r,s)$house(s)                    a:GOVT t:tk(r,s)$house(s)         p:(1+tk0(r))$house(s)          

$report:
	v:KD(r,s)$kd0(r,s)	i:RK(r,s)	prod:Y(r,s)

$prod:X(r,g)$x_(r,g)  t:esubnat
        o:PFX           q:(x0(r,g)-rx0(r,g))
        o:PN(g)         q:xn0(r,g)
        o:PD(r,g)       q:xd0(r,g)
        i:PY(r,g)       q:s0(r,g)

$prod:A(r,g)$a_(r,g)  s:0 dm:nu_m  d(dm):nu
        o:PA(r,g)       q:a0(r,g)               a:GOVT t:ta(r,g)       p:(1-ta0(r,g))
        o:PFX           q:rx0(r,g)
        i:PN(g)         q:nd0(r,g)      d:
        i:PD(r,g)       q:dd0(r,g)      d:
        i:PFX           q:m0(r,g)       dm:     a:GOVT t:tm(r,g)       p:(1+tm0(r,g))
        i:PM(r,m)       q:md0(r,m,g)

$report:
	v:MD(r,g)$m0(r,g)	i:PFX	prod:A(r,g)

$prod:MS(r,m)
        o:PM(r,m)       q:(sum(gm, md0(r,m,gm)))
        i:PN(gm)        q:nm0(r,gm,m)
        i:PD(r,gm)      q:dm0(r,gm,m)

$prod:C(r,h,sk)	  s:esubc
        o:PC(r,h,sk)       q:c0_h_d(r,h,sk)
        i:PA(r,g)       q:cd0_h_d(r,g,h,sk)

$prod:KS	t:etaK
	o:RK(r,s)	q:kd0(r,s)
	i:RKS		q:(sum((r,s),kd0(r,s)))


$demand:RA(r,h,sk)
        d:PC(r,h,sk)    q:c0_h_d(r,h,sk)
        e:PL(q,sk)      q:le0_d(r,q,h,sk)
        e:PL(q,sk)      q:(-tl0_d(r,h,sk)*le0_d(r,q,h,sk))	r:TAXRATE
	e:PFX		q:(sum(trn, hhtrn0_d(r,h,sk,trn)))
        e:PK		q:ke0_d(r,h,sk)
        e:PP(r)         q:pe0_d(r,h,sk)
	e:PFX		q:(-sav0_d(r,h,sk))	r:SAVRATE

$report:
	v:W(r,h,sk)	w:RA(r,h,sk)
       
	
$demand:NYSE
	d:PK
	e:PY(r,g)	q:yh0(r,g)
	e:RKS		q:(sum((r,s),kd0(r,s)))	r:SSK

$demand:RLAND(r)
	d:PP(r)
        e:PP(r)         q:(sum(s, pd0(r,s)))    r:SSK

$prod:P(r)        t:etaK
        o:PP(r)         q:(sum(s,pd0(r,s)))  
        i:PP(r)         q:(sum(s,pd0(r,s)))


$demand:INVEST  s:0
	d:PA(r,g)	q:i0(r,g)
	e:PFX		q:totsav0	r:SAVRATE
	e:PFX		q:fsav0

$demand:GOVT
	d:PA(r,g)	q:g0(r,g)
	e:PFX           q:(-sum((r,h,sk), trn0_d(r,h,sk)))
	e:PFX           q:govdef0
 	e:PL(r,sk)      q:taxrevL(r,sk)	r:TAXRATE

$constraint:SSK
	sum((r,g),i0(r,g)*PA(r,g)) =e= sum((r,g),i0(r,g))*RKS;

$constraint:SAVRATE
	INVEST =e= sum((r,g), PA(r,g)*i0(r,g))*SSK;

$constraint:TAXRATE
	GOVT =e= sum((r,g),PA(r,g)*g0(r,g));
	
$offtext
$sysinclude mpsgeset mgemodel 

TAXRATE.L = 1;
SAVRATE.L = 1;
SSK.FX = 1;
mgemodel.savepoint = 1;
mgemodel.workspace = 1000;
mgemodel.iterlim=0;
$include MGEMODEL.GEN

solve mgemodel using mcp;


*get benchmark rpts

PARAMETERS
cons0_rpt
ys0_rpt
le0_d_rpt
ld0_d_rpt(r,s,sk)
cd0_h_d_rpt(r,g,h,sk)
c0_h_d_rpt(r,h,sk)
hhtrn0_d_rpt(r,h,sk,trn)
ke0_d_rpt(r,h,sk)
sav0_d_rpt(r,h,sk)
id0_rpt(r,g,s)
le0_d_rpt00(r,q,h,sk)
tl0_d_rpt(r,h,sk)
kd0_rpt(r,s)
;

kd0_rpt(r,s)=kd0(r,s);
tl0_d_rpt(r,h,sk)=tl0_d(r,h,sk);
le0_d_rpt00(r,q,h,sk)=le0_d(r,q,h,sk);
le0_d_rpt(r,h,sk)=sum((q),le0_d(r,q,h,sk));
cons0_rpt(r,h,sk)=c0_h_d(r,h,sk);
ys0_rpt(r,s,g)=ys0(r,s,g);
ld0_d_rpt(r,s,sk)=ld0_d(r,s,sk);
cd0_h_d_rpt(r,g,h,sk)=cd0_h_d(r,g,h,sk);
c0_h_d_rpt(r,h,sk)=c0_h_d(r,h,sk);
hhtrn0_d_rpt(r,h,sk,trn)=hhtrn0_d(r,h,sk,trn);
ke0_d_rpt(r,h,sk)=ke0_d(r,h,sk);
sav0_d_rpt(r,h,sk)=sav0_d(r,h,sk);
id0_rpt(r,g,s)=id0(r,g,s);

execute_unload "staticmodel_d2_csubs_bmk.gdx" kd0_rpt ,tl0_d_rpt,c0_h_d_rpt  ,le0_d_rpt00, le0_d_rpt,cons0_rpt, ys0_rpt, ld0_d_rpt,cd0_h_d_rpt,c0_h_d_rpt,hhtrn0_d_rpt,ke0_d_rpt,sav0_d_rpt,id0_rpt;



*** allow more time per solve

mgemodel.iterlim=1000;
option resLim=6000;

***START OF COUNTERFACTUALS***

***FIRST SHOCK***


TABLE  pct_le0_ch0(r,q,h,sk,col)
$ondelim
$include le0_shock0_v2_test2_adj.csv
$offdelim
;

PARAMETERS
labor_pct_ch0(r,q,h,sk)
tot_wrkers_b(r,h,sk);

**get total workers living in region BEFORE the shock

tot_wrkers_b(r,h,sk)=sum(q,le0_d(r,q,h,sk));

***change allocation of skilled and unskilled in affected regions

labor_pct_ch0(r,q,h,sk)=pct_le0_ch0(r,q,h,sk,"skill_shr");

le0_d(r,q,h,sk)=le0_d(r,q,h,sk)+(le0_d(r,q,h,sk)*labor_pct_ch0(r,q,h,sk));

** now sum recalculated workers to get new population of workers who live in a region

PARAMETERS
tot_wrkers_a(r,h,sk)
pct_change_tot0(r,h,sk)
;
**this is the new population that LIVES in region r

tot_wrkers_a(r,h,sk)=sum(q,le0_d(r,q,h,sk));

**get percent change from old population that LIVES in region r

pct_change_tot0(r,h,sk)=(tot_wrkers_a(r,h,sk)-tot_wrkers_b(r,h,sk))/tot_wrkers_b(r,h,sk);

display pct_change_tot0;

***ADJUST OTHER CONSUMER PARAMETERS***
***(THESE PARAMETERS ARE INDEXED BY R ONLY, NOT R AND Q COMBINED)***

***for other household variables skill PRPOPORTION has been adjusted but not LEVEL
***so need to adjust aggregate household values by percent change in total population living in r

ke0_d(r,h,sk)=ke0_d(r,h,sk) + (ke0_d(r,h,sk)*(pct_change_tot0(r,h,sk)));

sav0_d(r,h,sk)=sav0_d(r,h,sk) + (sav0_d(r,h,sk)*(pct_change_tot0(r,h,sk)));

trn0_d(r,h,sk)=trn0_d(r,h,sk) + (trn0_d(r,h,sk)*(pct_change_tot0(r,h,sk)));

hhtrn0_d(r,h,sk,trn)=hhtrn0_d(r,h,sk,trn) + (hhtrn0_d(r,h,sk,trn)*(pct_change_tot0(r,h,sk)));

*cd0_h_d(r,g,h,sk)=cd0_h_d(r,g,h,sk) + (cd0_h_d(r,g,h,sk)*(pct_change_tot0(r,h,sk)));

*c0_h_d(r,h,sk)=c0_h_d(r,h,sk) + (c0_h_d(r,h,sk)*(pct_change_tot0(r,h,sk)));


display pct_change_tot0, le0_d;

$include MGEMODEL.GEN
solve mgemodel using mcp;


PARAMETERS
c_rpt0
y_rpt0
pl_rpt0
w_rpt0
pc_rpt0
phou_rpt0
le0_d_rpt0
ra_rpt0
pfx_rpt0
pk_rpt0
pn_rpt0(g)
pm_rpt0(r,m)
pa_rpt0(r,g)
py_rpt0(r,g)
pd_rpt0(r,g)
rk_rpt0(r,s)
a_rpt0(r,g)
TAXRATE_rpt
SAVRATE_rpt

;

TAXRATE_rpt=TAXRATE.l;

SAVRATE_rpt=SAVRATE.l;

le0_d_rpt0(r,h,sk)=sum((q),le0_d(r,q,h,sk));

y_rpt0(r,s)=Y.l(r,s);

c_rpt0(r,h,sk)=C.l(r,h,sk);

pl_rpt0(r,sk)=PL.l(r,sk);

pc_rpt0(r,h,sk)=PC.l(r,h,sk);

w_rpt0(r,h,sk)=W.l(r,h,sk);

phou_rpt0(r)=PY.l(r,"hou");

ra_rpt0(r,h,sk)=RA.l(r,h,sk);

pfx_rpt0=PFX.l;

pk_rpt0=PK.l;

pn_rpt0(g)=PN.l(g);

pm_rpt0(r,m)=PM.l(r,m);

pa_rpt0(r,g)=PA.l(r,g);

py_rpt0(r,g)=PY.l(r,g);

pd_rpt0(r,g)=PD.l(r,g);

rk_rpt0(r,s)=RK.l(r,s);

a_rpt0(r,g)=A.l(r,g);


execute_unload "staticmodel_d2_csubs_it0.gdx" a_rpt0, SAVRATE_rpt,TAXRATE_rpt,  ra_rpt0, y_rpt0,c_rpt0,pl_rpt0,pc_rpt0,w_rpt0,phou_rpt0, le0_d_rpt0, pfx_rpt0,pk_rpt0,pn_rpt0, pm_rpt0, pa_rpt0,py_rpt0, pd_rpt0,rk_rpt0;

$exit;

***first iteration

TABLE  pct_le0_ch1(r,q,h,sk,col)
$ondelim
$include le0_shock1_v2_test2_adj.csv
$offdelim
;

PARAMETERS
labor_pct_ch1(r,q,h,sk)
tot_wrkers_b1(r,h,sk);

tot_wrkers_b1(r,h,sk)=sum(q,le0_d(r,q,h,sk));
***change allocation of skilled and unskilled in affected regions

labor_pct_ch1(r,q,h,sk)=pct_le0_ch1(r,q,h,sk,"skill_shr");

le0_d(r,q,h,sk)=le0_d(r,q,h,sk)+(le0_d(r,q,h,sk)*labor_pct_ch1(r,q,h,sk));

** now sum recalculated workers to get new population of workers who live in a region

PARAMETERS
tot_wrkers_a1(r,h,sk)
pct_change_tot1(r,h,sk)
;

**this is the new population that LIVES in region r

tot_wrkers_a1(r,h,sk)=sum(q,le0_d(r,q,h,sk));

**get percent change from old population that LIVES in region r

pct_change_tot1(r,h,sk)=(tot_wrkers_a1(r,h,sk)-tot_wrkers_b1(r,h,sk))/tot_wrkers_b1(r,h,sk);

display pct_change_tot1, le0_d;


***for other household variables skill PRPOPORTION has been adjusted but not LEVEL
***so need to adjust aggregate household values by percent change in total population

ke0_d(r,h,sk)=ke0_d(r,h,sk) + (ke0_d(r,h,sk)*(pct_change_tot1(r,h,sk)));

sav0_d(r,h,sk)=sav0_d(r,h,sk) + (sav0_d(r,h,sk)*(pct_change_tot1(r,h,sk)));

trn0_d(r,h,sk)=trn0_d(r,h,sk) + (trn0_d(r,h,sk)*(pct_change_tot1(r,h,sk)));

hhtrn0_d(r,h,sk,trn)=hhtrn0_d(r,h,sk,trn) + (hhtrn0_d(r,h,sk,trn)*(pct_change_tot1(r,h,sk)));

cd0_h_d(r,g,h,sk)=cd0_h_d(r,g,h,sk) + (cd0_h_d(r,g,h,sk)*(pct_change_tot1(r,h,sk)));

c0_h_d(r,h,sk)=c0_h_d(r,h,sk) + (c0_h_d(r,h,sk)*(pct_change_tot1(r,h,sk)));


display pct_change_tot1,tot_wrkers_a1, tot_wrkers_b ;

$include MGEMODEL.GEN
solve mgemodel using mcp;

PARAMETERS
c_rpt1
y_rpt1
pl_rpt1
w_rpt1
pc_rpt1
phou_rpt1
le0_d_rpt1
ra_rpt1
pfx_rpt1
pk_rpt1
pn_rpt1(g)
pm_rpt1(r,m)
pa_rpt1(r,g)
py_rpt1(r,g)
pd_rpt1(r,g)
rk_rpt1(r,s)
TAXRATE_rpt1
SAVRATE_rpt1

;

TAXRATE_rpt1=TAXRATE.l;

SAVRATE_rpt1=SAVRATE.l;

le0_d_rpt1(r,h,sk)=sum((q),le0_d(r,q,h,sk));

y_rpt1(r,s)=Y.l(r,s);

c_rpt1(r,h,sk)=C.l(r,h,sk);

pl_rpt1(r,sk)=PL.l(r,sk);

pc_rpt1(r,h,sk)=PC.l(r,h,sk);

w_rpt1(r,h,sk)=W.l(r,h,sk);

phou_rpt1(r)=PY.l(r,"hou");

ra_rpt1(r,h,sk)=RA.l(r,h,sk);

pfx_rpt1=PFX.l;

pk_rpt1=PK.l;

pn_rpt1(g)=PN.l(g);

pm_rpt1(r,m)=PM.l(r,m);

pa_rpt1(r,g)=PA.l(r,g);

py_rpt1(r,g)=PY.l(r,g);

pd_rpt1(r,g)=PD.l(r,g);

rk_rpt1(r,s)=RK.l(r,s);



execute_unload "staticmodel_v8t2_it1.gdx" SAVRATE_rpt1,TAXRATE_rpt1,  ra_rpt1, y_rpt1,c_rpt1,pl_rpt1,pc_rpt1,w_rpt1,phou_rpt1, le0_d_rpt1, pfx_rpt1,pk_rpt1,pn_rpt1, pm_rpt1, pa_rpt1,py_rpt1, pd_rpt1,rk_rpt1;
$exit;

