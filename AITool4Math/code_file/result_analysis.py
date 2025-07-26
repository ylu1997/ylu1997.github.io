import json
from typing import Optional


def print_filtered_papers_from_emergency(
        emergency_file_path: str,
        score_threshold: int,
        min_score: int = 0,
        show_details: bool = True
):
    """
    从emergency JSON文件中筛选并打印论文信息

    Args:
        emergency_file_path: emergency JSON文件路径
        score_threshold: 评分上限 (K值，不超过此值)
        min_score: 评分下限 (大于此值)
        show_details: 是否显示详细信息
    """
    try:
        with open(emergency_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        all_papers = data.get('all_papers', [])
        filtered_papers = []

        # 筛选条件：有AI评分 且 min_score < score <= score_threshold
        for paper in all_papers:
            ai_eval = paper.get('ai_evaluation')
            if ai_eval and isinstance(ai_eval, dict):
                score = ai_eval.get('score', 0)
                if min_score < score <= score_threshold:
                    filtered_papers.append(paper)

        # 按评分降序排列
        filtered_papers.sort(key=lambda x: x.get('ai_evaluation', {}).get('score', 0), reverse=True)

        print(f"\n{'=' * 60}")
        print(f"筛选条件: {min_score} < 评分 <= {score_threshold}")
        print(f"找到 {len(filtered_papers)} 篇符合条件的论文")
        print(f"{'=' * 60}")

        if not filtered_papers:
            print("未找到符合条件的论文")
            return

        for i, paper in enumerate(filtered_papers, 1):
            ai_eval = paper.get('ai_evaluation', {})
            score = ai_eval.get('score', 0)
            comment = ai_eval.get('comment', '无评论')

            print(f"\n[{i}] 评分: {score}")
            print(f"ID: {paper.get('paper_id', 'N/A')}")
            print(f"标题: {paper.get('title', '无标题')}")

            if show_details:
                print(f"作者: {', '.join(paper.get('authors', []))}")
                print(f"年份: {paper.get('year', 'N/A')}")
                print(f"引用数: {paper.get('citation_count', 'N/A')}")
                print(f"状态: {paper.get('status', 'N/A')}")
                print(f"AI评论: {comment}")

                # 显示摘要前200字符
                abstract = paper.get('abstract', '')
                if abstract:
                    abstract_preview = abstract[:200] + '...' if len(abstract) > 200 else abstract
                    print(f"摘要: {abstract_preview}")

            print("-" * 40)

        # 统计信息
        scores = [p.get('ai_evaluation', {}).get('score', 0) for p in filtered_papers]
        print(f"\n统计信息:")
        print(f"平均评分: {sum(scores) / len(scores):.2f}")
        print(f"最高评分: {max(scores)}")
        print(f"最低评分: {min(scores)}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {emergency_file_path}")
    except json.JSONDecodeError:
        print(f"错误: JSON文件格式错误 {emergency_file_path}")
    except Exception as e:
        print(f"错误: {e}")


def print_papers_by_score_range(emergency_file_path: str, min_score: int, max_score: int):
    """
    简化版本：打印指定评分范围的论文
    """
    print_filtered_papers_from_emergency(
        emergency_file_path=emergency_file_path,
        score_threshold=max_score,
        min_score=min_score,
        show_details=True
    )


# 使用示例函数
def example_usage():
    """
    使用示例
    """
    # # 示例1: 打印评分在60-100之间的论文
    # print_filtered_papers_from_emergency(
    #     emergency_file_path="my_research_emergency.json",
    #     score_threshold=100,
    #     min_score=60
    # )

    # 示例2: 打印评分在K-100之间的论文（简化调用）
    K = 70
    print_papers_by_score_range(
        emergency_file_path="research_state_final.json",
        min_score=K,
        max_score=100
    )

if __name__ == '__main__':
    example_usage()