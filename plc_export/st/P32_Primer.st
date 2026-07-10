(* Generated ST from context: P32_Primer *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P32_Primer' *)
(* ============================================================ *)

PROGRAM P32_Primer
VAR
    X2 : BOOL;
    T2 : TON;
    M110 : BOOL; (* OLD     PRIMER *)
    M111 : BOOL; (* NEW     PRIMER *)
    X3 : BOOL;
    T3 : TON;
    X1103 : BOOL; (* 현대 프라이머토출    PRIMER]  ON *)
    M102 : BOOL; (* OLD     PRIMER  ON *)
    M103 : BOOL; (* OLD     PRIMER  OFF *)
    M100 : BOOL; (* NEW     PRIMER  ON *)
    SM400 : BOOL; (* 항상on *)
    Y2D : BOOL; (* 프라이머토출 ON *)
    T10 : TON;
    Y2E : BOOL; (* 프라이머토출 OFF *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

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

