(* Generated ST from context: P21_BodyRobot *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P21_BodyRobot' *)
(* ============================================================ *)

PROGRAM P21_BodyRobot
VAR
    X103D : BOOL; (* 실러[ RB]HOME    POSITION *)
    T70 : TON; (* 실러    ROBOT   HOME    POSITION *)
    M1553 : BOOL; (* 실러    ROBOT   HOME    POSITION *)
    M1556 : BOOL; (* 실러로봇센터링 진입가능 반전  ( ) *)
    M2005 : BOOL; (* 센터링 글라스 감지단 *)
    M1522 : BOOL; (* 실러 센터링 완료 *)
    M50 : BOOL; (* 제어반 비상정지 *)
    M7750 : BOOL; (* Body    Auto    Start   COND *)
    M1552 : BOOL; (* 실러로봇START   CONDITION *)
    X7 : BOOL; (* 로보트 재기동    [PB] *)
    M1555 : BOOL; (* 실러 로봇재기동   (M1552.2 *)
    M215 : BOOL; (* 가와실러자동기동 *)
    X103C : BOOL; (* 실러[ RB]TEACH   MODE *)
    X103E : BOOL; (* 실러[ RB]MOTOR   POWER ON *)
    X103B : BOOL; (* 실러[ RB]ERROR *)
    M712 : BOOL; (* 실러 로보트[HMI]         PASS PB *)
    T71 : TON; (* 실러[ RB]ROBOT   START   DELAY *)
    T72 : TON; (* 실러[ RB]ROBOT   START   OFF *)
    Y1030 : BOOL; (* 실러[ RB]external_cycle   start *)
    Y1032 : BOOL; (* 실러[ RB]RPS ON  (Q206.2) *)
    Y1035 : BOOL; (* 실러[ RB]MOTOR ON *)
    X1117 : BOOL; (* 현대 로봇 비상정지    PRIMER] *)
    X1036 : BOOL; (* 실러 로보트 비상정지[ RB] *)
    Y1033 : BOOL; (* 가와실러[ ]external hold *)
    M212 : BOOL; (* 이상해제 *)
    Y1034 : BOOL; (* 실러[ RB]external hold   RESET *)
    Y1031 : BOOL; (* 실러[ RB]external error  reset *)
    X1000 : BOOL; (* 실러 센터링 간섭무[ RB] *)
    M1554 : BOOL; (* 실러 간섭무    ROBOT *)
    M2003 : BOOL; (* 센터링 이컬라이져 전진단 *)
    M2001 : BOOL; (* 센터링 가압 전진단 *)
    X1007 : BOOL; (* 실러 센터링 언클램프요구[ RB] *)
    M1421 : BOOL; (* 센터링 언클램프 요구      (M1422.1 *)
    Y1000 : BOOL; (* 실러 센터링 진입가능[ RB] *)
    Y100A : BOOL; (* 실러 실러비젼[ RB]  NG *)
    Y100C : BOOL; (* 실러 바디비젼[ RB] NG *)
    M2000 : BOOL; (* 센터링 가압 후진단 *)
    M2002 : BOOL; (* 센터링 이컬라이져 후진단 *)
    Y1001 : BOOL; (* 실러 바디 진입[ RB]  OK *)
    Y48 : BOOL; (* 실링 카트리지정회전 토출      [ ] *)
    Y4C : BOOL; (* 컨트롤러속도선택DM300   1 *)
    X111F : BOOL; (* 현대    PRIMER] HOME *)
    M710 : BOOL; (* 프라이머로보트[HMI]     PASS PB *)
    X1A : BOOL; (* 실링 카트리지후진단 *)
    M999 : BOOL;
    Y1002 : BOOL; (* 실러 실러 진입[ RB]  OK *)
    M3000 : BOOL; (* 그리퍼 진공흡착확인 *)
    Y1003 : BOOL; (* 실러 진공흡착확인[ RB]  OK *)
    M3001 : BOOL; (* 그리퍼 진공탈착확인 *)
    Y1004 : BOOL; (* 실러 진공탈착확인[ RB]  OK *)
    Y1005 : BOOL; (* 실러 센터링 언클램프[ RB]   OK *)
    X1102 : BOOL; (* 현대 실러 상호인터록    PRIMER] RB *)
    Y1018 : BOOL; (* 실러 프라이머로봇 상호인터록[ RB] *)
    SM400 : BOOL; (* 항상on *)
    M5000 : BOOL; (* 실러비전OK *)
    M5001 : BOOL; (* 실러비전NG *)
    Y1009 : BOOL; (* 실러 실러비젼[ RB] OK *)
    M6000 : BOOL; (* 바디비전OK *)
    M6001 : BOOL; (* 바디비전NG *)
    Y100B : BOOL; (* 실러 바디비전[ RB] OK *)
    M6100 : BOOL; (* Gap Complete *)
    Y100D : BOOL; (* 실러[ RB]GAP COMP *)
    M181 : BOOL; (* PC      Change  Complete *)
    T700 : TON;
    Y100F : BOOL;
    M702 : BOOL; (* 실러 로보트 선택      _HMIPB *)
    M700 : BOOL; (* 프라이머로보트 선택  _HMIPB *)
    M701 : BOOL; (* 비젼 로보트 선택      _HMIPB *)
    M620 : BOOL; (* 실러 차종선택    1 HMI *)
    M621 : BOOL; (* 실러 차종선택   2 HMI *)
    M622 : BOOL; (* 실러 차종선택   4 *)
    D620 : WORD; (* 실러 차종입력 *)
    D720 : WORD; (* 실러차종 *)
    X103D_PLS : BOOL; (* 실러[ RB]HOME    POSITION *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 | HOME --- *)
