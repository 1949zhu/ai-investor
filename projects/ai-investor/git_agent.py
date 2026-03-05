# -*- coding: utf-8 -*-
"""
AI 自主代码管理 - 智能体自主控制 Git 仓库

功能：
1. 监控代码变更
2. 自主提交有意义的变更
3. 自动同步 GitHub
4. 生成变更日志
5. 创建 Issue/PR（需要 API）
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from github_integration import GitHubIntegration
import dashscope
from dashscope import Generation


class AutonomousCodeManager:
    """AI 自主代码管理器"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.git = GitHubIntegration(str(self.base_path))
        self.storage_path = self.base_path / "storage"
        self.logs_path = self.base_path / "logs" / "git"
        self.logs_path.mkdir(parents=True, exist_ok=True)
        
    def monitor_and_commit(self) -> Dict:
        """监控变更并自主提交"""
        print("="*60)
        print("        🔍 AI 代码监控")
        print("="*60)
        
        # 检查变更
        status = self.git.get_status()
        
        if not status['has_changes']:
            print("\n✅ 没有需要提交的变更")
            return {"status": "no_changes"}
        
        print(f"\n📝 发现 {len(status['changed_files'])} 个变更文件")
        
        # 智能分类变更
        categories = self._classify_changes(status['changed_files'])
        
        # 为每类变更生成提交信息
        commits = []
        for category, files in categories.items():
            message = self._generate_commit_message(category, files)
            print(f"\n  📦 {category}: {len(files)} 个文件")
            print(f"     提交信息：{message[:50]}...")
            
            # 临时只添加这些文件
            for f in files:
                self.git.run_git('add', f)
            
            result = self.git.commit(message)
            commits.append({
                "category": category,
                "files": len(files),
                "message": message
            })
        
        print(f"\n✅ 完成 {len(commits)} 个提交")
        
        return {
            "status": "success",
            "commits": commits,
            "total_files": len(status['changed_files'])
        }
    
    def _classify_changes(self, files: List[Dict]) -> Dict[str, List[str]]:
        """智能分类变更"""
        categories = {
            "feature": [],      # 新功能
            "fix": [],          # 修复
            "optimize": [],     # 优化
            "docs": [],         # 文档
            "config": [],       # 配置
            "other": []         # 其他
        }
        
        for f in files:
            filepath = f['file']
            status = f['status']
            
            # 根据文件路径和状态分类
            if filepath.endswith('.md'):
                categories['docs'].append(filepath)
            elif filepath.endswith('.json') or filepath.endswith('.yaml'):
                categories['config'].append(filepath)
            elif 'test' in filepath.lower():
                categories['fix'].append(filepath)
            elif 'autonomous' in filepath or 'agent' in filepath:
                categories['feature'].append(filepath)
            elif 'optimize' in filepath or 'performance' in filepath:
                categories['optimize'].append(filepath)
            else:
                categories['other'].append(filepath)
        
        # 移除空类别
        return {k: v for k, v in categories.items() if v}
    
    def _generate_commit_message(self, category: str, files: List[str]) -> str:
        """生成提交信息"""
        messages = {
            "feature": f"feat: 自主开发新功能 ({len(files)} 个文件)",
            "fix": f"fix: 自主修复问题 ({len(files)} 个文件)",
            "optimize": f"perf: 自主优化性能 ({len(files)} 个文件)",
            "docs": f"docs: 自主更新文档 ({len(files)} 个文件)",
            "config": f"chore: 自主更新配置 ({len(files)} 个文件)",
            "other": f"chore: 自主更新 ({len(files)} 个文件)"
        }
        
        base = messages.get(category, "chore: 自主更新")
        
        # 使用 LLM 生成更详细的提交信息
        try:
            prompt = f"""为以下代码变更生成简短的提交信息（一行，不超过 50 字）：
类别：{category}
文件：{', '.join(files[:3])}{'...' if len(files) > 3 else ''}

只返回提交信息，不要其他内容。"""
            
            response = dashscope.Generation.call(
                model='qwen-plus',
                prompt=prompt,
                api_key=os.environ.get('DASHSCOPE_API_KEY')
            )
            
            if response.status_code == 200:
                llm_message = response.output.text.strip()
                if len(llm_message) < 50:
                    return llm_message
        except:
            pass
        
        return base
    
    def sync_to_github(self, github_url: str = None) -> Dict:
        """同步到 GitHub"""
        print("="*60)
        print("        📤 同步到 GitHub")
        print("="*60)
        
        # 先提交本地变更
        self.monitor_and_commit()
        
        # 检查远程仓库
        remotes = self.git.get_remotes()
        
        if not github_url and not any(r['name'] == 'origin' for r in remotes):
            print("\n❌ 未配置远程仓库")
            print("   请使用：python github_integration.py setup <URL>")
            return {"status": "error", "reason": "no_remote"}
        
        if github_url and not any(r['name'] == 'origin' for r in remotes):
            print(f"\n🔗 添加远程仓库：{github_url}")
            self.git.add_remote('origin', github_url)
        
        # 拉取最新
        print("\n📥 拉取远程变更...")
        self.git.pull()
        
        # 推送
        print("\n📤 推送本地提交...")
        self.git.push()
        
        print("\n✅ 同步完成")
        
        return {
            "status": "success",
            "message": "已同步到 GitHub"
        }
    
    def generate_changelog(self, days: int = 7) -> str:
        """生成变更日志"""
        commits = self.git.get_log(50)
        
        changelog = f"# 变更日志\n\n"
        changelog += f"**生成时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        changelog += f"**统计范围：** 最近 {days} 天\n\n"
        
        # 按日期分组
        by_date = {}
        for commit in commits:
            date = commit['date'][:10]
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(commit)
        
        for date, day_commits in sorted(by_date.items(), reverse=True):
            changelog += f"## {date}\n\n"
            for c in day_commits:
                changelog += f"- {c['message']} `[{c['hash']}]`\n"
            changelog += "\n"
        
        # 保存
        changelog_file = self.logs_path / f"changelog_{datetime.now().strftime('%Y%m%d')}.md"
        with open(changelog_file, 'w', encoding='utf-8') as f:
            f.write(changelog)
        
        return changelog
    
    def get_project_status(self) -> Dict:
        """获取项目完整状态"""
        git_status = self.git.get_status()
        commits = self.git.get_log(10)
        
        # 统计
        total_commits_output = self.git.run_git('rev-list', '--count', 'HEAD').strip()
        total_commits = int(total_commits_output) if total_commits_output and total_commits_output.isdigit() else 0
        
        return {
            "branch": git_status['branch'],
            "has_changes": git_status['has_changes'],
            "changed_files": len(git_status['changed_files']),
            "total_commits": total_commits,
            "recent_commits": commits,
            "remotes": self.git.get_remotes()
        }
    
    def autonomous_git_workflow(self) -> Dict:
        """自主 Git 工作流"""
        print("="*60)
        print("        🤖 AI 自主 Git 工作流")
        print("="*60)
        
        results = []
        
        # 1. 检查状态
        print("\n【1/4】检查项目状态...")
        status = self.get_project_status()
        print(f"  分支：{status['branch']}")
        print(f"  总提交：{status['total_commits']}")
        print(f"  待提交变更：{status['changed_files']} 个文件")
        results.append({"step": "status", "data": status})
        
        # 2. 监控并提交
        print("\n【2/4】监控并自主提交...")
        commit_result = self.monitor_and_commit()
        results.append({"step": "commit", "data": commit_result})
        
        # 3. 生成变更日志
        print("\n【3/4】生成变更日志...")
        changelog = self.generate_changelog()
        print(f"  ✅ 已生成")
        results.append({"step": "changelog", "status": "success"})
        
        # 4. 同步到 GitHub（如果有配置）
        print("\n【4/4】同步到 GitHub...")
        if status['remotes']:
            sync_result = self.sync_to_github()
            results.append({"step": "sync", "data": sync_result})
        else:
            print("  ⚠️  未配置远程仓库，跳过")
            results.append({"step": "sync", "status": "skipped", "reason": "no_remote"})
        
        print("\n" + "="*60)
        print("                    ✅ 自主工作流完成")
        print("="*60)
        
        return {
            "status": "success",
            "results": results
        }


# ========== CLI 入口 ==========

if __name__ == "__main__":
    import sys
    
    manager = AutonomousCodeManager()
    
    if len(sys.argv) < 2:
        print("AI 自主代码管理")
        print("\n用法:")
        print("  python git_agent.py status    - 查看项目状态")
        print("  python git_agent.py commit    - 自主提交变更")
        print("  python git_agent.py sync      - 同步到 GitHub")
        print("  python git_agent.py changelog - 生成变更日志")
        print("  python git_agent.py workflow  - 完整自主工作流")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == 'status':
        status = manager.get_project_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    
    elif cmd == 'commit':
        manager.monitor_and_commit()
    
    elif cmd == 'sync':
        github_url = sys.argv[2] if len(sys.argv) > 2 else None
        manager.sync_to_github(github_url)
    
    elif cmd == 'changelog':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        changelog = manager.generate_changelog(days)
        print(changelog)
    
    elif cmd == 'workflow':
        manager.autonomous_git_workflow()
    
    else:
        print(f"❌ 未知命令：{cmd}")
