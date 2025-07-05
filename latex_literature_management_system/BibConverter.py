import re


class BibConverter:
    """BibTeX转换器类"""

    def __init__(self):
        pass

    def convert_bib_to_addliterature(self, bib_text):
        """
        将BibTeX文本转换为addliterature格式

        Args:
            bib_text (str): BibTeX格式的文本

        Returns:
            str: 转换后的addliterature格式文本

        Raises:
            ValueError: 当BibTeX格式不正确或缺少必要字段时
        """
        try:
            # 提取条目键
            key_match = re.search(r'@\w+\{([^,]+),', bib_text)
            if not key_match:
                raise ValueError("未找到有效的BibTeX条目键")
            key = key_match.group(1).strip()

            # 提取title
            title_match = re.search(r'title\s*=\s*\{([^}]+)\}', bib_text)
            if not title_match:
                raise ValueError("未找到title字段")
            title = title_match.group(1).strip()

            # 提取author
            author_match = re.search(r'author\s*=\s*\{([^}]+)\}', bib_text)
            if not author_match:
                raise ValueError("未找到author字段")
            author = author_match.group(1).strip()

            # 提取year
            year_match = re.search(r'year\s*=\s*\{([^}]+)\}', bib_text)
            if not year_match:
                raise ValueError("未找到year字段")
            year = year_match.group(1).strip()

            # 构建结果 - 标签项留空
            result = f"\\addliterature{{{title}\\cite{{{key}}}}}{{{author}}}{{{year}}}{{}}{{}}"

            return result

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            else:
                raise ValueError(f"解析BibTeX时出错: {str(e)}")

    def split_multiple_bibs(self, text):
        """
        将包含多个BibTeX条目的文本分割成单独的条目

        Args:
            text (str): 包含多个BibTeX条目的文本

        Returns:
            list: BibTeX条目列表
        """
        # 使用正则表达式找到所有@开头的条目
        entries = []

        # 匹配@article{...}, @book{...}, @inproceedings{...}等
        pattern = r'@\w+\s*\{'
        matches = list(re.finditer(pattern, text))

        if not matches:
            return []

        for i, match in enumerate(matches):
            start_pos = match.start()

            # 找到对应的结束位置
            if i < len(matches) - 1:
                # 不是最后一个条目，结束位置是下一个条目的开始位置
                end_pos = matches[i + 1].start()
                entry_text = text[start_pos:end_pos].strip()
            else:
                # 最后一个条目，取到文本结尾
                entry_text = text[start_pos:].strip()

            # 确保条目以}结尾
            if entry_text and not entry_text.endswith('}'):
                # 寻找最后一个}
                last_brace = entry_text.rfind('}')
                if last_brace != -1:
                    entry_text = entry_text[:last_brace + 1]

            if entry_text:
                entries.append(entry_text)

        return entries

    def convert_multiple_bibs(self, text):
        """
        批量转换多个BibTeX条目

        Args:
            text (str): 包含多个BibTeX条目的文本

        Returns:
            tuple: (成功结果列表, 失败信息列表)
        """
        entries = self.split_multiple_bibs(text)

        if not entries:
            # 尝试作为单个条目处理
            try:
                result = self.convert_bib_to_addliterature(text)
                return [result], []
            except Exception as e:
                return [], [f"解析失败: {str(e)}"]

        success_results = []
        error_messages = []

        for i, entry in enumerate(entries, 1):
            try:
                result = self.convert_bib_to_addliterature(entry)
                success_results.append(result)
            except Exception as e:
                error_messages.append(f"第{i}个条目转换失败: {str(e)}")

        return success_results, error_messages

    def validate_bib_format(self, bib_text):
        """
        验证BibTeX格式是否正确

        Args:
            bib_text (str): 要验证的BibTeX文本

        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            success_results, error_messages = self.convert_multiple_bibs(bib_text)
            if error_messages:
                return False, "\n".join(error_messages)
            return True, f"成功验证 {len(success_results)} 个条目"
        except Exception as e:
            return False, str(e)

    def extract_field(self, bib_text, field_name):
        """
        从BibTeX文本中提取指定字段

        Args:
            bib_text (str): BibTeX文本
            field_name (str): 字段名称

        Returns:
            str: 字段值，如果未找到返回空字符串
        """
        pattern = rf'{field_name}\s*=\s*\{{([^}}]+)\}}'
        match = re.search(pattern, bib_text, re.IGNORECASE)
        return match.group(1).strip() if match else ""

    def get_entry_key(self, bib_text):
        """
        从BibTeX文本中提取条目键

        Args:
            bib_text (str): BibTeX文本

        Returns:
            str: 条目键，如果未找到返回空字符串
        """
        match = re.search(r'@\w+\{([^,]+),', bib_text)
        return match.group(1).strip() if match else ""


# 测试代码
if __name__ == "__main__":
    converter = BibConverter()

    # 测试多个条目
    multiple_bibs = """@article{Kuronya2014LocalPO,
title={Local positivity of linear series on surfaces},
author={Alex Kuronya and Victor Lozovanu},
journal={arXiv: Algebraic Geometry},
year={2014},
url={https://api.semanticscholar.org/CorpusID:119288694}
}

@article{Smith2020TestArticle,
title={Test Article Title},
author={John Smith and Jane Doe},
journal={Test Journal},
year={2020}
}"""

    success_results, error_messages = converter.convert_multiple_bibs(multiple_bibs)

    print(f"成功转换 {len(success_results)} 个条目:")
    for i, result in enumerate(success_results, 1):
        print(f"\n第{i}个结果:")
        print(result)

    if error_messages:
        print(f"\n错误信息:")
        for error in error_messages:
            print(error)