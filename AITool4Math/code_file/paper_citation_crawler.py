import json
from enum import Enum
from typing import List, Dict, Optional, Any
from jsonschemaGenAI import SchemaJsonGenAI
from Semantic_Scholar_Fetcher import SemanticScholarFetcher
import atexit



class PaperStatus(Enum):
    UNQUERIED = "未查询"
    FETCHED = "已获取"
    EVALUATED = "已评论"
    ADOPTED = "已采纳"
    COMPLETED = "已完成"


class Paper:
    def __init__(self, paper_id: str, title: str = "", abstract: str = "", authors: Optional[List[str]] = None,
                 year: int = 0, citation_count: int = 0, status: PaperStatus = PaperStatus.UNQUERIED,
                 ai_evaluation: Optional[Dict] = None, citations: Optional[List[str]] = None):
        self.paper_id = paper_id
        self.title = title
        self.abstract = abstract
        self.authors = authors if authors else []
        self.year = year
        self.citation_count = citation_count
        self.status = status
        self.ai_evaluation = ai_evaluation if ai_evaluation else {}
        self.citations = citations if citations else []


class AIPaperResearch:
    def __init__(
            self,
            root_paper_ids: List[str],
            prompt: str,
            max_depth: int = 4,
            top_k: int = 30,
            max_input_tokens: int = 3000,
            api_key: Optional[str] = None,
            model_name: str = "gemini-1.5-flash",
            verbose: bool = True,
            semantic_scholar_api_key: Optional[str] = None,
            auto_save_path: Optional[str] = None  # 新增自动保存路径参数
    ):
        self.papers: Dict[str, Paper] = {}
        for pid in root_paper_ids:
            self.papers[pid] = Paper(paper_id=pid)
        self.prompt = prompt
        self.max_depth = max_depth
        self.top_k = top_k
        self.max_input_tokens = max_input_tokens
        self.current_depth = 0
        self.verbose = verbose
        self.schema = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "本轮论文所在index"},
                    "comment": {"type": "string", "description": "评论内容"},
                    "score": {"type": "integer", "description": "打分"}
                },
                "required": ["index", "comment", "score"]
            }
        }
        self.gen_ai_client = SchemaJsonGenAI(
            schema=self.schema,
            api_key=api_key,
            model_name=model_name,
            verbose=False
        )
        # 实例化SemanticScholarFetcher，传入API key（如果需要）
        if semantic_scholar_api_key != None:
            self.fetcher = SemanticScholarFetcher(semantic_scholar_api_key)
        else:
            self.fetcher = SemanticScholarFetcher()

        # 自动保存配置
        self.auto_save_path = auto_save_path or "emergency_save"
        self.emergency_save_enabled = True

        # 注册退出时保存函数
        atexit.register(self._emergency_save)

        if self.verbose:
            print(f"[初始化] 已注册紧急保存机制，保存路径: {self.auto_save_path}_emergency.json")

    def _emergency_save(self):
        """
        紧急保存函数，在程序退出时自动调用
        """
        if not self.emergency_save_enabled:
            return

        try:
            state = self.save_state()
            filename = f"{self.auto_save_path}_emergency.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            print(f"[紧急保存] 状态已保存到: {filename}")
        except Exception as e:
            print(f"[紧急保存] 保存失败: {e}")

    def disable_emergency_save(self):
        """
        禁用紧急保存（正常完成时调用）
        """
        self.emergency_save_enabled = False
        if self.verbose:
            print("[紧急保存] 已禁用紧急保存机制")

    def fetch_paper_details(self, paper_ids: List[str]) -> None:
        try:
            papers_info = self.fetcher.get_papers_batch(paper_ids)
            count = 0
            for info in papers_info:
                pid = info.get("paperId") or info.get("paper_id")
                if pid and pid in self.papers:
                    paper = self.papers[pid]
                    paper.title = info.get("title", "")
                    paper.abstract = info.get("abstract", "")
                    paper.authors = [a.get("name", "") for a in info.get("authors", [])] if info.get("authors") else []
                    paper.year = info.get("year", 0)
                    paper.citation_count = info.get("citationCount", 0)
                    paper.status = PaperStatus.FETCHED
                    count += 1
            if self.verbose:
                print(f"[fetch_paper_details] 成功获取 {count} 篇论文详情")
        except Exception as e:
            if self.verbose:
                print(f"[fetch_paper_details] 批量获取论文详情失败: {e}")

    def ai_evaluate_papers(self, papers: List[Paper]) -> None:
        def batch_papers_by_token_limit(papers: List[Paper], max_tokens: int) -> List[List[Paper]]:
            batches = []
            current_batch = []
            current_tokens = 0
            for p in papers:
                text = f"论文标题: {p.title}\n摘要: {p.abstract}\n"
                tokens = self.gen_ai_client.estimate_tokens(text)
                if tokens > max_tokens:
                    if current_batch:
                        batches.append(current_batch)
                        current_batch = []
                        current_tokens = 0
                    batches.append([p])
                    continue
                if current_tokens + tokens > max_tokens:
                    if current_batch:
                        batches.append(current_batch)
                    current_batch = [p]
                    current_tokens = tokens
                else:
                    current_batch.append(p)
                    current_tokens += tokens
            if current_batch:
                batches.append(current_batch)
            return batches

        fetched_papers = [p for p in papers if p.status == PaperStatus.FETCHED]
        batches = batch_papers_by_token_limit(fetched_papers, self.max_input_tokens)

        system_prompt = self.prompt

        for batch in batches:
            # 动态构造schema，顶层对象，comment1,score1,...必需字段
            properties = {}
            required = []
            for i, paper in enumerate(batch, 1):
                properties[f"comment{i}"] = {
                    "type": "string",
                    "description": f"第{i}篇论文({paper.paper_id})的评论，限制100字以内",
                    "maxLength": 200
                }
                properties[f"score{i}"] = {
                    "type": "integer",
                    "description": f"第{i}篇论文({paper.paper_id})的评分"
                }
                required.extend([f"comment{i}", f"score{i}"])

            dynamic_schema = {
                "type": "object",
                "properties": properties,
                "required": required
            }

            self.gen_ai_client.set_schema(dynamic_schema)

            batch_texts = [f"论文标题: {p.title}\n摘要: {p.abstract}" for p in batch]
            full_input = system_prompt + "\n\n" + "\n\n".join(batch_texts)

            try:
                academic_config = {
                    "temperature": 0.2,  # 较低的温度，使输出更加聚焦和分析性
                    "top_p": 0.95,  # 较高的top_p，确保全面覆盖学术概念
                    "top_k": 40,  # 较高的top_k，允许多样化的学术术语
                }
                response = self.gen_ai_client.generate_text(full_input, config=academic_config)
                eval_result = json.loads(response.text)
                # 判断返回是否为dict且包含所有必需字段
                if not isinstance(eval_result, dict) or not all(field in eval_result for field in required):
                    if self.verbose:
                        print(f"[ai_evaluate_papers] 返回结果格式异常，跳过该批次")
                    continue
                for i, paper in enumerate(batch, 1):
                    paper.ai_evaluation = {
                        "comment": eval_result.get(f"comment{i}", ""),
                        "score": eval_result.get(f"score{i}", 0),
                        "index": i
                    }
                    paper.status = PaperStatus.EVALUATED  # 修改状态为已评论
                if self.verbose:
                    print(f"[ai_evaluate_papers] 完成对 {len(batch)} 篇论文的AI评分")
            except json.JSONDecodeError as jde:
                if self.verbose:
                    print(f"[ai_evaluate_papers] JSON解析错误: {jde}")
            except Exception as e:
                if self.verbose:
                    print(f"[ai_evaluate_papers] 批量评分失败: {e}")

    def rank_and_filter(self, papers: List[Paper]) -> None:
        evaluated_papers = [p for p in papers if p.status == PaperStatus.EVALUATED]
        evaluated_papers.sort(key=lambda x: x.ai_evaluation.get("score", 0), reverse=True)
        for i, paper in enumerate(evaluated_papers):
            if i < self.top_k:
                paper.status = PaperStatus.ADOPTED  # 高分采纳
            else:
                paper.status = PaperStatus.COMPLETED  # 低分直接完成
        if self.verbose:
            print(f"[rank_and_filter] 采纳前 {self.top_k} 篇论文，其他标记已完成")

    def fetch_citations(self, adopted_papers: List[Paper]) -> List[str]:
        new_paper_ids = []
        try:
            citations_map = self.fetcher.get_citations_batch_smart([p.paper_id for p in adopted_papers])
            for paper in adopted_papers:
                if paper.status == PaperStatus.ADOPTED:
                    cids = citations_map.get(paper.paper_id, [])
                    # 如果之前已获取过引用，且本次无新增，标记完成
                    if paper.citations and set(cids).issubset(set(paper.citations)):
                        paper.status = PaperStatus.COMPLETED
                    else:
                        paper.citations = cids
                        for cid in cids:
                            if cid not in self.papers:
                                self.papers[cid] = Paper(paper_id=cid)
                                new_paper_ids.append(cid)
            for pid in new_paper_ids:
                self.papers[pid].status = PaperStatus.UNQUERIED
            if self.verbose:
                print(f"[fetch_citations] 新增 {len(new_paper_ids)} 篇引用论文")
        except Exception as e:
            if self.verbose:
                print(f"[fetch_citations] 获取引用失败: {e}")
        return new_paper_ids

    def mark_completed(self, adopted_papers: List[Paper]) -> None:
        for paper in adopted_papers:
            if paper.status == PaperStatus.ADOPTED:
                paper.status = PaperStatus.COMPLETED
        if self.verbose:
            print(f"[mark_completed] 标记 {len(adopted_papers)} 篇论文为已完成")

    def save_state(self) -> Dict:
        """
        保存当前状态为JSON格式，包含未查询论文ID列表、已评论论文ID列表和所有论文详情
        """
        unqueried_ids = [pid for pid, p in self.papers.items() if p.status == PaperStatus.UNQUERIED]
        evaluated_ids = [pid for pid, p in self.papers.items() if p.status == PaperStatus.EVALUATED]
        all_papers = []
        for p in self.papers.values():
            all_papers.append({
                "paper_id": p.paper_id,
                "title": p.title,
                "abstract": p.abstract,
                "authors": p.authors,
                "year": p.year,
                "citation_count": p.citation_count,
                "status": p.status.value,
                "ai_evaluation": p.ai_evaluation,
                "citations": p.citations
            })
        return {
            "unqueried_paper_ids": unqueried_ids,
            "evaluated_paper_ids": evaluated_ids,
            "all_papers": all_papers,
            "current_depth": self.current_depth
        }

    def run(self, save_path: Optional[str] = None):
        """
        主流程控制，循环处理未查询论文，深度限制max_depth
        每次循环都保存状态到JSON文件
        """
        try:
            while self.current_depth < self.max_depth:
                unqueried_papers = [p for p in self.papers.values() if p.status == PaperStatus.UNQUERIED]
                if not unqueried_papers:
                    break

                if self.verbose:
                    print(f"\n=== 开始第 {self.current_depth + 1} 轮处理 ===")

                # 1. 获取未查询论文信息
                self.fetch_paper_details([p.paper_id for p in unqueried_papers])

                # 2. AI评分评价
                fetched_papers = [p for p in self.papers.values() if p.status == PaperStatus.FETCHED]
                self.ai_evaluate_papers(fetched_papers)

                # 3. 按评分排序采纳
                evaluated_papers = [p for p in self.papers.values() if p.status == PaperStatus.EVALUATED]
                self.rank_and_filter(evaluated_papers)

                # 4. 获取采纳论文引用，设置新论文状态为未查询
                adopted_papers = [p for p in self.papers.values() if p.status == PaperStatus.ADOPTED]
                self.fetch_citations(adopted_papers)

                # 5. 标记已采纳论文为已完成
                self.mark_completed(adopted_papers)

                # 6. 更新深度
                self.current_depth += 1

                # 7. 保存当前轮次状态
                state = self.save_state()
                if save_path:
                    filename = f"{save_path}_depth_{self.current_depth}.json"
                else:
                    filename = f"research_state_depth_{self.current_depth}.json"

                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(state, f, ensure_ascii=False, indent=2)
                    if self.verbose:
                        print(f"[保存状态] 第 {self.current_depth} 轮状态已保存到: {filename}")
                except Exception as e:
                    if self.verbose:
                        print(f"[保存状态] 保存失败: {e}")

                if self.verbose:
                    print(f"=== 第 {self.current_depth} 轮处理完成 ===\n")

            # 最终状态保存
            final_state = self.save_state()
            final_filename = f"{save_path}_final.json" if save_path else "research_state_final.json"
            try:
                with open(final_filename, 'w', encoding='utf-8') as f:
                    json.dump(final_state, f, ensure_ascii=False, indent=2)
                if self.verbose:
                    print(f"[最终保存] 研究完成，最终状态保存到: {final_filename}")
            except Exception as e:
                if self.verbose:
                    print(f"[最终保存] 保存失败: {e}")

            # 正常完成，禁用紧急保存
            self.disable_emergency_save()
            return final_state

        except KeyboardInterrupt:
            if self.verbose:
                print("\n[中断] 检测到用户中断，触发紧急保存...")
            raise
        except Exception as e:
            if self.verbose:
                print(f"\n[异常] 程序异常退出: {e}，触发紧急保存...")
            raise

