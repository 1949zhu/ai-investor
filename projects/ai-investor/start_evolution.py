# -*- coding: utf-8 -*-
"""启动自主进化"""

from autonomous.problem_solver import AutonomousProblemSolver

print("="*60)
print("        AI 自主进化系统启动")
print("="*60)

solver = AutonomousProblemSolver()
result = solver.autonomous_self_improvement()

print("\n" + "="*60)
print("进化周期完成")
print("="*60)
