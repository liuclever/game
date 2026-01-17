# MCP 服务器配置说明

## 概述

本文档说明如何配置 Model Context Protocol (MCP) 服务器以连接远程 MySQL 数据库。

## 快速开始

1. **复制配置模板**: 项目根目录包含 `mcp_config_template.json` 文件
2. **配置 Cursor**: 按照下面的步骤将配置添加到 Cursor 设置中
3. **重启 Cursor**: 使配置生效
4. **测试连接**: 运行测试脚本验证连接

## 配置步骤

### 方法 1: 通过 Cursor 设置界面配置（推荐）

1. **打开 Cursor 设置**:
   - Windows/Linux: 按 `Ctrl + Shift + P`，输入 "Preferences: Open User Settings (JSON)"
   - 或直接打开设置文件: `%APPDATA%\Cursor\User\settings.json` (Windows)
   - Mac: `~/Library/Application Support/Cursor/User/settings.json`

2. **添加 MCP 配置**:
   在设置文件中添加以下配置（如果已有 `mcpServers` 字段，则合并配置）:

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": [
        "-y",
        "mcpp-mysql@latest"
      ],
      "env": {
        "MCP_ACCESS_KEY": "mcp_a1e3c7a560ec4f83a6fa77bd3e025876",
        "MYSQL_HOST": "8.146.206.229",
        "MYSQL_DATABASE": "game_tower",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "Wxs1230.0"
      },
      "autoApprove": [
        "read_query"
      ]
    },
    "prompt": {
      "command": "npx",
      "args": [
        "-y",
        "mcpp-prompt@latest"
      ],
      "env": {
        "MCP_ACCESS_KEY": "mcp_a1e3c7a560ec4f83a6fa77bd3e025876"
      }
    }
  }
}
```

3. **保存并重启 Cursor**

### 方法 2: 使用配置文件模板

项目根目录包含 `mcp_config_template.json` 文件，您可以：
1. 复制其内容
2. 添加到 Cursor 设置中
3. 或根据 Cursor 版本要求放置到相应位置

1. 打开 Cursor 设置：
   - Windows/Linux: `Ctrl + ,` 或 `File > Preferences > Settings`
   - Mac: `Cmd + ,` 或 `Code > Preferences > Settings`

2. 搜索 "MCP" 或 "Model Context Protocol"

3. 找到 MCP 服务器配置部分，添加以下配置：

```json
{
  "mcpServers": {
    "mysql": {
      "command": "npx",
      "args": [
        "-y",
        "mcpp-mysql@latest"
      ],
      "env": {
        "MCP_ACCESS_KEY": "mcp_a1e3c7a560ec4f83a6fa77bd3e025876",
        "MYSQL_HOST": "8.146.206.229",
        "MYSQL_DATABASE": "game_tower",
        "MYSQL_USER": "root",
        "MYSQL_PASSWORD": "Wxs1230.0"
      },
      "autoApprove": [
        "read_query"
      ]
    },
    "prompt": {
      "command": "npx",
      "args": [
        "-y",
        "mcpp-prompt@latest"
      ],
      "env": {
        "MCP_ACCESS_KEY": "mcp_a1e3c7a560ec4f83a6fa77bd3e025876"
      }
    }
  }
}
```

4. 保存设置并重启 Cursor

## 数据库连接信息

- **主机**: 8.146.206.229
- **端口**: 3306 (默认)
- **数据库**: game_tower
- **用户名**: root
- **密码**: Wxs1230.0

## 验证配置

配置完成后，可以通过以下方式验证：

1. **使用测试脚本**（已创建）:
   ```bash
   python scripts/test_remote_db_connection.py
   ```

2. **在 Cursor 中测试 MCP 连接**:
   - 配置成功后，MCP 工具应该可用
   - 可以尝试查询数据库

## 注意事项

1. **安全性**: 
   - 配置文件包含敏感信息（密码），请勿提交到公共仓库
   - 建议将 `.cursor/mcp.json` 添加到 `.gitignore`

2. **网络要求**:
   - 确保可以访问远程数据库服务器 (8.146.206.229:3306)
   - 检查防火墙设置

3. **依赖要求**:
   - 需要安装 Node.js 和 npm（用于运行 npx）
   - MCP 服务器将通过 npx 自动下载

## 故障排除

### 连接失败

1. 检查网络连接
2. 验证数据库服务器是否运行
3. 确认防火墙规则允许连接
4. 验证用户名和密码是否正确

### MCP 服务器未启动

1. 确保已安装 Node.js
2. 检查 npx 是否可用: `npx --version`
3. 查看 Cursor 的 MCP 日志

## 相关文件

- `.cursor/mcp.json` - MCP 配置文件
- `scripts/test_remote_db_connection.py` - 数据库连接测试脚本
- `SERVER_CONFIG.md` - 服务器配置信息
