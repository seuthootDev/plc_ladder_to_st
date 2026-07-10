(* Generated ST from context: P31_Sealer *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P31_Sealer' *)
(* ============================================================ *)

PROGRAM P31_Sealer
VAR
    SM400 : BOOL; (* 항상on *)
    X1A : BOOL; (* 실링 카트리지후진단 *)
    M2500 : BOOL; (* 실링 카트리지후진단 원점      [ ] *)
    X1B : BOOL; (* 실링 카트리지전진단 *)
    M2501 : BOOL; (* 실링 카트리지전진단 *)
    M2520 : BOOL; (* 실링 카트리지원점위치 *)
    M202 : BOOL; (* 제어반 운전준비완료 *)
    M2521 : BOOL; (* 실링 카트리지운전준비완료 *)
    M211 : BOOL; (* 운전모드 자동[ ] *)
    X1039 : BOOL; (* 실러[ RB]CYCLE   START *)
    M999 : BOOL;
    X1004 : BOOL; (* 실러 실러 토출[ RB]  ON *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M522 : BOOL; (* 실링카트리지정회전[HMI] *)
    M523 : BOOL; (* 실링카트리지역회전[HMI] *)
    M521 : BOOL; (* 실러토출미사용[HMI]   PB *)
    Y49 : BOOL; (* 실링 카트리지역회전 원점      [ ] *)
    Y48 : BOOL; (* 실링 카트리지정회전 토출      [ ] *)
    M2527 : BOOL; (* 실링 카트리지원점복귀보조 *)
    M526 : BOOL; (* 실링 카트리지 원점복귀[HMI]    PB *)
    Y2B : BOOL; (* 실링 카트리지모터 브레이크 *)
    Y4C : BOOL; (* 컨트롤러속도선택DM300   1 *)
    Y4A : BOOL; (* 실링 모터 알람해제속도선택  2 *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 --- *)
IF (SM400) AND (X1A) THEN
    M2500 := TRUE;
ELSE
    M2500 := FALSE;
END_IF;
IF (SM400) AND (X1B) THEN
    M2501 := TRUE;
ELSE
    M2501 := FALSE;
END_IF;

(* --- Rung 2, step 7 --- *)
IF (X1A) AND (NOT (X1B)) THEN
    M2520 := TRUE;
ELSE
    M2520 := FALSE;
END_IF;

(* --- Rung 3, step 10 --- *)
IF M202 THEN
    M2521 := TRUE;
ELSE
    M2521 := FALSE;
END_IF;

(* --- Rung 4, step 12 --- *)
IF (M2521) AND (((M211) AND ((X1039) OR (M999)) AND (X1004)) OR ((M210) AND ((M522) OR (X1004)) AND (NOT (M523)))) AND (NOT (M521)) AND (NOT (X1B)) AND (NOT (Y49)) THEN
    Y48 := TRUE;
ELSE
    Y48 := FALSE;
END_IF;

(* --- Rung 5, step 29 --- *)
IF (M2521) AND (((M211) AND (((X1B) AND (NOT (X1004))) OR (Y49))) OR ((M210) AND ((M523) OR (M2527)) AND (NOT (M522)))) AND ((NOT (M521)) OR (M999)) AND (NOT (X1A)) AND (NOT (Y48)) THEN
    Y49 := TRUE;
ELSE
    Y49 := FALSE;
END_IF;

(* --- Rung 6, step 48 --- *)
IF (M2521) AND (M210) AND ((M526) OR (M2527)) AND (NOT (X1A)) THEN
    M2527 := TRUE;
ELSE
    M2527 := FALSE;
END_IF;

(* --- Rung 7, step 55 --- *)
IF NOT ((NOT (Y48)) AND (NOT (Y49))) THEN
    Y2B := TRUE;
ELSE
    Y2B := FALSE;
END_IF;

(* --- Rung 8, step 59 --- *)
IF Y48 THEN
    Y4C := TRUE;
ELSE
    Y4C := FALSE;
END_IF;

(* --- Rung 9, step 61 --- *)
IF Y49 THEN
    Y4A := TRUE;
ELSE
    Y4A := FALSE;
END_IF;

