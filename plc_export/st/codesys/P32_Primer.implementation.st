(* --- Rung 1, step 0 --- *)
IF (X2) AND (T2) THEN
    M110 := TRUE;
END_IF;
IF X2 THEN
    M111 := FALSE;
END_IF;
IF X2 THEN
    T2(IN := TRUE, PT := T#1s);
ELSE
    T2(IN := FALSE);
END_IF;

(* --- Rung 2, step 10 --- *)
IF (X3) AND (T3) THEN
    M111 := TRUE;
END_IF;
IF X3 THEN
    M110 := FALSE;
END_IF;
IF X3 THEN
    T3(IN := TRUE, PT := T#1s);
ELSE
    T3(IN := FALSE);
END_IF;

(* --- Rung 3, step 20 --- *)
IF (M110) AND (X1103) THEN
    M102 := TRUE;
ELSE
    M102 := FALSE;
END_IF;
IF (M110) AND (NOT (X1103)) THEN
    M103 := TRUE;
ELSE
    M103 := FALSE;
END_IF;

(* --- Rung 4, step 27 --- *)
IF (M111) AND (X1103) THEN
    M100 := TRUE;
ELSE
    M100 := FALSE;
END_IF;

(* --- Rung 5, step 30 --- *)
IF (SM400) AND ((M102) OR (M100)) THEN
    Y2D := TRUE;
ELSE
    Y2D := FALSE;
END_IF;
IF (SM400) AND ((M103) OR (M100)) AND ((NOT (T10)) OR (M100)) THEN
    Y2E := TRUE;
ELSE
    Y2E := FALSE;
END_IF;
IF (SM400) AND ((M103) OR (M100)) THEN
    T10(IN := TRUE, PT := T#500ms);
ELSE
    T10(IN := FALSE);
END_IF;
