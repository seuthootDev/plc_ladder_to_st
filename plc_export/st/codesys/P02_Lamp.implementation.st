(* --- Rung 1, step 0 --- *)
IF (M202) OR ((NOT (M202)) AND (SM412)) OR (M503) THEN
    Y20 := TRUE;
ELSE
    Y20 := FALSE;
END_IF;

(* --- Rung 2, step 6 --- *)
IF ((M57) AND (SM412)) OR (M503) THEN
    Y3C := TRUE;
ELSE
    Y3C := FALSE;
END_IF;

(* --- Rung 3, step 10 --- *)
IF ((M202) AND (M210)) OR (M503) THEN
    Y3D := TRUE;
ELSE
    Y3D := FALSE;
END_IF;

(* --- Rung 4, step 14 --- *)
IF ((M202) AND (((M211) AND (SM412)) OR ((M215) AND (M216)))) OR (M503) THEN
    Y3E := TRUE;
ELSE
    Y3E := FALSE;
END_IF;

(* --- Rung 5, step 23 --- *)
IF ((NOT (NOT (M57))) AND (NOT (M220))) OR (M503) THEN
    Y3F := TRUE;
ELSE
    Y3F := FALSE;
END_IF;
