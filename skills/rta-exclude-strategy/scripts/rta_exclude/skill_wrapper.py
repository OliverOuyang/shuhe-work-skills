"""
RTA排除策略分析 Skill Wrapper
"""
import sys
from pathlib import Path
from typing import Dict, Optional, List, Union

def run_rta_exclude_strategy(
    data_path: str,
    ctrl_group_value: str,
    output_dir: Optional[str] = None,
    old_exclude_rule: Optional[Union[str, List[str]]] = None,
    spr_threshold: float = 0.10,
    max_exclude_ratio: float = 0.20,
    verbose: bool = True
) -> Dict:
    result = {"success": False, "output_file": None, "summary": {}, "error": None}
    try:
        data_path_obj = Path(data_path)
        if not data_path_obj.is_absolute():
            data_path_obj = Path.cwd() / data_path_obj
        if not data_path_obj.exists():
            raise FileNotFoundError(f"File not found: {data_path_obj}")
        
        original_impl_path = Path(__file__).parent.parent
        sys.path.insert(0, str(original_impl_path))
        
        from data_preprocessing import load_data, preprocess_data, split_control_group, validate_data
        from place_in_out_algorithm import run_place_in_out_algorithm
        from report_generator import generate_report
        
        df = load_data(str(data_path_obj))
        df = preprocess_data(df)
        validate_data(df)
        df_combined, df_ctrl = split_control_group(df, ctrl_group_value)
        algorithm_result = run_place_in_out_algorithm(df_combined, df_ctrl, spr_threshold=spr_threshold, max_exclude_ratio=max_exclude_ratio)
        
        old_list = old_exclude_rule.split(',') if isinstance(old_exclude_rule, str) else (old_exclude_rule or [])
        report_path = generate_report(algorithm_result, old_list, output_path=output_dir or '.')
        
        result["success"] = True
        result["output_file"] = str(Path(report_path).absolute())
        result["summary"] = {k: len(algorithm_result[k]) for k in ['initial_region', 'place_in_region', 'place_out_region', 'exclude_region']}
        return result
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {str(e)}"
        return result
    finally:
        if 'original_impl_path' in locals():
            try:
                sys.path.remove(str(original_impl_path))
            except ValueError:
                pass

def validate_config(data_path: str, ctrl_group_value: str, output_dir: Optional[str] = None) -> Dict:
    result = {"valid": True, "data_file_exists": False, "errors": []}
    try:
        dp = Path(data_path) if Path(data_path).is_absolute() else Path.cwd() / data_path
        if not dp.exists():
            result["errors"].append(f"File not found: {dp}")
            result["valid"] = False
        else:
            result["data_file_exists"] = True
    except Exception as e:
        result["errors"].append(str(e))
        result["valid"] = False
    return result
