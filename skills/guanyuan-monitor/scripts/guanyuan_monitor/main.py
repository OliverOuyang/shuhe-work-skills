"""观远数据监控主入口"""

import argparse
import logging
from pathlib import Path

from monitor_config import MonitorConfig
from data_fetcher import DataFetcher
from alert_rules import create_rule
from dingtalk_notifier import DingTalkNotifier
from scheduler_manager import SchedulerManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GuanyuanMonitor:
    """观远数据监控主类"""

    def __init__(self, config_path: str, dry_run: bool = False):
        """
        初始化监控器

        Args:
            config_path: 配置文件路径
            dry_run: 是否为测试模式
        """
        self.config = MonitorConfig(config_path)
        self.data_fetcher = DataFetcher()
        self.notifier = DingTalkNotifier()
        self.dry_run = dry_run

        logger.info(f"Monitor initialized with config: {config_path}")
        if dry_run:
            logger.warning("Running in DRY-RUN mode - no notifications will be sent")

    def run_monitor(self):
        """执行一次监控检查"""
        # TODO: 实现监控执行逻辑
        logger.info("Running monitor check...")
        pass

    def start_scheduled_monitoring(self):
        """启动定时监控"""
        # TODO: 实现定时监控逻辑
        logger.info("Starting scheduled monitoring...")
        pass


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='观远数据监控')
    parser.add_argument(
        '--config',
        required=True,
        help='配置文件路径'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='单次执行模式(不启动定时任务)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='测试模式(不发送通知)'
    )

    args = parser.parse_args()

    monitor = GuanyuanMonitor(args.config, dry_run=args.dry_run)

    if args.once:
        monitor.run_monitor()
    else:
        monitor.start_scheduled_monitoring()


if __name__ == "__main__":
    main()
