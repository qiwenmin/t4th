: \ tib @ >in ! ; immediate

: here dp @ ;

: hex $10 base ! ;
: decimal #10 base ! ;

: 1+ 1 + ;

: +! swap over @ + swap ! ;
: allot dp +! ;
: rot >r swap r> swap ;

: 2dup over over ;
: 2drop drop drop ;

: chars ;
: cells ;

: c@ @ ;
: c, , ;
: c! ! ;

: char+ 1+ ;

: begin here ; immediate
: again (literal) branch , , ; immediate

: ['] ' postpone literal ; immediate

: variable create 0 , ;
: constant create , does> @ ;

: >body 1+ ;

-1 constant true
0 constant false

true constant <true>
false constant <false>

: >mark    ( -- addr )  here 0 , ;           \ 记下当前位置，填0做占位
: >resolve ( addr -- )  here swap ! ;        \ 将 addr 处的0改为当前地址

: if ( -- ) postpone 0branch >mark ; immediate

: else ( addr1 -- addr2 )
  postpone branch >mark
  swap >resolve ; immediate

: then ( addr -- ) >resolve ; immediate

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

create user-word-begin
