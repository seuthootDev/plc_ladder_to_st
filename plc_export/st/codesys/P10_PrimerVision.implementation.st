(* --- Rung 1, step 0 | Live Bit --- *)
IF (SM401) AND (D100_F) AND (T210) THEN
    D100_F := FALSE;
END_IF;
IF (SM401) AND (D100_F) THEN
    T210(IN := TRUE, PT := T#500s);
ELSE
    T210(IN := FALSE);
END_IF;

(* --- Rung 2, step 16 --- *)
IF (SM400) AND (NOT (D100_F)) THEN
    T200(IN := TRUE, PT := T#10s);
ELSE
    T200(IN := FALSE);
END_IF;

(* --- Rung 3, step 22 --- *)
IF (SM400) AND (SM412) THEN
    D110_F := TRUE;
ELSE
    D110_F := FALSE;
END_IF;

(* --- Rung 4, step 25 | Vision Start --- *)
IF (X1104) OR (M720) THEN
    D110_0 := TRUE;
ELSE
    D110_0 := FALSE;
END_IF;

(* --- Rung 5, step 36 --- *)
IF (X1104) OR (M720) THEN
    D110_1 := TRUE;
ELSE
    D110_1 := FALSE;
END_IF;

(* --- Rung 6, step 39 --- *)
IF (X1105) OR (M721) THEN
    D110_2 := TRUE;
ELSE
    D110_2 := FALSE;
END_IF;

(* --- Rung 7, step 42 --- *)
IF (M1321) OR (M722) THEN
    D110_E := TRUE;
ELSE
    D110_E := FALSE;
END_IF;

(* --- Rung 8, step 45 --- *)
IF ((M210) AND (M171) AND (X111F)) OR (M723) THEN
    D110_C := TRUE;
ELSE
    D110_C := FALSE;
END_IF;

(* --- Rung 9, step 50 | POS --- *)
IF (SM400) AND (X1106) THEN
    D110_8 := TRUE;
ELSE
    D110_8 := FALSE;
END_IF;
IF (SM400) AND (X1107) THEN
    D110_9 := TRUE;
ELSE
    D110_9 := FALSE;
END_IF;
IF (SM400) AND (X1108) THEN
    D110_A := TRUE;
ELSE
    D110_A := FALSE;
END_IF;
IF (SM400) AND (X1109) THEN
    D110_B := TRUE;
ELSE
    D110_B := FALSE;
END_IF;

(* --- Rung 10, step 67 --- *)
IF D100_0 THEN
    M7000 := TRUE;
END_IF;

(* --- Rung 11, step 69 --- *)
IF (M210) AND (M171) AND (X111F) THEN
    M7000 := FALSE;
END_IF;

(* --- Rung 12, step 73 --- *)
IF D100_1 THEN
    M7001 := TRUE;
END_IF;

(* --- Rung 13, step 75 --- *)
IF (M210) AND (M171) AND (X111F) THEN
    M7001 := FALSE;
END_IF;
