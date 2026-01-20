#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导航后白屏问题诊断

问题描述：
- 点击"返回地图首页"或"返回游戏首页"能正常跳转
- 但是页面显示白屏（空白）
- 点击刷新后就能正常显示数据

根本原因：
- 导航成功，但目标组件的数据加载失败
- 可能是 onMounted 钩子中的异步请求出错
- 可能是数据加载时抛出异常但未被捕获
- 可能是组件渲染时数据为空导致渲染失败
"""

print("=" * 60)
print("导航后白屏问题诊断")
print("=" * 60)

print("\n问题特征：")
print("1. 导航成功（URL 改变）")
print("2. 页面白屏（无内容显示）")
print("3. 刷新后正常（说明数据加载逻辑本身没问题）")

print("\n可能原因：")
print("1. 组件 onMounted 中的异步请求失败")
print("2. 数据加载时抛出异常但未被捕获")
print("3. 组件渲染时数据为空导致渲染失败")
print("4. 路由导航时组件状态未正确重置")
print("5. 异步请求的 loading 状态未正确处理")

print("\n需要检查的文件：")
print("1. MainPage.vue - 首页组件")
print("2. MapPage.vue - 地图页组件")
print("3. 这两个组件的 onMounted 钩子")
print("4. 这两个组件的数据加载函数")

print("\n修复方案：")
print("1. 在 onMounted 中添加 try-catch 错误处理")
print("2. 在数据加载函数中添加错误处理")
print("3. 添加 loading 状态和错误状态显示")
print("4. 确保数据为空时也能正常渲染")
print("5. 添加详细的调试日志")
