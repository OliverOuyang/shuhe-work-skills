"""
数据预处理模块
负责数据加载、清洗和模型分组聚合
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# 模型名到原始列名的默认映射
MODEL_COLUMN_DEFAULTS = {
    'V8': 'v8_ato_safe_bin_req',
    'V9RN': 'merge_ato_safe_v9_rn_bin_req',
    'V10': 'v10_model_bin_req',
}


def _get_raw_column_name(model_name, df_columns):
    """
    智能匹配原始列名

    查找顺序:
    1. 默认映射表
    2. 列名直接匹配
    3. 小写模糊匹配

    Args:
        model_name: 模型名称 (如 'V8', 'V10')
        df_columns: DataFrame 列名列表

    Returns:
        str: 匹配到的原始列名

    Raises:
        ValueError: 无法找到对应列
    """
    # 1. 先查默认映射
    if model_name in MODEL_COLUMN_DEFAULTS:
        default_col = MODEL_COLUMN_DEFAULTS[model_name]
        if default_col in df_columns:
            return default_col
    # 2. 如果数据中已有该模型名(如直接叫V8), 直接用
    if model_name in df_columns:
        return model_name
    # 3. 模糊匹配(小写)
    lower_name = model_name.lower()
    for col in df_columns:
        if lower_name in col.lower():
            return col
    raise ValueError(f"无法找到模型 {model_name} 对应的列")


def load_data(file_path, model_x='V8', model_y='V9RN'):
    """
    加载数据文件

    Args:
        file_path: 数据文件路径，支持CSV或Excel格式
        model_x: X轴模型名称 (默认V8)
        model_y: Y轴模型名称 (默认V9RN)

    Returns:
        DataFrame: 加载的数据
    """
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_path}")

    print(f"数据加载完成，共 {len(df)} 行")

    # 动态构建列名映射: 将原始列名映射到内部标准名 V8/V9RN
    model_x_col = _get_raw_column_name(model_x, df.columns)
    model_y_col = _get_raw_column_name(model_y, df.columns)

    column_mapping = {
        model_x_col: 'V8',      # 内部统一用 V8
        model_y_col: 'V9RN',    # 内部统一用 V9RN
    }

    # act_type -> group 映射(如果需要)
    if 'act_type' in df.columns and 'group' not in df.columns:
        column_mapping['act_type'] = 'group'
    elif 'group' in df.columns:
        pass  # 已有 group 列, 跳过映射

    df = df.rename(columns=column_mapping)
    print(f"字段映射完成: {list(column_mapping.keys())} -> {list(column_mapping.values())}")

    return df


def preprocess_data(df):
    r"""
    数据预处理（仅3步）

    步骤1：将所有 `/N`、`#N/A`、`\N` 值替换为 0
    步骤2：转换数值列为正确的数据类型
    步骤3：分别对V8和V9RN模型分组聚合为12组

    Args:
        df: 原始数据DataFrame

    Returns:
        DataFrame: 预处理后的数据
    """
    print("\n" + "="*80)
    print("数据预处理")
    print("="*80)

    # 步骤1：替换缺失值为0
    print("\n步骤1：处理缺失值")
    missing_values = ['/N', '#N/A', '\\N', 'nan', 'NaN', 'NA', 'N/A']
    df = df.replace(missing_values, 0)
    df = df.fillna(0)
    print("  缺失值已替换为0")

    # 如果数据中没有cost字段,添加默认值0
    if 'cost' not in df.columns:
        df['cost'] = 0
        print("  数据中缺少cost字段,已添加默认值0(CPS指标将无法准确计算)")

    # 步骤2：转换数值列为正确的数据类型
    print("\n步骤2：转换数值列类型")
    numeric_columns = ['expo_cnt', 'cost', 't3_ato', 't3_safe_adt', 't3_loan_amt']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            print(f"  {col}: 转换为数值类型")

    # 步骤3：模型分组聚合
    print("\n步骤3：模型分组聚合")
    df = aggregate_model_groups(df)

    print("\n数据预处理完成")
    print(f"  最终数据行数: {len(df)}")

    return df


def aggregate_model_groups(df):
    """
    模型分组聚合

    聚合逻辑：
    - 01q-09q → 01Q
    - 10q → 02Q
    - 11q → 03Q
    - 12q → 04Q
    - ...
    - 20q → 12Q
    - UNK → UNK（保持不变）

    Args:
        df: 包含V8和V9RN列的DataFrame

    Returns:
        DataFrame: 聚合后的数据
    """
    def _vectorized_map(series):
        """将01q-20q向量化映射到01Q-12Q"""
        # 提取数字部分（仅匹配以 q 结尾的字符串）
        num = series.str.extract(r'^(\d+)q$', expand=False).astype(float)
        # 1-9 → '01Q'；10-20 → '{num-8:02d}Q'；其余 → 'UNK'
        q_label = np.where(
            (num >= 10) & (num <= 20),
            (num - 8).astype('Int64').astype(str).str.zfill(2) + 'Q',
            np.where((num >= 1) & (num <= 9), '01Q', 'UNK')
        )
        # NaN / 'UNK' 原值保持 'UNK'
        return np.where(series.isna() | (series == 'UNK') | (num.isna() & (series != 'UNK')),
                        'UNK', q_label)

    # 聚合V8
    if 'V8' in df.columns:
        df['V8_Q'] = _vectorized_map(df['V8'].astype(str).where(df['V8'].notna(), other=np.nan))
        print(f"  V8聚合完成: {df['V8'].nunique()} 个分组 → {df['V8_Q'].nunique()} 个分组")

    # 聚合V9RN
    if 'V9RN' in df.columns:
        df['V9RN_Q'] = _vectorized_map(df['V9RN'].astype(str).where(df['V9RN'].notna(), other=np.nan))
        print(f"  V9RN聚合完成: {df['V9RN'].nunique()} 个分组 → {df['V9RN_Q'].nunique()} 个分组")

    return df


def split_control_group(df, ctrl_group_value):
    """
    分离对照组和全量数据

    Args:
        df: 预处理后的数据
        ctrl_group_value: 对照组标识值

    Returns:
        tuple: (df_combined全量数据, df_ctrl对照组数据)
    """
    print("\n" + "="*80)
    print("分离对照组数据")
    print("="*80)

    # 全量数据
    df_combined = df.copy()

    # 对照组数据
    df_ctrl = df[df['group'] == ctrl_group_value].copy()

    print(f"\n全量数据: {len(df_combined)} 行")
    print(f"对照组数据: {len(df_ctrl)} 行")
    print(f"对照组占比: {len(df_ctrl)/len(df_combined)*100:.2f}%")

    return df_combined, df_ctrl


def validate_data(df):
    """
    验证数据完整性

    Args:
        df: 数据DataFrame

    Raises:
        ValueError: 如果数据不符合要求
    """
    required_columns = ['V8_Q', 'V9RN_Q', 'group', 'expo_cnt', 'cost',
                       't3_ato', 't3_safe_adt', 't3_loan_amt']

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"缺少必需字段: {missing_columns}")

    # 验证模型分组格式
    v8_groups = df['V8_Q'].unique()
    v9_groups = df['V9RN_Q'].unique()

    valid_groups = [f'{i:02d}Q' for i in range(1, 13)] + ['UNK']

    invalid_v8 = [g for g in v8_groups if g not in valid_groups]
    invalid_v9 = [g for g in v9_groups if g not in valid_groups]

    if invalid_v8:
        raise ValueError(f"V8_Q包含无效分组: {invalid_v8}")
    if invalid_v9:
        raise ValueError(f"V9RN_Q包含无效分组: {invalid_v9}")

    print("\n数据验证通过")
