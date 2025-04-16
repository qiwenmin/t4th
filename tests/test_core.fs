\ 从 https://forth-standard.org/standard/testsuite 复制的测试用例

\ F.3 Core Tests

BASE @

HEX

\ F.3.1 Basic Assumptions

T{ -> }T                      ( Start with a clean slate )
( Test if any bits are set; Answer in base 1 )
T{ : BITSSET? IF 0 0 ELSE 0 THEN ; -> }T
T{  0 BITSSET? -> 0 }T        ( Zero is all bits clear )
T{  1 BITSSET? -> 0 0 }T      ( Other numbers have at least one bit )
T{ -1 BITSSET? -> 0 0 }T

\ F.3.2 Booleans

0 constant 0S
0S invert constant 1S

\ F.3.3 Shifts

1S 1 RSHIFT INVERT CONSTANT MSB
T{ MSB BITSSET? -> 0 0 }T

\ F.3.4 Numeric notation

DECIMAL
T{ #1289       -> 1289        }T
T{ #12346789.  -> 12346789.   }T
T{ #-1289      -> -1289       }T
T{ #-12346789. -> -12346789.  }T
T{ $12eF       -> 4847        }T
T{ $12aBcDeF.  -> 313249263.  }T
T{ $-12eF      -> -4847       }T
T{ $-12AbCdEf. -> -313249263. }T
T{ %10010110   -> 150         }T
T{ %10010110.  -> 150.        }T
T{ %-10010110  -> -150        }T
T{ %-10010110. -> -150.       }T
T{ 'z'         -> 122         }T
HEX

\ F.3.5 Comparisons

0 INVERT CONSTANT MAX-UINT
0 INVERT 1 RSHIFT CONSTANT MAX-INT
0 INVERT 1 RSHIFT INVERT CONSTANT MIN-INT
0 INVERT 1 RSHIFT CONSTANT MID-UINT
0 INVERT 1 RSHIFT INVERT CONSTANT MID-UINT+1

0S CONSTANT <FALSE>
1S CONSTANT <TRUE>

\ F.3.6 Stack Operators

\ F.3.7 Return Stack Operators

\ F.3.8 Addition and Subtraction

\ F.3.9 Multiplication

\ F.3.10 Division

: IFFLOORED [ -3 2 / -2 = INVERT ] LITERAL IF POSTPONE \ THEN ;
: IFSYM      [ -3 2 / -1 = INVERT ] LITERAL IF POSTPONE \ THEN ;

\ F.3.11 Memory

\ F.3.12 Characters

\ F.3.13 Dictionary

\ F.3.14 Flow Control

\ F.3.15 Counted Loops

\ F.3.15 Counted Loops

\ F.3.17 Evaluate

\ F.3.18 Parser Input Source Control

\ F.3.19 Number Patterns

: S= \ ( ADDR1 C1 ADDR2 C2 -- T/F ) Compare two strings.
   >R SWAP R@ = IF            \ Make sure strings have same length
     R> ?DUP IF               \ If non-empty strings
       0 DO
         OVER C@ OVER C@ - IF 2DROP <FALSE> UNLOOP EXIT THEN
         SWAP CHAR+ SWAP CHAR+
       LOOP
     THEN
     2DROP <TRUE>            \ If we get here, strings match
   ELSE
     R> DROP 2DROP <FALSE> \ Lengths mismatch
   THEN ;

24 CONSTANT MAX-BASE                  \ BASE 2 ... 36

: COUNT-BITS
   0 0 INVERT BEGIN DUP WHILE >R 1+ R> 2* REPEAT DROP ;
COUNT-BITS 2* CONSTANT #BITS-UD    \ NUMBER OF BITS IN UD

\ F.3.20 Memory Movement

CREATE FBUF 00 C, 00 C, 00 C,
CREATE SBUF 12 C, 34 C, 56 C,
: SEEBUF FBUF C@ FBUF CHAR+ C@ FBUF CHAR+ CHAR+ C@ ;

\ F.3.21 Output

\ F.3.22 Input

\ F.3.23 Dictionary Search Rules

T{ : GDX     123 ; -> }T    \ First defintion
T{ : GDX GDX 234 ; -> }T    \ Second defintion
T{ GDX -> 123 234 }T


\ F.6 The Core word set

\ F.6.1.0010 !

\ F.6.1.0030 #

: GP3 <# 1 0 # # #> S" 01" S= ;
T{ GP3 -> <TRUE> }T

\ F.6.1.0040 #>

\ F.6.1.0050 #S

: GP4 <# 1 0 #S #> S" 1" S= ;
T{ GP4 -> <TRUE> }T
: GP5
   BASE @ <TRUE>
   MAX-BASE 1+ 2 DO      \ FOR EACH POSSIBLE BASE
     I BASE !              \ TBD: ASSUMES BASE WORKS
       I 0 <# #S #> S" 10" S= AND
   LOOP
   SWAP BASE ! ;
T{ GP5 -> <TRUE> }T

: GP6
   BASE @ >R 2 BASE !
   MAX-UINT MAX-UINT <# #S #>    \ MAXIMUM UD TO BINARY
   R> BASE !                        \ S: C-ADDR U
   DUP #BITS-UD = SWAP
   0 DO                              \ S: C-ADDR FLAG
     OVER C@ [CHAR] 1 = AND     \ ALL ONES
     >R CHAR+ R>
   LOOP SWAP DROP ;
T{ GP6 cr -> <TRUE> }T

: GP7
   BASE @ >R MAX-BASE BASE !
   <TRUE>
   A 0 DO
     I 0 <# #S #>
     1 = SWAP C@ I 30 + = AND AND
   LOOP
   MAX-BASE A DO
     I 0 <# #S #>
     1 = SWAP C@ 41 I A - + = AND AND
   LOOP
   R> BASE ! ;
T{ GP7 -> <TRUE> }T

\ F.6.1.0070 '

T{ : GT1 123 ;   ->     }T
T{ ' GT1 EXECUTE -> 123 }T

\ F.6.1.0080 (

\ There is no space either side of the ).
T{ ( A comment)1234 -> 1234 }T
T{ : pc1 ( A comment)1234 ; pc1 -> 1234 }T

\ F.6.1.0090 *

T{  0  0 * ->  0 }T          \ TEST IDENTITIE\S
T{  0  1 * ->  0 }T
T{  1  0 * ->  0 }T
T{  1  2 * ->  2 }T
T{  2  1 * ->  2 }T
T{  3  3 * ->  9 }T
T{ -3  3 * -> -9 }T
T{  3 -3 * -> -9 }T
T{ -3 -3 * ->  9 }T
T{ MID-UINT+1 1 RSHIFT 2 *               -> MID-UINT+1 }T
T{ MID-UINT+1 2 RSHIFT 4 *               -> MID-UINT+1 }T
T{ MID-UINT+1 1 RSHIFT MID-UINT+1 OR 2 * -> MID-UINT+1 }T

\ TODO: F.6.1.0110 */MOD

\ TODO: F.6.1.0100 */

\ F.6.1.0120 +

T{        0  5 + ->          5 }T
T{        5  0 + ->          5 }T
T{        0 -5 + ->         -5 }T
T{       -5  0 + ->         -5 }T
T{        1  2 + ->          3 }T
T{        1 -2 + ->         -1 }T
T{       -1  2 + ->          1 }T
T{       -1 -2 + ->         -3 }T
T{       -1  1 + ->          0 }T
T{ MID-UINT  1 + -> MID-UINT+1 }T

\ F.6.1.0150 ,

HERE 1 ,
HERE 2 ,
CONSTANT 2ND
CONSTANT 1ST
T{       1ST 2ND U< -> <TRUE> }T \ HERE MUST GROW WITH ALLOT
T{       1ST CELL+  -> 2ND }T \ ... BY ONE CELL
T{   1ST 1 CELLS +  -> 2ND }T
T{     1ST @ 2ND @  -> 1 2 }T
T{         5 1ST !  ->     }T
T{     1ST @ 2ND @  -> 5 2 }T
T{         6 2ND !  ->     }T
T{     1ST @ 2ND @  -> 5 6 }T
T{           1ST 2@ -> 6 5 }T
T{       2 1 1ST 2! ->     }T
T{           1ST 2@ -> 2 1 }T
T{ 1S 1ST !  1ST @  -> 1S  }T    \ CAN STORE CELL-WIDE VALUE

\ F.6.1.0130 +!

T{  0 1ST !        ->   }T
T{  1 1ST +!       ->   }T
T{    1ST @        -> 1 }T
T{ -1 1ST +! 1ST @ -> 0 }T

\ TODO: F.6.1.0140 +LOOP

\ F.6.1.0160 -

T{          0  5 - ->       -5 }T
T{          5  0 - ->        5 }T
T{          0 -5 - ->        5 }T
T{         -5  0 - ->       -5 }T
T{          1  2 - ->       -1 }T
T{          1 -2 - ->        3 }T
T{         -1  2 - ->       -3 }T
T{         -1 -2 - ->        1 }T
T{          0  1 - ->       -1 }T
T{ MID-UINT+1  1 - -> MID-UINT }T

\ F.6.1.0180 .

\ F.6.1.0190 ."

T{ : pb1 CR ." You should see 2345: "." 2345"; pb1 -> }T

\ TODO: F.6.1.0230 /

\ TODO: F.6.1.0240 /MOD

\ F.6.1.02500 <

T{       0 0< -> <FALSE> }T
T{      -1 0< -> <TRUE>  }T
T{ MIN-INT 0< -> <TRUE>  }T
T{       1 0< -> <FALSE> }T
T{ MAX-INT 0< -> <FALSE> }T

\ F.6.1.0270 0=

T{        0 0= -> <TRUE>  }T
T{        1 0= -> <FALSE> }T
T{        2 0= -> <FALSE> }T
T{       -1 0= -> <FALSE> }T
T{ MAX-UINT 0= -> <FALSE> }T
T{ MIN-INT  0= -> <FALSE> }T
T{ MAX-INT  0= -> <FALSE> }T

\ F.6.1.0290 1+

T{        0 1+ ->          1 }T
T{       -1 1+ ->          0 }T
T{        1 1+ ->          2 }T
T{ MID-UINT 1+ -> MID-UINT+1 }T

\ F.6.1.0300 1-

T{          2 1- ->        1 }T
T{          1 1- ->        0 }T
T{          0 1- ->       -1 }T
T{ MID-UINT+1 1- -> MID-UINT }T

\ F.6.1.0310 2!

\ F.6.1.0320 2*

T{   0S 2*       ->   0S }T
T{    1 2*       ->    2 }T
T{ 4000 2*       -> 8000 }T
T{   1S 2* 1 XOR ->   1S }T
T{  MSB 2*       ->   0S }T

\ F.6.1.0330 2/

T{          0S 2/ ->   0S }T
T{           1 2/ ->    0 }T
T{        4000 2/ -> 2000 }T
T{          1S 2/ ->   1S }T \ MSB PROPOGATED
T{    1S 1 XOR 2/ ->   1S }T
T{ MSB 2/ MSB AND ->  MSB }T

\ F.6.1.0350 2@

\ F.6.1.0370 2DROP

T{ 1 2 2DROP -> }T

\ F.6.1.0380 2DUP

T{ 1 2 2DUP -> 1 2 1 2 }T

\ F.6.1.0400 2OVER

T{ 1 2 3 4 2OVER -> 1 2 3 4 1 2 }T

\ F.6.1.0430 2SWAP

T{ 1 2 3 4 2SWAP -> 3 4 1 2 }T

\ F.6.1.0450 :

T{ : NOP : POSTPONE ; ; -> }T
T{ NOP NOP1 NOP NOP2 -> }T
T{ NOP1 -> }T
T{ NOP2 -> }T

T{ : GDX   123 ;    : GDX   GDX 234 ; -> }T
T{ GDX -> 123 234 }T

\ F.6.1.0460 ;

\ F.6.1.0480 <

T{       0       1 < -> <TRUE>  }T
T{       1       2 < -> <TRUE>  }T
T{      -1       0 < -> <TRUE>  }T
T{      -1       1 < -> <TRUE>  }T
T{ MIN-INT       0 < -> <TRUE>  }T
T{ MIN-INT MAX-INT < -> <TRUE>  }T
T{       0 MAX-INT < -> <TRUE>  }T
T{       0       0 < -> <FALSE> }T
T{       1       1 < -> <FALSE> }T
T{       1       0 < -> <FALSE> }T
T{       2       1 < -> <FALSE> }T
T{       0      -1 < -> <FALSE> }T
T{       1      -1 < -> <FALSE> }T
T{       0 MIN-INT < -> <FALSE> }T
T{ MAX-INT MIN-INT < -> <FALSE> }T
T{ MAX-INT       0 < -> <FALSE> }T

\ F.6.1.0490 <#

\ F.6.1.0530 =

T{  0  0 = -> <TRUE>  }T
T{  1  1 = -> <TRUE>  }T
T{ -1 -1 = -> <TRUE>  }T
T{  1  0 = -> <FALSE> }T
T{ -1  0 = -> <FALSE> }T
T{  0  1 = -> <FALSE> }T
T{  0 -1 = -> <FALSE> }T

\ F.6.1.0540 >

T{       0       1 > -> <FALSE> }T
T{       1       2 > -> <FALSE> }T
T{      -1       0 > -> <FALSE> }T
T{      -1       1 > -> <FALSE> }T
T{ MIN-INT       0 > -> <FALSE> }T
T{ MIN-INT MAX-INT > -> <FALSE> }T
T{       0 MAX-INT > -> <FALSE> }T
T{       0       0 > -> <FALSE> }T
T{       1       1 > -> <FALSE> }T
T{       1       0 > -> <TRUE>  }T
T{       2       1 > -> <TRUE>  }T
T{       0      -1 > -> <TRUE>  }T
T{       1      -1 > -> <TRUE>  }T
T{       0 MIN-INT > -> <TRUE>  }T
T{ MAX-INT MIN-INT > -> <TRUE>  }T
T{ MAX-INT       0 > -> <TRUE>  }T

\ F.6.1.0550 >BODY

T{  CREATE CR0 ->      }T
T{ ' CR0 >BODY -> HERE }T

\ TODO: F.6.1.0560 >IN

\ TODO: F.6.1.0570 >NUMBER

\ F.6.1.0580 >R

T{ : GR1 >R R> ; -> }T
T{ : GR2 >R R@ R> DROP ; -> }T
T{ 123 GR1 -> 123 }T
T{ 123 GR2 -> 123 }T
T{  1S GR1 ->  1S }T      ( Return stack holds cells )

\ F.6.1.0630 ?DUP

T{ -1 ?DUP -> -1 -1 }T
T{  0 ?DUP ->  0    }T
T{  1 ?DUP ->  1  1 }T

\ F.6.1.0650 @

\ TODO: F.6.1.0690 ABS

\ TODO: F.6.1.0695 ACCEPT

\ TODO: F.6.1.0705 ALIGN

\ F.6.1.0710 ALLOT

HERE 1 ALLOT
HERE
CONSTANT 2NDA
CONSTANT 1STA
T{ 1STA 2NDA U< -> <TRUE> }T    \ HERE MUST GROW WITH ALLOT
T{      1STA 1+ ->   2NDA }T    \ ... BY ONE ADDRESS UNIT
( MISSING TEST: NEGATIVE ALLOT )

\ F.6.1.0720 AND

T{ 0 0 AND -> 0 }T
T{ 0 1 AND -> 0 }T
T{ 1 0 AND -> 0 }T
T{ 1 1 AND -> 1 }T
T{ 0 INVERT 1 AND -> 1 }T
T{ 1 INVERT 1 AND -> 0 }T

T{ 0S 0S AND -> 0S }T
T{ 0S 1S AND -> 0S }T
T{ 1S 0S AND -> 0S }T
T{ 1S 1S AND -> 1S }T

\ F.6.1.0750 BASE

: GN2 \ ( -- 16 10 )
   BASE @ >R HEX BASE @ DECIMAL BASE @ R> BASE ! ;
T{ GN2 -> 10 A }T

\ F.6.1.0760 BEGIN

\ F.6.1.0770 BL

T{ BL -> 20 }T

\ F.6.1.0850 C!

\ F.6.1.0860 C,

HERE 1 C,
HERE 2 C,
CONSTANT 2NDC
CONSTANT 1STC
T{    1STC 2NDC U< -> <TRUE> }T \ HERE MUST GROW WITH ALLOT
T{      1STC CHAR+ ->  2NDC  }T \ ... BY ONE CHAR
T{  1STC 1 CHARS + ->  2NDC  }T
T{ 1STC C@ 2NDC C@ ->   1 2  }T
T{       3 1STC C! ->        }T
T{ 1STC C@ 2NDC C@ ->   3 2  }T
T{       4 2NDC C! ->        }T
T{ 1STC C@ 2NDC C@ ->   3 4  }T

\ F.6.1.0870 C@

\ F.6.1.0880 CELL+

\ F.6.1.0890 CELLS

: BITS ( X -- U )
   0 SWAP BEGIN DUP WHILE
     DUP MSB AND IF >R 1+ R> THEN 2*
   REPEAT DROP ;
( CELLS >= 1 AU, INTEGRAL MULTIPLE OF CHAR SIZE, >= 16 BITS )
T{ 1 CELLS 1 <         -> <FALSE> }T
T{ 1 CELLS 1 CHARS MOD ->    0    }T
T{ 1S BITS 10 <        -> <FALSE> }T

\ F.6.1.0895 CHAR

T{ CHAR X     -> 58 }T
T{ CHAR HELLO -> 48 }T

\ F.6.1.0897 CHAR+

\ F.6.1.0898 CHARS

( CHARACTERS >= 1 AU, <= SIZE OF CELL, >= 8 BITS )
T{ 1 CHARS 1 <       -> <FALSE> }T
T{ 1 CHARS 1 CELLS > -> <FALSE> }T
( TBD: HOW TO FIND NUMBER OF BITS? )

\ F.6.1.0950 CONSTANT

T{ 123 CONSTANT X123 -> }T
T{ X123 -> 123 }T
T{ : EQU CONSTANT ; -> }T
T{ X123 EQU Y123 -> }T
T{ Y123 -> 123 }T

\ F.6.1.1550 FIND

HERE 3 C, CHAR G C, CHAR T C, CHAR 1 C, CONSTANT GT1STRING
HERE 3 C, CHAR G C, CHAR T C, CHAR 2 C, CONSTANT GT2STRING
\ TODO: T{ GT1STRING FIND -> ' GT1 -1 }T
\ TODO: T{ GT2STRING FIND -> ' GT2 1  }T
( HOW TO SEARCH FOR NON-EXISTENT WORD? )

\ F.6.1.0980 COUNT

T{ GT1STRING COUNT -> GT1STRING CHAR+ 3 }T

\ F.6.1.0990 CR

\ F.6.1.1000 CREATE

\ F.6.1.1170 DECIMAL

\ F.6.1.1200 DEPTH

base !

T{ 0 1 DEPTH -> 0 1 2 }T
T{   0 DEPTH -> 0 1   }T
T{     DEPTH -> 0     }T

base @
hex

\ F.6.1.1240 DO

\ F.6.1.1250 DOES>

T{ : DOES1 DOES> @ 1 + ; -> }T
T{ : DOES2 DOES> @ 2 + ; -> }T
T{ CREATE CR1 -> }T
T{ CR1   -> HERE }T
T{ 1 ,   ->   }T
T{ CR1 @ -> 1 }T
T{ DOES1 ->   }T
T{ CR1   -> 2 }T
T{ DOES2 ->   }T
T{ CR1   -> 3 }T
T{ : WEIRD: CREATE DOES> 1 + DOES> 2 + ; -> }T
T{ WEIRD: W1 -> }T
T{ ' W1 >BODY -> HERE }T
T{ W1 -> HERE 1 + }T
T{ W1 -> HERE 2 + }T

\ F.6.1.1260 DROP

T{ 1 2 DROP -> 1 }T
T{ 0   DROP ->   }T

\ F.6.1.1290 DUP

T{ 1 DUP -> 1 1 }T

\ F.6.1.1310 ELSE

\ F.6.1.1320 EMIT

: OUTPUT-TEST
   cr \ 为了测试输出结果好看，加个换行。
   ." YOU SHOULD SEE THE STANDARD GRAPHIC CHARACTERS:" CR
   41 BL DO I EMIT LOOP CR
   61 41 DO I EMIT LOOP CR
   7F 61 DO I EMIT LOOP CR
   ." YOU SHOULD SEE 0-9 SEPARATED BY A SPACE:" CR
   9 1+ 0 DO I . LOOP CR
   ." YOU SHOULD SEE 0-9 (WITH NO SPACES):" CR
   [CHAR] 9 1+ [CHAR] 0 DO I 0 SPACES EMIT LOOP CR
   ." YOU SHOULD SEE A-G SEPARATED BY A SPACE:" CR
   [CHAR] G 1+ [CHAR] A DO I EMIT SPACE LOOP CR
   ." YOU SHOULD SEE 0-5 SEPARATED BY TWO SPACES:" CR
   5 1+ 0 DO I [CHAR] 0 + EMIT 2 SPACES LOOP CR
   ." YOU SHOULD SEE TWO SEPARATE LINES:" CR
   S" LINE 1" TYPE CR S" LINE 2" TYPE CR
   ." YOU SHOULD SEE THE NUMBER RANGES OF SIGNED AND UNSIGNED NUMBERS:" CR
   ." SIGNED: " MIN-INT . MAX-INT . CR
   ." UNSIGNED: " 0 U. MAX-UINT U. CR
;
T{ OUTPUT-TEST -> }T

\ TODO: F.6.1.1345 ENVIRONMENT?

\ TODO: F.6.1.1360 EVALUATE

\ F.6.1.1370 EXECUTE

\ F.6.1.1380 EXIT

\ TODO: F.6.1.1540 FILL

\ TODO: F.6.1.1561 FM/MOD

\ F.6.1.1650 HERE

\ F.6.1.1670 HOLD

: GP1 <# 41 HOLD 42 HOLD 0 0 #> S" BA" S= ;
T{ GP1 -> <TRUE> }T

\ F.6.1.1680 I

\ F.6.1.1700 IF

T{ : GI1 IF 123 THEN ; -> }T
T{ : GI2 IF 123 ELSE 234 THEN ; -> }T
T{  0 GI1 ->     }T
T{  1 GI1 -> 123 }T
T{ -1 GI1 -> 123 }T
T{  0 GI2 -> 234 }T
T{  1 GI2 -> 123 }T
T{ -1 GI1 -> 123 }T
\ Multiple ELSEs in an IF statement
: melse IF 1 ELSE 2 ELSE 3 ELSE 4 ELSE 5 THEN ;
T{ <FALSE> melse -> 2 4 }T
T{ <TRUE>  melse -> 1 3 5 }T

\ TODO: F.6.1.1710 IMMEDIATE

\ F.6.1.1720 INVERT

T{ 0S INVERT -> 1S }T
T{ 1S INVERT -> 0S }T

\ F.6.1.1730 J

T{ : GD3 DO 1 0 DO J LOOP LOOP ; -> }T
T{          4        1 GD3 ->  1 2 3   }T
T{          2       -1 GD3 -> -1 0 1   }T
T{ MID-UINT+1 MID-UINT GD3 -> MID-UINT }T
T{ : GD4 DO 1 0 DO J LOOP -1 +LOOP ; -> }T
T{        1          4 GD4 -> 4 3 2 1             }T
T{       -1          2 GD4 -> 2 1 0 -1            }T
T{ MID-UINT MID-UINT+1 GD4 -> MID-UINT+1 MID-UINT }T

\ F.6.1.1760 LEAVE

T{ : GD5 123 SWAP 0 DO
     I 4 > IF DROP 234 LEAVE THEN
   LOOP ; -> }T
T{ 1 GD5 -> 123 }T
T{ 5 GD5 -> 123 }T
T{ 6 GD5 -> 234 }T

\ F.6.1.0070 '

T{ : GT1 123 ;   ->     }T
T{ ' GT1 EXECUTE -> 123 }T

\ F.6.1.2510 [']

T{ : GT2 ['] GT1 ; IMMEDIATE -> }T
T{ GT2 EXECUTE -> 123 }T

\ F.6.1.1780 LITERAL

T{ : GT3 GT2 LITERAL ; -> }T
T{ GT3 -> ' GT1 }T

\ F.6.1.1800 LOOP

T{ : GD1 DO I LOOP ; -> }T
T{          4        1 GD1 ->  1 2 3   }T
T{          2       -1 GD1 -> -1 0 1   }T
T{ MID-UINT+1 MID-UINT GD1 -> MID-UINT }T


\ Finished

BASE !
