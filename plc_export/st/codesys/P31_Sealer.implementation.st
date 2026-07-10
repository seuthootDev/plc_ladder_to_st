(* --- Rung 1, step 0 --- *)
IF (SM400) AND (X1A) THEN
    M2500 := TRUE;
ELSE
    M2500 := FALSE;
END_IF;
IF (SM400) AND (X1B) THEN
    M2501 := TRUE;
ELSE
    M2501 := FALSE;
END_IF;

(* --- Rung 2, step 7 --- *)
IF (X1A) AND (NOT (X1B)) THEN
    M2520 := TRUE;
ELSE
    M2520 := FALSE;
END_IF;

(* --- Rung 3, step 10 --- *)
IF M202 THEN
    M2521 := TRUE;
ELSE
    M2521 := FALSE;
END_IF;

(* --- Rung 4, step 12 --- *)
IF (M2521) AND (((M211) AND ((X1039) OR (M999)) AND (X1004)) OR ((M210) AND ((M522) OR (X1004)) AND (NOT (M523)))) AND (NOT (M521)) AND (NOT (X1B)) AND (NOT (Y49)) THEN
    Y48 := TRUE;
ELSE
    Y48 := FALSE;
END_IF;

(* --- Rung 5, step 29 --- *)
IF (M2521) AND (((M211) AND (((X1B) AND (NOT (X1004))) OR (Y49))) OR ((M210) AND ((M523) OR (M2527)) AND (NOT (M522)))) AND ((NOT (M521)) OR (M999)) AND (NOT (X1A)) AND (NOT (Y48)) THEN
    Y49 := TRUE;
ELSE
    Y49 := FALSE;
END_IF;

(* --- Rung 6, step 48 --- *)
IF (M2521) AND (M210) AND ((M526) OR (M2527)) AND (NOT (X1A)) THEN
    M2527 := TRUE;
ELSE
    M2527 := FALSE;
END_IF;

(* --- Rung 7, step 55 --- *)
IF NOT ((NOT (Y48)) AND (NOT (Y49))) THEN
    Y2B := TRUE;
ELSE
    Y2B := FALSE;
END_IF;

(* --- Rung 8, step 59 --- *)
IF Y48 THEN
    Y4C := TRUE;
ELSE
    Y4C := FALSE;
END_IF;

(* --- Rung 9, step 61 --- *)
IF Y49 THEN
    Y4A := TRUE;
ELSE
    Y4A := FALSE;
END_IF;
