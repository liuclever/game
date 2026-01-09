"""
内网穿透启动脚本
运行后会获取公网地址，并自动更新支付宝配置
"""
import json
from pathlib import Path

def update_alipay_config(public_url: str):
    """更新支付宝配置中的回调地址"""
    config_path = Path(__file__).parent / "infrastructure" / "alipay" / "config.json"
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 更新回调地址
    config["alipay"]["notify_url"] = f"{public_url}/api/pay/notify"
    config["alipay"]["return_url"] = f"{public_url}/sponsor"
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 已更新支付宝配置:")
    print(f"   notify_url: {config['alipay']['notify_url']}")
    print(f"   return_url: {config['alipay']['return_url']}")

def main():
    try:
        from pyngrok import ngrok
        
        print("🚀 正在启动内网穿透...")
        tunnel = ngrok.connect(5000)
        public_url = tunnel.public_url
        
        print(f"\n✅ 内网穿透已启动!")
        print(f"📡 公网地址: {public_url}")
        print(f"🔗 本地地址: http://localhost:5000")
        
        # 自动更新配置
        update_alipay_config(public_url)
        
        print("\n⚠️  注意: 请重启后端服务以加载新配置")
        print("按 Ctrl+C 停止内网穿透...")
        
        # 保持运行
        ngrok.get_ngrok_process().proc.wait()
        
    except ImportError:
        print("❌ 请先安装 pyngrok: pip install pyngrok")
    except KeyboardInterrupt:
        print("\n👋 内网穿透已停止")
        ngrok.kill()

if __name__ == "__main__":
    main()
