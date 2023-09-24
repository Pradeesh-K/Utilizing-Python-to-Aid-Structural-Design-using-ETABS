import sympy as sp
import scipy as sc
from scipy.interpolate import interp1d
import math
import pandas as pd


def table_b(fy, es=200000):                             # provides the limiting neutral axis depth as per Table B, SP-16
    return 0.0035 / (0.0055 + 0.87 * (fy / es))

def table_c(fy):                                        # returns data for Table D and Table E, as per  SP-16
    return 0.36 * table_b(fy) * (1 - 0.416 * table_b(fy)), 100 * (0.36 / 0.87) * table_b(fy)

def table_d_e(fy, fck):                                 # returns the limiting Moment and percentage of steel for a given
    mu_lim_by_fck_bd2, pt_lim_fy_by_fck = table_c(fy)    #Fy and Fck, as per Table D, E  SP-16
    return mu_lim_by_fck_bd2 * fck, pt_lim_fy_by_fck * fck / fy


def table_f(fy, d_dash_d):                              # returns the stress in compression reinforcement as per Table F, SP- 16
    x = [0.05, 0.1, 0.15, 0.2]
    y = [[355, 353, 342, 329], [424, 412, 395, 370]]
    if fy == 415:
        pred = interp1d(x, y[0], kind="linear")
    elif fy == 500:
        pred = interp1d(x, y[1], kind="linear")
    return pred(d_dash_d)


def shear_max(fck):                                     # returns the limiting shear stress for a given grade of concrete
    x = [15, 20, 25, 30, 35, 40]                        # as per IS - 456
    y = [2.5, 2.8, 3.1, 3.5, 3.7, 4.0]
    pred = interp1d(x, y, kind="linear")
    if fck > 40:
        return pred(40)
    else:
        return pred(fck)


