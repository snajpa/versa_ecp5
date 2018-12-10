#!/usr/bin/env python3

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.build.generic_platform import *
from litex.boards.platforms import versa_ecp5

from litex.soc.cores.clock import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

import ecp5ddrphy
from litedram.modules import SDRAMModule, _TechnologyTimings, _SpeedgradeTimings

_ddram_io = [
    ("ddram", 0,
        Subsignal("a", Pins(
            "P2 C4 E5 F5 B3 F4 B5 E4",
            "C5 E3 D5 B4 C3"),
            IOStandard("SSTL135_I")),
        Subsignal("ba", Pins("P5 N3 M3"), IOStandard("SSTL135_I")),
        Subsignal("ras_n", Pins("P1"), IOStandard("SSTL135_I")),
        Subsignal("cas_n", Pins("L1"), IOStandard("SSTL135_I")),
        Subsignal("we_n", Pins("M1"), IOStandard("SSTL135_I")),
        Subsignal("cs_n", Pins("K1"), IOStandard("SSTL135_I")),
        Subsignal("dm", Pins("J4 H5"), IOStandard("SSTL135_I")),
        Subsignal("dq", Pins(
            "L5 F1 K4 G1 L4 H1 G2 J3",
            "D1 C1 E2 C2 F3 A2 E1 B1"),
            IOStandard("SSTL135_I"),
            Misc("TERMINATION=75")),
        Subsignal("dqs_p", Pins("K2 H4"), IOStandard("SSTL135D_I")),
        Subsignal("dqs_n", Pins("J1 G5"), IOStandard("SSTL135D_I")),
        Subsignal("clk_p", Pins("P3"), IOStandard("SSTL135D_I")),
        Subsignal("clk_n", Pins("P4"), IOStandard("SSTL135D_I")),
        Subsignal("cke", Pins("N2"), IOStandard("SSTL135_I")),
        Subsignal("odt", Pins("L2"), IOStandard("SSTL135_I")),
        Subsignal("reset_n", Pins("N4"), IOStandard("SSTL135_I")),
        Misc("SLEW=FAST"),
    )
]

class MT41K64M16(SDRAMModule):
    memtype = "DDR3"
    # geometry
    nbanks = 8
    nrows  = 8192
    ncols  = 1024
    # timings
    technology_timings = _TechnologyTimings(tREFI=64e6/8192, tWTR=(4, 7.5), tCCD=(4, None), tRRD=(4, 10))
    speedgrade_timings = {
        "800": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=64, tFAW=(None, 50), tRAS=37.5),
        "1066": _SpeedgradeTimings(tRP=13.1, tRCD=13.1, tWR=13.1, tRFC=86, tFAW=(None, 50), tRAS=37.5),
        "1333": _SpeedgradeTimings(tRP=13.5, tRCD=13.5, tWR=13.5, tRFC=107, tFAW=(None, 45), tRAS=36),
        "1600": _SpeedgradeTimings(tRP=13.75, tRCD=13.75, tWR=13.75, tRFC=128, tFAW=(None, 40), tRAS=35),
    }
    speedgrade_timings["default"] = speedgrade_timings["1600"]


class _CRG(Module):
    def __init__(self, platform, sys_clk_freq):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys2x = ClockDomain(reset_less=True)

        # # #

        # clk / rst
        clk100 = platform.request("clk100")
        rst_n = platform.request("rst_n")
        platform.add_period_constraint(clk100, 10.0)

        # pll
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_sys2x, 2*sys_clk_freq)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | ~rst_n)


class BaseSoC(SoCSDRAM):
    csr_map = {
        "ddrphy":    16,
    }
    csr_map.update(SoCSDRAM.csr_map)
    def __init__(self, **kwargs):
        platform = versa_ecp5.Platform(toolchain="diamond")
        platform.add_extension(_ddram_io)
        sys_clk_freq = int(50e6)
        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
                          cpu_type="picorv32", l2_size=32,
                          integrated_rom_size=0x8000,
                          **kwargs)

        # crg
        self.submodules.crg = _CRG(platform, sys_clk_freq)

        # sdram
        self.submodules.ddrphy = ecp5ddrphy.ECP5DDRPHY(
            platform.request("ddram"),
            sys_clk_freq=sys_clk_freq)
        sdram_module = MT41K64M16(sys_clk_freq, "1:4")
        self.register_sdram(self.ddrphy,
            sdram_module.geom_settings,
            sdram_module.timing_settings)

        # led blinking
        led_counter = Signal(32)
        self.sync += led_counter.eq(led_counter + 1)
        self.comb += platform.request("user_led", 0).eq(led_counter[26])


def main():
    parser = argparse.ArgumentParser(description="LiteX SoC port to the ULX3S")
    builder_args(parser)
    soc_sdram_args(parser)
    args = parser.parse_args()

    soc = BaseSoC(**soc_sdram_argdict(args))
    builder = Builder(soc, **builder_argdict(args))
    builder.build(toolchain_path="/usr/local/diamond/3.10_x64/bin/lin64")


if __name__ == "__main__":
    main()
