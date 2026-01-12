#!/usr/bin/env python3
"""
evaluate.py: 情感基准测试统一评估脚本 (中文化优化版)
支持四种评估模式，输入和输出均使用 JSON 格式：

1. classification (分类评估) — 标准标签分类指标 (准确率 Accuracy, 精确率 Precision, 召回率 Recall, F1值)
2. joint (联合评估) — 情感(Emotion)与意图(Intent)的联合标签评估
3. generation (生成评估) — 评估生成文本与参考文本的质量 (BLEU, ROUGE, BERTScore)
4. all (全量评估) — 一条命令运行以上所有评估

使用方法示例:

# 仅运行分类评估
python evaluate.py classification --json results1.json results2.json --output classification.json

# 仅运行联合评估
python evaluate.py joint --json emotions.json --output joint.json

# 仅运行生成评估
python evaluate.py generation --json gen.json --output generation.json

# 一次性运行所有评估
python evaluate.py all \
  --classification-json results1.json \
  --joint-json emotions.json \
  --generation-json gen.json \
  --output-dir results/
"""

import os
import json
import argparse
from typing import List
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from nltk.translate.bleu_score import sentence_bleu
from rouge_score import rouge_scorer
from bert_score import score as bert_score

# ------------------------
# 1. 分类任务评估 (Classification Evaluation)
# 适用于：情绪识别 (如：用户是焦虑还是抑郁？)
# ------------------------
def evaluate_classification(json_paths: List[str], output_metrics: str) -> None:
    targets, preds = [], []
    # 支持传入多个结果文件进行合并计算
    for path in json_paths:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for sample in data:
            # 读取预期值(标签)和预测值
            exp = sample.get('expected_value', '').strip().lower()
            pre = sample.get('predicted_value', '').strip().lower()
            if exp and pre:
                targets.append(exp)
                preds.append(pre)
    
    if targets:
        # 计算核心指标
        metrics = {
            'accuracy': accuracy_score(targets, preds),
            'precision': precision_score(targets, preds, average='weighted', zero_division=0),
            'recall': recall_score(targets, preds, average='weighted', zero_division=0),
            'f1_score': f1_score(targets, preds, average='weighted', zero_division=0)
        }
        # 保存结果
        with open(output_metrics, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"[分类评估] 指标已保存至: {output_metrics}")
    else:
        print("[分类评估] 未找到有效样本。")

