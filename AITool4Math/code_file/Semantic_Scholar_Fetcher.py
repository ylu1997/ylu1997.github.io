import requests
import json
import time


def get_api_key_from_json():
    """请自行实现该部分功能"""
    pass


class SemanticScholarFetcher:
    """
    Semantic Scholar API 数据获取器

    这个类提供了与 Semantic Scholar API 交互的完整功能，用于批量获取学术论文的详细信息和引用关系。

    主要功能：
    - 批量获取论文详情信息（标题、摘要、作者、被引用数等）
    - 智能获取论文引用关系，根据被引用数自动优化请求策略
    - 根据论文标题搜索相关论文
    - 自动处理API限流和异常情况
    - 支持大批量数据处理，自动分组和重试机制

    主要方法：

    get_papers_batch(paper_ids, fields=None, batch_size=500):
        批量获取论文详情信息
        输入：
            - paper_ids: list[str] - 论文ID列表
            - fields: str - 需要获取的字段，默认包含标题、年份、摘要等
            - batch_size: int - 每批处理的论文数量，默认500
        输出：
            - list[dict] - 论文信息字典列表

    get_papers_citation_counts(paper_ids):
        批量获取论文的被引用数
        输入：
            - paper_ids: list[str] - 论文ID列表
        输出：
            - dict[str, int] - 论文ID到被引用数的映射

    get_citation_ids(paper_id, max_retries=3):
        获取单个论文的所有引用论文ID
        输入：
            - paper_id: str - 论文ID
            - max_retries: int - 最大重试次数，默认3
        输出：
            - list[str] - 引用该论文的论文ID列表

    get_citations_batch_smart(paper_ids, citation_threshold=400):
        智能批量获取citations，根据被引用数自动选择批量或单独获取策略
        输入：
            - paper_ids: list[str] - 论文ID列表
            - citation_threshold: int - 被引用数阈值，超过则单独获取，默认400
        输出：
            - dict[str, list[str]] - 论文ID到其引用论文ID列表的映射

    get_citations_batch(paper_ids, delay_between_requests=2.0):
        逐个获取多个论文的引用论文ID
        输入：
            - paper_ids: list[str] - 论文ID列表
            - delay_between_requests: float - 请求间隔时间，默认2.0秒
        输出：
            - dict[str, list[str]] - 论文ID到其引用论文ID列表的映射

    search_papers_by_title(title, limit=10, max_retries=2):
        根据论文标题搜索相关论文
        输入：
            - title: str - 论文标题或关键词
            - limit: int - 返回结果数量限制，默认10
            - max_retries: int - 最大重试次数，默认2
        输出：
            - list[dict] - 搜索到的论文信息列表

    使用示例：
        fetcher = SemanticScholarFetcher()

        # 批量获取论文信息
        papers = fetcher.get_papers_batch(['paper_id_1', 'paper_id_2'])

        # 智能获取引用关系
        citations = fetcher.get_citations_batch_smart(['paper_id_1', 'paper_id_2'])

        # 搜索论文
        results = fetcher.search_papers_by_title("machine learning")

    注意事项：
    - 需要有效的 Semantic Scholar API 密钥
    - 自动处理请求限流，包含适当的延时机制
    - 支持大批量处理，会自动分组避免单次请求过大
    - 智能引用获取会根据论文被引用数选择最优策略
    - 所有方法都包含异常处理和重试机制
    """

    def __init__(self, api_key=get_api_key_from_json()):
        self.api_key = api_key
        self.url = "https://api.semanticscholar.org/graph/v1/paper/batch"

    def _rate_limit(self, delay=1.1):
        """内部函数：请求时间限制"""
        time.sleep(delay)

    def _handle_response(self, response, operation="请求"):
        """统一处理API响应和异常"""
        try:
            if response.status_code == 200:
                return response.json(), True
            elif response.status_code == 429:
                print(f"{operation}被限流，等待更长时间...")
                time.sleep(5)
                return None, False
            elif response.status_code == 404:
                print(f"{operation}未找到资源")
                return None, False
            else:
                print(f"{operation}失败: {response.status_code} - {response.text}")
                return None, False
        except requests.exceptions.RequestException as e:
            print(f"{operation}网络异常: {str(e)}")
            return None, False
        except Exception as e:
            print(f"{operation}处理异常: {str(e)}")
            return None, False

    def get_papers_batch(self, paper_ids, fields=None, batch_size=499, max_retries=3):
        """
        批量获取论文详情
        """
        self._rate_limit()

        if fields is None:
            fields = "title,year,abstract,citationCount,authors,url,publicationDate,venue"

        query_params = {"fields": fields}
        headers = {"x-api-key": self.api_key}
        all_papers = []

        for i in range(0, len(paper_ids), batch_size):
            batch_ids = paper_ids[i:i + batch_size]
            data = {"ids": batch_ids}

            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = requests.post(self.url, params=query_params, json=data, headers=headers)
                    result, success = self._handle_response(response, "批量获取论文")

                    if success and result:
                        all_papers.extend(result)
                        print(f"已处理 {i + len(batch_ids)}/{len(paper_ids)} 篇论文")
                        time.sleep(1)
                        break  # 成功获取数据，跳出重试循环
                    elif response.status_code == 429:  # 被限流
                        retry_count += 1
                        wait_time = 5 * retry_count  # 指数退避策略
                        print(f"批次被限流，第 {retry_count}/{max_retries} 次重试，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                    else:
                        # 其他错误不重试
                        break

                except Exception as e:
                    print(f"处理批次出错: {str(e)}")
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 3 * retry_count
                        print(f"第 {retry_count}/{max_retries} 次重试，等待 {wait_time} 秒...")
                        time.sleep(wait_time)
                    else:
                        print(f"达到最大重试次数 {max_retries}，跳过当前批次")
                        break

            # 如果所有重试都失败，继续处理下一批
            if retry_count == max_retries:
                print(f"批次 {i // batch_size + 1} 处理失败，继续下一批")

        return all_papers

    def get_papers_citation_counts(self, paper_ids):
        """
        批量获取论文的被引用数 - 使用get_papers_batch简化
        """
        papers = self.get_papers_batch(paper_ids, fields="paperId,citationCount")

        citation_counts = {}
        for paper in papers:
            if paper and paper.get('paperId'):
                paper_id = paper.get('paperId')
                citation_count = paper.get('citationCount', 0)
                citation_counts[paper_id] = citation_count

        return citation_counts

    def get_citation_ids(self, paper_id, max_retries=3):
        """
        获取单个论文的所有引用论文ID - 使用get_papers_batch简化
        """
        for attempt in range(max_retries):
            try:
                papers = self.get_papers_batch([paper_id], fields="paperId,citations.paperId")

                if papers and papers[0] and papers[0].get('citations'):
                    citation_ids = [
                        citation.get('paperId')
                        for citation in papers[0].get('citations', [])
                        if citation.get('paperId')
                    ]
                    return citation_ids
                else:
                    return []

            except requests.exceptions.Timeout:
                print(f"请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
                    continue
            except requests.exceptions.ConnectionError:
                print(f"连接错误 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(3 * (attempt + 1))
                    continue
            except Exception as e:
                print(f"获取引用异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                    continue

        print(f"获取论文 {paper_id} 的引用失败，已达到最大重试次数")
        return []

    def get_citations_batch_smart(self, paper_ids, citation_threshold=400):
        """
        智能批量获取citations：根据被引用数决定批量还是单独获取
        """
        # 1. 先获取所有论文的被引用数
        print("正在获取论文被引用数...")
        citation_counts = self.get_papers_citation_counts(paper_ids)

        if not citation_counts:
            print("获取被引用数失败，改用单独获取模式")
            return self.get_citations_batch(paper_ids)

        # 2. 根据被引用数进行智能分组
        batch_groups = []
        single_papers = []

        current_group = []
        current_count = 0

        for paper_id in paper_ids:
            count = citation_counts.get(paper_id, 0)
            # print(f"论文 {paper_id}: {count} 个被引用")

            if count > citation_threshold:
                single_papers.append(paper_id)
            else:
                if current_count + count <= citation_threshold:
                    current_group.append(paper_id)
                    current_count += count
                else:
                    if current_group:
                        batch_groups.append(current_group)
                    current_group = [paper_id]
                    current_count = count

        if current_group:
            batch_groups.append(current_group)

        print(f"分组结果: {len(batch_groups)} 个批量组, {len(single_papers)} 个单独论文")

        # 3. 执行获取
        all_results = {}

        # 批量获取 - 使用get_papers_batch
        for i, group in enumerate(batch_groups):
            print(f"正在批量获取第 {i + 1}/{len(batch_groups)} 组 ({len(group)} 篇论文)...")
            papers = self.get_papers_batch(group, fields="paperId,citations.paperId")

            for paper in papers:
                if paper and paper.get('paperId'):
                    paper_id = paper.get('paperId')
                    citations = paper.get('citations', [])
                    citation_ids = [
                        citation.get('paperId')
                        for citation in citations
                        if citation.get('paperId')
                    ]
                    all_results[paper_id] = citation_ids
                    # print(f"论文 {paper_id}: 获得 {len(citation_ids)} 个citations")

            time.sleep(1.5)

        # 单独获取
        for i, paper_id in enumerate(single_papers):
            print(f"正在单独获取第 {i + 1}/{len(single_papers)} 篇论文: {paper_id}")
            citation_ids = self.get_citation_ids(paper_id)
            if citation_ids is not None:
                all_results[paper_id] = citation_ids
            time.sleep(2.0)

        return all_results

    def get_citations_batch(self, paper_ids, delay_between_requests=2.0):
        """
        批量获取多个论文的引用论文ID (逐个获取)
        """
        results = {}
        failed_ids = []

        for i, paper_id in enumerate(paper_ids):
            try:
                print(f"正在获取第 {i + 1}/{len(paper_ids)} 篇论文的引用: {paper_id}")
                citation_ids = self.get_citation_ids(paper_id)

                if citation_ids is not None:
                    results[paper_id] = citation_ids
                    print(f"获得 {len(citation_ids)} 个引用")
                else:
                    failed_ids.append(paper_id)
                    print(f"获取失败: {paper_id}")

                if i < len(paper_ids) - 1:
                    time.sleep(delay_between_requests)

            except KeyboardInterrupt:
                print("用户中断操作")
                break
            except Exception as e:
                print(f"处理论文 {paper_id} 时发生异常: {str(e)}")
                failed_ids.append(paper_id)
                continue

        if failed_ids:
            print(f"以下 {len(failed_ids)} 个论文ID获取失败: {failed_ids[:5]}{'...' if len(failed_ids) > 5 else ''}")

        return results

    def search_papers_by_title(self, title, limit=10, max_retries=2):
        """
        根据论文标题搜索并返回论文信息
        """
        for attempt in range(max_retries):
            try:
                self._rate_limit()

                url = "https://api.semanticscholar.org/graph/v1/paper/search"
                query_params = {
                    "query": title,
                    "limit": limit,
                    "fields": "paperId,title,year,authors"
                }
                headers = {"x-api-key": self.api_key}

                response = requests.get(url, params=query_params, headers=headers, timeout=30)
                result, success = self._handle_response(response, f"搜索论文 (尝试 {attempt + 1})")

                if success and result:
                    papers = result.get('data', [])
                    return papers
                elif response.status_code == 429:
                    continue
                else:
                    break

            except requests.exceptions.Timeout:
                print(f"搜索请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
            except Exception as e:
                print(f"搜索异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue

        print("搜索失败，已达到最大重试次数")
        return []
