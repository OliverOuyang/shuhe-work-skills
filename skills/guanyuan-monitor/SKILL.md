> 🚧 **IN DEVELOPMENT - 功能未完整实现**
>
> 本 skill 当前处于**原型阶段**，核心功能尚未实现（所有主要方法为 TODO stubs）。
>
> **已实现**: 项目结构、配置模板、日志框架
> **未实现**: MonitorConfig 加载、AlertRule 逻辑、DataFetcher MCP 集成、DingTalkNotifier、SchedulerManager
>
> **预计完成时间**: 待定

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