if __name__ == '__main__':
    paper_ids = ["ce60f33d657f970fd89ff549761f6f110d86e785"]
    research_interest = """
研究兴趣：
Newton-Okounkov体构造技术，包括flag方法、valuation方法和截面方法，旨在获取复射影代数簇上的更多几何信息，结合凸几何、热带几何与组合几何，关注infinitesimal Newton-Okounkov体，避免超越和算术方法，纯数学范畴，排除用户提及范围以外的跨学科内容。

评分标准：

| 评分维度                                    | 权重  |
|---------------------------------------------|-------|
| 理论通用性（复射影代数簇上的代数几何，结合凸几何、热带几何、组合几何） | 30%   |
| Newton-Okounkov体构造技术的多样性与深度（flag、valuation、section等） | 25%   |
| 几何信息获取能力及应用价值                    | 20%   |
| 是否涉及infinitesimal Newton-Okounkov体      | 15%   |
| 具体例子的数量与质量                          | 10%   |
| 是否避免用户提及范围以外的跨学科内容，以及空摘要、无效摘要        | 额外扣分 |

评分说明：
1. 理论通用性：考察理论是否适用于复射影代数簇上的代数几何，结合凸几何、热带几何、组合几何，且属于纯数学范畴，避免超越和算术方法。
2. 构造技术多样性与深度：涉及的Newton-Okounkov体构造技术种类越多、方法越深入，评分越高。
3. 几何信息获取能力：文献通过Newton-Okounkov体技术获得更多几何信息及应用价值越高，评分越高。
4. infinitesimal Newton-Okounkov体：涉及该内容的文献评分较高。
5. 具体例子：若文献主要为具体例子展示且缺乏通用理论，评分适当降低。
6. 用户提及范围以外的跨学科内容：涉及用户未提及范围的跨学科内容（如物理、生物等）将被扣分。
      """

    aipr = AIPaperResearch(paper_ids, research_interest,model_name="gemini-2.0-flash-lite")
    aipr.run()