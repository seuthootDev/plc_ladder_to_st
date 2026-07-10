(* --- Rung 1, step 0 --- *)
IF (SM400) AND (D200_F) THEN
    T201(IN := TRUE, PT := T#5s);
ELSE
    T201(IN := FALSE);
END_IF;
IF (SM400) AND (SM412) THEN
    D210_F := TRUE;
ELSE
    D210_F := FALSE;
END_IF;

(* --- Rung 2, step 10 | POS --- *)
IF (SM400) AND (X100B) THEN
    D210_8 := TRUE;
ELSE
    D210_8 := FALSE;
END_IF;
IF (SM400) AND (X100C) THEN
    D210_9 := TRUE;
ELSE
    D210_9 := FALSE;
END_IF;
IF (SM400) AND (X100D) THEN
    D210_A := TRUE;
ELSE
    D210_A := FALSE;
END_IF;
IF (SM400) AND (X100E) THEN
    D210_B := TRUE;
ELSE
    D210_B := FALSE;
END_IF;

(* --- Rung 3, step 27 --- *)
IF X1009 THEN
    D210_0 := TRUE;
ELSE
    D210_0 := FALSE;
END_IF;

(* --- Rung 4, step 29 --- *)
IF X1009 THEN
    D210_1 := TRUE;
ELSE
    D210_1 := FALSE;
END_IF;

(* --- Rung 5, step 31 --- *)
IF X100A THEN
    D210_2 := TRUE;
ELSE
    D210_2 := FALSE;
END_IF;

(* --- Rung 6, step 33 --- *)
IF M60 THEN
    D210_E := TRUE;
ELSE
    D210_E := FALSE;
END_IF;

(* --- Rung 7, step 35 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    D210_C := TRUE;
ELSE
    D210_C := FALSE;
END_IF;

(* --- Rung 8, step 39 --- *)
IF D200_0 THEN
    M5000 := TRUE;
END_IF;

(* --- Rung 9, step 41 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M5000 := FALSE;
END_IF;

(* --- Rung 10, step 45 --- *)
IF D200_1 THEN
    M5001 := TRUE;
END_IF;

(* --- Rung 11, step 47 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M5001 := FALSE;
END_IF;
