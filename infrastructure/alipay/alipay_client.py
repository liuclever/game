"""
支付宝支付客户端
"""
import base64
import json
import time
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlencode, quote_plus
import requests

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
except ImportError:
    raise ImportError("请安装 cryptography: pip install cryptography")


class AlipayClient:
    """支付宝支付客户端"""
    
    GATEWAY_URL = "https://openapi.alipay.com/gateway.do"
    SANDBOX_GATEWAY_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
    
    def __init__(self, config: dict):
        self.app_id = config["app_id"]
        self.notify_url = config.get("notify_url", "")
        self.return_url = config.get("return_url", "")
        self.sign_type = config.get("sign_type", "RSA2")
        self.sandbox = config.get("sandbox", False)
        
        # 加载密钥
        config_dir = Path(__file__).parent
        private_key_path = config_dir / config["private_key_path"]
        public_key_path = config_dir / config["alipay_public_key_path"]
        
        with open(private_key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        
        with open(public_key_path, "rb") as f:
            self.alipay_public_key = serialization.load_pem_public_key(
                f.read(), backend=default_backend()
            )
    
    @property
    def gateway_url(self) -> str:
        return self.SANDBOX_GATEWAY_URL if self.sandbox else self.GATEWAY_URL
    
    def _sign(self, params: dict) -> str:
        """RSA2签名"""
        # 排序并拼接
        sorted_params = sorted(params.items())
        unsigned_str = "&".join(f"{k}={v}" for k, v in sorted_params if v)
        
        # 签名
        if self.sign_type == "RSA2":
            signature = self.private_key.sign(
                unsigned_str.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
        else:
            signature = self.private_key.sign(
                unsigned_str.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA1()
            )
        
        return base64.b64encode(signature).decode("utf-8")
    
    def _verify(self, params: dict, signature: str) -> bool:
        """验证支付宝签名"""
        # 移除sign和sign_type
        params_copy = {k: v for k, v in params.items() if k not in ("sign", "sign_type")}
        sorted_params = sorted(params_copy.items())
        unsigned_str = "&".join(f"{k}={v}" for k, v in sorted_params if v)
        
        try:
            if self.sign_type == "RSA2":
                self.alipay_public_key.verify(
                    base64.b64decode(signature),
                    unsigned_str.encode("utf-8"),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
            else:
                self.alipay_public_key.verify(
                    base64.b64decode(signature),
                    unsigned_str.encode("utf-8"),
                    padding.PKCS1v15(),
                    hashes.SHA1()
                )
            return True
        except Exception:
            return False
    
    def _build_common_params(self, method: str) -> dict:
        """构建公共请求参数"""
        return {
            "app_id": self.app_id,
            "method": method,
            "format": "JSON",
            "charset": "utf-8",
            "sign_type": self.sign_type,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
        }
    
    def page_pay(self, out_trade_no: str, total_amount: str, subject: str, 
                 body: str = "", timeout: str = "30m") -> str:
        """电脑网站支付，返回跳转URL"""
        params = self._build_common_params("alipay.trade.page.pay")
        params["notify_url"] = self.notify_url
        params["return_url"] = self.return_url
        
        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject,
            "body": body,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            "timeout_express": timeout,
        }
        params["biz_content"] = json.dumps(biz_content, ensure_ascii=False)
        params["sign"] = self._sign(params)
        
        return f"{self.gateway_url}?{urlencode(params, quote_via=quote_plus)}"
    
    def wap_pay(self, out_trade_no: str, total_amount: str, subject: str,
                body: str = "", timeout: str = "30m") -> str:
        """手机网站支付，返回跳转URL"""
        params = self._build_common_params("alipay.trade.wap.pay")
        params["notify_url"] = self.notify_url
        params["return_url"] = self.return_url
        
        biz_content = {
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "subject": subject,
            "body": body,
            "product_code": "QUICK_WAP_WAY",
            "timeout_express": timeout,
        }
        params["biz_content"] = json.dumps(biz_content, ensure_ascii=False)
        params["sign"] = self._sign(params)
        
        return f"{self.gateway_url}?{urlencode(params, quote_via=quote_plus)}"
    
    def query(self, out_trade_no: str = None, trade_no: str = None) -> dict:
        """查询订单"""
        params = self._build_common_params("alipay.trade.query")
        
        biz_content = {}
        if out_trade_no:
            biz_content["out_trade_no"] = out_trade_no
        if trade_no:
            biz_content["trade_no"] = trade_no
        
        params["biz_content"] = json.dumps(biz_content, ensure_ascii=False)
        params["sign"] = self._sign(params)
        
        resp = requests.get(self.gateway_url, params=params)
        result = resp.json()
        return result.get("alipay_trade_query_response", {})
    
    def verify_notify(self, params: dict) -> bool:
        """验证异步通知签名"""
        signature = params.get("sign", "")
        if not signature:
            return False
        return self._verify(params, signature)


def generate_out_trade_no(prefix: str = "") -> str:
    """生成订单号"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = "".join(random.choices(string.digits, k=6))
    return f"{prefix}{timestamp}{random_str}"


# 加载配置
def load_alipay_config() -> dict:
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)["alipay"]


# 全局客户端实例
_client: Optional[AlipayClient] = None


def get_alipay_client() -> Optional[AlipayClient]:
    """获取支付宝客户端单例"""
    global _client
    if _client is None:
        try:
            config = load_alipay_config()
            _client = AlipayClient(config)
        except Exception as e:
            print(f"[Alipay] 初始化失败: {e}")
            return None
    return _client
