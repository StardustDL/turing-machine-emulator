; Copyright 2021 StardustDL
; Calculate gcd(a,b)

0 1** *** *** pre1

; pre: split two integer a,b to tape 1,2

pre1 1** 11* rr* pre1
pre1 0** 1** rl* pre2
pre2 1** 1*1 r*r pre2
pre2 *** *** l*l pback0

; back: back to position 0
pback0 1** _** l** pback0
pback0 _** *** r** pback1
pback1 *1* *** *l* pback1
pback1 *_* *** *r* pback2
pback2 **1 *** **l pback2
pback2 **_ *** **r small

sback0 1** *** l** sback0
sback0 _** *** r** sback1
sback1 *1* *** *l* sback1
sback1 *_* *** *r* sback2
sback2 **1 *** **l sback2
sback2 **_ *** **r test1

; small: move min(a,b) to tape 0
small *11 1** rrr small
small *1_ *** lll sback0
small *_1 *** lll sback0

; test: test d is divisor of a and b
test1 11* *** rr* test1
test1 _1* *** l** testb1
test1 1_* *** *l* fail
test1 __* *** ll* testb2

test2 1*1 *** r*r test2
test2 _*1 *** l** testb2
test2 1*_ *** **l fail
test2 _*_ *** l*l halt_final

testb1 1** *** l** testb1
testb1 _** *** r** test1
testb2 1** *** l** testb2
testb2 _** *** r** test2

; fail: test fail, decrease d and test again
fail 1** *** r** fail
fail _** *** l** minus
minus 1** _** l** sback0