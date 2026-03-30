"""Complete data fetching script for all 5 cards"""
import sys
sys.path.insert(0, 'C:/Users/Oliver/Desktop/数禾工作/16_AI项目/2_预算MMM模型')

from scripts.guanyuan_fetch.main import get_all_cards, prepare_fetch_params, process_card_response, create_initial_metadata
from scripts.guanyuan_fetch.metadata_writer import write_metadata, add_card_result, add_error
from pathlib import Path
from datetime import datetime
import json

# Initialize
metadata = create_initial_metadata()
cards = get_all_cards()
output_dir = Path("Data/guanyuan")

print(f"开始抓取 {len(cards)} 个卡片的数据...")
print(f"时间范围: {metadata['query_parameters']['start_date']} 至 {metadata['query_parameters']['end_date']}\n")

results = []
for i, card in enumerate(cards, 1):
    print(f"[{i}/{len(cards)}] 处理卡片: {card.card_name}")

    try:
        # Prepare parameters
        fetch_params = prepare_fetch_params(card)
        print(f"  - Card ID: {fetch_params['cardId']}")
        print(f"  - 筛选器数量: {len(fetch_params['cardFilters'])}")

        # Save parameters to file for manual MCP call
        params_file = output_dir / f"_params_card{i}.json"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(params_file, 'w', encoding='utf-8') as f:
            json.dump({
                "cardId": fetch_params['cardId'],
                "cardFilters": fetch_params['cardFilters']
            }, f, ensure_ascii=False, indent=2)

        print(f"  - 参数已保存至: {params_file}")
        results.append({
            "card_num": i,
            "card_id": card.card_id,
            "card_name": card.card_name,
            "params_file": str(params_file),
            "status": "params_ready"
        })

    except Exception as e:
        print(f"  ✗ 失败: {str(e)}")
        add_error(metadata, card.card_id, card.card_name, str(e))
        results.append({
            "card_num": i,
            "card_id": card.card_id,
            "card_name": card.card_name,
            "status": "error",
            "error": str(e)
        })

print(f"\n参数准备完成！")
print(f"共准备 {len([r for r in results if r['status'] == 'params_ready'])} 个卡片的参数")
print(f"\n下一步: 使用 MCP 工具调用这些参数获取数据")