# ------------------------
# 2. 情感+意图联合评估 (Joint Emotion + Intent Evaluation)
# 适用于：判断AI是否同时理解了“我很生气(情绪)”和“我想投诉(意图)”
# ------------------------
def evaluate_joint(json_path: str, output_metrics: str) -> None:
    true_e, pred_e, true_i, pred_i = [], [], [], []
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for s in data:
        te = s.get('expected_emotion', '').strip().lower()
        pe = s.get('predicted_emotion', '').strip().lower()
        ti = s.get('expected_intent', '').strip().lower()
        pi = s.get('predicted_intent', '').strip().lower()
        
        if te and pe and ti and pi:
            true_e.append(te)
            pred_e.append(pe)
            true_i.append(ti)
            pred_i.append(pi)
            
    # 将“情绪”和“意图”拼接成一个联合标签进行评估 (例如: happy_encouraging)
    joint_true = [f"{e}_{i}" for e, i in zip(true_e, true_i)]
    joint_pred = [f"{e}_{i}" for e, i in zip(pred_e, pred_i)]
    
    if joint_true:
        metrics = {
            'joint_accuracy': accuracy_score(joint_true, joint_pred),
            'joint_precision': precision_score(joint_true, joint_pred, average='weighted', zero_division=0),
            'joint_recall': recall_score(joint_true, joint_pred, average='weighted', zero_division=0),
            'joint_f1': f1_score(joint_true, joint_pred, average='weighted', zero_division=0),
            'total': len(joint_true)
        }
        with open(output_metrics, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        print(f"[联合评估] 指标已保存至: {output_metrics}")
    else:
        print("[联合评估] 未找到有效样本。")

# ------------------------
# 3. 生成任务评估 (Generation Evaluation)
# 适用于：评估AI写的回复好不好 (对比专家回复)
# ------------------------
def evaluate_generation(json_file: str, output_metrics: str) -> None:
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    bleu_list, rouge_list, bert_list = [], [], []
    
    # 提取所有预测文本和参考文本用于批量计算 BERTScore
    all_preds = []
    all_refs = []
    
    for s in data:
        pred = s.get('prediction', '').strip()
        ref = s.get('reference', '').strip()
        
        if not pred or not ref:
            continue
            
        # 1. 计算 BLEU (n-gram 重合度) - 简单分词
        bleu_val = sentence_bleu([ref.split()], pred.split())
        bleu_list.append(bleu_val)
        
        # 2. 计算 ROUGE-L (最长公共子序列)
        rouge_val = scorer.score(ref, pred)['rougeL'].fmeasure
        rouge_list.append(rouge_val)
        
        all_preds.append(pred)
        all_refs.append(ref)

    # 3. 计算 BERTScore (语义相似度) - 针对中文优化
    # 注意：这里改成了 lang='zh'，适合您的中文毕设
    if all_preds:
        try:
            print("[生成评估] 正在计算 BERTScore (可能需要下载模型)...")
            _, _, F = bert_score(all_preds, all_refs, lang='zh', verbose=True)
            bert_avg = F.mean().item()
        except Exception as e:
            print(f"[警告] BERTScore 计算失败 (可能是网络问题无法下载模型): {e}")
            bert_avg = 0.0
    else:
        bert_avg = 0.0

    metrics = {
        'avg_bleu': sum(bleu_list) / len(bleu_list) if bleu_list else 0,
        'avg_rouge': sum(rouge_list) / len(rouge_list) if rouge_list else 0,
        'avg_bert': bert_avg,
        'total': len(bleu_list)
    }
    
    with open(output_metrics, 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    print(f"[生成评估] 指标已保存至: {output_metrics}")

# ------------------------
# 主入口 + 命令行参数解析
# ------------------------
def main():
    parser = argparse.ArgumentParser(description='心理咨询系统统一评估脚本 (JSON only)')
    sub = parser.add_subparsers(dest='mode', required=True, help='选择评估模式')

    # 模式 1: Classification
    pc = sub.add_parser('classification', help='运行分类指标评估')
    pc.add_argument('--json', nargs='+', required=True, help='输入的结果JSON文件路径 (支持多个)')
    pc.add_argument('--output', required=True, help='输出的指标JSON文件路径')

    # 模式 2: Joint
    pj = sub.add_parser('joint', help='运行情感+意图联合评估')
    pj.add_argument('--json', required=True, help='输入的联合结果JSON文件路径')
    pj.add_argument('--output', required=True, help='输出的指标JSON文件路径')

    # 模式 3: Generation
    pg = sub.add_parser('generation', help='运行生成文本质量评估')
    pg.add_argument('--json', required=True, help='输入的生成结果JSON文件路径')
    pg.add_argument('--output', required=True, help='输出的指标JSON文件路径')

    # 模式 4: All
    pa = sub.add_parser('all', help='一次性运行所有评估')
    pa.add_argument('--classification-json', nargs='+', help='分类结果文件路径')
    pa.add_argument('--joint-json', help='联合结果文件路径')
    pa.add_argument('--generation-json', help='生成结果文件路径')
    pa.add_argument('--output-dir', required=True, help='所有指标文件的输出目录')

    args = parser.parse_args()

    # 根据模式执行相应函数
    if args.mode == 'classification':
        evaluate_classification(args.json, args.output)
    elif args.mode == 'joint':
        evaluate_joint(args.json, args.output)
    elif args.mode == 'generation':
        evaluate_generation(args.json, args.output)
    elif args.mode == 'all':
        os.makedirs(args.output_dir, exist_ok=True)
        if args.classification_json:
            evaluate_classification(args.classification_json, os.path.join(args.output_dir, 'classification_metrics.json'))
        if args.joint_json:
            evaluate_joint(args.joint_json, os.path.join(args.output_dir, 'joint_metrics.json'))
        if args.generation_json:
            evaluate_generation(args.generation_json, os.path.join(args.output_dir, 'generation_metrics.json'))

if __name__ == '__main__':
    main()

# ==========================================
# 数据文件格式说明 (请确保您的测试结果符合以下格式)
# ==========================================

# 1. 分类结果文件 (results.json)
# [
#   {"video":"case_id_1", "expected_value":"positive", "predicted_value":"neutral"},
#   {"video":"case_id_2", "expected_value":"negative", "predicted_value":"negative"}
# ]

# 2. 联合评估文件 (emotions.json)
# [
#   {
#     "modal_path": "case_id_1",
#     "expected_emotion": "happy", "expected_intent": "encouraging",
#     "predicted_emotion": "happy", "predicted_intent": "encouraging"
#   }
# ]

# 3. 生成结果文件 (gen.json)
# [
#   {
#     "video": "case_id_1",
#     "prediction": "AI生成的回复内容...",
#     "reference": "专家/咨询师的标准回复..."
#   }
# ]