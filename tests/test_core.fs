\ 从 https://forth-standard.org/standard/testsuite 复制的测试用例

\ F.3 Core Tests


\ F.3.1 Basic Assumptions

T{ -> }T                      ( Start with a clean slate )
( Test if any bits are set; Answer in base 1 )
T{ : BITSSET? IF 0 0 ELSE 0 THEN ; -> }T
T{  0 BITSSET? -> 0 }T        ( Zero is all bits clear )
T{  1 BITSSET? -> 0 0 }T      ( Other numbers have at least one bit )
T{ -1 BITSSET? -> 0 0 }T


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
