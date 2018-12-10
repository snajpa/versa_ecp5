#!/usr/bin/env python3

import argparse

from migen import *
from migen.genlib.resetsync import AsyncResetSynchronizer

from litex.boards.platforms import versa_ecp5

from litex.soc.cores.clock import *
from litex.soc.integration.soc_sdram import *
from litex.soc.integration.builder import *

from litedram.modules import AS4C32M16
from litedram.phy import GENSDRPHY
from litedram.core.controller import ControllerSettings


class _CRG(Module):
    def __init__(self, platform):
        self.clock_domains.cd_sys = ClockDomain()
        self.clock_domains.cd_sys_ps = ClockDomain()

        # # #

        # clk / rst
        clk100 = platform.request("clk100")
        rst_n = platform.request("rst_n")
        platform.add_period_constraint(clk100, 10.0)

        # pll
        self.submodules.pll = pll = ECP5PLL()
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, 50e6)
        self.specials += AsyncResetSynchronizer(self.cd_sys, ~pll.locked | ~rst_n)


class BaseSoC(SoCSDRAM):
    def __init__(self, **kwargs):
        platform = versa_ecp5.Platform(toolchain="diamond")
        platform.add_extension(versa_ecp5._ecp5_soc_hat_io)
        sys_clk_freq = int(50e6)
        SoCSDRAM.__init__(self, platform, clk_freq=sys_clk_freq,
                          cpu_type="picorv32", l2_size=32,
                          integrated_rom_size=0x8000,
                          integrated_main_ram_size=0x8000,
                          **kwargs)

        self.submodules.crg = _CRG(platform)

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
