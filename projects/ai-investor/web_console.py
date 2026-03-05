"""
AI 投资智能体 - 精美 Web 控制台
Apple-inspired 设计语言
"""

import os
import sys
sys.path.insert(0, '.')

os.environ['DASHSCOPE_API_KEY'] = 'sk-fb6aa9235b6b4627aa2ac5f7295db04c'

from flask import Flask, render_template_string, jsonify, request, send_from_directory
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import threading
import time
import hashlib

app = Flask(__name__)

# 基础路径 - 使用绝对路径避免工作目录问题
BASE_PATH = Path(r"D:\openclaw\workspace\projects\ai-investor")
STORAGE_PATH = BASE_PATH / "storage"
REPORTS_PATH = BASE_PATH / "reports"
SOLUTIONS_PATH = BASE_PATH / "solutions"
LOGS_PATH = BASE_PATH / "logs"


# ========== 精美 HTML 模板 ==========
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 投资智能体</title>
    <style>
        :root {
            --bg-primary: #000000;
            --bg-secondary: #1c1c1e;
            --bg-tertiary: #2c2c2e;
            --text-primary: #ffffff;
            --text-secondary: #86868b;
            --accent-green: #30d158;
            --accent-blue: #0a84ff;
            --accent-orange: #ff9f0a;
            --accent-red: #ff453a;
            --accent-purple: #bf5af2;
            --border-color: rgba(255,255,255,0.1);
            --card-radius: 20px;
            --button-radius: 12px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* 背景渐变 */
        .bg-gradient {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 600px;
            background: radial-gradient(ellipse at top, rgba(48,209,88,0.1) 0%, transparent 70%),
                        radial-gradient(ellipse at bottom right, rgba(10,132,255,0.08) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        
        /* 主容器 */
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 24px;
            position: relative;
            z-index: 1;
        }
        
        /* 头部 */
        header {
            text-align: center;
            margin-bottom: 48px;
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 16px;
            background: rgba(48,209,88,0.1);
            border: 1px solid rgba(48,209,88,0.3);
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            color: var(--accent-green);
            margin-bottom: 16px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            animation: pulse 2s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(0.9); }
        }
        
        h1 {
            font-size: 28px;
            font-weight: 700;
            letter-spacing: -0.02em;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #fff 0%, #86868b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .subtitle {
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 400;
        }
        
        /* 网格系统 */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 24px;
            margin-bottom: 32px;
        }
        
        .grid-2 {
            grid-template-columns: repeat(2, 1fr);
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        /* 卡片 */
        .card {
            background: var(--bg-secondary);
            border-radius: var(--card-radius);
            padding: 20px;
            border: 1px solid var(--border-color);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .card:hover {
            transform: translateY(-2px);
            border-color: rgba(255,255,255,0.2);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }
        
        .card-header {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .card-icon {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: -0.01em;
        }
        
        /* 指标卡片 */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
        }
        
        .metric-item {
            background: var(--bg-tertiary);
            border-radius: 16px;
            padding: 20px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-green), var(--accent-blue));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
        }
        
        .metric-label {
            font-size: 13px;
            color: var(--text-secondary);
            margin-top: 8px;
            font-weight: 500;
        }
        
        /* 仪表盘 */
        .gauge-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px 0;
        }
        
        .gauge-wrapper {
            position: relative;
            width: 160px;
            height: 80px;
        }
        
        .gauge-svg {
            width: 100%;
            height: 100%;
        }
        
        .gauge-bg {
            fill: none;
            stroke: var(--bg-tertiary);
            stroke-width: 12;
        }
        
        .gauge-fill {
            fill: none;
            stroke: url(#gauge-gradient);
            stroke-width: 12;
            stroke-linecap: round;
            stroke-dasharray: 251;
            stroke-dashoffset: 251;
            transition: stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .gauge-value {
            position: absolute;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            font-size: 20px;
            font-weight: 700;
        }
        
        /* 列表项 */
        .item-list {
            list-style: none;
        }
        
        .item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            margin: 0 -16px;
            border-radius: 12px;
            transition: background 0.2s;
        }
        
        .item:hover {
            background: rgba(255,255,255,0.03);
        }
        
        .item-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-top: 6px;
            flex-shrink: 0;
        }
        
        .item-indicator.success { background: var(--accent-green); }
        .item-indicator.warning { background: var(--accent-orange); }
        .item-indicator.error { background: var(--accent-red); }
        
        .item-content {
            flex: 1;
            min-width: 0;
        }
        
        .item-title {
            font-size: 15px;
            font-weight: 500;
            margin-bottom: 4px;
            word-break: break-word;
        }
        
        .item-meta {
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        .item-badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-left: 8px;
        }
        
        .badge-high { background: rgba(255,69,58,0.2); color: var(--accent-red); }
        .badge-medium { background: rgba(255,159,10,0.2); color: var(--accent-orange); }
        .badge-low { background: rgba(48,209,88,0.2); color: var(--accent-green); }
        
        /* 按钮 */
        .btn-group {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 20px;
        }
        
        .btn {
            flex: 1;
            min-width: 140px;
            padding: 14px 20px;
            border: none;
            border-radius: var(--button-radius);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-green), #24b346);
            color: #000;
        }
        
        .btn-secondary {
            background: var(--bg-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }
        
        .btn:hover {
            transform: scale(1.02);
        }
        
        .btn-primary:hover {
            box-shadow: 0 10px 30px rgba(48,209,88,0.3);
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        /* 日志 */
        .log-container {
            background: var(--bg-primary);
            border-radius: 16px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
            font-size: 13px;
            border: 1px solid var(--border-color);
        }
        
        .log-entry {
            display: flex;
            gap: 12px;
            padding: 10px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .log-time {
            color: var(--text-secondary);
            font-size: 12px;
            min-width: 70px;
        }
        
        .log-text { flex: 1; }
        .log-info { color: var(--accent-green); }
        .log-warning { color: var(--accent-orange); }
        .log-error { color: var(--accent-red); }
        .log-busy { color: var(--accent-blue); }
        
        /* 进度条 */
        .progress-container {
            margin-top: 16px;
        }
        
        .progress-bar {
            height: 4px;
            background: var(--bg-tertiary);
            border-radius: 2px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
            border-radius: 2px;
            transition: width 0.5s ease;
            width: 0%;
        }
        
        /* 空状态 */
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-secondary);
        }
        
        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
            opacity: 0.5;
        }
        
        /* 滚动条 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-secondary);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--bg-tertiary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: rgba(255,255,255,0.2);
        }
        
        /* 响应式 */
        @media (max-width: 1024px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 640px) {
            .container {
                padding: 24px 16px;
            }
            
            h1 {
                font-size: 32px;
            }
            
            .grid {
                grid-template-columns: 1fr;
            }
            
            .btn-group {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
        
        /* 加载动画 */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255,255,255,0.1);
            border-top-color: var(--accent-green);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    
    <div class="container">
        <header>
            <div class="status-badge">
                <span class="status-dot"></span>
                <span id="status-text">运行中</span>
            </div>
            <h1>AI 投资智能体</h1>
            <p class="subtitle">自主进化 · 智能决策 · 持续学习</p>
            <p class="subtitle" style="margin-top: 8px; font-size: 14px; color: var(--text-secondary);">
                最后更新：<span id="last-update">--:--:--</span>
            </p>
        </header>
        
        <!-- 第一行：核心指标 -->
        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📊</div>
                    <div class="card-title">系统状态</div>
                </div>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-value" id="win-rate">--</div>
                        <div class="metric-label">决策胜率</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="db-size">--</div>
                        <div class="metric-label">数据量 (MB)</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="run-count">--</div>
                        <div class="metric-label">自主运行</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value" id="problems-count">--</div>
                        <div class="metric-label">待解决问题</div>
                    </div>
                </div>
                <div class="gauge-container">
                    <div class="gauge-wrapper">
                        <svg class="gauge-svg" viewBox="0 0 200 100">
                            <defs>
                                <linearGradient id="gauge-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                    <stop offset="0%" style="stop-color:var(--accent-green)"/>
                                    <stop offset="100%" style="stop-color:var(--accent-blue)"/>
                                </linearGradient>
                            </defs>
                            <path class="gauge-bg" d="M 20 80 A 60 60 0 0 1 180 80"/>
                            <path class="gauge-fill" id="gauge-fill" d="M 20 80 A 60 60 0 0 1 180 80" stroke-dasharray="377" stroke-dashoffset="377"/>
                        </svg>
                        <div class="gauge-value" id="gauge-text">--%</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 8px; color: var(--text-secondary); font-size: 13px;">
                    系统置信度
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🔍</div>
                    <div class="card-title">问题与发现</div>
                </div>
                <ul class="item-list" id="problems-list">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>加载中...</div>
                    </div>
                </ul>
                <div class="btn-group">
                    <button class="btn btn-primary" onclick="runAnalysis()">
                        <span>🔍</span> 立即分析
                    </button>
                    <button class="btn btn-secondary" onclick="viewReports()">
                        <span>📄</span> 查看报告
                    </button>
                </div>
            </div>
        </div>
        
        <!-- 第二行：能力和日志 -->
        <div class="grid grid-2">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">🧠</div>
                    <div class="card-title">能力状态</div>
                </div>
                <ul class="item-list" id="capabilities-list">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>加载中...</div>
                    </div>
                </ul>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📜</div>
                    <div class="card-title">实时日志</div>
                </div>
                <div class="log-container" id="log-container">
                    <div class="log-entry">
                        <span class="log-time">--:--:--</span>
                        <span class="log-text log-info">等待日志...</span>
                    </div>
                </div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-fill" id="progress-fill"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 第三行：报告和控制 -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">📋</div>
                    <div class="card-title">最近报告</div>
                </div>
                <ul class="item-list" id="reports-list">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>暂无报告</div>
                    </div>
                </ul>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">💡</div>
                    <div class="card-title">最近改进</div>
                </div>
                <ul class="item-list" id="improvements-list">
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>暂无改进</div>
                    </div>
                </ul>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <div class="card-icon">⚙️</div>
                    <div class="card-title">控制中心</div>
                </div>
                <div style="color: var(--text-secondary); font-size: 14px; margin-bottom: 16px; line-height: 1.6;">
                    手动触发智能体操作，查看系统自主运行过程
                </div>
                <div class="btn-group" style="flex-direction: column;">
                    <button class="btn btn-secondary" onclick="runEvolution()">
                        <span>🧬</span> 自主进化检查
                    </button>
                    <button class="btn btn-secondary" onclick="runProblemSolving()">
                        <span>🔧</span> 自主问题分析
                    </button>
                    <button class="btn btn-primary" onclick="runFullCycle()">
                        <span>🚀</span> 完整自主周期
                    </button>
                    <button class="btn btn-secondary" onclick="refreshData()">
                        <span>🔄</span> 刷新数据
                    </button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const REFRESH_INTERVAL = 5000;
        let isBusy = false;
        
        function formatTime(date) {
            return date.toLocaleTimeString('zh-CN', {hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit'});
        }
        
        function formatNumber(num) {
            if (num >= 1000) return (num/1000).toFixed(1) + 'k';
            return num.toString();
        }
        
        function updateStatus(data) {
            // 指标
            document.getElementById('win-rate').textContent = (data.win_rate * 100).toFixed(0) + '%';
            document.getElementById('db-size').textContent = data.db_size || '--';
            document.getElementById('run-count').textContent = formatNumber(data.run_count || 0);
            document.getElementById('problems-count').textContent = (data.problems || []).length;
            
            // 仪表盘
            const gaugeFill = document.getElementById('gauge-fill');
            const gaugeText = document.getElementById('gauge-text');
            const confidence = data.confidence * 100 || 0;
            const maxOffset = 377;
            const offset = maxOffset - (confidence / 100 * maxOffset);
            gaugeFill.style.strokeDashoffset = offset;
            gaugeText.textContent = confidence.toFixed(0) + '%';
            
            // 置信度颜色
            if (confidence < 40) {
                gaugeText.style.background = 'linear-gradient(135deg, var(--accent-red), var(--accent-orange))';
            } else if (confidence < 60) {
                gaugeText.style.background = 'linear-gradient(135deg, var(--accent-orange), var(--accent-green))';
            } else {
                gaugeText.style.background = 'linear-gradient(135deg, var(--accent-green), var(--accent-blue))';
            }
            gaugeText.style.webkitBackgroundClip = 'text';
            gaugeText.style.webkitTextFillColor = 'transparent';
            
            document.getElementById('last-update').textContent = formatTime(new Date());
        }
        
        function updateProblems(problems) {
            const list = document.getElementById('problems-list');
            if (!problems || problems.length === 0) {
                list.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">✅</div>
                        <div>暂无问题</div>
                    </div>
                `;
                return;
            }
            
            list.innerHTML = problems.map(p => `
                <li class="item">
                    <span class="item-indicator ${p.severity === 'high' ? 'error' : p.severity === 'medium' ? 'warning' : 'success'}"></span>
                    <div class="item-content">
                        <div class="item-title">${escapeHtml(p.problem)}</div>
                        <div class="item-meta">
                            ${escapeHtml(p.category)}
                            <span class="item-badge badge-${p.severity}">${p.severity}</span>
                        </div>
                    </div>
                </li>
            `).join('');
        }
        
        function updateCapabilities(gaps) {
            const list = document.getElementById('capabilities-list');
            if (!gaps || gaps.length === 0) {
                list.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">✅</div>
                        <div>能力完整</div>
                    </div>
                `;
                return;
            }
            
            list.innerHTML = gaps.map(g => `
                <li class="item">
                    <span class="item-indicator ${g.priority === 'high' ? 'warning' : 'success'}"></span>
                    <div class="item-content">
                        <div class="item-title">${escapeHtml(g.capability)}</div>
                        <div class="item-meta">${escapeHtml(g.why_needed)}</div>
                    </div>
                </li>
            `).join('');
        }
        
        function updateReports(reports) {
            const list = document.getElementById('reports-list');
            if (!reports || reports.length === 0) {
                list.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>暂无报告</div>
                    </div>
                `;
                return;
            }
            
            list.innerHTML = reports.slice(0, 5).map(r => `
                <li class="item">
                    <span class="item-indicator success"></span>
                    <div class="item-content">
                        <div class="item-title">${escapeHtml(r.name)}</div>
                        <div class="item-meta">${r.time}</div>
                    </div>
                </li>
            `).join('');
        }
        
        function updateImprovements(improvements) {
            const list = document.getElementById('improvements-list');
            if (!improvements || improvements.length === 0) {
                list.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <div>暂无改进</div>
                    </div>
                `;
                return;
            }
            
            list.innerHTML = improvements.slice(0, 5).map(i => `
                <li class="item">
                    <span class="item-indicator ${i.success ? 'success' : 'warning'}"></span>
                    <div class="item-content">
                        <div class="item-title">${i.success ? '✅' : '⚠️'} ${escapeHtml(i.improvement)}</div>
                        <div class="item-meta">${escapeHtml(i.result || i.reason || '')}</div>
                    </div>
                </li>
            `).join('');
        }
        
        function addLog(message, type = 'info') {
            const container = document.getElementById('log-container');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            
            const typeClass = type === 'error' ? 'log-error' : type === 'warning' ? 'log-warning' : type === 'busy' ? 'log-busy' : 'log-info';
            
            entry.innerHTML = `
                <span class="log-time">${formatTime(new Date())}</span>
                <span class="log-text ${typeClass}">${escapeHtml(message)}</span>
            `;
            container.insertBefore(entry, container.firstChild);
            
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }
        
        function showProgress(show) {
            const fill = document.getElementById('progress-fill');
            fill.style.width = show ? '100%' : '0%';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        async function refreshData() {
            if (isBusy) return;
            
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateStatus(data);
                updateProblems(data.problems);
                updateCapabilities(data.gaps);
                updateReports(data.reports);
                updateImprovements(data.improvements);
            } catch (error) {
                addLog('刷新失败：' + error.message, 'error');
            }
        }
        
        async function runAnalysis() {
            if (isBusy) return;
            isBusy = true;
            addLog('开始分析...', 'busy');
            showProgress(true);
            
            try {
                await fetch('/api/analyze', {method: 'POST'});
                addLog('分析已启动（后台运行）', 'info');
                setTimeout(() => { showProgress(false); isBusy = false; refreshData(); }, 2000);
            } catch (error) {
                addLog('分析失败：' + error.message, 'error');
                isBusy = false;
                showProgress(false);
            }
        }
        
        function viewReports() {
            window.open('/reports', '_blank');
        }
        
        async function runEvolution() {
            if (isBusy) return;
            isBusy = true;
            addLog('启动自主进化检查...', 'busy');
            showProgress(true);
            
            try {
                await fetch('/api/evolution', {method: 'POST'});
                addLog('进化检查已启动', 'info');
                setTimeout(() => { showProgress(false); isBusy = false; refreshData(); }, 2000);
            } catch (error) {
                addLog('进化检查失败：' + error.message, 'error');
                isBusy = false;
                showProgress(false);
            }
        }
        
        async function runProblemSolving() {
            if (isBusy) return;
            isBusy = true;
            addLog('启动自主问题分析...', 'busy');
            showProgress(true);
            
            try {
                await fetch('/api/problems', {method: 'POST'});
                addLog('问题分析已启动', 'info');
                setTimeout(() => { showProgress(false); isBusy = false; refreshData(); }, 2000);
            } catch (error) {
                addLog('问题分析失败：' + error.message, 'error');
                isBusy = false;
                showProgress(false);
            }
        }
        
        async function runFullCycle() {
            if (isBusy) return;
            isBusy = true;
            addLog('🚀 启动完整自主周期...', 'busy');
            showProgress(true);
            
            try {
                await fetch('/api/full-cycle', {method: 'POST'});
                addLog('完整周期已启动（约 1 分钟）', 'info');
                setTimeout(() => { showProgress(false); isBusy = false; refreshData(); }, 2000);
            } catch (error) {
                addLog('完整周期失败：' + error.message, 'error');
                isBusy = false;
                showProgress(false);
            }
        }
        
        // 初始加载
        refreshData();
        addLog('控制台已就绪', 'info');
        
        // 自动刷新
        setInterval(refreshData, REFRESH_INTERVAL);
    </script>
</body>
</html>
"""


# ========== API 端点（与之前相同） ==========

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/test')
def test():
    """测试页面"""
    with open(BASE_PATH / 'simple.html', 'r', encoding='utf-8') as f:
        return f.read()


@app.route('/simple')
def simple():
    """极简测试页面"""
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Test</title></head>
<body style="background:#000;color:#fff;font-family:sans-serif;padding:40px;text-align:center;">
<h1 style="color:#30d158;">✅ 服务器运行正常!</h1>
<p>请访问 <a href="/test" style="color:#30d158;">/test</a> 或 <a href="/" style="color:#30d158;">/</a> 查看界面</p>
<p id="t"></p>
<script>document.getElementById('t').textContent=new Date().toLocaleString('zh-CN');</script>
</body></html>'''


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    # 调试日志
    with open(BASE_PATH / "debug_api.log", 'a', encoding='utf-8') as f:
        f.write(f"\n[{datetime.now().isoformat()}] API called\n")
        f.write(f"STORAGE_PATH: {STORAGE_PATH}\n")
    
    status = {
        "win_rate": 0.5,
        "confidence": 0.6,
        "db_size": 0,
        "run_count": 0,
        "problems": [],
        "gaps": [],
        "reports": [],
        "improvements": []
    }
    
    # 获取决策胜率
    try:
        db_path = STORAGE_PATH / "agent_memory.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT outcome FROM decision_log WHERE outcome IS NOT NULL AND outcome != '待验证' ORDER BY date DESC LIMIT 20")
            decisions = cursor.fetchall()
            conn.close()
            if decisions:
                winning = sum(1 for d in decisions if d[0] and ('收益' in str(d[0]) or '避险' in str(d[0])))
                status["win_rate"] = round(winning / len(decisions), 2)
    except Exception as e:
        print(f"Win rate error: {e}")
    
    # 获取数据库大小
    try:
        db_path = STORAGE_PATH / "ashare.db"
        if db_path.exists():
            status["db_size"] = round(db_path.stat().st_size / (1024*1024), 1)
    except Exception as e:
        print(f"DB size error: {e}")
    
    # 获取运行次数
    try:
        config_path = BASE_PATH / "config" / "scheduler.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                status["run_count"] = config.get('run_count', 0)
    except Exception as e:
        print(f"Run count error: {e}")
    
    # 获取问题
    try:
        db_path = STORAGE_PATH / "problems.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT problem, category, severity FROM problems WHERE status = 'identified' ORDER BY created_at DESC LIMIT 10")
            problems = cursor.fetchall()
            conn.close()
            status["problems"] = [{"problem": p[0], "category": p[1], "severity": p[2]} for p in problems]
    except Exception as e:
        print(f"Problems error: {e}")
    
    # 获取能力缺口
    try:
        db_path = STORAGE_PATH / "problems.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT capability, why_needed, priority FROM capability_gaps ORDER BY created_at DESC LIMIT 10")
            gaps = cursor.fetchall()
            conn.close()
            status["gaps"] = [{"capability": g[0], "why_needed": g[1], "priority": g[2]} for g in gaps]
    except Exception as e:
        print(f"Gaps error: {e}")
    
    # 获取报告
    try:
        reports_dir = REPORTS_PATH / "autonomous"
        if reports_dir.exists():
            reports = list(reports_dir.glob("*.md"))
            reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            status["reports"] = [{"name": r.stem, "time": datetime.fromtimestamp(r.stat().st_mtime).strftime('%Y-%m-%d %H:%M')} for r in reports[:5]]
    except Exception as e:
        print(f"Reports error: {e}")
    
    # 获取改进
    try:
        db_path = STORAGE_PATH / "problems.db"
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT improvement, impact, verified FROM improvements ORDER BY created_at DESC LIMIT 10")
            improvements = cursor.fetchall()
            conn.close()
            status["improvements"] = [{"improvement": i[0], "impact": i[1], "success": bool(i[2])} for i in improvements]
    except Exception as e:
        print(f"Improvements error: {e}")
    
    return jsonify(status)


@app.route('/api/analyze', methods=['POST'])
def run_analysis():
    try:
        from autonomous.evolution_engine import SelfEvolutionEngine
        engine = SelfEvolutionEngine()
        threading.Thread(target=lambda: engine.autonomous_run()).start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/evolution', methods=['POST'])
def run_evolution():
    try:
        from autonomous.evolution_engine import SelfEvolutionEngine
        engine = SelfEvolutionEngine()
        threading.Thread(target=lambda: engine.autonomous_run()).start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/problems', methods=['POST'])
def run_problem_solving():
    try:
        from autonomous.problem_solver import AutonomousProblemSolver
        solver = AutonomousProblemSolver()
        threading.Thread(target=lambda: solver.autonomous_self_improvement()).start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/full-cycle', methods=['POST'])
def run_full_cycle():
    try:
        from autonomous.agent import AutonomousAgent
        agent = AutonomousAgent()
        threading.Thread(target=lambda: agent.full_autonomous_cycle()).start()
        return jsonify({"status": "started"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/reports')
def view_reports():
    reports_dir = REPORTS_PATH / "autonomous"
    reports_html = ''
    if reports_dir.exists():
        reports = sorted(reports_dir.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True)[:10]
        reports_html = ''.join([f'<div style="padding:12px;border-bottom:1px solid rgba(255,255,255,0.1);"><a href="file://{r.absolute()}" target="_blank" style="color:#30d158;text-decoration:none;">{r.name}</a><br><small style="color:#86868b;">{datetime.fromtimestamp(r.stat().st_mtime).strftime("%Y-%m-%d %H:%M")}</small></div>' for r in reports])
    else:
        reports_html = '<p style="color:#86868b;">暂无报告</p>'
    
    return f"""
    <html>
    <head>
        <title>报告目录</title>
        <style>
            body {{ background: #000; color: #fff; font-family: -apple-system, sans-serif; padding: 40px; }}
            h1 {{ color: #30d158; margin-bottom: 20px; }}
            a {{ color: #0a84ff; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            .back {{ color: #86868b; margin-bottom: 30px; display: block; }}
        </style>
    </head>
    <body>
        <a href="/" class="back">← 返回控制台</a>
        <h1>📄 报告目录</h1>
        {reports_html}
    </body>
    </html>
    """


if __name__ == "__main__":
    print("\n" + "="*60)
    print("        AI Investment Agent Console")
    print("="*60)
    print("\n  URL: http://localhost:5000")
    print("\n  Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
