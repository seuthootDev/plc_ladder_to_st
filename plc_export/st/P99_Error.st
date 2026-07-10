(* Generated ST from context: P99_Error *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P99_Error' *)
(* ============================================================ *)

PROGRAM P99_Error
VAR
    M54 : BOOL; (* 비상정지TOTAL *)
    M2127 : BOOL; (* 글라스 센터링 이상    TOTAL *)
    M3127 : BOOL; (* 그리퍼 이상  TOTAL *)
    M57 : BOOL; (* 설비 종합이상 *)
    X1F : BOOL; (* 제어반 비상정지  [EPBL] *)
    M50 : BOOL; (* 제어반 비상정지 *)
    M212 : BOOL; (* 이상해제 *)
    SM401 : BOOL; (* 항상off *)
    M51 : BOOL; (* 프라이머로보트 비상정지 *)
    M52 : BOOL; (* 실러 로보트 비상정지 *)
    M53 : BOOL;
    Y40 : BOOL; (* 센터링 가압 전진    SOL *)
    M2000 : BOOL; (* 센터링 가압 후진단 *)
    Y41 : BOOL; (* 센터링 가압 후진   SOL *)
    M2001 : BOOL; (* 센터링 가압 전진단 *)
    T100 : TON; (* 글라스 센터링 가압단 이상      SOL *)
    M2100 : BOOL; (* 글라스 센터링 가압단 이상      SOL *)
    Y42 : BOOL; (* 센터링 이컬라이져 후진         SOL *)
    M2002 : BOOL; (* 센터링 이컬라이져 후진단 *)
    Y43 : BOOL; (* 센터링 이컬라이져 전진         SOL *)
    M2003 : BOOL; (* 센터링 이컬라이져 전진단 *)
    T101 : TON; (* 글라스센터링 이컬라이져 이상   SOL *)
    M2101 : BOOL; (* 글라스센터링 이컬라이져 이상   SOL *)
    Y54 : BOOL; (* 가와사키로보트 진공  ON  SOL_1 *)
    Y56 : BOOL; (* 가와사키로보트 진공  ON  SOL_2 *)
    X1C : BOOL; (* 로보트 그리퍼 진공확인    #1 *)
    X1D : BOOL; (* 로보트 그리퍼 진공확인    #2 *)
    M3100 : BOOL; (* 실러 로보트 그리퍼 진공이상 *)
    T110 : TON; (* 실러 로보트 그리퍼 진공이상 *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

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

