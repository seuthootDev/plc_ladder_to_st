(* Generated ST from context: P01_Main *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P01_Main' *)
(* ============================================================ *)

PROGRAM P01_Main
VAR
    SM400 : BOOL; (* 항상on *)
    M200 : BOOL; (* 제어전원ON *)
    X0 : BOOL; (* 운전준비ON [PBL] *)
    M201 : BOOL; (* 운전준비 PLS *)
    M202 : BOOL; (* 제어반 운전준비완료 *)
    M50 : BOOL; (* 제어반 비상정지 *)
    X1 : BOOL; (* 운전모드 자동[ ]  [SS] *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M211 : BOOL; (* 운전모드 자동[ ] *)
    M500 : BOOL; (* 기동시작[HMI]   PB *)
    M215 : BOOL; (* 가와실러자동기동 *)
    M216 : BOOL; (* 현대 프라이머자동기동 *)
    M2127 : BOOL; (* 글라스 센터링 이상    TOTAL *)
    M2021 : BOOL; (* 글라스 센터링 운전준비 완료 *)
    X8 : BOOL; (* 이상해제[PB] *)
    M501 : BOOL; (* 이상해제[HMI]   PB *)
    M212 : BOOL; (* 이상해제 *)
    Y77 : BOOL; (* 선두 이더넷 카드 이상해제XY60 *)
    M502 : BOOL; (* 부저정지[HMI]   PB *)
    M220 : BOOL; (* 부져정지 SET *)
    M57 : BOOL; (* 설비 종합이상 *)
    X1100 : BOOL; (* 현대 작업완료    PRIMER] *)
    M170 : BOOL; (* 프라이머작업완료[HMI]   SET PB *)
    M171 : BOOL; (* 프라이머작업완료[HMI]   RST PB *)
    M710 : BOOL; (* 프라이머로보트[HMI]     PASS PB *)
    M1321 : BOOL; (* 프라이머로보트 작업완료 *)
    X111F : BOOL; (* 현대    PRIMER] HOME *)
    X1018 : BOOL; (* 실러 작업완료[ RB] *)
    M174 : BOOL; (* 실러작업완료[HMI] SET PB *)
    M175 : BOOL; (* 실러작업완료[HMI] RST PB *)
    M712 : BOOL; (* 실러 로보트[HMI]         PASS PB *)
    M60 : BOOL; (* 실러 로보트 작업완료 *)
    M2005 : BOOL; (* 센터링 글라스 감지단 *)
    M180 : BOOL; (* 글라스 반전 완료[HMI]      PB *)
    M2000 : BOOL; (* 센터링 가압 후진단 *)
    M2002 : BOOL; (* 센터링 이컬라이져 후진단 *)
    M1422 : BOOL; (* 센터링 글라스 로딩완료 *)
    M1522 : BOOL; (* 실러 센터링 완료 *)
    M5000 : BOOL; (* 실러비전OK *)
    M5001 : BOOL; (* 실러비전NG *)
    M6000 : BOOL; (* 바디비전OK *)
    M6001 : BOOL; (* 바디비전NG *)
    M6100 : BOOL; (* Gap Complete *)
    T70 : TON; (* 실러    ROBOT   HOME    POSITION *)
    M7750 : BOOL; (* Body    Auto    Start   COND *)
    M7000 : BOOL; (* 프라이머OK *)
    M7001 : BOOL; (* 프라이머NG *)
    T50 : TON; (* PRIMER  ROBOT   HOME    DELAY *)
    M7751 : BOOL; (* Primer  Auto    Start   COND *)
    X0_PLS : BOOL; (* 운전준비ON [PBL] *)
    X1018_PLS : BOOL; (* 실러 작업완료[ RB] *)
    X1100_PLS : BOOL; (* 현대 작업완료    PRIMER] *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 | MODE --- *)
IF SM400 THEN
    M200 := TRUE;
ELSE
    M200 := FALSE;
END_IF;

(* --- Rung 2, step 6 --- *)
IF X0_PLS THEN
    M201 := TRUE;
ELSE
    M201 := FALSE;
END_IF;

(* --- Rung 3, step 8 --- *)
IF (((M201) AND (NOT (M202))) OR ((NOT (M201)) AND (M202))) AND (M200) AND (NOT (M50)) THEN
    M202 := TRUE;
ELSE
    M202 := FALSE;
END_IF;

(* --- Rung 4, step 16 --- *)
IF (M202) AND (NOT (X1)) THEN
    M210 := TRUE;
ELSE
    M210 := FALSE;
END_IF;

(* --- Rung 5, step 19 --- *)
IF (M202) AND (X1) THEN
    M211 := TRUE;
ELSE
    M211 := FALSE;
END_IF;

(* --- Rung 6, step 22 --- *)
IF ((M500) OR (M215)) AND (M211) AND (NOT (M50)) THEN
    M215 := TRUE;
ELSE
    M215 := FALSE;
END_IF;

(* --- Rung 7, step 27 --- *)
IF ((M500) OR (M216)) AND (M211) AND (NOT (M50)) THEN
    M216 := TRUE;
ELSE
    M216 := FALSE;
END_IF;

(* --- Rung 8, step 32 --- *)
IF (M202) AND (NOT (M2127)) THEN
    M2021 := TRUE;
ELSE
    M2021 := FALSE;
END_IF;

(* --- Rung 9, step 35 | Error Reset --- *)
IF (X8) OR (M501) THEN
    M212 := TRUE;
ELSE
    M212 := FALSE;
END_IF;

(* --- Rung 10, step 46 --- *)
IF M212 THEN
    Y77 := TRUE;
ELSE
    Y77 := FALSE;
END_IF;

(* --- Rung 11, step 48 --- *)
IF (SM400) AND (M502) THEN
    M220 := TRUE;
END_IF;
IF (SM400) AND (NOT (M57)) THEN
    M220 := FALSE;
END_IF;

(* --- Rung 12, step 55 | Work --- *)
IF (X1100_PLS) OR ((M210) AND (M170) AND (NOT (M171))) OR (M710) THEN
    M1321 := TRUE;
END_IF;

(* --- Rung 13, step 66 --- *)
IF (M210) AND (M171) AND (X111F) THEN
    M1321 := FALSE;
END_IF;

(* --- Rung 14, step 84 | - --- *)
IF (X1018_PLS) OR ((M210) AND (M174) AND (NOT (M175))) OR (M712) THEN
    M60 := TRUE;
END_IF;

(* --- Rung 15, step 80 --- *)
IF (M210) AND (M175) AND (NOT (M174)) THEN
    M60 := FALSE;
END_IF;

(* --- Rung 16, step 84 | - --- *)
IF (M2005) AND (M180) AND (M2005) AND (M2000) AND (M2002) THEN
    M1422 := TRUE;
END_IF;

(* --- Rung 17, step 93 --- *)
IF (M1522) OR (M2005) THEN
    M1422 := FALSE;
END_IF;

(* --- Rung 18, step 96 --- *)
IF (NOT (M60)) AND (NOT (M5000)) AND (NOT (M5001)) AND (NOT (M6000)) AND (NOT (M6001)) AND (NOT (M6100)) AND (T70) THEN
    M7750 := TRUE;
ELSE
    M7750 := FALSE;
END_IF;

(* --- Rung 19, step 104 --- *)
IF (NOT (M1321)) AND (NOT (M7000)) AND (NOT (M7001)) AND (T50) THEN
    M7751 := TRUE;
ELSE
    M7751 := FALSE;
END_IF;

