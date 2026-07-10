(* Generated ST from context: P11_SealerVision *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P11_SealerVision' *)
(* ============================================================ *)

PROGRAM P11_SealerVision
VAR
    SM400 : BOOL; (* 항상on *)
    D200 : WORD; (* 실러비전→ PLC *)
    T201 : TON; (* 실러비전통신이상 *)
    SM412 : BOOL; (* 초 클럭1 *)
    D210 : WORD; (* 실러비전PLC → *)
    X100B : BOOL; (* 실러 구간[ RB]  1 *)
    D210_8 : BOOL; (* 실러비전PLC → *)
    X100C : BOOL; (* 실러 구간[ RB]  2 *)
    D210_9 : BOOL; (* 실러비전PLC → *)
    X100D : BOOL; (* 실러 구간[ RB]  4 *)
    X100E : BOOL; (* 실러 구간[ RB]  8 *)
    X1009 : BOOL; (* 실러 실러비전스타트[ RB] *)
    D210_0 : BOOL; (* 실러비전PLC → *)
    D210_1 : BOOL; (* 실러비전PLC → *)
    X100A : BOOL; (* 실러 실러비전[ RB] OFF *)
    D210_2 : BOOL; (* 실러비전PLC → *)
    M60 : BOOL; (* 실러 로보트 작업완료 *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M175 : BOOL; (* 실러작업완료[HMI] RST PB *)
    M174 : BOOL; (* 실러작업완료[HMI] SET PB *)
    D200_0 : BOOL; (* 실러비전→ PLC *)
    M5000 : BOOL; (* 실러비전OK *)
    D200_1 : BOOL; (* 실러비전→ PLC *)
    M5001 : BOOL; (* 실러비전NG *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

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

