from m5.objects import *
from m5.util import addToPath
import os

addToPath('../../')
from configs.common import Simulation
from configs.common.Options import addCommonOptions

# Define system
system = System()
system.clk_domain = SrcClockDomain(clock="3GHz", voltage_domain=VoltageDomain())
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('2GB')]

# Define CPU
system.cpu = TimingSimpleCPU()

# Optimized DRAM controller with reduced latencies
system.membus = SystemXBar()
system.mem_ctrl = DDR4_2400_8x8()  # Upgrade to DDR4 for higher bandwidth
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.read_latency = '8ns'  # Reduced read latency
system.mem_ctrl.write_latency = '8ns'  # Reduced write latency
system.mem_ctrl.burst_length = 8  # Optimize burst length for better throughput
system.mem_ctrl.port = system.membus.mem_side_ports

# Enable prefetching to improve memory access patterns
system.cpu.icache = L1_ICache(size='64kB', assoc=8, latency='1ns')  # Larger, more associative L1 cache
system.cpu.dcache = L1_DCache(size='64kB', assoc=8, latency='1ns')
system.cpu.icache.prefetcher = StridePrefetcher(degree=4, latency='1ns')  # Efficient for sequential access
system.cpu.dcache.prefetcher = TaggedPrefetcher(degree=8, latency='2ns')  # Handles irregular access patterns

# Connect CPU to bus
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)

# Simulation setup
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting Optimized DRAM Efficiency Evaluation...")
exit_event = m5.simulate()
print(f"Exit at tick {m5.curTick()} due to {exit_event.getCause()}")