IF (X103D) AND (T70) THEN
    M1553 := TRUE;
ELSE
    M1553 := FALSE;
END_IF;
IF X103D THEN
    T70(IN := TRUE, PT := T#1s);
ELSE
    T70(IN := FALSE);
END_IF;

(* --- Rung 2, step 13 | START --- *)
IF ((K0 <> K0)) AND (M1556) AND (M2005) AND (M1522) AND (NOT (M50)) AND (M7750) THEN
    M1552 := TRUE;
ELSE
    M1552 := FALSE;
END_IF;

(* --- Rung 3, step 27 --- *)
IF (X7) AND (NOT (X103D)) THEN
    M1555 := TRUE;
ELSE
    M1555 := FALSE;
END_IF;

(* --- Rung 4, step 30 --- *)
IF (M215) AND (((M1552) AND (T70)) OR ((M1555) AND (NOT (T70)))) AND (NOT (X103C)) AND (X103E) AND (NOT (X103B)) AND (NOT (M712)) AND (T71) AND (NOT (T72)) AND (NOT (M712)) THEN
    Y1030 := TRUE;
ELSE
    Y1030 := FALSE;
END_IF;
IF (M215) AND (((M1552) AND (T70)) OR ((M1555) AND (NOT (T70)))) AND (NOT (X103C)) AND (X103E) AND (NOT (X103B)) AND (NOT (M712)) AND (T71) AND (NOT (T72)) AND (NOT (M712)) THEN
    Y1032 := TRUE;
ELSE
    Y1032 := FALSE;
END_IF;
IF (M215) AND (((M1552) AND (T70)) OR ((M1555) AND (NOT (T70)))) AND (NOT (X103C)) AND (X103E) AND (NOT (X103B)) AND (NOT (M712)) THEN
    T71(IN := TRUE, PT := T#500ms);
ELSE
    T71(IN := FALSE);
END_IF;
IF (M215) AND (((M1552) AND (T70)) OR ((M1555) AND (NOT (T70)))) AND (NOT (X103C)) AND (X103E) AND (NOT (X103B)) AND (NOT (M712)) THEN
    T72(IN := TRUE, PT := T#2s);
ELSE
    T72(IN := FALSE);
END_IF;

(* --- Rung 5, step 56 --- *)
IF (M215) AND (NOT (X103E)) THEN
    Y1035 := TRUE;
ELSE
    Y1035 := FALSE;
END_IF;

(* --- Rung 6, step 59 --- *)
IF (M215) AND (NOT (X1117)) AND (NOT (X1036)) THEN
    Y1033 := TRUE;
ELSE
    Y1033 := FALSE;
END_IF;

(* --- Rung 7, step 63 --- *)
IF (M212) OR (Y1030) THEN
    Y1034 := TRUE;
ELSE
    Y1034 := FALSE;
END_IF;

(* --- Rung 8, step 66 --- *)
IF M212 THEN
    Y1031 := TRUE;
ELSE
    Y1031 := FALSE;
END_IF;

(* --- Rung 9, step 68 | INPUT --- *)
IF X1000 THEN
    M1554 := TRUE;
ELSE
    M1554 := FALSE;
END_IF;

(* --- Rung 10, step 75 --- *)
IF (M215) AND ((M2003) OR (M2001)) AND (X1007) THEN
    M1421 := TRUE;
ELSE
    M1421 := FALSE;
END_IF;

(* --- Rung 11, step 81 | OUTPUT --- *)
IF (M215) AND (M1522) AND (M2005) THEN
    M1556 := TRUE;
ELSE
    M1556 := FALSE;
END_IF;

(* --- Rung 12, step 90 --- *)
IF M1556 THEN
    Y1000 := TRUE;
ELSE
    Y1000 := FALSE;
END_IF;

(* --- Rung 13, step 92 --- *)
IF ((Y100A) OR (Y100C)) AND (NOT (M2005)) AND (M2000) AND (M2002) THEN
    Y1001 := TRUE;
ELSE
    Y1001 := FALSE;
END_IF;

(* --- Rung 14, step 98 --- *)
IF (NOT (Y48)) AND (NOT (Y4C)) AND ((X111F) OR (M710)) AND ((X1A) OR (M999)) THEN
    Y1002 := TRUE;
ELSE
    Y1002 := FALSE;
END_IF;

(* --- Rung 15, step 107 --- *)
IF M3000 THEN
    Y1003 := TRUE;
ELSE
    Y1003 := FALSE;
END_IF;

(* --- Rung 16, step 109 --- *)
IF M3001 THEN
    Y1004 := TRUE;
ELSE
    Y1004 := FALSE;
END_IF;

(* --- Rung 17, step 111 --- *)
IF (M2000) AND (M2002) THEN
    Y1005 := TRUE;
ELSE
    Y1005 := FALSE;
END_IF;

(* --- Rung 18, step 114 --- *)
IF (X1102) OR ((M710) AND (M999)) THEN
    Y1018 := TRUE;
ELSE
    Y1018 := FALSE;
END_IF;

(* --- Rung 19, step 119 --- *)
IF (SM400) AND (M5000) AND (NOT (M5001)) THEN
    Y1009 := TRUE;
ELSE
    Y1009 := FALSE;
END_IF;
IF (SM400) AND (NOT (M5000)) AND (M5001) THEN
    Y100A := TRUE;
ELSE
    Y100A := FALSE;
END_IF;

(* --- Rung 20, step 128 --- *)
IF (SM400) AND (M6000) AND (NOT (M6001)) THEN
    Y100B := TRUE;
ELSE
    Y100B := FALSE;
END_IF;
IF (SM400) AND (NOT (M6000)) AND (M6001) THEN
    Y100C := TRUE;
ELSE
    Y100C := FALSE;
END_IF;

(* --- Rung 21, step 137 --- *)
IF M6100 THEN
    Y100D := TRUE;
ELSE
    Y100D := FALSE;
END_IF;

(* --- Rung 22, step 139 --- *)
IF (M181) AND (T700) THEN
    Y100F := TRUE;
ELSE
    Y100F := FALSE;
END_IF;
IF M181 THEN
    T700(IN := TRUE, PT := T#1s);
ELSE
    T700(IN := FALSE);
END_IF;

(* --- Rung 23, step 148 | Car Type --- *)
IF (SM400) AND (M702) AND (NOT (M700)) AND (NOT (M701)) AND (M620) THEN
    D720 := K1;
END_IF;
IF (SM400) AND (M702) AND (NOT (M700)) AND (NOT (M701)) AND (M621) THEN
    D720 := K2;
END_IF;
IF (SM400) AND (M702) AND (NOT (M700)) AND (NOT (M701)) AND (M622) THEN
    D720 := K3;
END_IF;
IF (SM400) AND (M702) AND (NOT (M700)) AND (NOT (M701)) THEN
    D720 := D620;
END_IF;
IF (SM400) AND (M702) AND (NOT (M700)) AND (NOT (M701)) THEN
    K1Y1038 := D720;
END_IF;

(* --- Rung 24, step 176 --- *)
IF X103D_PLS THEN
    D720 := K0;
END_IF;
IF X103D_PLS THEN
    D620 := K0;
END_IF;

