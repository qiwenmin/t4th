: here dp @ ;

: hex $10 base ! ;
: decimal #10 base ! ;

: 1+ 1 + ;

: +! swap over @ + swap ! ;
: allot dp +! ;
: rot >r swap r> swap ;

: chars ;
: cells ;

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

create user-word-begin
