lw F1, 256(R1)
lw F2, 512(R2)
and F3, F1, F2
or F4, F1, F2
not F5, F1
not F6, F2
sw F1, 0(R6)
sw F2, 4(R6)
sw F3, 8(R6)
sw F4, 12(R6)
sw F5, 16(R6)
sw F6, 20(R6)
