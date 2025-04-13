: \ tib @ >in ! ; immediate

: here dp @ ;

: hex $10 base ! ;
: decimal #10 base ! ;

: rot >r swap r> swap ;
: nip swap drop ;
: tuck swap over ;

: 2dup over over ;
: 2drop drop drop ;

: >mark    ( -- addr )  here 0 , ;           \ 记下当前位置，填0做占位
: >resolve ( addr -- )  here swap ! ;        \ 将 addr 处的0改为当前地址

: if ( -- ) postpone 0branch >mark ; immediate

: else ( addr1 -- addr2 )
  postpone branch >mark
  swap >resolve ; immediate

: then ( addr -- ) >resolve ; immediate

: while ( addr -- addr addr )
    postpone if      \ 编译 if (留下 addr1)
    swap             \ 交换 begin 的地址到栈顶
; immediate

: repeat ( addr1 addr2 -- )
    postpone branch  \ 编译 branch
    ,                \ 填入 begin 的地址（回跳）
    >resolve         \ 解析 if 的地址（addr2）
; immediate

: 1+ 1 + ;
: 1- 1 - ;
: 2* 2 * ;

: < ( a b -- flag ) - 0< ;
: > ( a b -- flag ) swap - 0< ;
: = ( a b -- flag ) - 0= ;
: <> ( a b -- flag ) - 0= 0= ;

: U< < ;
: U> > ;

: or ( a b -- a|b )
  dup 0= if drop else nip then
;

: +! swap over @ + swap ! ;
: allot dp +! ;

: chars ;
: cells ;
: aligned ;

: c@ @ ;
: c, , ;
: c! ! ;

: char+ 1+ ;

: variable create 0 , ;
: constant create , does> @ ;

-1 constant true
0 constant false

true constant <true>
false constant <false>

$20 constant bl

: >body 1+ ;

: begin here ; immediate
: again (literal) branch , , ; immediate
: until postpone 0branch , ; immediate

: ['] ' postpone literal ; immediate

: MIN 2DUP > IF SWAP THEN DROP ;
: MAX 2DUP < IF SWAP THEN DROP ;

: ?dup dup if dup then ;

: [char]  ( -- )
    char
    postpone literal
; immediate

: source tib dup 1+ swap @ ;

: s"
  [char] " parse          \ ( -- c-addr u ) 获得字符串地址和长度
  state @ if              \ Compilation ( "ccc<quote>" -- )
    postpone branch >mark \ ( -- c-addr u mark-addr ) 记住当前位置，跳过字符串
    >r                    \ ( -- c-addr u ) 保存需要跳转的回填地址，下面将复制字符串
    here swap             \ ( -- c-addr dst-addr u ) 目标地址就是这里开始
    dup allot             \ ( -- c-addr dst-addr u ) 给字符串分配内存
    rot                   \ ( -- dist-addr u c-addr )
    2 pick 2 pick         \ ( -- dist-addr u c-addr dist-addr u )
    move                  \ ( -- dist-addr u ) 将字符串复制到目标地址
    r>                    \ ( -- dist-addr u mark-addr ) 恢复标记的地址
    >resolve              \ ( -- dist-addr u ) 确定branch跳转地址
    swap                  \ ( -- u dist-addr ) 调整参数顺序
    postpone (literal) ,  \ ( -- u ) 加载字符串地址
    postpone (literal) ,  \ ( -- ) 加载字符串长度
  else                    \ Runtime ( -- c-addr u )
    pad                   \ ( -- c-addr u pad-addr )
    swap                  \ ( -- c-addr pad-addr u )
    dup >r                \ ( -- c-addr pad-addr u )
    move                  \ ( -- )
    pad r>                \ ( -- pad-addr u )
  then
; immediate

: /string ( c-addr1 u1 n -- c-addr2 u2 )
  DUP >R - SWAP R> CHARS + SWAP
;

\ PARSE-NAME Implementation (from Forth-Standard.org)
: isspace? ( c -- f )
   BL 1+ U< ;
: isnotspace? ( c -- f )
   isspace? 0= ;

: xt-skip ( addr1 n1 xt -- addr2 n2 )
   \ skip all characters satisfying xt ( c -- f )
   >R
   BEGIN
     DUP
   WHILE
     OVER C@ R@ EXECUTE
   WHILE
     1 /STRING
   REPEAT THEN
   R> DROP ;

: parse-name ( "name" -- c-addr u )
   SOURCE >IN @ /STRING
   ['] isspace? xt-skip OVER >R
   ['] isnotspace? xt-skip ( end-word restlen r: start-word )
   2DUP 1 MIN + SOURCE DROP - >IN !
   DROP R> TUCK - ;

: ."
  postpone s"
  state @ if
    postpone type
  else
    type
  then
; immediate

: environment? 2drop 0 ;

: [THEN] ( -- ) ; IMMEDIATE

: [IF] ( flag -- )
   0= IF POSTPONE [ELSE] THEN
; IMMEDIATE

: 2>R ( x1 x2 -- ) ( R: -- x1 x2 )
          \ ( x1 x2 ) ( R: x0 )
  SWAP    \ ( x2 x1 ) ( R: x0 )
  R>      \ ( x2 x1 x0 ) ( R: )
  SWAP    \ ( x2 x0 x1 ) ( R: )
  >R      \ ( x2 x0 ) ( R: x1 )
  SWAP    \ ( x0 x2 ) ( R: x1 )
  >R      \ ( x0 ) ( R: x1 x2 )
  >R      \ ( ) ( R: x1 x2 x0 )
;

: 2R> ( -- x1 x2 ) ( R: x1 x2 -- )
          \ ( ) ( R: x1 x2 x0 )
  R>      \ ( x0 ) ( R: x1 x2 )
  R>      \ ( x0 x2 ) ( R: x1 )
  SWAP    \ ( x2 x0 ) ( R: x1 )
  R>      \ ( x2 x0 x1 ) ( R: )
  SWAP    \ ( x2 x1 x0 ) ( R: )
  >R      \ ( x2 x1 ) ( R: x0 )
  SWAP    \ ( x1 x2 ) ( R: x0 )
;

\ 这个词之后的，才能forget。
create user-word-begin
