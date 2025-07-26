import json
from typing import Dict, Any, Optional, List, Union
from GeminiClient import EnhancedGenAI


"""
    增强型GenAI客户端，提供高级错误处理、输入验证和智能重试机制。

    继承自QuotaControlledGenAI，在保留日志记录和配额控制功能的基础上，
    添加了智能错误分类、自动重试、参数验证和模型回退等高级功能。

    构造函数参数:
        api_key (str, optional): Google API密钥，默认为None时自动调用get_gemini_api_key()获取
        model_name (str, optional): 要使用的模型名称，默认为"gemini-1.5-flash"
        log_dir (str, optional): 对话日志目录路径，默认为"logs"
        quota_log_dir (str, optional): 配额监控日志目录，默认为"quota_logs"
        custom_sleep_time (float, optional): 自定义延迟时间(秒)，默认为None时根据模型限制自动计算
        max_retries (int, optional): 最大重试次数，默认为3
        fallback_models (List[str], optional): 回退模型列表，默认为["gemini-2.5-flash-lite", "gemini-2.0-flash"]
        verbose (bool, optional): 是否在命令行显示运行信息，默认为True

    EnhancedGenAI特有方法:
        generate_text(contents, config=None) -> GenerateContentResponse:
            增强版文本生成方法，包含错误处理和重试机制
            参数:
                contents: 输入文本内容，可以是字符串或结构化内容
                config (Dict[str, Any], optional): 生成配置参数字典
            返回:
                GenerateContentResponse: Gemini API的原始响应对象
            异常:
                Exception: 当所有尝试都失败时抛出，包含详细的错误分类和解决方案
            说明:
                1. 自动验证和清理输入内容和配置参数
                2. 对可重试错误进行多次尝试，使用指数退避策略
                3. 在主模型失败后尝试回退到备选模型
                4. 提供详细的错误分类和解决方案建议

    继承自QuotaControlledGenAI的方法:
        estimate_tokens(text) -> int:
            估计文本的token数量
            参数:
                text (str): 要估计的文本
            返回:
                int: 估计的token数量

        calculate_response_tokens(response) -> Dict[str, int]:
            从响应中计算实际消耗的token
            参数:
                response: Gemini API响应对象
            返回:
                Dict[str, int]: 包含input_tokens、output_tokens和total_tokens的字典

        smart_sleep() -> None:
            智能延迟，根据请求频率和模型限制动态调整延迟时间

        get_quota_status() -> Dict[str, Any]:
            获取当前配额使用状态
            返回:
                Dict[str, Any]: 包含日期、模型、使用量、剩余请求等信息的字典

    继承自LoggedGenAI的方法:
        set_model(model_name) -> None:
            更改当前使用的模型
            参数:
                model_name (str): 新的模型名称

        get_conversation_history() -> List[Dict[str, Any]]:
            获取对话历史记录
            返回:
                List[Dict[str, Any]]: 对话历史记录列表

        clear_history() -> None:
            清空对话历史记录（但不清空日志文件）

        close_session() -> None:
            手动关闭会话，添加会话结束日志并关闭日志文件

        get_session_info() -> Dict[str, Any]:
            获取会话信息
            返回:
                Dict[str, Any]: 包含会话ID、创建时间、对话次数等信息

        load_logs_from_file() -> List[Dict[str, Any]]:
            从日志文件加载所有日志记录
            返回:
                List[Dict[str, Any]]: 日志记录列表

    继承自BaseGenAI的方法:
        print_status(message, level='info') -> None:
            输出状态信息
            参数:
                message (str): 要输出的信息
                level (str): 信息级别，可选值为'info'、'success'、'warning'、'error'

    使用示例:
        client = EnhancedGenAI(
            model_name="gemini-2.5-pro",
            max_retries=3,
            fallback_models=["gemini-2.5-flash", "gemini-1.5-flash"]
        )

        try:
            response = client.generate_text(
                "请解释量子计算的基本原理",
                config={"temperature": 0.7}
            )
            print(response.text)
        except Exception as e:
            print(f"生成失败: {e}")
    """


