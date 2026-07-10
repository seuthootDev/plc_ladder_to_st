PROGRAM P10_PrimerVision
VAR
    SM401 : BOOL; (* 항상off *)
    D100 : WORD; (* 프라이머비전 → PLC *)
    T210 : TON; (* 프라이머비전 라이브 비트지연 *)
    SM400 : BOOL; (* 항상on *)
    T200 : TON; (* 프라이머비전 통신이상 *)
    SM412 : BOOL; (* 초 클럭1 *)
    D110 : WORD; (* 프라이머비전PLC → *)
    X1104 : BOOL; (* 현대 비전 스타트    PRIMER] *)
    M720 : BOOL;
    D110_0 : BOOL; (* 프라이머비전PLC → *)
    D110_1 : BOOL; (* 프라이머비전PLC → *)
    X1105 : BOOL; (* 현대 비전    PRIMER]  OFF *)
    M721 : BOOL;
    D110_2 : BOOL; (* 프라이머비전PLC → *)
    M1321 : BOOL; (* 프라이머로보트 작업완료 *)
    M722 : BOOL;
    M210 : BOOL; (* 운전모드 수동[ ] *)
    M171 : BOOL; (* 프라이머작업완료[HMI]   RST PB *)
    X111F : BOOL; (* 현대    PRIMER] HOME *)
    M723 : BOOL;
    X1106 : BOOL; (* 현대 포지션    PRIMER] _1 *)
    D110_8 : BOOL; (* 프라이머비전PLC → *)
    X1107 : BOOL; (* 현대 포지션    PRIMER] _2 *)
    D110_9 : BOOL; (* 프라이머비전PLC → *)
    X1108 : BOOL; (* 현대 포지션    PRIMER] _4 *)
    X1109 : BOOL; (* 현대 포지션    PRIMER] _8 *)
    D100_0 : BOOL; (* 프라이머비전 → PLC *)
    M7000 : BOOL; (* 프라이머OK *)
    D100_1 : BOOL; (* 프라이머비전 → PLC *)
    M7001 : BOOL; (* 프라이머NG *)
END_VAR