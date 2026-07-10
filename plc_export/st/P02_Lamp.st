(* Generated ST from context: P02_Lamp *)
(* Project: plc project_260626 *)
(* CPU: QCPU (Q mode) Q06H *)

(* ============================================================ *)
(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)
(*          POU 이름과 PROGRAM 이름이 같아야 함: 'P02_Lamp' *)
(* ============================================================ *)

PROGRAM P02_Lamp
VAR
    M202 : BOOL; (* 제어반 운전준비완료 *)
    SM412 : BOOL; (* 초 클럭1 *)
    M503 : BOOL; (* 램프 테스트[HMI]       PB *)
    Y20 : BOOL; (* 운전준비ON PBL  LAMP *)
    M57 : BOOL; (* 설비 종합이상 *)
    Y3C : BOOL; (* 제어반 타워램프 적색  [ ] *)
    M210 : BOOL; (* 운전모드 수동[ ] *)
    Y3D : BOOL; (* 제어반 타워램프 황색  [ ] *)
    M211 : BOOL; (* 운전모드 자동[ ] *)
    M215 : BOOL; (* 가와실러자동기동 *)
    M216 : BOOL; (* 현대 프라이머자동기동 *)
    Y3E : BOOL; (* 제어반 타워램프 녹색  [ ] *)
    M220 : BOOL; (* 부져정지 SET *)
    Y3F : BOOL; (* 제어반 타워램프 부져  [ ] *)
END_VAR

(* ============================================================ *)
(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)
(*          VAR 블록은 여기 넣으면 안 됨 *)
(* ============================================================ *)

(* --- Rung 1, step 0 --- *)
IF (M202) OR ((NOT (M202)) AND (SM412)) OR (M503) THEN
    Y20 := TRUE;
ELSE
    Y20 := FALSE;
END_IF;

(* --- Rung 2, step 6 --- *)
IF ((M57) AND (SM412)) OR (M503) THEN
    Y3C := TRUE;
ELSE
    Y3C := FALSE;
END_IF;

(* --- Rung 3, step 10 --- *)
IF ((M202) AND (M210)) OR (M503) THEN
    Y3D := TRUE;
ELSE
    Y3D := FALSE;
END_IF;

(* --- Rung 4, step 14 --- *)
IF ((M202) AND (((M211) AND (SM412)) OR ((M215) AND (M216)))) OR (M503) THEN
    Y3E := TRUE;
ELSE
    Y3E := FALSE;
END_IF;

(* --- Rung 5, step 23 --- *)
IF ((NOT (NOT (M57))) AND (NOT (M220))) OR (M503) THEN
    Y3F := TRUE;
ELSE
    Y3F := FALSE;
END_IF;

