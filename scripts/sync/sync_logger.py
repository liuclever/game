"""
同步日志记录模块
"""
import sys
import io
from datetime import datetime
from typing import Optional

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


class SyncLogger:
    """同步日志记录器"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.stats = {
            'tables_processed': 0,
            'tables_skipped': 0,
            'rows_inserted': 0,
            'rows_updated': 0,
            'rows_skipped': 0,
            'errors': 0,
        }
    
    def _write(self, message: str, level: str = 'INFO'):
        """写入日志"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_message + '\n')
            except Exception as e:
                print(f"[警告] 无法写入日志文件: {e}")
    
    def info(self, message: str):
        """信息日志"""
        self._write(message, 'INFO')
    
    def success(self, message: str):
        """成功日志"""
        self._write(message, 'SUCCESS')
    
    def warning(self, message: str):
        """警告日志"""
        self._write(message, 'WARNING')
    
    def error(self, message: str):
        """错误日志"""
        self._write(message, 'ERROR')
        self.stats['errors'] += 1
    
    def table_start(self, table_name: str):
        """表同步开始"""
        self.info(f"开始同步表: {table_name}")
    
    def table_success(self, table_name: str, inserted: int, updated: int, skipped: int):
        """表同步成功"""
        self.stats['tables_processed'] += 1
        self.stats['rows_inserted'] += inserted
        self.stats['rows_updated'] += updated
        self.stats['rows_skipped'] += skipped
        self.success(f"表 {table_name} 同步完成: 插入 {inserted}, 更新 {updated}, 跳过 {skipped}")
    
    def table_skip(self, table_name: str, reason: str):
        """跳过表"""
        self.stats['tables_skipped'] += 1
        self.warning(f"跳过表 {table_name}: {reason}")
    
    def print_summary(self):
        """打印统计摘要"""
        self.info("=" * 60)
        self.info("同步统计摘要")
        self.info("=" * 60)
        self.info(f"处理的表数: {self.stats['tables_processed']}")
        self.info(f"跳过的表数: {self.stats['tables_skipped']}")
        self.info(f"插入的行数: {self.stats['rows_inserted']}")
        self.info(f"更新的行数: {self.stats['rows_updated']}")
        self.info(f"跳过的行数: {self.stats['rows_skipped']}")
        self.info(f"错误数: {self.stats['errors']}")
        self.info("=" * 60)


# 全局日志实例
_logger: Optional[SyncLogger] = None


def get_logger(log_file: Optional[str] = None) -> SyncLogger:
    """获取日志实例"""
    global _logger
    if _logger is None:
        _logger = SyncLogger(log_file)
    return _logger
