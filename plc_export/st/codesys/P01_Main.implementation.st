(* --- Rung 1, step 0 | MODE --- *)
IF SM400 THEN
    M200 := TRUE;
ELSE
    M200 := FALSE;
END_IF;

(* --- Rung 2, step 6 --- *)
IF X0_PLS THEN
    M201 := TRUE;
ELSE
    M201 := FALSE;
END_IF;

(* --- Rung 3, step 8 --- *)
IF (((M201) AND (NOT (M202))) OR ((NOT (M201)) AND (M202))) AND (M200) AND (NOT (M50)) THEN
    M202 := TRUE;
ELSE
    M202 := FALSE;
END_IF;

(* --- Rung 4, step 16 --- *)
IF (M202) AND (NOT (X1)) THEN
    M210 := TRUE;
ELSE
    M210 := FALSE;
END_IF;

(* --- Rung 5, step 19 --- *)
IF (M202) AND (X1) THEN
    M211 := TRUE;
ELSE
    M211 := FALSE;
END_IF;

(* --- Rung 6, step 22 --- *)
IF ((M500) OR (M215)) AND (M211) AND (NOT (M50)) THEN
    M215 := TRUE;
ELSE
    M215 := FALSE;
END_IF;

(* --- Rung 7, step 27 --- *)
IF ((M500) OR (M216)) AND (M211) AND (NOT (M50)) THEN
    M216 := TRUE;
ELSE
    M216 := FALSE;
END_IF;

(* --- Rung 8, step 32 --- *)
IF (M202) AND (NOT (M2127)) THEN
    M2021 := TRUE;
ELSE
    M2021 := FALSE;
END_IF;

(* --- Rung 9, step 35 | Error Reset --- *)
IF (X8) OR (M501) THEN
    M212 := TRUE;
ELSE
    M212 := FALSE;
END_IF;

(* --- Rung 10, step 46 --- *)
IF M212 THEN
    Y77 := TRUE;
ELSE
    Y77 := FALSE;
END_IF;

(* --- Rung 11, step 48 --- *)
IF (SM400) AND (M502) THEN
    M220 := TRUE;
END_IF;
IF (SM400) AND (NOT (M57)) THEN
    M220 := FALSE;
END_IF;

(* --- Rung 12, step 55 | Work --- *)
IF (X1100_PLS) OR ((M210) AND (M170) AND (NOT (M171))) OR (M710) THEN
    M1321 := TRUE;
END_IF;

(* --- Rung 13, step 66 --- *)
IF (M210) AND (M171) AND (X111F) THEN
    M1321 := FALSE;
END_IF;

(* --- Rung 14, step 84 | - --- *)
IF (X1018_PLS) OR ((M210) AND (M174) AND (NOT (M175))) OR (M712) THEN
    M60 := TRUE;
END_IF;

(* --- Rung 15, step 80 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M60 := FALSE;
END_IF;

(* --- Rung 16, step 84 | - --- *)
IF (M2005) AND (M180) AND (M2005) AND (M2000) AND (M2002) THEN
    M1422 := TRUE;
END_IF;

(* --- Rung 17, step 93 --- *)
IF (M1522) OR (M2005) THEN
    M1422 := FALSE;
END_IF;

(* --- Rung 18, step 96 --- *)
IF (NOT (M60)) AND (NOT (M5000)) AND (NOT (M5001)) AND (NOT (M6000)) AND (NOT (M6001)) AND (NOT (M6100)) AND (T70) THEN
    M7750 := TRUE;
ELSE
    M7750 := FALSE;
END_IF;

(* --- Rung 19, step 104 --- *)
IF (NOT (M1321)) AND (NOT (M7000)) AND (NOT (M7001)) AND (T50) THEN
    M7751 := TRUE;
ELSE
    M7751 := FALSE;
END_IF;
