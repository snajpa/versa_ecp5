from migen import *

from litex.soc.interconnect.csr import *
from litex.soc.interconnect.csr_eventmanager import *
from litex.soc.interconnect import wishbone

class RomPhy(Module, AutoCSR):
    def __init__(self, platform, pads):
        
        self.pads = pads

        self.submodules.ev = EventManager()
        self.ev.oeirq = EventSourceProcess()
        self.ev.finalize()
        self.comb += self.ev.oeirq.trigger.eq(self.pads.oe)

        self.req_addr = CSRStatus(20)
        self.lst_addr = CSRStatus(20)
        self.ans_data = CSRStorage(8)

        self.comb += self.req_addr.status.eq(self.pads.addr_i)
        self.comb += self.pads.data_o.eq(self.ans_data.storage)
        self.comb += If(self.req_addr.status != 0,
                        self.lst_addr.status.eq(self.req_addr.status))