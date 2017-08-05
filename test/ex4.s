lw F0, 256(R1)
lw F1, 512(R2)
add F2, F0, F1
sub F3, F0, F1
mul F4, F0, F1
div F5, F0, F1
sw F0, 0(R6)
sw F1, 4(R6)
sw F2, 8(R6)
sw F3, 12(R6)
sw F4, 16(R6)
sw F5, 20(R6)