class SchemaJsonGenAI(EnhancedGenAI):
    """
    基于Schema的JSON输出GenAI客户端，继承自EnhancedGenAI。

    在保留所有增强功能的基础上，添加了JSON Schema约束功能，
    确保AI输出符合预定义的JSON格式。

    构造函数参数:
        schema (Dict[str, Any]): JSON Schema定义，用于约束AI输出格式
        api_key (str, optional): Google API密钥，默认为None时自动调用get_gemini_api_key()获取
        model_name (str, optional): 要使用的模型名称，默认为"gemini-1.5-flash"
        log_dir (str, optional): 对话日志目录路径，默认为"logs"
        quota_log_dir (str, optional): 配额监控日志目录，默认为"quota_logs"
        custom_sleep_time (float, optional): 自定义延迟时间(秒)，默认为None时根据模型限制自动计算
        max_retries (int, optional): 最大重试次数，默认为3
        fallback_models (List[str], optional): 回退模型列表，默认为["gemini-2.5-flash-lite", "gemini-2.0-flash"]
        verbose (bool, optional): 是否在命令行显示运行信息，默认为True
        strict_schema (bool, optional): 是否严格遵循schema，默认为True

    新增属性:
        schema (Dict[str, Any]): 当前使用的JSON Schema
        strict_schema (bool): 是否严格遵循schema模式

    重载方法:
        generate_text(contents, config=None) -> GenerateContentResponse:
            增强版文本生成方法，自动应用JSON Schema约束
            参数:
                contents: 输入文本内容，可以是字符串或结构化内容
                config (Dict[str, Any], optional): 生成配置参数字典，会自动合并schema配置
            返回:
                GenerateContentResponse: Gemini API的原始响应对象，输出符合指定schema

    新增方法:
        set_schema(schema) -> None:
            更新JSON Schema
            参数:
                schema (Dict[str, Any]): 新的JSON Schema定义

        get_schema() -> Dict[str, Any]:
            获取当前的JSON Schema
            返回:
                Dict[str, Any]: 当前的JSON Schema定义

        validate_response(response_text) -> bool:
            验证响应是否符合schema（可选功能）
            参数:
                response_text (str): AI响应文本
            返回:
                bool: 是否符合schema要求

    使用示例:
        # 定义输出schema
        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_points": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["summary", "key_points", "confidence"]
        }

        client = SchemaJsonGenAI(
            schema=schema,
            model_name="gemini-2.5-pro",
            strict_schema=True
        )

        response = client.generate_text("请总结量子计算的核心概念")
        # 输出将自动符合指定的JSON格式
    """

    def __init__(
            self,
            schema: Dict[str, Any],
            api_key: Optional[str] = None,
            model_name: str = "gemini-1.5-flash",
            log_dir: str = "logs",
            quota_log_dir: str = "quota_logs",
            custom_sleep_time: Optional[float] = None,
            max_retries: int = 3,
            fallback_models: Optional[List[str]] = None,
            verbose: bool = True,
            strict_schema: bool = True
    ):
        """
        初始化SchemaJsonGenAI客户端

        Args:
            schema: JSON Schema定义，用于约束AI输出格式
            其他参数: 继承自EnhancedGenAI的参数
            strict_schema: 是否严格遵循schema，默认为True
        """
        # 调用父类构造函数
        super().__init__(
            api_key=api_key,
            model_name=model_name,
            log_dir=log_dir,
            quota_log_dir=quota_log_dir,
            custom_sleep_time=custom_sleep_time,
            max_retries=max_retries,
            fallback_models=fallback_models,
            verbose=verbose
        )

        # 设置schema相关属性
        self.schema = schema
        self.strict_schema = strict_schema

        if self.verbose:
            self.print_status(f"SchemaJsonGenAI初始化完成，使用模型: {model_name}", "success")
            self.print_status(f"Schema约束模式: {'严格' if strict_schema else '宽松'}", "info")

    def generate_text(
            self,
            contents: Union[str, List[Dict[str, Any]]],
            config: Optional[Dict[str, Any]] = None
    ):
        """
        生成符合Schema约束的JSON格式文本

        Args:
            contents: 输入文本内容
            config: 生成配置参数，会自动合并schema配置

        Returns:
            GenerateContentResponse: 包含符合schema的JSON响应
        """
        # 初始化配置字典
        if config is None:
            config = {}

        # 准备response schema配置
        response_schema_config = {
            "response_mime_type": "application/json",
            "response_schema": self.schema
        }

        # 合并用户配置和schema配置
        # schema配置优先级更高，确保输出格式约束生效
        merged_config = {**config, **response_schema_config}

        if self.verbose:
            self.print_status("应用JSON Schema约束到生成配置", "info")

        # 调用父类的generate_text方法
        try:
            response = super().generate_text(contents, merged_config)

            if self.verbose:
                self.print_status("JSON格式响应生成成功", "success")

            return response

        except Exception as e:
            if self.verbose:
                self.print_status(f"Schema约束生成失败: {str(e)}", "error")
            raise

    def set_schema(self, schema: Dict[str, Any]) -> None:
        """
        更新JSON Schema

        Args:
            schema: 新的JSON Schema定义
        """
        self.schema = schema

        if self.verbose:
            self.print_status("JSON Schema已更新", "info")

    def get_schema(self) -> Dict[str, Any]:
        """
        获取当前的JSON Schema

        Returns:
            当前的JSON Schema定义
        """
        return self.schema

    def validate_response(self, response_text: str) -> bool:
        """
        验证响应是否符合schema（基础验证）

        Args:
            response_text: AI响应文本

        Returns:
            是否为有效JSON格式
        """
        try:
            json.loads(response_text)
            return True
        except json.JSONDecodeError:
            return False

    def __repr__(self) -> str:
        """返回对象的字符串表示"""
        return (f"SchemaJsonGenAI(model='{self.model_name}', "
                f"strict_schema={self.strict_schema}, "
                f"session_id='{self.session_id}')")

# 使用示例
if __name__ == "__main__":
    # 定义一个简单的schema示例
    example_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"},
            "tags": {
                "type": "array",
                "items": {"type": "string"}
            },
            "priority": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5
            }
        },
        "required": ["title", "content"]
    }

    # 创建客户端实例
    client = SchemaJsonGenAI(
        schema=example_schema,
        model_name="gemini-1.5-flash",
        verbose=True
    )

    # 生成结构化响应
    try:
        response = client.generate_text(
            "请为'机器学习入门'这个主题创建一个学习计划",
            config={"temperature": 0.7}
        )
        print("生成的JSON响应:")
        print(response.text)
    except Exception as e:
        print(f"生成失败: {e}")