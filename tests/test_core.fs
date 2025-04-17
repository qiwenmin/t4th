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

\ F.6.1.0110 */MOD

IFFLOORED    : T*/MOD >R M* R> FM/MOD ;
IFSYM        : T*/MOD >R M* R> SM/REM ;
T{       0 2       1 */MOD ->       0 2       1 T*/MOD }T
T{       1 2       1 */MOD ->       1 2       1 T*/MOD }T
T{       2 2       1 */MOD ->       2 2       1 T*/MOD }T
T{      -1 2       1 */MOD ->      -1 2       1 T*/MOD }T
T{      -2 2       1 */MOD ->      -2 2       1 T*/MOD }T
T{       0 2      -1 */MOD ->       0 2      -1 T*/MOD }T
T{       1 2      -1 */MOD ->       1 2      -1 T*/MOD }T
T{       2 2      -1 */MOD ->       2 2      -1 T*/MOD }T
T{      -1 2      -1 */MOD ->      -1 2      -1 T*/MOD }T
T{      -2 2      -1 */MOD ->      -2 2      -1 T*/MOD }T
T{       2 2       2 */MOD ->       2 2       2 T*/MOD }T
T{      -1 2      -1 */MOD ->      -1 2      -1 T*/MOD }T
T{      -2 2      -2 */MOD ->      -2 2      -2 T*/MOD }T
T{       7 2       3 */MOD ->       7 2       3 T*/MOD }T
T{       7 2      -3 */MOD ->       7 2      -3 T*/MOD }T
T{      -7 2       3 */MOD ->      -7 2       3 T*/MOD }T
T{      -7 2      -3 */MOD ->      -7 2      -3 T*/MOD }T
T{ MAX-INT 2 MAX-INT */MOD -> MAX-INT 2 MAX-INT T*/MOD }T
T{ MIN-INT 2 MIN-INT */MOD -> MIN-INT 2 MIN-INT T*/MOD }T

\ F.6.1.0100 */

IFFLOORED    : T*/ T*/MOD SWAP DROP ;
IFSYM        : T*/ T*/MOD SWAP DROP ;
T{       0 2       1 */ ->       0 2       1 T*/ }T
T{       1 2       1 */ ->       1 2       1 T*/ }T
T{       2 2       1 */ ->       2 2       1 T*/ }T
T{      -1 2       1 */ ->      -1 2       1 T*/ }T
T{      -2 2       1 */ ->      -2 2       1 T*/ }T
T{       0 2      -1 */ ->       0 2      -1 T*/ }T
T{       1 2      -1 */ ->       1 2      -1 T*/ }T
T{       2 2      -1 */ ->       2 2      -1 T*/ }T
T{      -1 2      -1 */ ->      -1 2      -1 T*/ }T
T{      -2 2      -1 */ ->      -2 2      -1 T*/ }T
T{       2 2       2 */ ->       2 2       2 T*/ }T
T{      -1 2      -1 */ ->      -1 2      -1 T*/ }T
T{      -2 2      -2 */ ->      -2 2      -2 T*/ }T
T{       7 2       3 */ ->       7 2       3 T*/ }T
T{       7 2      -3 */ ->       7 2      -3 T*/ }T
T{      -7 2       3 */ ->      -7 2       3 T*/ }T
T{      -7 2      -3 */ ->      -7 2      -3 T*/ }T
T{ MAX-INT 2 MAX-INT */ -> MAX-INT 2 MAX-INT T*/ }T
T{ MIN-INT 2 MIN-INT */ -> MIN-INT 2 MIN-INT T*/ }T

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

\ F.6.1.0140 +LOOP

decimal

T{ : GD2 DO I -1 +LOOP ; -> }T
T{        1          4 GD2 -> 4 3 2  1 }T
T{       -1          2 GD2 -> 2 1 0 -1 }T
T{ MID-UINT MID-UINT+1 GD2 -> MID-UINT+1 MID-UINT }T
VARIABLE gditerations
VARIABLE gdincrement

: gd7 ( limit start increment -- )
   gdincrement !
   0 gditerations !
   DO
     1 gditerations +!
     I
     gditerations @ 6 = IF LEAVE THEN
     gdincrement @
   +LOOP gditerations @
;

T{    4  4  -1 gd7 ->  4                  1  }T
T{    1  4  -1 gd7 ->  4  3  2  1         4  }T
T{    4  1  -1 gd7 ->  1  0 -1 -2  -3  -4 6  }T
T{    4  1   0 gd7 ->  1  1  1  1   1   1 6  }T
T{    0  0   0 gd7 ->  0  0  0  0   0   0 6  }T
T{    1  4   0 gd7 ->  4  4  4  4   4   4 6  }T
T{    1  4   1 gd7 ->  4  5  6  7   8   9 6  }T
T{    4  1   1 gd7 ->  1  2  3            3  }T
T{    4  4   1 gd7 ->  4  5  6  7   8   9 6  }T
T{    2 -1  -1 gd7 -> -1 -2 -3 -4  -5  -6 6  }T
T{   -1  2  -1 gd7 ->  2  1  0 -1         4  }T
T{    2 -1   0 gd7 -> -1 -1 -1 -1  -1  -1 6  }T
T{   -1  2   0 gd7 ->  2  2  2  2   2   2 6  }T
T{   -1  2   1 gd7 ->  2  3  4  5   6   7 6  }T
T{    2 -1   1 gd7 -> -1 0 1              3  }T
T{  -20 30 -10 gd7 -> 30 20 10  0 -10 -20 6  }T
T{  -20 31 -10 gd7 -> 31 21 11  1  -9 -19 6  }T
T{  -20 29 -10 gd7 -> 29 19  9 -1 -11     5  }T

