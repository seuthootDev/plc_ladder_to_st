(* Generated ST from context: P20_PrimerRobot *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P20_PrimerRobot' *)
(* ============================================================ *)

PROGRAM P20_PrimerRobot
VAR
    X111F : BOOL; (* 현대    PRIMER] HOME *)
    T50 : TON; (* PRIMER  ROBOT   HOME    DELAY *)
    M1353 : BOOL; (* PRIMER  ROBOT   HOME    (M1350.3 *)
    M1321 : BOOL; (* 프라이머로보트 작업완료 *)
    M50 : BOOL; (* 제어반 비상정지 *)
    M7751 : BOOL; (* Primer  Auto    Start   COND *)
    M1362 : BOOL; (* PRIMER  RB STARTCONDITION *)
    X7 : BOOL; (* 로보트 재기동    [PB] *)
    X1119 : BOOL; (* 현대[    PRIMER] program end *)
    M1364 : BOOL; (* 로봇 재기동PRIMER        (M1352.2 *)
    M216 : BOOL; (* 현대 프라이머자동기동 *)
    X111D : BOOL; (* 현대 로봇    PRIMER] Auto mode *)
    X111E : BOOL; (* 현대    PRIMER] Robot   Ready On *)
    X111A : BOOL; (* 현대    PRIMER] Robot   Error *)
    M710 : BOOL; (* 프라이머로보트[HMI]     PASS PB *)
    T51 : TON; (* PRIMER  ROBOT   START   DELAY *)
    T52 : TON; (* PRIMER  ROBOT   START   OFF *)
    X111C : BOOL; (* 현대    PRIMER] Robot   Running *)
    Y1116 : BOOL; (* 현대    PRIMER] ROBOT   START *)
    X1117 : BOOL; (* 현대 로봇 비상정지    PRIMER] *)
    X1036 : BOOL; (* 실러 로보트 비상정지[ RB] *)
    Y1117 : BOOL; (* 현대    PRIMER] ROBOT   PAUSE *)
    M212 : BOOL; (* 이상해제 *)
    Y1103 : BOOL; (* 현대 로봇 이상해제    PRIMER] *)
    X1101 : BOOL; (* 현대 센터링 간섭무    PRIMER] *)
    M1354 : BOOL; (* 불간섭PRIMER  ROBOT     (M1350.4 *)
    SM400 : BOOL; (* 항상on *)
    Y1100 : BOOL; (* 현대 센터링 진입가능    PRIMER] *)
    X1002 : BOOL; (* 실러 프라이머로봇 상호인터록[ RB] *)
    M712 : BOOL; (* 실러 로보트[HMI]         PASS PB *)
    X103D : BOOL; (* 실러[ RB]HOME    POSITION *)
    Y1102 : BOOL; (* 현대 실러 상호인터록    PRIMER] RB *)
    M700 : BOOL; (* 프라이머로보트 선택  _HMIPB *)
    M701 : BOOL; (* 비젼 로보트 선택      _HMIPB *)
    M702 : BOOL; (* 실러 로보트 선택      _HMIPB *)
    M600 : BOOL; (* 프라이머차종선택1 HMI *)
    M601 : BOOL; (* 프라이머차종선택2 HMI *)
    M602 : BOOL; (* 프라이머차종선택4 HMI *)
    D600 : WORD; (* 프라이머차종입력 *)
    D700 : WORD; (* 프라이머차종 *)
    X111F_PLS : BOOL; (* 현대    PRIMER] HOME *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 | HOME --- *)
IF (X111F) AND (T50) THEN
    M1353 := TRUE;
ELSE
    M1353 := FALSE;
END_IF;
IF X111F THEN
    T50(IN := TRUE, PT := T#1s);
ELSE
    T50(IN := FALSE);
END_IF;

(* --- Rung 2, step 13 | START --- *)
IF ((K0 <> K0)) AND (NOT (M1321)) AND (NOT (M50)) AND (M7751) THEN
    M1362 := TRUE;
ELSE
    M1362 := FALSE;
END_IF;

(* --- Rung 3, step 25 --- *)
IF (X7) AND ((NOT (X111F)) OR (X1119)) THEN
    M1364 := TRUE;
ELSE
    M1364 := FALSE;
END_IF;

(* --- Rung 4, step 30 --- *)
IF (M216) AND (((M1362) AND (T50)) OR ((M1364) AND (NOT (T50)))) AND (X111D) AND (X111E) AND (NOT (X111A)) AND (NOT (M710)) AND (T51) AND (NOT (T52)) AND (NOT (X111C)) AND (NOT (M710)) THEN
    Y1116 := TRUE;
ELSE
    Y1116 := FALSE;
END_IF;
IF (M216) AND (((M1362) AND (T50)) OR ((M1364) AND (NOT (T50)))) AND (X111D) AND (X111E) AND (NOT (X111A)) AND (NOT (M710)) THEN
    T51(IN := TRUE, PT := T#500ms);
ELSE
    T51(IN := FALSE);
END_IF;
IF (M216) AND (((M1362) AND (T50)) OR ((M1364) AND (NOT (T50)))) AND (X111D) AND (X111E) AND (NOT (X111A)) AND (NOT (M710)) THEN
    T52(IN := TRUE, PT := T#2s);
ELSE
    T52(IN := FALSE);
END_IF;

(* --- Rung 5, step 56 --- *)
IF (M216) AND (NOT (X1117)) AND (NOT (X1036)) THEN
    Y1117 := TRUE;
ELSE
    Y1117 := FALSE;
END_IF;

(* --- Rung 6, step 60 --- *)
IF M212 THEN
    Y1103 := TRUE;
ELSE
    Y1103 := FALSE;
END_IF;

(* --- Rung 7, step 62 | INPUT --- *)
IF (X1101) OR (M710) THEN
    M1354 := TRUE;
ELSE
    M1354 := FALSE;
END_IF;

(* --- Rung 8, step 70 | OUTPUT --- *)
IF SM400 THEN
    Y1100 := TRUE;
ELSE
    Y1100 := FALSE;
END_IF;

(* --- Rung 9, step 77 --- *)
IF (X1002) OR ((M712) AND (X103D)) THEN
    Y1102 := TRUE;
ELSE
    Y1102 := FALSE;
END_IF;

(* --- Rung 10, step 82 | Car Type --- *)
IF (SM400) AND (M700) AND (NOT (M701)) AND (NOT (M702)) AND (M600) THEN
    D700 := K1;
END_IF;
IF (SM400) AND (M700) AND (NOT (M701)) AND (NOT (M702)) AND (M601) THEN
    D700 := K2;
END_IF;
IF (SM400) AND (M700) AND (NOT (M701)) AND (NOT (M702)) AND (M602) THEN
    D700 := K3;
END_IF;
IF (SM400) AND (M700) AND (NOT (M701)) AND (NOT (M702)) THEN
    D700 := D600;
END_IF;
IF (SM400) AND (M700) AND (NOT (M701)) AND (NOT (M702)) THEN
    K1Y1118 := D700;
END_IF;

(* --- Rung 11, step 110 --- *)
IF X111F_PLS THEN
    D700 := K0;
END_IF;
IF X111F_PLS THEN
    D600 := K0;
END_IF;

