(* --- Rung 1, step 0 | Total Error --- *)
IF NOT ((NOT (M54)) AND (NOT (M2127)) AND (NOT (M3127))) THEN
    M57 := TRUE;
ELSE
    M57 := FALSE;
END_IF;

(* --- Rung 2, step 13 | MCP Error --- *)
IF (NOT (X1F)) OR ((M50) AND (NOT (M212))) THEN
    M50 := TRUE;
ELSE
    M50 := FALSE;
END_IF;

(* --- Rung 3, step 25 --- *)
IF (SM401) OR ((M51) AND (NOT (M212))) THEN
    M51 := TRUE;
ELSE
    M51 := FALSE;
END_IF;

(* --- Rung 4, step 30 --- *)
IF (SM401) OR ((M52) AND (NOT (M212))) THEN
    M52 := TRUE;
ELSE
    M52 := FALSE;
END_IF;

(* --- Rung 5, step 35 --- *)
IF NOT ((NOT (M50)) AND (NOT (M51)) AND (NOT (M52)) AND (NOT (M53))) THEN
    M54 := TRUE;
ELSE
    M54 := FALSE;
END_IF;

(* --- Rung 6, step 41 | Centering Error --- *)
IF ((((Y40) AND (NOT (M2000))) OR ((Y41) AND (NOT (M2001)))) AND (T100)) OR ((M2100) AND (NOT (M212))) THEN
    M2100 := TRUE;
ELSE
    M2100 := FALSE;
END_IF;
IF ((((Y40) AND (NOT (M2000))) OR ((Y41) AND (NOT (M2001)))) AND (T100)) OR ((M2100) AND (NOT (M212))) THEN
    T100(IN := TRUE, PT := T#8s);
ELSE
    T100(IN := FALSE);
END_IF;

(* --- Rung 7, step 65 --- *)
IF ((((Y42) AND (NOT (M2002))) OR ((Y43) AND (NOT (M2003)))) AND (T101)) OR ((M2101) AND (NOT (M212))) THEN
    M2101 := TRUE;
ELSE
    M2101 := FALSE;
END_IF;
IF ((((Y42) AND (NOT (M2002))) OR ((Y43) AND (NOT (M2003)))) AND (T101)) OR ((M2101) AND (NOT (M212))) THEN
    T101(IN := TRUE, PT := T#8s);
ELSE
    T101(IN := FALSE);
END_IF;

(* --- Rung 8, step 79 --- *)
IF NOT ((NOT (M2100)) AND (NOT (M2101))) THEN
    M2127 := TRUE;
ELSE
    M2127 := FALSE;
END_IF;

(* --- Rung 9, step 83 | Gripper Error --- *)
IF (((Y54) AND (Y56) AND ((NOT (X1C)) OR (X1D))) OR ((M3100) AND (NOT (M212)))) AND (T110) THEN
    M3100 := TRUE;
ELSE
    M3100 := FALSE;
END_IF;
IF ((Y54) AND (Y56) AND ((NOT (X1C)) OR (X1D))) OR ((M3100) AND (NOT (M212))) THEN
    T110(IN := TRUE, PT := T#3s);
ELSE
    T110(IN := FALSE);
END_IF;

(* --- Rung 10, step 108 --- *)
IF NOT (NOT (M3100)) THEN
    M3127 := TRUE;
ELSE
    M3127 := FALSE;
END_IF;
