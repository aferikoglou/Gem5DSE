import os
import subprocess

import numpy as np

from pymoo.core.problem import ElementwiseProblem

class OptimizationProblem(ElementwiseProblem):
    def __init__(self, nVar, xL, xU, **kwargs):    
        super().__init__(n_var=nVar, n_obj=2, n_constr=0, xl=xL, xu=xU, type_var=int, **kwargs)
        
    def _gem5Simulation(self, x):
        
        """
        L1 Instruction Cache Size
            * 2kB is encoded to 0
            * 4kB is encoded to 1
            * 8kB is encoded to 2
            * 16kB is encoded to 3
            * 32kB is encoded to 4
            * 64kB is encoded to 5
        L1 Data Cache Size
            * 2kB is encoded to 0
            * 4kB is encoded to 1
            * 8kB is encoded to 2
            * 16kB is encoded to 3
            * 32kB is encoded to 4
            * 64kB is encoded to 5
        L2 Cache Size
            * 128kB is encoded to 0
            * 256kB is encoded to 1
            * 512B is encoded to 2
            * 1024kB is encoded to 3
        Unrolling Factor
            * Unrolling factor is 2 encoded to 0
            * Unrolling factor is 4 encoded to 1
            * Unrolling factor is 8 encoded to 2
            * Unrolling factor is 16 encoded to 3
            * Unrolling factor is 32 encoded to 4
        """

        # Get the actual values for L1I cache size, L1D cache size, L2 cache size, and unrolling factor
        L1ICacheSizeKB  = 2 * (2 ** x[0])
        L1DCacheSizeKB  = 2 * (2 ** x[1])
        L2CacheSizeKB   = 128 * (2 ** x[2])
        unrollingFactor = 2 * (2 ** x[3])
        
        L1ICacheSizeKBSTR = str(L1ICacheSizeKB) + 'kB'
        L1DCacheSizeKBSTR = str(L1DCacheSizeKB) + 'kB'
        L2CacheSizeKBSTR = str(L2CacheSizeKB) + 'kB'
        unrollingFactorSTR = str(unrollingFactor)
        
        # Execute simulation
        gem5Command = "/gem5/build/X86/gem5.opt /gem5/configs/learning_gem5/part1/two_level.py /gem5/tables_UF/tables_uf" + unrollingFactorSTR + ".exe --l1i_size=" + L1ICacheSizeKBSTR + " --l1d_size=" + L1DCacheSizeKBSTR + " --l2_size=" + L2CacheSizeKBSTR
        os.system(gem5Command)

        # Parse output.txt and get the loop execution time in msec
        loopExecutionTimeCC = -1
        
        fr = open('./m5out/stats.txt', 'r')
        lines = fr.readlines()
        fr.close()
        
        pattern = "system.cpu.numCycles"
        for line in lines:
            if pattern in line:
                parts = line.split(" ")
                loopExecutionTimeCC = float(parts[25])
        
        # Get total used memory in KB
        totalMemoryKB = float(L1ICacheSizeKB + L1DCacheSizeKB + L2CacheSizeKB)

        return [loopExecutionTimeCC, totalMemoryKB]
 
    def _evaluate(self, x, out, *args, **kwargs):
        # Get Loop Latency in msec and Total Memory in KB for configuration x
        metrics = self._gem5Simulation(x)
        # Return the results of the evaluated configuration
        out["F"] = np.asarray(metrics)
