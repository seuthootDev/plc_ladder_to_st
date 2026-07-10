(* --- Rung 1, step 0 --- *)
IF X1011 THEN
    D310_0 := TRUE;
ELSE
    D310_0 := FALSE;
END_IF;
IF X1011 THEN
    D310_1 := TRUE;
ELSE
    D310_1 := FALSE;
END_IF;

(* --- Rung 2, step 3 --- *)
IF X1012 THEN
    D310_7 := TRUE;
ELSE
    D310_7 := FALSE;
END_IF;

(* --- Rung 3, step 5 --- *)
IF M60 THEN
    D310_E := TRUE;
ELSE
    D310_E := FALSE;
END_IF;

(* --- Rung 4, step 7 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    D310_C := TRUE;
ELSE
    D310_C := FALSE;
END_IF;

(* --- Rung 5, step 11 --- *)
IF D300_0 THEN
    M6000 := TRUE;
END_IF;

(* --- Rung 6, step 13 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M6000 := FALSE;
END_IF;

(* --- Rung 7, step 17 --- *)
IF D300_1 THEN
    M6001 := TRUE;
END_IF;

(* --- Rung 8, step 19 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M6001 := FALSE;
END_IF;

(* --- Rung 9, step 23 --- *)
IF (D300_2) OR (D300_3) THEN
    M6100 := TRUE;
END_IF;

(* --- Rung 10, step 26 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M6100 := FALSE;
END_IF;
