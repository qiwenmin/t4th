: here dp @ ;

: hex $10 base ! ;
: decimal #10 base ! ;

: variable create 0 , ;
: constant create , does> @ ;

: 1+ 1 + ;

: +! swap over @ + swap ! ;
: allot dp +! ;
: rot >r swap r> swap ;

: chars ;
: cells ;

: begin here ; immediate
: again (literal) branch , here - 1+ , ; immediate
