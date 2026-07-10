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