(* Generated ST from context: P12_BodyVision *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P12_BodyVision' *)
(* ============================================================ *)

PROGRAM P12_BodyVision
VAR
    X1011 : BOOL; (* 실러[ RB]BODY START *)
    D310_0 : BOOL;
    D310_1 : BOOL;
    X1012 : BOOL; (* 실러[ RB]GAP START *)
    D310_7 : BOOL;
    M60 : BOOL; (* 실러 로보트 작업완료 *)
    D310 : WORD;
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M175 : BOOL; (* 실러작업완료[HMI] RST PB *)
    M174 : BOOL; (* 실러작업완료[HMI] SET PB *)
    D300_0 : BOOL;
    M6000 : BOOL; (* 바디비전OK *)
    D300_1 : BOOL;
    M6001 : BOOL; (* 바디비전NG *)
    D300_2 : BOOL;
    D300_3 : BOOL;
    M6100 : BOOL; (* Gap Complete *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

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

