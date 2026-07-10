(* Generated ST from context: P30_Centering *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P30_Centering' *)
(* ============================================================ *)

PROGRAM P30_Centering
VAR
    SM400 : BOOL; (* 항상on *)
    X10 : BOOL; (* 센터링 가압 후진단 *)
    T20 : TON; (* 센터링 가압 후진단 지연 *)
    M2000 : BOOL; (* 센터링 가압 후진단 *)
    T21 : TON; (* 센터링 가압 전진단 지연 *)
    M2001 : BOOL; (* 센터링 가압 전진단 *)
    X11 : BOOL; (* 센터링 이컬라이져 후진단 *)
    T22 : TON; (* 센터링 이컬라이져 후진단 *)
    M2002 : BOOL; (* 센터링 이컬라이져 후진단 *)
    T23 : TON; (* 센터링 이컬라이져 전진단 *)
    M2003 : BOOL; (* 센터링 이컬라이져 전진단 *)
    X14 : BOOL; (* 글라스 센터링 글라스 감지단 *)
    T35 : TON; (* 센터링 글라스 감지단 *)
    M2005 : BOOL; (* 센터링 글라스 감지단 *)
    M1522 : BOOL; (* 실러 센터링 완료 *)
    M2020 : BOOL; (* 글라스 센터링    HOME POS. *)
    M2021 : BOOL; (* 글라스 센터링 운전준비 완료 *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M516 : BOOL; (* 센타링 원점복귀[HMI]     PB *)
    M2027 : BOOL; (* 글라스 센터링 원점복귀보조 *)
    M215 : BOOL; (* 가와실러자동기동 *)
    M1421 : BOOL; (* 센터링 언클램프 요구      (M1422.1 *)
    M511 : BOOL; (* 가압단 후진[HMI]     PB *)
    Y40 : BOOL; (* 센터링 가압 전진    SOL *)
    Y41 : BOOL; (* 센터링 가압 후진   SOL *)
    M1422 : BOOL; (* 센터링 글라스 로딩완료 *)
    M510 : BOOL; (* 가압단 전진[HMI]     PB *)
    M1554 : BOOL; (* 실러 간섭무    ROBOT *)
    M513 : BOOL; (* 이컬러이져 후진[HMI]   PB *)
    Y43 : BOOL; (* 센터링 이컬라이져 전진         SOL *)
    Y42 : BOOL; (* 센터링 이컬라이져 후진         SOL *)
    M512 : BOOL; (* 이컬러이져 전진[HMI]   PB *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 | Senser --- *)
IF (SM400) AND (X10) AND (T20) THEN
    M2000 := TRUE;
ELSE
    M2000 := FALSE;
END_IF;
IF (SM400) AND (X10) THEN
    T20(IN := TRUE, PT := T#1s);
ELSE
    T20(IN := FALSE);
END_IF;
IF (SM400) AND (NOT (X10)) AND (T21) THEN
    M2001 := TRUE;
ELSE
    M2001 := FALSE;
END_IF;
IF (SM400) AND (NOT (X10)) THEN
    T21(IN := TRUE, PT := T#1s);
ELSE
    T21(IN := FALSE);
END_IF;

(* --- Rung 2, step 26 --- *)
IF (SM400) AND (X11) AND (T22) THEN
    M2002 := TRUE;
ELSE
    M2002 := FALSE;
END_IF;
IF (SM400) AND (X11) THEN
    T22(IN := TRUE, PT := T#1s);
ELSE
    T22(IN := FALSE);
END_IF;
IF (SM400) AND (NOT (X11)) AND (T23) THEN
    M2003 := TRUE;
ELSE
    M2003 := FALSE;
END_IF;
IF (SM400) AND (NOT (X11)) THEN
    T23(IN := TRUE, PT := T#1s);
ELSE
    T23(IN := FALSE);
END_IF;
IF (SM400) AND (X14) AND (T35) THEN
    M2005 := TRUE;
ELSE
    M2005 := FALSE;
END_IF;
IF (SM400) AND (X14) THEN
    T35(IN := TRUE, PT := T#3s);
ELSE
    T35(IN := FALSE);
END_IF;

(* --- Rung 3, step 57 --- *)
IF (M2001) AND (M2003) THEN
    M1522 := TRUE;
ELSE
    M1522 := FALSE;
END_IF;

(* --- Rung 4, step 60 --- *)
IF (M2000) AND (M2002) THEN
    M2020 := TRUE;
ELSE
    M2020 := FALSE;
END_IF;

(* --- Rung 5, step 63 | Home Return --- *)
IF (M2021) AND (M210) AND ((M516) OR (M2027)) AND (NOT (M2020)) THEN
    M2027 := TRUE;
ELSE
    M2027 := FALSE;
END_IF;

(* --- Rung 6, step 107 | - --- *)
IF (M2021) AND (((M215) AND (M1421)) OR ((M210) AND ((M511) OR (M2027)))) AND (M2002) AND (NOT (M2000)) AND (NOT (Y40)) THEN
    Y41 := TRUE;
ELSE
    Y41 := FALSE;
END_IF;

(* --- Rung 7, step 94 --- *)
IF (M2021) AND (((M215) AND (M2005) AND (M1422)) OR ((M210) AND (M510))) AND (M2002) AND (NOT (M2001)) AND (M1554) AND (NOT (Y41)) THEN
    Y40 := TRUE;
ELSE
    Y40 := FALSE;
END_IF;

(* --- Rung 8, step 107 | - --- *)
IF (M2021) AND (((M215) AND (M1421)) OR ((M210) AND ((M513) OR (M2027)))) AND (M2001) AND (NOT (M2002)) AND (NOT (Y43)) THEN
    Y42 := TRUE;
ELSE
    Y42 := FALSE;
END_IF;

(* --- Rung 9, step 123 --- *)
IF (M2021) AND (((M215) AND (M2005) AND (M1422)) OR ((M210) AND (M512))) AND (M2001) AND (NOT (M2003)) AND (M1554) AND (NOT (Y42)) THEN
    Y43 := TRUE;
ELSE
    Y43 := FALSE;
END_IF;