\ With large and small increments

MAX-UINT 8 RSHIFT 1+ CONSTANT ustep
ustep NEGATE CONSTANT -ustep
MAX-INT 7 RSHIFT 1+ CONSTANT step
step NEGATE CONSTANT -step

VARIABLE bump

T{  : gd8 bump ! DO 1+ bump @ +LOOP ; -> }T

T{  0 MAX-UINT 0 ustep gd8 -> 256 }T
T{  0 0 MAX-UINT -ustep gd8 -> 256 }T
T{  0 MAX-INT MIN-INT step gd8 -> 256 }T
T{  0 MIN-INT MAX-INT -step gd8 -> 256 }T

hex

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

\ F.6.1.0240 /MOD

IFFLOORED    : T/MOD >R S>D R> FM/MOD ;
IFSYM        : T/MOD >R S>D R> SM/REM ;
T{       0       1 /MOD ->       0       1 T/MOD }T
T{       1       1 /MOD ->       1       1 T/MOD }T
T{       2       1 /MOD ->       2       1 T/MOD }T
T{      -1       1 /MOD ->      -1       1 T/MOD }T
T{      -2       1 /MOD ->      -2       1 T/MOD }T
T{       0      -1 /MOD ->       0      -1 T/MOD }T
T{       1      -1 /MOD ->       1      -1 T/MOD }T
T{       2      -1 /MOD ->       2      -1 T/MOD }T
T{      -1      -1 /MOD ->      -1      -1 T/MOD }T
T{      -2      -1 /MOD ->      -2      -1 T/MOD }T
T{       2       2 /MOD ->       2       2 T/MOD }T
T{      -1      -1 /MOD ->      -1      -1 T/MOD }T
T{      -2      -2 /MOD ->      -2      -2 T/MOD }T
T{       7       3 /MOD ->       7       3 T/MOD }T
T{       7      -3 /MOD ->       7      -3 T/MOD }T
T{      -7       3 /MOD ->      -7       3 T/MOD }T
T{      -7      -3 /MOD ->      -7      -3 T/MOD }T
T{ MAX-INT       1 /MOD -> MAX-INT       1 T/MOD }T
T{ MIN-INT       1 /MOD -> MIN-INT       1 T/MOD }T
T{ MAX-INT MAX-INT /MOD -> MAX-INT MAX-INT T/MOD }T
T{ MIN-INT MIN-INT /MOD -> MIN-INT MIN-INT T/MOD }T

\ F.6.1.0230 /

IFFLOORED    : T/ T/MOD SWAP DROP ;
IFSYM        : T/ T/MOD SWAP DROP ;
T{       0       1 / ->       0       1 T/ }T
T{       1       1 / ->       1       1 T/ }T
T{       2       1 / ->       2       1 T/ }T
T{      -1       1 / ->      -1       1 T/ }T
T{      -2       1 / ->      -2       1 T/ }T
T{       0      -1 / ->       0      -1 T/ }T
T{       1      -1 / ->       1      -1 T/ }T
T{       2      -1 / ->       2      -1 T/ }T
T{      -1      -1 / ->      -1      -1 T/ }T
T{      -2      -1 / ->      -2      -1 T/ }T
T{       2       2 / ->       2       2 T/ }T
T{      -1      -1 / ->      -1      -1 T/ }T
T{      -2      -2 / ->      -2      -2 T/ }T
T{       7       3 / ->       7       3 T/ }T
T{       7      -3 / ->       7      -3 T/ }T
T{      -7       3 / ->      -7       3 T/ }T
T{      -7      -3 / ->      -7      -3 T/ }T
T{ MAX-INT       1 / -> MAX-INT       1 T/ }T
T{ MIN-INT       1 / -> MIN-INT       1 T/ }T
T{ MAX-INT MAX-INT / -> MAX-INT MAX-INT T/ }T
T{ MIN-INT MIN-INT / -> MIN-INT MIN-INT T/ }T

\ F.6.1.0250 0<

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

\ F.6.1.0570 >NUMBER

CREATE GN-BUF 0 C,
: GN-STRING GN-BUF 1 ;
: GN-CONSUMED GN-BUF CHAR+ 0 ;
: GN' [CHAR] ' WORD CHAR+ C@ GN-BUF C! GN-STRING ;
T{ 0 0 GN' 0' >NUMBER ->         0 0 GN-CONSUMED }T
T{ 0 0 GN' 1' >NUMBER ->         1 0 GN-CONSUMED }T
T{ 1 0 GN' 1' >NUMBER -> BASE @ 1+ 0 GN-CONSUMED }T
\ FOLLOWING SHOULD FAIL TO CONVERT
T{ 0 0 GN' -' >NUMBER ->         0 0 GN-STRING   }T
T{ 0 0 GN' +' >NUMBER ->         0 0 GN-STRING   }T
T{ 0 0 GN' .' >NUMBER ->         0 0 GN-STRING   }T

: >NUMBER-BASED
   BASE @ >R BASE ! >NUMBER R> BASE ! ;

T{ 0 0 GN' 2'       10 >NUMBER-BASED ->  2 0 GN-CONSUMED }T
T{ 0 0 GN' 2'        2 >NUMBER-BASED ->  0 0 GN-STRING   }T
T{ 0 0 GN' F'       10 >NUMBER-BASED ->  F 0 GN-CONSUMED }T
T{ 0 0 GN' G'       10 >NUMBER-BASED ->  0 0 GN-STRING   }T
T{ 0 0 GN' G' MAX-BASE >NUMBER-BASED -> 10 0 GN-CONSUMED }T
T{ 0 0 GN' Z' MAX-BASE >NUMBER-BASED -> 23 0 GN-CONSUMED }T

