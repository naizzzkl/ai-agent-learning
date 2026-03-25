import logging
import os
from datetime import datetime

# 创建 logs 目录（如果不存在）
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 生成日志文件名（按日期）
log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别，INFO 及以上会被记录
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),  # 输出到文件
        logging.StreamHandler()                          # 输出到控制台
    ]
)

# 创建专用日志记录器（可单独获取）
logger = logging.getLogger(__name__)