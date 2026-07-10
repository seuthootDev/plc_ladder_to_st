(* Generated ST from context: P33_Gripper *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P33_Gripper' *)
(* ============================================================ *)

PROGRAM P33_Gripper
VAR
    SM400 : BOOL; (* 항상on *)
    Y54 : BOOL; (* 가와사키로보트 진공  ON  SOL_1 *)
    Y56 : BOOL; (* 가와사키로보트 진공  ON  SOL_2 *)
    X1C : BOOL; (* 로보트 그리퍼 진공확인    #1 *)
    X1D : BOOL; (* 로보트 그리퍼 진공확인    #2 *)
    T25 : TON; (* 그리퍼 진공흡착확인 지연 *)
    M3000 : BOOL; (* 그리퍼 진공흡착확인 *)
    T26 : TON; (* 그리퍼 진공탈착확인 지연 *)
    M3001 : BOOL; (* 그리퍼 진공탈착확인 *)
    M3020 : BOOL; (* 실러 로보트 원위치 *)
    M202 : BOOL; (* 제어반 운전준비완료 *)
    M3127 : BOOL; (* 그리퍼 이상  TOTAL *)
    M3021 : BOOL; (* 실러 로보트 운전전비완료 *)
    X1005 : BOOL; (* 실러 그리퍼 진공흡착[ RB] *)
    X1006 : BOOL; (* 실러 그리퍼 진공탈착[ RB] *)
    M630 : BOOL; (* 실러 로봇그리퍼 진공 보조    ON *)
    M631 : BOOL; (* 실러 로봇그리퍼 진공 보조    OFF *)
    X1013 : BOOL;
    X1014 : BOOL;
    M633 : BOOL; (* SEALER  ROVOT   PUSH    ADV *)
    M634 : BOOL; (* SEALER  ROBOT   PUSH    REV *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M215 : BOOL; (* 가와실러자동기동 *)
    M530 : BOOL; (* 진공흡착[HMI]   PB *)
    M531 : BOOL; (* 진공탈착[HMI]   PB *)
    Y46 : BOOL; (* 가와사키로보트 진공파기  SOL_1 *)
    Y47 : BOOL; (* 가와사키로보트 진공파기  SOL_2 *)
    T209 : TON; (* 진공 파기 SOL ON  TIME *)
    Y55 : BOOL; (* 가와사키로보트 진공  OFF SOL_1 *)
    Y57 : BOOL; (* 가와사키로보트 진공  OFF SOL_2 *)
    M7500 : BOOL;
    Y4E : BOOL; (* PUSH    ADV *)
    M7501 : BOOL;
    Y4D : BOOL; (* PUSH    REV *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 --- *)
IF (SM400) AND ((Y54) OR (Y56)) AND (X1C) AND (X1D) AND (T25) THEN
    M3000 := TRUE;
ELSE
    M3000 := FALSE;
END_IF;
IF (SM400) AND ((Y54) OR (Y56)) AND (X1C) AND (X1D) THEN
    T25(IN := TRUE, PT := T#1s);
ELSE
    T25(IN := FALSE);
END_IF;

(* --- Rung 2, step 14 --- *)
IF (SM400) AND (NOT (Y54)) AND (NOT (Y56)) AND (NOT (X1C)) AND (NOT (X1D)) AND (T26) THEN
    M3001 := TRUE;
ELSE
    M3001 := FALSE;
END_IF;
IF (SM400) AND (NOT (Y54)) AND (NOT (Y56)) AND (NOT (X1C)) AND (NOT (X1D)) THEN
    T26(IN := TRUE, PT := T#1s);
ELSE
    T26(IN := FALSE);
END_IF;

(* --- Rung 3, step 27 --- *)
IF SM400 THEN
    M3020 := TRUE;
ELSE
    M3020 := FALSE;
END_IF;

(* --- Rung 4, step 29 --- *)
IF (M202) AND (NOT (M3127)) THEN
    M3021 := TRUE;
ELSE
    M3021 := FALSE;
END_IF;

(* --- Rung 5, step 32 --- *)
IF (SM400) AND (X1005) AND (NOT (X1006)) THEN
    M630 := TRUE;
ELSE
    M630 := FALSE;
END_IF;
IF (SM400) AND (X1006) AND (NOT (X1005)) THEN
    M631 := TRUE;
ELSE
    M631 := FALSE;
END_IF;
IF (SM400) AND (X1013) AND (NOT (X1014)) THEN
    M633 := TRUE;
ELSE
    M633 := FALSE;
END_IF;
IF (SM400) AND (NOT (X1013)) AND (X1014) THEN
    M634 := TRUE;
ELSE
    M634 := FALSE;
END_IF;

(* --- Rung 6, step 49 --- *)
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M530) OR (M630))) OR ((M215) AND ((M630) OR (Y54) OR (Y56)) AND (NOT (M631)))) THEN
    Y54 := TRUE;
ELSE
    Y54 := FALSE;
END_IF;
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M530) OR (M630))) OR ((M215) AND ((M630) OR (Y54) OR (Y56)) AND (NOT (M631)))) THEN
    Y56 := TRUE;
ELSE
    Y56 := FALSE;
END_IF;
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M531) OR (M631))) OR ((M215) AND ((M631) OR (Y46) OR (Y47)) AND (NOT (M630)) AND (NOT (T209)))) THEN
    Y55 := TRUE;
ELSE
    Y55 := FALSE;
END_IF;
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M531) OR (M631))) OR ((M215) AND ((M631) OR (Y46) OR (Y47)) AND (NOT (M630)) AND (NOT (T209)))) THEN
    Y57 := TRUE;
ELSE
    Y57 := FALSE;
END_IF;
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M531) OR (M631))) OR ((M215) AND ((M631) OR (Y46) OR (Y47)) AND (NOT (M630)) AND (NOT (T209)))) THEN
    Y46 := TRUE;
ELSE
    Y46 := FALSE;
END_IF;
IF (SM400) AND (((M210) AND (NOT (M215)) AND ((M531) OR (M631))) OR ((M215) AND ((M631) OR (Y46) OR (Y47)) AND (NOT (M630)) AND (NOT (T209)))) THEN
    Y47 := TRUE;
ELSE
    Y47 := FALSE;
END_IF;
IF (SM400) AND ((Y46) OR (Y47)) THEN
    T209(IN := TRUE, PT := T#5s);
ELSE
    T209(IN := FALSE);
END_IF;
IF (SM400) AND (T209) THEN
    M531 := FALSE;
END_IF;
IF (SM400) AND (M215) THEN
    M530 := FALSE;
END_IF;
IF (SM400) AND (M215) THEN
    M531 := FALSE;
END_IF;

(* --- Rung 7, step 100 --- *)
IF (M633) OR (M7500) THEN
    Y4E := TRUE;
ELSE
    Y4E := FALSE;
END_IF;

(* --- Rung 8, step 103 --- *)
IF (M634) OR (M7501) THEN
    Y4D := TRUE;
ELSE
    Y4D := FALSE;
END_IF;

