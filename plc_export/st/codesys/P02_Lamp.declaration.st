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