def beam_design(torsion, shear, moment, bar=20, bar_shear=10, fy=415, fck=20): # function to design an RCC beam
    status = 0
    cover = 25                  # assumed clear cover for concrete
    b = 230                     # assumed width of beam
    d = b                                                               # for flexure failure we take 2 * b, the default
    eff_d = d - cover - (bar / 2)
    rd = 0                      # to identify redesigning of singly reinforced beams
    double = 0                  # to identify doubly reinforced beams
    min_bar = 12                # this is the minimum bar diameter for singly reinforced beam.
    print(f'From the user input: fck = {fck} N/mm2, fy = {fy} N/mm2 and \n'
          f'moment = {moment} KNm, shear = {shear} KN, torsion = {torsion} KN.m')
    print(f'The assumed initial dimensions of the beam is {b} x {d} mm')

    # SHEAR CHECK
    print('\n\n#### SHEAR CHECK ###')
    inp_shear = abs(shear)  # pure shear
    shear = abs(shear + 1.6 * (torsion * 1000 / b))  # combined shear due to torsion and shear
    print(f'the total shear including torsion is {round(shear, 3)} KN')
    nominal_shear_spacing = 0.87 * fy * (2 * 0.25 * 3.14 * bar_shear ** 2) / (0.4 * b)  # nominal shear reinforcement
    max_shear_stress = shear_max(fck)  # in N/mm2      # maximum permissible shear stress
    shear_stress = shear * 1000 / (b * eff_d)  # shear stress on beam
    print(f'The shear_stress is {round(shear_stress, 3)} N/mm2')
    print(f'The maximum permissible shear stress as per IS code is {max_shear_stress} N/mm2')
    if shear_stress > max_shear_stress:
        print(
            f'The shear stress on beam is {round(shear_stress, 3)} N/mm2 while the maximum permissible shear stress '
            f'is {max_shear_stress} N/mm2' Redesigning ...')
        while shear_stress > max_shear_stress:
            b = b + 25
            d = b                                       # for flexural failure we take 2 * b, the default
            eff_d = d - cover - (bar / 2)
            shear_stress = shear * 1000 / (b * eff_d)
        print(f'The revised dimension of beam to satisfy shear is {b} x {d} mm')


    # DESIGN FOR BENDING RESISTANCE
    print('\n\n#### MOMENT CALCULATION ###')
    moment = abs(moment + (torsion * (1 + 2) / 1.7))
    print(f'Moment including Torsion = {round(moment, 3)} KNm')
    while status == 0:
        d = b                                   # for flexural failure we take 2 * b, the default
        eff_d = d - cover - (bar / 2)
        lim_m, lim_pt = table_d_e(fy, fck)
        if moment > lim_m * (1 / 1000000) * b * eff_d ** 2:
            print(f'The section cannot be designed as a singly reinforced section'
                  f'as the the limiting moment is {round((lim_m * (1 / 1000000) * b * eff_d ** 2),3)} while given moment is '
                  f'{round(moment, 3)}')
            status = 1
            double = 1
        else:
            p = sp.symbols("p")
            # eqn = sp.solveset((1.005 * (fy ** 2 / fck) * 0.87 * 0.01 ** 2) * p - (0.87 * fy * 0.01) * p + (moment * 1000 * 1000/ (b * eff_d * eff_d)) , p)
            # THE ABOVE EQUATION WAS WRONG SO IT GAVE ERRANEOUS RESULTS
            eqn = sp.solveset((1.005 * (fy / fck) * 0.01 * 0.01 * p ** 2 - 0.01 * p + (moment * 1000 * 1000 / (0.87 * fy * b * eff_d ** 2))) , p)
            perc = eqn.args[0]
            print(f' eff_d = {eff_d} mm')
            if perc > lim_pt:
                print(f'Reinforcement {round(perc, 3)} % is greater than allowed {round(lim_pt, 3)} %. Redesigning')
                rd = 1
                b = b + 25

            else:
                print(f'The percentage of steel is {round(perc,3)} % while the limiting reinforcement is {round(lim_pt,3)} %')
                print(f'\n thus, the required area of steel is {round(perc * b * eff_d * 0.01,3)} mm2')
                asc = 0
                total_tension_ast = perc * 0.01 * b * eff_d
                if eff_d > 750:
                    print(f'As the depth of beam is more than 750 mm provide side face reinforcement of {round(0.05 * 0.01 * b * eff_d, 3)} mm2'
                          f' at a spacing of {round(min(0.5 * eff_d, 300, b), 3)}')
                status = 1
    if rd == 1:
        print(f'The revised dimension of beam is {b} x {d} mm')
        eff_d = d - cover - (bar / 2)

    # CALCULATION FOR DOUBLY REINFORCED BEAMS IN CASE THE APPLIED MOMENT EXCEEDS THE LIMITING MOMENT
    if double == 1:
        perc = 9
        while perc > 8:
            mu2 = moment - (lim_m * (1 / 1000000) * b * eff_d ** 2)
            d_dash = cover + (bar/2)
            d_dash_by_d = d_dash / eff_d
            # comp_st = 0.0035 * (1 - d_dash / (eff_d * table_b(fy)))
            # print(f' comp_st {comp_st}')
            ast2 = mu2 * 1000 * 1000 / (0.87 * fy * (eff_d - d_dash))
            total_tension_ast = lim_pt * b * eff_d * 0.01 + ast2
            asc = 0
            if d_dash_by_d <= 0.2:
                fcc = 0.446 * fck
                fsc = table_f(fy, d_dash_by_d)
                asc = ast2 * 0.87 * fy / (fsc - fcc)
            perc = (total_tension_ast + asc) * 100 / (b * eff_d)
            if perc > 8:
                b = b + 25
                d = b                                           # for flexural failure we take 2 * b, the default
                eff_d = d - cover - (bar / 2)
        print(f' additional tension steel = {round(ast2,3)} mm2, additional compression steel = {round(asc,3)} mm2,'
              f' total tension steel = {round(total_tension_ast,3)} mm2')
        print(f'The required dimension of beam is {b} x {d} mm with total percentage of reinforcement {round(perc, 3)} %')
        if eff_d > 750:
            print(f'As the depth of beam is more than 750 mm provide side face reinforcement of {round(0.05 * 0.01 * b * eff_d, 3)} mm2'
                f' at a spacing of {round(min(0.5 * eff_d, 300, b), 3)}')


    # SHEAR DESIGN
    print('\n\n#### SHEAR CALCULATION ###')
    d = b                                               # for flexural failure we take 2 * b, the default
    eff_d = d - cover - (bar / 2)
    if double == 1:
        perc = (total_tension_ast + asc) * 100 / (b * eff_d)
    if perc <= 0.15:
        p_sh = 0.15
    elif perc >= 3:
        p_sh = 3.0
    else:
        p_sh = perc
    beta = 0.8 * fck / (6.89 * p_sh)
    design_shear = (0.85 * math.sqrt(0.8 * fck) * (math.sqrt(1 + 5 * beta) - 1)) / (6 * beta)
    if fck == 15 and p_sh >= 1.75:
        design_shear = 0.71
    if fck == 20 and p_sh >= 2.5:
        design_shear = 0.82

    if design_shear > shear_stress:
        shear_spacing = nominal_shear_spacing
        print(f'Shear stress on beam is = {round(shear_stress, 3)} N/mm2  while design_shear capacity = {round(design_shear, 3)} N/mm2 ')
        print(f' provide nominal shear reinforcement @ {shear_spacing} mm c/c ')
    else:
        print(f'Shear stress = {round(shear_stress, 3)} N/mm2 while design_shear = {round(design_shear, 3)} N/mm2 '
              f'\n, thus additional shear reinforcement is provided')
        b1 = b - 2 * cover - bar_shear
        if double == 1:
            d1 = d - 2 * cover - bar
        else:
            d1 = d - 2 * cover - 0.5 * bar - 0.5 * min_bar
        shear_spacing1 = 0.87 * fy * (2 * 0.25 * 3.14 * bar_shear ** 2) / (
                (abs(torsion) * 1000000 / (b1 * d1)) + (inp_shear * 1000 / (2.5 * d1)))
        print(f' shear_spacing1 {round(shear_spacing1, 3)} mm')
        shear_spacing2 = 0.87 * fy * (2 * 0.25 * 3.14 * bar_shear ** 2) / ((shear_stress - design_shear) * b)
        print(f' shear_spacing2 {round(shear_spacing2, 3)} mm')
        shear_spacing = min(shear_spacing1, shear_spacing2)
        print(f'The preferred {bar_shear} mm bars should be provided at a spacing of \n'
              f'{min(round(shear_spacing, 3), 300, eff_d)} mm c/c to satisfy the shear criterion')

    return b, d, round(total_tension_ast, 3), asc, bar_shear, round(shear_spacing, 3)


beam_id = ['B10', 'B11', 'B14', 'B34', 'B35', 'B38']            # LIST OF BEAM IDS THAT FAILED, TAKEN FROM ETABS

# CODE TO EXTRACT THE MAXIMUM SHEAR AND MOMENTS, POSITIVE AND NEGATIVE
df = pd.read_excel('Etabs failed beam forces.xlsx', header=0)
max_shear = []
max_moment_pos = []
max_moment_neg = []
j = 0
for i in range(len(beam_id)):
    mp = 0
    mn = 0
    s = 0
    max_s = 0
    max_mp = 0
    max_mn = 0
    while (df.iloc[j][1] == beam_id[i]):                                # Maximum shear identification
        if abs(df.iloc[j][6]) + 1.6 * abs(df.iloc[j][8]) * (1000 / 400) > max_s:
            s = j
            max_s = abs(df.iloc[j][6]) + 1.6 * abs(df.iloc[j][8]) * (1000 / 400)
        if df.iloc[j][10] + (df.iloc[j][8] * (2 / 1.7)) < 0:            # maximum negative moment identification
            if abs(df.iloc[j][10] + (df.iloc[j][8] * (2 / 1.7))) > max_mn:
                mn = j
                max_mn = abs(df.iloc[j][10] + (df.iloc[j][8] * (2 / 1.7)))
        else:                                                            # maximum positive moment identification
            if abs(df.iloc[j][10] + (df.iloc[j][8] * (2 / 1.7))) > max_mp:
                mp = j
                max_mp = abs(df.iloc[j][10] + (df.iloc[j][8] * (2 / 1.7)))
        j += 1
    max_shear.append(df.iloc[s][6:12])
    max_moment_pos.append(df.iloc[mp][6:12])
    max_moment_neg.append(df.iloc[mn][6:12])

# Obtaining the required dimensions for the failed beams using the beam_design function defined above
beam_calc = []
for i in range(len(beam_id)):
    beam_calc.append(beam_design(abs(max_shear[i][2]), abs(max_shear[i][0]), max_shear[i][4], 20, 16, 500, 50))

# Saving the results in an excel sheet
result_df = pd.DataFrame(beam_calc, columns=['B (mm)', 'D (mm)', 'Tension rf (mm2)', 'Comp rf (mm2)', 'Stirrup dia (mm)', 'Stirrup spacing (mm)'], index=beam_id)
result_df.to_excel('ETABS calculation results for failed beams.xlsx')

