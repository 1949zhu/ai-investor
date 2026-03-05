# -*- coding: utf-8 -*-
"""
GitHub 集成模块 - AI 智能体自主代码管理

功能：
1. 自动检测代码变更
2. 自动提交并推送
3. 查看项目状态
4. 创建/更新 Issue
5. 同步远程仓库
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class GitHubIntegration:
    """GitHub 集成控制器"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = Path(repo_path) if repo_path else Path(__file__).parent.parent
        self.git_dir = self.repo_path / ".git"
        self.status_cache = {}
        
    def run_git(self, *args, capture=True) -> str:
        """执行 git 命令"""
        try:
            cmd = ['git'] + list(args)
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=capture,
                text=True,
                timeout=30
            )
            return result.stdout if capture else None
        except subprocess.TimeoutExpired:
            return f"Error: Command timeout"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_git_initialized(self) -> bool:
        """检查 Git 是否初始化"""
        return self.git_dir.exists()
    
    def init_repo(self) -> Dict:
        """初始化仓库"""
        if self.check_git_initialized():
            return {"status": "exists", "message": "仓库已初始化"}
        
        self.run_git('init')
        self.run_git('config', 'user.name', 'AI Investment Agent')
        self.run_git('config', 'user.email', 'ai-agent@localhost')
        
        return {"status": "success", "message": "仓库初始化完成"}
    
    def get_status(self) -> Dict:
        """获取仓库状态"""
        status_output = self.run_git('status', '--porcelain')
        branch_output = self.run_git('branch', '--show-current')
        
        changed_files = []
        for line in status_output.strip().split('\n'):
            if line.strip():
                status = line[:2].strip()
                file = line[3:]
                changed_files.append({
                    'status': status,
                    'file': file
                })
        
        return {
            'branch': branch_output.strip() or 'main',
            'changed_files': changed_files,
            'has_changes': len(changed_files) > 0
        }
    
    def add_all(self) -> str:
        """添加所有变更"""
        self.run_git('add', '.')
        return "已添加所有变更"
    
    def commit(self, message: str) -> Dict:
        """提交变更"""
        self.run_git('add', '.')
        
        # 生成提交信息
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{message}\n\n[AI Agent] {timestamp}"
        
        self.run_git('commit', '-m', full_message)
        
        return {
            "status": "success",
            "message": message,
            "timestamp": timestamp
        }
    
    def push(self, remote: str = 'origin', branch: str = None) -> Dict:
        """推送到远程"""
        if branch is None:
            branch = self.get_status()['branch']
        
        output = self.run_git('push', '-u', remote, branch, capture=False)
        
        return {
            "status": "success",
            "remote": remote,
            "branch": branch
        }
    
    def pull(self, remote: str = 'origin', branch: str = None) -> Dict:
        """从远程拉取"""
        if branch is None:
            branch = self.get_status()['branch']
        
        self.run_git('pull', remote, branch)
        
        return {
            "status": "success",
            "message": "已同步远程仓库"
        }
    
    def get_log(self, limit: int = 10) -> List[Dict]:
        """获取提交历史"""
        output = self.run_git(
            'log', f'-{limit}',
            '--format=%H|%an|%ae|%ai|%s'
        )
        
        commits = []
        for line in output.strip().split('\n'):
            if line.strip():
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0][:8],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })
        
        return commits
    
    def create_branch(self, name: str) -> Dict:
        """创建新分支"""
        self.run_git('checkout', '-b', name)
        return {
            "status": "success",
            "branch": name
        }
    
    def checkout(self, branch: str) -> Dict:
        """切换分支"""
        self.run_git('checkout', branch)
        return {
            "status": "success",
            "branch": branch
        }
    
    def add_remote(self, name: str, url: str) -> Dict:
        """添加远程仓库"""
        self.run_git('remote', 'add', name, url)
        return {
            "status": "success",
            "name": name,
            "url": url
        }
    
    def get_remotes(self) -> List[Dict]:
        """获取远程仓库列表"""
        output = self.run_git('remote', '-v')
        remotes = []
        for line in output.strip().split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    remotes.append({
                        'name': parts[0],
                        'url': parts[1],
                        'type': 'push' if '(push)' in line else 'fetch'
                    })
        return remotes
    
    def auto_commit_changes(self, category: str = "update") -> Dict:
        """自动提交变更（AI 自主使用）"""
        status = self.get_status()
        
        if not status['has_changes']:
            return {"status": "no_changes", "message": "没有需要提交的变更"}
        
        # 根据变更类型生成提交信息
        messages = {
            "update": "自动更新代码",
            "fix": "修复问题",
            "feature": "新增功能",
            "optimize": "性能优化",
            "docs": "文档更新"
        }
        
        message = messages.get(category, "自动更新")
        
        # 添加文件列表
        files = [f['file'] for f in status['changed_files'][:5]]
        if len(status['changed_files']) > 5:
            files.append(f"... 等 {len(status['changed_files'])} 个文件")
        
        full_message = f"{message}: {', '.join(files)}"
        
        result = self.commit(full_message)
        
        return {
            "status": "success",
            "files_changed": len(status['changed_files']),
            "commit": result
        }
    
    def sync_with_github(self, github_url: str) -> Dict:
        """同步到 GitHub"""
        # 检查是否有远程仓库
        remotes = self.get_remotes()
        has_origin = any(r['name'] == 'origin' for r in remotes)
        
        if not has_origin:
            self.add_remote('origin', github_url)
        
        # 拉取最新代码
        self.pull()
        
        # 提交本地变更
        self.auto_commit_changes()
        
        # 推送
        self.push()
        
        return {
            "status": "success",
            "message": "已与 GitHub 同步"
        }