: GN1 ( UD BASE -- UD' LEN )
   \ UD SHOULD EQUAL UD' AND LEN SHOULD BE ZERO.
   BASE @ >R BASE !
   <# #S #>
   0 0 2SWAP >NUMBER SWAP DROP    \ RETURN LENGTH ONLY
   R> BASE ! ;

T{        0   0        2 GN1 ->        0   0 0 }T
T{ MAX-UINT   0        2 GN1 -> MAX-UINT   0 0 }T
T{ MAX-UINT DUP        2 GN1 -> MAX-UINT DUP 0 }T
T{        0   0 MAX-BASE GN1 ->        0   0 0 }T
T{ MAX-UINT   0 MAX-BASE GN1 -> MAX-UINT   0 0 }T
T{ MAX-UINT DUP MAX-BASE GN1 -> MAX-UINT DUP 0 }T

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

\ F.6.1.0690 ABS

T{       0 ABS ->          0 }T
T{       1 ABS ->          1 }T
T{      -1 ABS ->          1 }T
T{ MIN-INT ABS -> MID-UINT+1 }T

\ F.6.1.0695 ACCEPT

decimal

CREATE ABUF 80 CHARS ALLOT
: ACCEPT-TEST
     CR ." PLEASE TYPE UP TO 80 CHARACTERS:" CR
     ABUF 80 ACCEPT
     CR ." RECEIVED: " [CHAR] " EMIT
     ABUF SWAP TYPE [CHAR] " EMIT CR
;

T{ ACCEPT-TEST -> }T
12345678901234567890123456789012345678901234567890123456789012345678901234567890======

hex

\ F.6.1.0705 ALIGN

ALIGN 1 ALLOT HERE ALIGN HERE 3 CELLS ALLOT
CONSTANT A-ADDR CONSTANT UA-ADDR
T{ UA-ADDR ALIGNED -> A-ADDR }T
T{       1 A-ADDR C!         A-ADDR       C@ ->       1 }T
T{    1234 A-ADDR !          A-ADDR       @  ->    1234 }T
T{ 123 456 A-ADDR 2!         A-ADDR       2@ -> 123 456 }T
T{       2 A-ADDR CHAR+ C!   A-ADDR CHAR+ C@ ->       2 }T
T{       3 A-ADDR CELL+ C!   A-ADDR CELL+ C@ ->       3 }T
T{    1234 A-ADDR CELL+ !    A-ADDR CELL+ @  ->    1234 }T
T{ 123 456 A-ADDR CELL+ 2!   A-ADDR CELL+ 2@ -> 123 456 }T

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

\ F.6.1.2510 [']

T{ : GT2 ['] GT1 ; IMMEDIATE -> }T
T{ GT2 EXECUTE -> 123 }T

\ F.6.1.1550 FIND

HERE 3 C, CHAR G C, CHAR T C, CHAR 1 C, CONSTANT GT1STRING
HERE 3 C, CHAR G C, CHAR T C, CHAR 2 C, CONSTANT GT2STRING
T{ GT1STRING FIND -> ' GT1 -1 }T
T{ GT2STRING FIND -> ' GT2 1  }T
( HOW TO SEARCH FOR NON-EXISTENT WORD? )
\ my test for non-existent word `_#!?`:
here 4 c, char _ c, char # c, char ! c, char ? c, constant nonexistentword
T{ nonexistentword FIND -> nonexistentword 0 }T

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

\ F.6.1.1345 ENVIRONMENT?

\ should be the same for any query starting with X:
\ T{ S" X:deferred" ENVIRONMENT? DUP 0= XOR INVERT -> <TRUE>  }T
\ T{ S" X:notfound" ENVIRONMENT? DUP 0= XOR INVERT -> <FALSE> }T
\ 上面的测试用例有问题，无论environment?返回是-1还是0，经过dup 0= xor invert后都是0。
\ 改为下面的用例：
T{ S" X:deferred" ENVIRONMENT? 0= INVERT -> <TRUE>  }T
T{ S" X:notfound" ENVIRONMENT? 0= INVERT -> <FALSE> }T

\ TODO: F.6.1.1360 EVALUATE

\ F.6.1.1370 EXECUTE

\ F.6.1.1380 EXIT

\ F.6.1.1540 FILL

T{ FBUF 0 20 FILL -> }T
T{ SEEBUF -> 00 00 00 }T
T{ FBUF 1 20 FILL -> }T
T{ SEEBUF -> 20 00 00 }T

T{ FBUF 3 20 FILL -> }T
T{ SEEBUF -> 20 20 20 }T

\ F.6.1.1561 FM/MOD

T{       0 S>D              1 FM/MOD ->  0       0 }T
T{       1 S>D              1 FM/MOD ->  0       1 }T
T{       2 S>D              1 FM/MOD ->  0       2 }T
T{      -1 S>D              1 FM/MOD ->  0      -1 }T
T{      -2 S>D              1 FM/MOD ->  0      -2 }T
T{       0 S>D             -1 FM/MOD ->  0       0 }T
T{       1 S>D             -1 FM/MOD ->  0      -1 }T
T{       2 S>D             -1 FM/MOD ->  0      -2 }T
T{      -1 S>D             -1 FM/MOD ->  0       1 }T
T{      -2 S>D             -1 FM/MOD ->  0       2 }T
T{       2 S>D              2 FM/MOD ->  0       1 }T
T{      -1 S>D             -1 FM/MOD ->  0       1 }T
T{      -2 S>D             -2 FM/MOD ->  0       1 }T
T{       7 S>D              3 FM/MOD ->  1       2 }T
T{       7 S>D             -3 FM/MOD -> -2      -3 }T
T{      -7 S>D              3 FM/MOD ->  2      -3 }T
T{      -7 S>D             -3 FM/MOD -> -1       2 }T
T{ MAX-INT S>D              1 FM/MOD ->  0 MAX-INT }T
T{ MIN-INT S>D              1 FM/MOD ->  0 MIN-INT }T
T{ MAX-INT S>D        MAX-INT FM/MOD ->  0       1 }T
T{ MIN-INT S>D        MIN-INT FM/MOD ->  0       1 }T
T{    1S 1                  4 FM/MOD ->  3 MAX-INT }T
T{       1 MIN-INT M*       1 FM/MOD ->  0 MIN-INT }T
T{       1 MIN-INT M* MIN-INT FM/MOD ->  0       1 }T
T{       2 MIN-INT M*       2 FM/MOD ->  0 MIN-INT }T
T{       2 MIN-INT M* MIN-INT FM/MOD ->  0       2 }T
T{       1 MAX-INT M*       1 FM/MOD ->  0 MAX-INT }T
T{       1 MAX-INT M* MAX-INT FM/MOD ->  0       1 }T
T{       2 MAX-INT M*       2 FM/MOD ->  0 MAX-INT }T
T{       2 MAX-INT M* MAX-INT FM/MOD ->  0       2 }T
T{ MIN-INT MIN-INT M* MIN-INT FM/MOD ->  0 MIN-INT }T
T{ MIN-INT MAX-INT M* MIN-INT FM/MOD ->  0 MAX-INT }T
T{ MIN-INT MAX-INT M* MAX-INT FM/MOD ->  0 MIN-INT }T
T{ MAX-INT MAX-INT M* MAX-INT FM/MOD ->  0 MAX-INT }T

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

\ F.6.1.1780 LITERAL

T{ : GT3 GT2 LITERAL ; -> }T
T{ GT3 -> ' GT1 }T

\ F.6.1.1800 LOOP

T{ : GD1 DO I LOOP ; -> }T
T{          4        1 GD1 ->  1 2 3   }T
T{          2       -1 GD1 -> -1 0 1   }T
T{ MID-UINT+1 MID-UINT GD1 -> MID-UINT }T

\ F.6.1.1805 LSHIFT

T{   1 0 LSHIFT ->    1 }T
T{   1 1 LSHIFT ->    2 }T
T{   1 2 LSHIFT ->    4 }T
T{   1 F LSHIFT -> 8000 }T      \ BIGGEST GUARANTEED SHIFT
T{  1S 1 LSHIFT 1 XOR -> 1S }T
T{ MSB 1 LSHIFT ->    0 }T

\ F.6.1.1810 M*

T{       0       0 M* ->       0 S>D }T
T{       0       1 M* ->       0 S>D }T
T{       1       0 M* ->       0 S>D }T
T{       1       2 M* ->       2 S>D }T
T{       2       1 M* ->       2 S>D }T
T{       3       3 M* ->       9 S>D }T
T{      -3       3 M* ->      -9 S>D }T
T{       3      -3 M* ->      -9 S>D }T
T{      -3      -3 M* ->       9 S>D }T
T{       0 MIN-INT M* ->       0 S>D }T
T{       1 MIN-INT M* -> MIN-INT S>D }T
T{       2 MIN-INT M* ->       0 1S  }T
T{       0 MAX-INT M* ->       0 S>D }T
T{       1 MAX-INT M* -> MAX-INT S>D }T
T{       2 MAX-INT M* -> MAX-INT     1 LSHIFT 0 }T
T{ MIN-INT MIN-INT M* ->       0 MSB 1 RSHIFT   }T
T{ MAX-INT MIN-INT M* ->     MSB MSB 2/         }T
T{ MAX-INT MAX-INT M* ->       1 MSB 2/ INVERT  }T

\ F.6.1.1870 MAX

T{       0       1 MAX ->       1 }T
T{       1       2 MAX ->       2 }T
T{      -1       0 MAX ->       0 }T
T{      -1       1 MAX ->       1 }T
T{ MIN-INT       0 MAX ->       0 }T
T{ MIN-INT MAX-INT MAX -> MAX-INT }T
T{       0 MAX-INT MAX -> MAX-INT }T
T{       0       0 MAX ->       0 }T
T{       1       1 MAX ->       1 }T
T{       1       0 MAX ->       1 }T
T{       2       1 MAX ->       2 }T
T{       0      -1 MAX ->       0 }T
T{       1      -1 MAX ->       1 }T
T{       0 MIN-INT MAX ->       0 }T
T{ MAX-INT MIN-INT MAX -> MAX-INT }T
T{ MAX-INT       0 MAX -> MAX-INT }T

\ F.6.1.1880 MIN

T{       0       1 MIN ->       0 }T
T{       1       2 MIN ->       1 }T
T{      -1       0 MIN ->      -1 }T
T{      -1       1 MIN ->      -1 }T
T{ MIN-INT       0 MIN -> MIN-INT }T
T{ MIN-INT MAX-INT MIN -> MIN-INT }T
T{       0 MAX-INT MIN ->       0 }T
T{       0       0 MIN ->       0 }T
T{       1       1 MIN ->       1 }T
T{       1       0 MIN ->       0 }T
T{       2       1 MIN ->       1 }T
T{       0      -1 MIN ->      -1 }T
T{       1      -1 MIN ->      -1 }T
T{       0 MIN-INT MIN -> MIN-INT }T
T{ MAX-INT MIN-INT MIN -> MIN-INT }T
T{ MAX-INT       0 MIN ->       0 }T

\ F.6.1.1890 MOD

IFFLOORED    : TMOD T/MOD DROP ;
IFSYM        : TMOD T/MOD DROP ;
T{       0       1 MOD ->       0       1 TMOD }T
T{       1       1 MOD ->       1       1 TMOD }T
T{       2       1 MOD ->       2       1 TMOD }T
T{      -1       1 MOD ->      -1       1 TMOD }T
T{      -2       1 MOD ->      -2       1 TMOD }T
T{       0      -1 MOD ->       0      -1 TMOD }T
T{       1      -1 MOD ->       1      -1 TMOD }T
T{       2      -1 MOD ->       2      -1 TMOD }T
T{      -1      -1 MOD ->      -1      -1 TMOD }T
T{      -2      -1 MOD ->      -2      -1 TMOD }T
T{       2       2 MOD ->       2       2 TMOD }T
T{      -1      -1 MOD ->      -1      -1 TMOD }T
T{      -2      -2 MOD ->      -2      -2 TMOD }T
T{       7       3 MOD ->       7       3 TMOD }T
T{       7      -3 MOD ->       7      -3 TMOD }T
T{      -7       3 MOD ->      -7       3 TMOD }T
T{      -7      -3 MOD ->      -7      -3 TMOD }T
T{ MAX-INT       1 MOD -> MAX-INT       1 TMOD }T
T{ MIN-INT       1 MOD -> MIN-INT       1 TMOD }T
T{ MAX-INT MAX-INT MOD -> MAX-INT MAX-INT TMOD }T
T{ MIN-INT MIN-INT MOD -> MIN-INT MIN-INT TMOD }T

\ F.6.1.1900 MOVE

T{ FBUF FBUF 3 CHARS MOVE -> }T \ BIZARRE SPECIAL CASE
T{ SEEBUF -> 20 20 20 }T
T{ SBUF FBUF 0 CHARS MOVE -> }T
T{ SEEBUF -> 20 20 20 }T

T{ SBUF FBUF 1 CHARS MOVE -> }T
T{ SEEBUF -> 12 20 20 }T

T{ SBUF FBUF 3 CHARS MOVE -> }T
T{ SEEBUF -> 12 34 56 }T

T{ FBUF FBUF CHAR+ 2 CHARS MOVE -> }T
T{ SEEBUF -> 12 12 34 }T

T{ FBUF CHAR+ FBUF 2 CHARS MOVE -> }T
T{ SEEBUF -> 12 34 34 }T

\ F.6.1.1910 NEGATE

T{  0 NEGATE ->  0 }T
T{  1 NEGATE -> -1 }T
T{ -1 NEGATE ->  1 }T
T{  2 NEGATE -> -2 }T
T{ -2 NEGATE ->  2 }T

\ F.6.1.1980 OR

T{ 0S 0S OR -> 0S }T
T{ 0S 1S OR -> 1S }T
T{ 1S 0S OR -> 1S }T
T{ 1S 1S OR -> 1S }T

\ F.6.1.1990 OVER

T{ 1 2 OVER -> 1 2 1 }T

\ F.6.1.2033 POSTPONE

T{ : GT4 POSTPONE GT1 ; IMMEDIATE -> }T
T{ : GT5 GT4 ; -> }T
T{ GT5 -> 123 }T
T{ : GT6 345 ; IMMEDIATE -> }T
T{ : GT7 POSTPONE GT6 ; -> }T
T{ GT7 -> 345 }T

\ F.6.1.2060 R>

\ F.6.1.2070 R@

\ F.6.1.2120 RECURSE

T{ : GI6 ( N -- 0,1,..N )
     DUP IF DUP >R 1- RECURSE R> THEN ; -> }T
T{ 0 GI6 -> 0 }T
T{ 1 GI6 -> 0 1 }T
T{ 2 GI6 -> 0 1 2 }T
T{ 3 GI6 -> 0 1 2 3 }T
T{ 4 GI6 -> 0 1 2 3 4 }T
DECIMAL
T{ :NONAME ( n -- 0, 1, .., n )
     DUP IF DUP >R 1- RECURSE R> THEN
   ;
   CONSTANT rn1 -> }T
T{ 0 rn1 EXECUTE -> 0 }T
T{ 4 rn1 EXECUTE -> 0 1 2 3 4 }T

:NONAME ( n -- n1 )
   1- DUP
   CASE 0 OF EXIT ENDOF
     1 OF 11 SWAP RECURSE ENDOF
     2 OF 22 SWAP RECURSE ENDOF
     3 OF 33 SWAP RECURSE ENDOF
     DROP ABS RECURSE EXIT
   ENDCASE
; CONSTANT rn2

T{  1 rn2 EXECUTE -> 0 }T
T{  2 rn2 EXECUTE -> 11 0 }T
T{  4 rn2 EXECUTE -> 33 22 11 0 }T
T{ 25 rn2 EXECUTE -> 33 22 11 0 }T

hex

\ F.6.1.2140 REPEAT

\ F.6.1.2160 ROT

T{ 1 2 3 ROT -> 2 3 1 }T

\ F.6.1.2162 RSHIFT

T{    1 0 RSHIFT -> 1 }T
T{    1 1 RSHIFT -> 0 }T
T{    2 1 RSHIFT -> 1 }T
T{    4 2 RSHIFT -> 1 }T
T{ 8000 F RSHIFT -> 1 }T                \ Biggest
T{  MSB 1 RSHIFT MSB AND ->   0 }T    \ RSHIFT zero fills MSBs
T{  MSB 1 RSHIFT     2*  -> MSB }T

\ F.6.1.2165 S"

T{ : GC4 S" XY" ; ->   }T
T{ GC4 SWAP DROP  -> 2 }T
T{ GC4 DROP DUP C@ SWAP CHAR+ C@ -> 58 59 }T
: GC5 S" A String"2DROP ; \ There is no space between the " and 2DROP
T{ GC5 -> }T

\ F.6.1.2170 S>D

T{       0 S>D ->       0  0 }T
T{       1 S>D ->       1  0 }T
T{       2 S>D ->       2  0 }T
T{      -1 S>D ->      -1 -1 }T
T{      -2 S>D ->      -2 -1 }T
T{ MIN-INT S>D -> MIN-INT -1 }T
T{ MAX-INT S>D -> MAX-INT  0 }T

\ TODO: F.6.1.2210 SIGN

\ F.6.1.2214 SM/REM

T{       0 S>D              1 SM/REM ->  0       0 }T
T{       1 S>D              1 SM/REM ->  0       1 }T
T{       2 S>D              1 SM/REM ->  0       2 }T
T{      -1 S>D              1 SM/REM ->  0      -1 }T
T{      -2 S>D              1 SM/REM ->  0      -2 }T
T{       0 S>D             -1 SM/REM ->  0       0 }T
T{       1 S>D             -1 SM/REM ->  0      -1 }T
T{       2 S>D             -1 SM/REM ->  0      -2 }T
T{      -1 S>D             -1 SM/REM ->  0       1 }T
T{      -2 S>D             -1 SM/REM ->  0       2 }T
T{       2 S>D              2 SM/REM ->  0       1 }T
T{      -1 S>D             -1 SM/REM ->  0       1 }T
T{      -2 S>D             -2 SM/REM ->  0       1 }T
T{       7 S>D              3 SM/REM ->  1       2 }T
T{       7 S>D             -3 SM/REM ->  1      -2 }T
T{      -7 S>D              3 SM/REM -> -1      -2 }T \ 官网这里是1 -2，应该是错了。
T{      -7 S>D             -3 SM/REM -> -1       2 }T
T{ MAX-INT S>D              1 SM/REM ->  0 MAX-INT }T
T{ MIN-INT S>D              1 SM/REM ->  0 MIN-INT }T
T{ MAX-INT S>D        MAX-INT SM/REM ->  0       1 }T
T{ MIN-INT S>D        MIN-INT SM/REM ->  0       1 }T
T{      1S 1                4 SM/REM ->  3 MAX-INT }T
T{       2 MIN-INT M*       2 SM/REM ->  0 MIN-INT }T
T{       2 MIN-INT M* MIN-INT SM/REM ->  0       2 }T
T{       2 MAX-INT M*       2 SM/REM ->  0 MAX-INT }T
T{       2 MAX-INT M* MAX-INT SM/REM ->  0       2 }T
T{ MIN-INT MIN-INT M* MIN-INT SM/REM ->  0 MIN-INT }T
T{ MIN-INT MAX-INT M* MIN-INT SM/REM ->  0 MAX-INT }T
T{ MIN-INT MAX-INT M* MAX-INT SM/REM ->  0 MIN-INT }T
T{ MAX-INT MAX-INT M* MAX-INT SM/REM ->  0 MAX-INT }T

\ TODO: F.6.1.2216 SOURCE

\ F.6.1.2220 SPACE

\ F.6.1.2230 SPACES

\ F.6.1.2250 STATE

T{ : GT8 STATE @ ; IMMEDIATE -> }T
T{ GT8 -> 0 }T
T{ : GT9 GT8 LITERAL ; -> }T
T{ GT9 0= -> <FALSE> }T

\ F.6.1.2260 SWAP

T{ 1 2 SWAP -> 2 1 }T

\ F.6.1.2270 THEN

\ F.6.1.2310 TYPE

\ F.6.1.2320 U.

\ F.6.1.2340U<
T{        0        1 U< -> <TRUE>  }T
T{        1        2 U< -> <TRUE>  }T
T{        0 MID-UINT U< -> <TRUE>  }T
T{        0 MAX-UINT U< -> <TRUE>  }T
T{ MID-UINT MAX-UINT U< -> <TRUE>  }T
T{        0        0 U< -> <FALSE> }T
T{        1        1 U< -> <FALSE> }T
T{        1        0 U< -> <FALSE> }T
T{        2        1 U< -> <FALSE> }T
T{ MID-UINT        0 U< -> <FALSE> }T
T{ MAX-UINT        0 U< -> <FALSE> }T
T{ MAX-UINT MID-UINT U< -> <FALSE> }T

\ F.6.1.2360 UM*

T{ 0 0 UM* -> 0 0 }T
T{ 0 1 UM* -> 0 0 }T
T{ 1 0 UM* -> 0 0 }T
T{ 1 2 UM* -> 2 0 }T
T{ 2 1 UM* -> 2 0 }T
T{ 3 3 UM* -> 9 0 }T
T{ MID-UINT+1 1 RSHIFT 2 UM* ->  MID-UINT+1 0 }T
T{ MID-UINT+1          2 UM* ->           0 1 }T
T{ MID-UINT+1          4 UM* ->           0 2 }T
T{         1S          2 UM* -> 1S 1 LSHIFT 1 }T
T{   MAX-UINT   MAX-UINT UM* ->    1 1 INVERT }T

\ F.6.1.2370 UM/MOD

T{        0            0        1 UM/MOD -> 0        0 }T
T{        1            0        1 UM/MOD -> 0        1 }T
T{        1            0        2 UM/MOD -> 1        0 }T
T{        3            0        2 UM/MOD -> 1        1 }T
T{ MAX-UINT        2 UM*        2 UM/MOD -> 0 MAX-UINT }T
T{ MAX-UINT        2 UM* MAX-UINT UM/MOD -> 0        2 }T
T{ MAX-UINT MAX-UINT UM* MAX-UINT UM/MOD -> 0 MAX-UINT }T

\ F.6.1.2380 UNLOOP

T{ : GD6 ( PAT: {0 0},{0 0}{1 0}{1 1},{0 0}{1 0}{1 1}{2 0}{2 1}{2 2} )
      0 SWAP 0 DO
         I 1+ 0 DO
           I J + 3 = IF I UNLOOP I UNLOOP EXIT THEN 1+
         LOOP
      LOOP ; -> }T
T{ 1 GD6 -> 1 }T
T{ 2 GD6 -> 3 }T
T{ 3 GD6 -> 4 1 2 }T

\ F.6.1.2390 UNTIL

T{ : GI4 BEGIN DUP 1+ DUP 5 > UNTIL ; -> }T
T{ 3 GI4 -> 3 4 5 6 }T
T{ 5 GI4 -> 5 6 }T
T{ 6 GI4 -> 6 7 }T

\ F.6.1.2410 VARIABLE

T{ VARIABLE V1 ->     }T
T{    123 V1 ! ->     }T
T{        V1 @ -> 123 }T

\ F.6.1.2430 WHILE

T{ : GI3 BEGIN DUP 5 < WHILE DUP 1+ REPEAT ; -> }T
T{ 0 GI3 -> 0 1 2 3 4 5 }T
T{ 4 GI3 -> 4 5 }T
T{ 5 GI3 -> 5 }T
T{ 6 GI3 -> 6 }T
T{ : GI5 BEGIN DUP 2 > WHILE
      DUP 5 < WHILE DUP 1+ REPEAT
      123 ELSE 345 THEN ; -> }T
T{ 1 GI5 -> 1 345 }T
T{ 2 GI5 -> 2 345 }T
T{ 3 GI5 -> 3 4 5 123 }T
T{ 4 GI5 -> 4 5 123 }T
T{ 5 GI5 -> 5 123 }T

\ F.6.1.2450 WORD

: GS3 WORD COUNT SWAP C@ ;
T{ BL GS3 HELLO -> 5 CHAR H }T
T{ CHAR " GS3 GOODBYE" -> 7 CHAR G }T
T{ BL GS3
   DROP -> 0 }T \ Blank lines return zero-length strings

\ F.6.1.2490 XOR

T{ 0S 0S XOR -> 0S }T
T{ 0S 1S XOR -> 1S }T
T{ 1S 0S XOR -> 1S }T
T{ 1S 1S XOR -> 0S }T

\ F.6.1.2520 [CHAR]

T{ : GC1 [CHAR] X     ; -> }T
T{ : GC2 [CHAR] HELLO ; -> }T
T{ GC1 -> 58 }T
T{ GC2 -> 48 }T

\ F.6.1.2500 [

T{ : GC3 [ GC1 ] LITERAL ; -> }T
T{ GC3 -> 58 }T

\ F.6.1.2510 [']

T{ : GT2 ['] GT1 ; IMMEDIATE -> }T
T{ GT2 EXECUTE -> 123 }T

\ F.6.1.2540 ]

\ F.6.2.0455 :NONAME

VARIABLE nn1
VARIABLE nn2
T{ :NONAME 1234 ; nn1 ! -> }T
T{ :NONAME 9876 ; nn2 ! -> }T
T{ nn1 @ EXECUTE -> 1234 }T
T{ nn2 @ EXECUTE -> 9876 }T

\ F.6.2.0620 ?DO

DECIMAL
: qd ?DO I LOOP ;
T{   789   789 qd -> }T
T{ -9876 -9876 qd -> }T
T{     5     0 qd -> 0 1 2 3 4 }T

: qd1 ?DO I 10 +LOOP ;
T{ 50 1 qd1 -> 1 11 21 31 41 }T
T{ 50 0 qd1 -> 0 10 20 30 40 }T

: qd2 ?DO I 3 > IF LEAVE ELSE I THEN LOOP ;
T{ 5 -1 qd2 -> -1 0 1 2 3 }T

: qd3 ?DO I 1 +LOOP ;
T{ 4  4 qd3 -> }T
T{ 4  1 qd3 ->  1 2 3 }T
T{ 2 -1 qd3 -> -1 0 1 }T

: qd4 ?DO I -1 +LOOP ;
T{  4 4 qd4 -> }T
T{  1 4 qd4 -> 4 3 2  1 }T
T{ -1 2 qd4 -> 2 1 0 -1 }T

: qd5 ?DO I -10 +LOOP ;
T{   1 50 qd5 -> 50 40 30 20 10   }T
T{   0 50 qd5 -> 50 40 30 20 10 0 }T
T{ -25 10 qd5 -> 10 0 -10 -20     }T

VARIABLE qditerations
VARIABLE qdincrement

: qd6 ( limit start increment -- )    qdincrement !
   0 qditerations !
   ?DO
     1 qditerations +!
     I
     qditerations @ 6 = IF LEAVE THEN
     qdincrement @
   +LOOP qditerations @
;

T{  4  4 -1 qd6 ->                   0  }T
T{  1  4 -1 qd6 ->  4  3  2  1       4  }T
T{  4  1 -1 qd6 ->  1  0 -1 -2 -3 -4 6  }T
T{  4  1  0 qd6 ->  1  1  1  1  1  1 6  }T
T{  0  0  0 qd6 ->                   0  }T
T{  1  4  0 qd6 ->  4  4  4  4  4  4 6  }T
T{  1  4  1 qd6 ->  4  5  6  7  8  9 6  }T
T{  4  1  1 qd6 ->  1  2  3          3  }T
T{  4  4  1 qd6 ->                   0  }T
T{  2 -1 -1 qd6 -> -1 -2 -3 -4 -5 -6 6  }T
T{ -1  2 -1 qd6 ->  2  1  0 -1       4  }T
T{  2 -1  0 qd6 -> -1 -1 -1 -1 -1 -1 6  }T
T{ -1  2  0 qd6 ->  2  2  2  2  2  2 6  }T
T{ -1  2  1 qd6 ->  2  3  4  5  6  7 6  }T
T{  2 -1  1 qd6 -> -1  0  1          3  }T

hex

\ TODO: F.6.2.0698 ACTION-OF

\ F.6.2.0825 BUFFER:

DECIMAL
T{ 127 CHARS BUFFER: TBUF1 -> }T
T{ 127 CHARS BUFFER: TBUF2 -> }T
\ Buffer is aligned
T{ TBUF1 ALIGNED -> TBUF1 }T

\ Buffers do not overlap
T{ TBUF2 TBUF1 - ABS 127 CHARS < -> <FALSE> }T

\ Buffer can be written to
1 CHARS CONSTANT /CHAR
: TFULL? ( c-addr n char -- flag )
   TRUE 2SWAP CHARS OVER + SWAP ?DO
     OVER I C@ = AND
   /CHAR +LOOP NIP
;

T{ TBUF1 127 CHAR * FILL   ->        }T
T{ TBUF1 127 CHAR * TFULL? -> <TRUE> }T

T{ TBUF1 127 0 FILL   ->        }T
T{ TBUF1 127 0 TFULL? -> <TRUE> }T

hex

\ TODO: F.6.2.0855 C"

\ F.6.2.0873 CASE

: cs1 CASE 1 OF 111 ENDOF
   2 OF 222 ENDOF
   3 OF 333 ENDOF
   >R 999 R>
   ENDCASE
;
T{ 1 cs1 -> 111 }T
T{ 2 cs1 -> 222 }T
T{ 3 cs1 -> 333 }T
T{ 4 cs1 -> 999 }T
: cs2 >R CASE
   -1 OF CASE R@ 1 OF 100 ENDOF
                2 OF 200 ENDOF
                >R -300 R>
        ENDCASE
     ENDOF
   -2 OF CASE R@ 1 OF -99 ENDOF
                >R -199 R>
        ENDCASE
     ENDOF
     >R 299 R>
   ENDCASE R> DROP ;

T{ -1 1 cs2 ->  100 }T
T{ -1 2 cs2 ->  200 }T
T{ -1 3 cs2 -> -300 }T
T{ -2 1 cs2 ->  -99 }T
T{ -2 2 cs2 -> -199 }T
T{  0 2 cs2 ->  299 }T

\ TODO: F.6.2.0945 COMPILE,

\ TODO: F.6.2.1173 DEFER

\ TODO: F.6.2.1175 DEFER!

\ TODO: F.6.2.1177 DEFER@

\ F.6.2.1342 ENDCASE

\ F.6.2.1343 ENDOF

\ F.6.2.1485 FALSE

T{ FALSE -> 0 }T
T{ FALSE -> <FALSE> }T

\ F.6.2.1660 HEX

\ F.6.2.1675 HOLDS

T{ 0. <# S" Test" HOLDS #> S" Test" COMPARE -> 0 }T

\ TODO: F.6.2.1725 IS

\ F.6.2.1950 OF

\ F.6.2.2020 PARSE-NAME

T{ PARSE-NAME abcd S" abcd" S= -> <TRUE> }T
T{ PARSE-NAME   abcde   S" abcde" S= -> <TRUE> }T
\ test empty parse area
T{ PARSE-NAME
   NIP -> 0 }T    \ empty line
T{ PARSE-NAME
   NIP -> 0 }T    \ line with white space

T{ : parse-name-test ( "name1" "name2" -- n )
   PARSE-NAME PARSE-NAME S= ; -> }T

T{ parse-name-test abcd abcd -> <TRUE> }T
T{ parse-name-test  abcd   abcd   -> <TRUE> }T
T{ parse-name-test abcde abcdf -> <FALSE> }T
T{ parse-name-test abcdf abcde -> <FALSE> }T
T{ parse-name-test abcde abcde
    -> <TRUE> }T
T{ parse-name-test abcde abcde
    -> <TRUE> }T    \ line with white space

\ TODO: F.6.2.2182 SAVE-INPUT

\ TODO: F.6.2.2295 TO

\ F.6.2.2298 TRUE

T{ TRUE -> <TRUE> }T
T{ TRUE -> 0 INVERT }T

\ TODO: F.6.2.2405 VALUE

\ TODO: F.6.2.2530 [COMPILE]


\ Finished

BASE !
