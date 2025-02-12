from m5.objects import *
from m5.util import addToPath
import os

# Import paths and x86 system setup
addToPath('../../')
from configs.common import Simulation
from configs.common.Caches import *
from configs.common.Options import addCommonOptions

# Define system
system = System()

# Optimized clock settings
system.clk_domain = SrcClockDomain(clock="4GHz", voltage_domain=VoltageDomain())  # High clock frequency
system.mem_mode = 'timing'  # Timing mode for detailed simulations
system.mem_ranges = [AddrRange('1GB')]  # Increased memory range

# Define x86 CPU
system.cpu = O3CPU()  # Out-of-Order CPU for better instruction-level parallelism

# Optimized L1, L2, L3 cache hierarchy
system.cpu.icache = L1_ICache(size='64kB', assoc=8, latency='1ns')  # Larger, more associative L1
system.cpu.dcache = L1_DCache(size='64kB', assoc=8, latency='1ns')
system.l2cache = L2Cache(size='512kB', assoc=16, latency='4ns')  # Balanced size and associativity for L2
system.l3cache = L3Cache(size='16MB', assoc=32, latency='8ns')  # Large shared L3 cache

# Coherence protocol
system.cache_line_size = 64  # Standard cache line size
system.coherence_protocol = 'MOESI'  # Advanced coherence protocol for improved memory consistency

# Configure Cache Bus
system.membus = SystemXBar()
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)
system.l2cache.connectBus(system.membus)
system.l3cache.connectBus(system.membus)

# Optimized DRAM configuration
system.mem_ctrl = DDR4_2400_16x4()  # Faster DDR4 memory with high bandwidth
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.read_latency = '8ns'  # Reduced read latency
system.mem_ctrl.write_latency = '8ns'  # Reduced write latency
system.mem_ctrl.burst_length = 8  # Optimized for higher throughput

# Prefetchers for improved memory access
system.cpu.icache.prefetcher = StridePrefetcher(degree=4, latency='1ns')  # Efficient for sequential access
system.cpu.dcache.prefetcher = TaggedPrefetcher(degree=8, latency='2ns')  # Handles irregular patterns

# Enable branch predictor for O3 CPU
system.cpu.branchPred = TournamentBP()  # Advanced branch prediction for reduced pipeline stalls

# Simulation setup
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting Optimized Simulation with Best Performance and Memory Consistency...")
exit_event = m5.simulate()
print(f"Exit at tick {m5.curTick()} due to {exit_event.getCause()}")