# ========== 便捷函数 ==========

def quick_setup(github_url: str = None):
    """快速设置 Git 仓库"""
    git = GitHubIntegration()
    
    print("🔧 初始化 Git 仓库...")
    result = git.init_repo()
    print(f"  {result['message']}")
    
    if github_url:
        print(f"\n🔗 添加远程仓库：{github_url}")
        git.add_remote('origin', github_url)
    
    return git


def quick_status():
    """快速查看状态"""
    git = GitHubIntegration()
    status = git.get_status()
    
    print(f"\n📊 仓库状态")
    print(f"  分支：{status['branch']}")
    print(f"  变更文件：{len(status['changed_files'])}")
    
    if status['changed_files']:
        for f in status['changed_files'][:10]:
            print(f"    {f['status']} {f['file']}")
    
    return status


def quick_commit(message: str, push: bool = True):
    """快速提交并推送"""
    git = GitHubIntegration()
    
    print(f"\n💾 提交：{message}")
    result = git.commit(message)
    print(f"  ✅ {result['status']}: {result['timestamp']}")
    
    if push:
        print(f"\n📤 推送到 GitHub...")
        git.push()
        print(f"  ✅ 推送完成")
    
    return result


# ========== CLI 入口 ==========

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("GitHub 集成模块")
        print("\n用法:")
        print("  python github_integration.py status     - 查看状态")
        print("  python github_integration.py commit     - 提交变更")
        print("  python github_integration.py push       - 推送")
        print("  python github_integration.py pull       - 拉取")
        print("  python github_integration.py log        - 查看历史")
        print("  python github_integration.py setup URL  - 设置远程仓库")
        sys.exit(0)
    
    cmd = sys.argv[1]
    git = GitHubIntegration()
    
    if cmd == 'status':
        quick_status()
    
    elif cmd == 'commit':
        message = sys.argv[2] if len(sys.argv) > 2 else "AI Agent 自动提交"
        quick_commit(message)
    
    elif cmd == 'push':
        git.push()
        print("✅ 推送完成")
    
    elif cmd == 'pull':
        git.pull()
        print("✅ 拉取完成")
    
    elif cmd == 'log':
        commits = git.get_log(5)
        for c in commits:
            print(f"  {c['hash']} {c['date'][:10]} {c['message'][:50]}")
    
    elif cmd == 'setup':
        if len(sys.argv) < 3:
            print("❌ 请提供 GitHub 仓库 URL")
            print("   例如：python github_integration.py setup https://github.com/user/repo.git")
        else:
            quick_setup(sys.argv[2])
            print("✅ 设置完成")
    
    else:
        print(f"❌ 未知命令：{cmd}")
