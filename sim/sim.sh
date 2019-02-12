#!/usr/bin/env bash
set -ex
ECP5=/usr/local/diamond/3.10_x64/cae_library/simulation/verilog/ecp5u
TOP=dqsbuf_tb
iverilog -s $TOP -o $TOP -Dmixed_hdl $ECP5/DQSBUFM.v $ECP5/IDDRX2DQA.v tb.v
vvp $TOP