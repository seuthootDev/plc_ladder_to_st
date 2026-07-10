PROGRAM P12_BodyVision
VAR
    X1011 : BOOL; (* 실러[ RB]BODY START *)
    D310_0 : BOOL;
    D310_1 : BOOL;
    X1012 : BOOL; (* 실러[ RB]GAP START *)
    D310_7 : BOOL;
    M60 : BOOL; (* 실러 로보트 작업완료 *)
    D310 : WORD;
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M175 : BOOL; (* 실러작업완료[HMI] RST PB *)
    M174 : BOOL; (* 실러작업완료[HMI] SET PB *)
    D300_0 : BOOL;
    M6000 : BOOL; (* 바디비전OK *)
    D300_1 : BOOL;
    M6001 : BOOL; (* 바디비전NG *)
    D300_2 : BOOL;
    D300_3 : BOOL;
    M6100 : BOOL; (* Gap Complete *)
END_VAR