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


\ Finished

BASE !
