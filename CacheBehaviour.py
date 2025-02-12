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
system.clk_domain = SrcClockDomain(clock="4GHz", voltage_domain=VoltageDomain())  # Increased clock speed
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('1GB')]  # Increased memory range

# Define x86 CPU
system.cpu = O3CPU()  # Use Out-of-Order CPU for better performance

# Optimized L1, L2, L3 cache hierarchy
system.cpu.icache = L1_ICache(size='64kB', assoc=8, latency='1ns')  # Larger size, higher associativity
system.cpu.dcache = L1_DCache(size='64kB', assoc=8, latency='1ns')
system.l2cache = L2Cache(size='512kB', assoc=16, latency='5ns')
system.l3cache = L3Cache(size='16MB', assoc=32, latency='10ns')  # Increased size and associativity

# Configure Cache Bus
system.membus = SystemXBar()
system.cpu.icache.connectCPU(system.cpu)
system.cpu.dcache.connectCPU(system.cpu)
system.cpu.icache.connectBus(system.membus)
system.cpu.dcache.connectBus(system.membus)
system.l2cache.connectBus(system.membus)
system.l3cache.connectBus(system.membus)

# Optimized DRAM configuration
system.mem_ctrl = DDR4_2400_16x4()  # Faster DDR4 memory with higher bandwidth
system.mem_ctrl.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports
system.mem_ctrl.read_latency = '8ns'  # Reduced latency
system.mem_ctrl.write_latency = '8ns'

# Set prefetcher for better memory access patterns
system.cpu.icache.prefetcher = StridePrefetcher(degree=4, latency='1ns')
system.cpu.dcache.prefetcher = TaggedPrefetcher(degree=8, latency='2ns')

# Enable branch predictor for O3 CPU
system.cpu.branchPred = TournamentBP()

# Simulation setup
root = Root(full_system=False, system=system)
m5.instantiate()

print("Starting Optimized Cache and Performance Simulation...")
exit_event = m5.simulate()
print(f"Exit at tick {m5.curTick()} due to {exit_event.getCause()}")
