# guanyuan-monitor

观远数据监控技能 - 基于观远数据API和钉钉通知的自动化监控

## Version

1.0.0

## Description

自动化数据监控系统,支持:
- 从观远数据平台获取指标数据
- 基于规则的告警判断(阈值、环比、同比)
- 钉钉消息推送
- 定时任务调度

## Dependencies

### MCP Tools
- `sh_guanyuan_data` - 观远数据查询
- `sh_messagengine_dingtalk` - 钉钉消息发送

### Python Packages
- schedule
- pyyaml

## Usage

```bash
/guanyuan-monitor --config configs/simple_monitor.json
```

## Parameters

- `--config` - 配置文件路径(必填)
- `--once` - 单次执行模式(不启动定时任务)
- `--dry-run` - 测试模式(不发送通知)

## Configuration

配置文件示例见 `configs/examples/`

## Author

Oliver

## Created

2026-03-30
