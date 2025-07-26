import atexit
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

from google import genai
from google.genai import types
from google.genai.types import GenerateContentResponse
import time


def get_gemini_api_key():
    """请自行实现该部分代码"""
    pass


class BaseGenAI:
    """
       Google Gemini API的基础封装类，提供核心功能访问。

       该类实现了与Google Gemini API的基本交互，包括模型初始化和文本生成。
       作为其他高级客户端类的基础类，提供最精简的API调用功能。

       构造函数参数:
           api_key (str, optional): Google API密钥，默认为None时自动调用get_gemini_api_key()获取
           model_name (str, optional): 要使用的模型名称，默认为"gemini-1.5-flash"
           verbose (bool, optional): 是否在命令行显示运行信息，默认为True

       公有方法:
           generate_text(contents, config=None) -> GenerateContentResponse:
               生成文本响应
               参数:
                   contents: 输入文本内容，可以是字符串或结构化内容
                   config (Dict[str, Any], optional): 生成配置参数字典，包含temperature等参数
               返回:
                   GenerateContentResponse: Gemini API的原始响应对象
               异常:
                   Exception: 当API调用失败时抛出，包含详细错误信息

           set_model(model_name) -> None:
               切换使用的模型
               参数:
                   model_name (str): 新的模型名称
               返回:
                   无
       """

    def __init__(self, api_key: str = None, model_name: str = "gemini-1.5-flash", verbose: bool = True):
        """
        初始化GenAI客户端和模型

        Args:
            api_key: Google API密钥，为None时自动调用get_gemini_api_key()
            model_name: 模型名称，默认为gemini-1.5-flash
        """
        # 获取API密钥
        if api_key is None:
            api_key = get_gemini_api_key()

        # 建立客户端
        self.client = genai.Client(api_key=api_key)

        # 模型设置
        self.model_name = model_name

        self.verbose = verbose

        self.print_status(f"初始化完成，使用模型: {self.model_name}")

    def print_status(self, message: str, level: str = 'info') -> None:
        """
        在命令行显示当前运行状态信息

        Args:
            message: 要显示的信息
            level: 信息级别，可选值为'info'、'warning'、'error'、'success'
        """
        if not self.verbose:
            return

        # 定义不同级别的颜色前缀（ANSI转义序列）
        prefixes = {
            'info': '\033[94m[INFO]\033[0m',  # 蓝色
            'warning': '\033[93m[WARN]\033[0m',  # 黄色
            'error': '\033[91m[ERROR]\033[0m',  # 红色
            'success': '\033[92m[SUCCESS]\033[0m'  # 绿色
        }

        # 获取当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 获取对应级别的前缀，如果不存在则使用info级别
        prefix = prefixes.get(level.lower(), prefixes['info'])

        # 打印信息
        print(f"{prefix} {current_time} - {message}")

    def generate_text(self, contents, config: Optional[Dict[str, Any]] = None) -> GenerateContentResponse:
        """
        生成文本回应

        Args:
            content: 输入文本内容
            config: 配置参数字典

        Returns:
            生成的文本回应
        """
        self.print_status(f"开始生成文本，使用模型: {self.model_name}")

        try:
            response = self.client.models.generate_content(model=self.model_name, contents=contents, config=config)
            self.print_status("文本生成成功", level='success')
            return response
        except Exception as e:
            raise Exception(f"API调用失败: {str(e)}")

    def set_model(self, model_name: str):
        """
        设置模型

        Args:
            model_name: 新的模型名称
        """
        self.print_status(f"切换模型: {self.model_name} -> {model_name}")
        self.model_name = model_name


class LoggedGenAI(BaseGenAI):
    """
    带日志记录功能的GenAI客户端。

    继承BaseGenAI，添加完整的日志记录功能，包括会话跟踪和持久化存储。
    每个会话创建单独的JSON日志文件，记录所有请求、响应和元数据。

    构造函数参数:
        api_key (str, optional): Google API密钥，默认为None时自动调用get_gemini_api_key()获取
        model_name (str, optional): 要使用的模型名称，默认为"gemini-1.5-flash"
        log_dir (str, optional): 日志文件存储目录，默认为"logs"
        verbose (bool, optional): 是否在命令行显示运行信息，默认为True

    公有方法:
        generate_text(contents, config=None) -> GenerateContentResponse:
            生成文本响应，并记录日志
            参数:
                contents: 输入文本内容，可以是字符串或结构化内容
                config (Dict, optional): 生成配置参数字典
            返回:
                GenerateContentResponse: Gemini API的原始响应对象
            异常:
                Exception: 当API调用失败时抛出，包含详细错误信息

        close_session() -> None:
            手动关闭会话，写入会话结束日志并闭合日志文件
            参数:
                无
            返回:
                无

        clear_history() -> None:
            清空对话历史记录（但不清空日志文件）
            参数:
                无
            返回:
                无

        get_conversation_history() -> List[Dict[str, Any]]:
            获取对话历史记录
            参数:
                无
            返回:
                List[Dict[str, Any]]: 对话历史记录列表

        get_session_info() -> Dict[str, Any]:
            获取会话信息
            参数:
                无
            返回:
                Dict[str, Any]: 包含会话ID、创建时间、对话数量等信息的字典

        load_logs_from_file() -> List[Dict[str, Any]]:
            从日志文件加载完整记录
            参数:
                无
            返回:
                List[Dict[str, Any]]: 日志文件中的所有记录
            说明:
                如果文件未闭合，会创建临时闭合文件进行读取
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-1.5-flash",
                 log_dir: str = "logs", verbose: bool = True):
        """
        初始化LoggedGenAI客户端
        """
        super().__init__(api_key, model_name, verbose)

        # 记录客户端建立时间
        self.client_created_at = datetime.now()

        # 对话历史记录
        self.conversation_history: List[Dict[str, Any]] = []

        # 创建日志目录
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

        # 生成唯一的日志文件名
        timestamp = self.client_created_at.strftime("%Y%m%d_%H%M%S")
        session_id = str(id(self))[-6:]
        self.log_file = os.path.join(log_dir, f"genai_{timestamp}_{session_id}.json")

        # 标记是否为第一次写入
        self.is_first_entry = True

        # 标记文件是否已闭合
        self.is_file_closed = False

        # 初始化日志文件（只写开头的[）
        self._init_log_file()

        # 注册程序退出时的清理函数
        atexit.register(self._ensure_file_closed)

        # 记录客户端建立日志
        self._log_client_creation()

        self.print_status(f"日志客户端初始化完成，日志文件: {self.log_file}", level='info')

    def _init_log_file(self):
        """初始化日志文件，只写开头的["""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('[')  # 只写开头，不闭合
            self.print_status("日志文件初始化成功", level='success')
        except Exception as e:
            self.print_status(f"初始化日志文件失败: {e}", level='error')

    def _log_client_creation(self):
        """记录客户端建立信息"""
        creation_log = {
            "event_type": "session_start",
            "timestamp": self.client_created_at.isoformat(),
            "session_id": id(self),
            "model_name": getattr(self, 'model_name', 'unknown'),
            "log_file": self.log_file
        }

        self._append_entry(creation_log)
        self.print_status("记录会话开始日志", level='info')

    def generate_text(self, contents, config: Optional[Dict] = None):
        """
        重载generate_text方法，添加日志记录功能
        """
        # 记录请求开始时间
        request_time = datetime.now()
        response = None
        error = None

        self.print_status("准备生成文本并记录日志", level='info')

        try:
            # 调用父类方法
            response = super().generate_text(contents, config)
        except Exception as e:
            error = e
            self.print_status(f"生成文本失败: {str(e)}", level='error')

        # 记录结束时间
        end_time = datetime.now()

        # 处理response对象
        response_json = None
        if response is not None:
            try:
                response_json = json.loads(response.model_dump_json(indent=2))
                self.print_status("成功解析响应为JSON", level='success')
            except Exception as json_error:
                response_json = {"raw_response": str(response), "json_error": str(json_error)}
                self.print_status(f"解析响应JSON失败: {str(json_error)}", level='warning')

        # 创建对话记录
        conversation_record = {
            "event_type": "conversation",
            "conversation_id": len(self.conversation_history) + 1,
            "request_time": request_time.isoformat(),
            "response_time": end_time.isoformat(),
            "duration_seconds": (end_time - request_time).total_seconds(),
            "input": {
                "contents": contents,
                "config": config
            },
            "output": {
                "response_json": response_json,
                "error": str(error) if error else None,
                "status": "error" if error else "success"
            },
            "session_id": id(self)
        }

        # 添加到历史记录
        self.conversation_history.append(conversation_record)
        self.print_status(f"添加对话记录 #{len(self.conversation_history)}", level='info')

        # 续写到日志文件
        self._append_entry(conversation_record)

        # 如果有错误，重新抛出
        if error:
            raise error

        return response

    def _append_entry(self, log_entry: Dict):
        """
        向未闭合的JSON数组中追加条目
        格式：第一个条目直接写，后续条目前加逗号
        """
        if self.is_file_closed:
            self.print_status("警告：文件已闭合，无法继续写入", level='warning')
            return

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                # 格式化JSON条目
                entry_json = json.dumps(log_entry, ensure_ascii=False, indent=2)

                # 添加适当的缩进（2个空格）
                indented_entry = '\n'.join('  ' + line for line in entry_json.split('\n'))

                if self.is_first_entry:
                    # 第一个条目：直接写入
                    f.write('\n' + indented_entry)
                    self.is_first_entry = False
                    self.print_status("写入首条日志记录", level='info')
                else:
                    # 后续条目：前面加逗号
                    f.write(',\n' + indented_entry)
                    self.print_status("追加日志记录", level='info')

        except Exception as e:
            self.print_status(f"写入日志条目失败: {e}", level='error')

    def _close_json_array(self):
        """闭合JSON数组，添加结尾的]"""
        if self.is_file_closed:
            return

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write('\n]')
            self.is_file_closed = True
            self.print_status("日志文件已闭合", level='success')
        except Exception as e:
            self.print_status(f"闭合JSON数组失败: {e}", level='error')

    def _ensure_file_closed(self):
        """确保文件被正确闭合（由atexit调用）"""
        if not self.is_file_closed:
            # 添加会话结束日志
            try:
                end_log = {
                    "event_type": "session_end",
                    "timestamp": datetime.now().isoformat(),
                    "session_id": id(self),
                    "total_conversations": len(self.conversation_history),
                    "session_duration_seconds": (datetime.now() - self.client_created_at).total_seconds()
                }
                self._append_entry(end_log)
                self.print_status("添加会话结束日志（程序退出时）", level='info')
            except Exception as e:
                self.print_status(f"添加会话结束日志失败: {e}", level='error')
                pass  # 如果添加结束日志失败，至少要闭合文件

            # 闭合JSON数组
            self._close_json_array()

    def close_session(self):
        """手动关闭会话"""
        if not self.is_file_closed:
            # 记录会话结束日志
            end_log = {
                "event_type": "session_end",
                "timestamp": datetime.now().isoformat(),
                "session_id": id(self),
                "total_conversations": len(self.conversation_history),
                "session_duration_seconds": (datetime.now() - self.client_created_at).total_seconds()
            }
            self._append_entry(end_log)
            self.print_status("手动关闭会话，添加会话结束日志", level='info')

            # 闭合文件
            self._close_json_array()

    def clear_history(self):
        """清空对话历史记录（但不清空日志文件）"""
        clear_log = {
            "event_type": "history_cleared",
            "timestamp": datetime.now().isoformat(),
            "session_id": id(self),
            "cleared_conversations": len(self.conversation_history)
        }

        self._append_entry(clear_log)
        self.print_status(f"清空历史记录，共{len(self.conversation_history)}条对话", level='warning')
        self.conversation_history.clear()

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史记录"""
        self.print_status(f"获取对话历史记录，共{len(self.conversation_history)}条", level='info')
        return self.conversation_history.copy()

    def get_session_info(self) -> Dict[str, Any]:
        """获取会话信息"""
        info = {
            "session_id": id(self),
            "client_created_at": self.client_created_at.isoformat(),
            "total_conversations": len(self.conversation_history),
            "model_name": getattr(self, 'model_name', 'unknown'),
            "log_file": self.log_file,
            "file_closed": self.is_file_closed
        }
        self.print_status("获取会话信息", level='info')
        return info

    def load_logs_from_file(self) -> List[Dict[str, Any]]:
        """
        从日志文件加载所有日志记录
        注意：如果文件还未闭合，会临时闭合后读取
        """
        self.print_status("尝试从日志文件加载记录", level='info')
        try:
            # 如果文件未闭合，先临时闭合
            temp_closed = False
            if not self.is_file_closed:
                self.print_status("文件未闭合，创建临时闭合文件", level='warning')
                # 读取当前内容
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 临时添加闭合括号
                with open(self.log_file + '.temp', 'w', encoding='utf-8') as f:
                    f.write(content + '\n]')
                temp_closed = True

            # 读取JSON
            file_to_read = self.log_file + '.temp' if temp_closed else self.log_file
            with open(file_to_read, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 清理临时文件
            if temp_closed:
                os.remove(self.log_file + '.temp')
                self.print_status("临时文件已删除", level='info')

            self.print_status(f"成功加载日志记录，共{len(data)}条", level='success')
            return data

        except Exception as e:
            self.print_status(f"读取日志文件失败: {e}", level='error')
            return []


class QuotaControlledGenAI(LoggedGenAI):
    """
        带配额控制和监控功能的GenAI客户端。

        继承LoggedGenAI，专注于API使用额度控制和监控，防止超出API限制。
        提供智能延迟、请求频率控制、独立配额日志和Token消耗统计。

        构造函数参数:
            api_key (str, optional): Google API密钥，默认为None时自动调用get_gemini_api_key()获取
            model_name (str, optional): 要使用的模型名称，默认为"gemini-1.5-flash"
            log_dir (str, optional): 对话日志目录路径，默认为"logs"
            quota_log_dir (str, optional): 配额监控日志目录，默认为"quota_logs"
            custom_sleep_time (float, optional): 自定义延迟时间(秒)，默认为None时根据模型限制自动计算
            verbose (bool, optional): 是否在命令行显示运行信息，默认为True

        公有方法:
            generate_text(contents, config=None) -> GenerateContentResponse:
                生成文本，包含配额控制和监控
                参数:
                    contents: 输入文本内容，可以是字符串或结构化内容
                    config (Dict, optional): 生成配置参数字典
                返回:
                    GenerateContentResponse: Gemini API的原始响应对象，出错时返回None
                说明:
                    自动记录请求时间、计算token消耗并更新配额日志

            estimate_tokens(text) -> int:
                估计文本的token数量
                参数:
                    text (str): 要估计的文本
                返回:
                    int: 估计的token数量
                说明:
                    使用启发式方法估算，英文约4字符/token，中文约1.5字符/token

            calculate_response_tokens(response) -> Dict[str, int]:
                从响应中计算实际消耗的token
                参数:
                    response: Gemini API响应对象
                返回:
                    Dict[str, int]: 包含input_tokens、output_tokens和total_tokens的字典

            smart_sleep() -> None:
                智能延迟，根据请求频率和模型限制动态调整延迟时间
                参数:
                    无
                返回:
                    无
                说明:
                    当接近RPM限制时会增加额外延迟

            get_quota_status() -> Dict[str, Any]:
                获取当前配额使用状态
                参数:
                    无
                返回:
                    Dict[str, Any]: 包含日期、模型、使用量、剩余请求等信息的字典
                说明:
                    还包含所有模型的使用摘要和是否超出警告阈值的标志
        """

    MODEL_LIMITS = {
        "gemini-2.5-pro": {"rpm": 5, "tpm": 250000, "rpd": 100},
        "gemini-2.5-flash": {"rpm": 10, "tpm": 250000, "rpd": 250},
        "gemini-2.5-flash-lite": {"rpm": 15, "tpm": 250000, "rpd": 1000},
        "gemini-2.0-flash": {"rpm": 15, "tpm": 1000000, "rpd": 200},
        "gemini-2.0-flash-lite": {"rpm": 30, "tpm": 1000000, "rpd": 200},
        "gemini-1.5-flash": {"rpm": 15, "tpm": 250000, "rpd": 50},
        "gemini-1.5-flash-8b": {"rpm": 15, "tpm": 250000, "rpd": 50},
        "gemma-3": {"rpm": 30, "tpm": 15000, "rpd": 14400},
        "gemma-3n": {"rpm": 30, "tpm": 15000, "rpd": 14400},
        "gemini-embedding": {"rpm": 5, "tpm": 0, "rpd": 100}
    }

    def __init__(self, api_key: Optional[str] = None,
                 model_name: str = "gemini-1.5-flash",
                 log_dir: str = "logs",
                 quota_log_dir: str = "quota_logs",
                 custom_sleep_time: Optional[float] = None,
                 verbose: bool = True):
        super().__init__(api_key, model_name, log_dir, verbose)

        # 配额监控日志目录和文件
        self.quota_log_dir = quota_log_dir
        os.makedirs(quota_log_dir, exist_ok=True)
        self.quota_file = os.path.join(quota_log_dir, "quota_usage.json")

        self.print_status(f"配额日志文件: {self.quota_file}", level='info')

        # 模型限制信息
        self.model_limits = self.MODEL_LIMITS.get(model_name, {
            "rpm": 10, "tpm": 100000, "rpd": 100
        })

        self.print_status(
            f"模型限制: RPM={self.model_limits.get('rpm')}, TPM={self.model_limits.get('tpm')}, RPD={self.model_limits.get('rpd')}",
            level='info')

        # 请求统计
        self.request_times = []

        # 延迟设置
        self.custom_sleep_time = custom_sleep_time
        self.base_sleep_time = self._calculate_base_sleep_time()
        self.print_status(f"基础延迟时间: {self.base_sleep_time:.2f}秒", level='info')

        # 初始化当日配额记录
        self._init_daily_quota()

    def _calculate_base_sleep_time(self) -> float:
        """根据模型限制计算基础延迟时间"""
        if self.custom_sleep_time is not None:
            self.print_status(f"使用自定义延迟时间: {self.custom_sleep_time}秒", level='info')
            return self.custom_sleep_time

        rpm = self.model_limits.get("rpm", 10)
        # 基于RPM计算安全间隔，留20%余量
        base_time = (60.0 / rpm) * 1.2
        self.print_status(f"基于RPM={rpm}计算延迟时间: {base_time:.2f}秒", level='info')
        return base_time

    def _init_daily_quota(self) -> None:
        """初始化当日配额记录"""
        today = datetime.now().date().isoformat()
        self.print_status(f"初始化{today}的配额记录", level='info')

        # 检查是否存在配额文件
        if os.path.exists(self.quota_file):
            try:
                with open(self.quota_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)

                # 如果是同一天，继续使用现有数据
                if existing_data.get("date") == today:
                    self.print_status("找到当日配额记录，继续使用", level='success')
                    # 修改：检查当前模型是否已存在于models字典中，如果不存在则添加
                    if self.model_name not in existing_data.get("models", {}):
                        if "models" not in existing_data:
                            existing_data["models"] = {}

                        # 为新模型添加初始记录
                        existing_data["models"][self.model_name] = {
                            "limits": self.model_limits,
                            "usage": {
                                "requests": 0,
                                "input_tokens": 0,
                                "output_tokens": 0,
                                "total_tokens": 0
                            },
                            "remaining": {
                                "requests": self.model_limits.get("rpd", 100),
                                "tokens": self.model_limits.get("tpm", 100000)
                            },
                            "records": []
                        }
                        self.print_status(f"为模型 {self.model_name} 添加初始记录", level='info')
                        # 保存更新后的数据
                        with open(self.quota_file, 'w', encoding='utf-8') as f:
                            json.dump(existing_data, f, indent=2, ensure_ascii=False)

                    return
            except (json.JSONDecodeError, KeyError) as e:
                self.print_status(f"解析现有配额文件失败: {e}", level='error')
                pass

        # 创建新的当日配额记录 - 修改为支持多模型格式
        initial_quota = {
            "date": today,
            "models": {
                self.model_name: {  # 使用模型名称作为键
                    "limits": self.model_limits,
                    "usage": {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0
                    },
                    "remaining": {
                        "requests": self.model_limits.get("rpd", 100),
                        "tokens": self.model_limits.get("tpm", 100000)
                    },
                    "records": []
                }
            }
        }

        try:
            with open(self.quota_file, 'w', encoding='utf-8') as f:
                json.dump(initial_quota, f, indent=2, ensure_ascii=False)
            self.print_status("创建新的配额记录文件", level='success')
        except Exception as e:
            self.print_status(f"创建配额文件失败: {e}", level='error')

    def _load_daily_quota(self) -> Dict[str, Any]:
        """加载当日配额记录"""
        try:
            with open(self.quota_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查日期，如果不是今天则重新初始化
            today = datetime.now().date().isoformat()
            if data.get("date") != today:
                self.print_status(f"配额文件日期{data.get('date')}不是今天{today}，重新初始化", level='warning')
                self._init_daily_quota()
                return self._load_daily_quota()

            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.print_status(f"加载配额文件失败: {e}，重新初始化", level='warning')
            self._init_daily_quota()
            return self._load_daily_quota()

    def _save_daily_quota(self, quota_data: Dict[str, Any]) -> None:
        """保存当日配额记录"""
        try:
            with open(self.quota_file, 'w', encoding='utf-8') as f:
                json.dump(quota_data, f, indent=2, ensure_ascii=False)
            self.print_status("更新配额记录已保存", level='info')
        except Exception as e:
            self.print_status(f"保存配额记录失败: {e}", level='error')

    def estimate_tokens(self, text: str) -> int:
        """
        估计文本的token数量（对外提供的方法）

        使用简单的启发式方法：
        - 英文：约4个字符=1个token
        - 中文：约1.5个字符=1个token

        Args:
            text (str): 要估计的文本

        Returns:
            int: 估计的token数量
        """
        if not text:
            return 0

        import re
        # 统计中英文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        other_chars = len(text) - chinese_chars

        # 估算token数
        estimated_tokens = int(chinese_chars / 1.5 + other_chars / 4)
        result = max(1, estimated_tokens)
        self.print_status(f"估计文本token数: {result} (中文字符: {chinese_chars}, 其他字符: {other_chars})",
                          level='info')
        return result

    def calculate_response_tokens(self, response) -> Dict[str, int]:
        """
        从response中计算实际消耗的token

        Args:
            response: Gemini API响应对象

        Returns:
            Dict[str, int]: 包含input_tokens, output_tokens, total_tokens
        """
        try:
            # 尝试从response中获取usage信息
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                result = {
                    "input_tokens": getattr(usage, 'prompt_token_count', 0),
                    "output_tokens": getattr(usage, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage, 'total_token_count', 0)
                }
                self.print_status(
                    f"从usage_metadata获取token使用: 输入={result['input_tokens']}, 输出={result['output_tokens']}, 总计={result['total_tokens']}",
                    level='success')
                return result
            elif hasattr(response, 'usage'):
                usage = response.usage
                result = {
                    "input_tokens": getattr(usage, 'input_tokens', 0),
                    "output_tokens": getattr(usage, 'output_tokens', 0),
                    "total_tokens": getattr(usage, 'total_tokens', 0)
                }
                self.print_status(
                    f"从usage获取token使用: 输入={result['input_tokens']}, 输出={result['output_tokens']}, 总计={result['total_tokens']}",
                    level='success')
                return result
        except Exception as e:
            self.print_status(f"无法提取token使用信息: {e}", level='warning')

        # 如果无法获取精确数据，返回0
        self.print_status("无法获取token使用信息，返回零值", level='warning')
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

    def smart_sleep(self) -> None:
        """
        智能延迟，根据请求频率和模型限制调整
        """
        current_time = time.time()

        # 清理1分钟前的请求记录
        old_count = len(self.request_times)
        self.request_times = [t for t in self.request_times
                              if current_time - t < 60]
        new_count = len(self.request_times)

        if old_count != new_count:
            self.print_status(f"清理过期请求记录: {old_count} -> {new_count}", level='info')

        # 检查是否需要额外延迟
        recent_requests = len(self.request_times)
        rpm_limit = self.model_limits.get("rpm", 10)

        if recent_requests >= rpm_limit:
            # 如果接近限制，增加延迟
            extra_delay = (recent_requests - rpm_limit + 1) * 2
            sleep_time = self.base_sleep_time + extra_delay
            self.print_status(f"接近RPM限制，增加额外延迟: +{extra_delay:.2f}秒", level='warning')
        else:
            sleep_time = self.base_sleep_time

        self.print_status(f"延迟{sleep_time:.2f}秒 (最近请求: {recent_requests}/{rpm_limit})", level='info')
        time.sleep(sleep_time)

    def _update_quota_log(self, token_usage: Dict[str, int]) -> None:
        """更新配额日志"""
        self.print_status("更新配额使用记录", level='info')
        quota_data = self._load_daily_quota()

        # 修改：更新特定模型的使用量
        if "models" not in quota_data:
            # 兼容旧格式，如果没有models字段，则初始化
            self.print_status("配额数据格式不兼容，初始化models字段", level='warning')
            quota_data["models"] = {
                self.model_name: {
                    "limits": self.model_limits,
                    "usage": {
                        "requests": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0
                    },
                    "remaining": {
                        "requests": self.model_limits.get("rpd", 100),
                        "tokens": self.model_limits.get("tpm", 100000)
                    },
                    "records": []
                }
            }

        # 确保当前模型存在于models字典中
        if self.model_name not in quota_data["models"]:
            self.print_status(f"在配额记录中添加新模型: {self.model_name}", level='info')
            quota_data["models"][self.model_name] = {
                "limits": self.model_limits,
                "usage": {
                    "requests": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                },
                "remaining": {
                    "requests": self.model_limits.get("rpd", 100),
                    "tokens": self.model_limits.get("tpm", 100000)
                },
                "records": []
            }

        # 更新特定模型的使用量
        model_data = quota_data["models"][self.model_name]
        model_data["usage"]["requests"] += 1
        model_data["usage"]["input_tokens"] += token_usage["input_tokens"]
        model_data["usage"]["output_tokens"] += token_usage["output_tokens"]
        model_data["usage"]["total_tokens"] += token_usage["total_tokens"]

        # 更新剩余量
        model_data["remaining"]["requests"] = max(0,
                                                  self.model_limits.get("rpd", 100) - model_data["usage"]["requests"])

        # 添加记录
        record = {
            "timestamp": datetime.now().isoformat(),
            "token_usage": token_usage,
            "remaining_requests": model_data["remaining"]["requests"]
        }
        model_data["records"].append(record)

        self.print_status(
            f"更新使用量: 请求+1, 输入tokens+{token_usage['input_tokens']}, 输出tokens+{token_usage['output_tokens']}",
            level='info')
        self.print_status(f"剩余请求数: {model_data['remaining']['requests']}",
                          level='warning' if model_data['remaining']['requests'] < 10 else 'info')

        # 保存更新后的数据
        self._save_daily_quota(quota_data)

    def get_quota_status(self) -> Dict[str, Any]:
        """获取当前配额状态"""
        self.print_status("获取当前配额状态", level='info')
        quota_data = self._load_daily_quota()

        # 修改：从多模型结构中获取当前模型的数据
        if "models" not in quota_data or self.model_name not in quota_data["models"]:
            # 如果找不到当前模型的数据，返回默认值
            self.print_status(f"找不到模型{self.model_name}的配额数据，返回默认值", level='warning')
            return {
                "date": quota_data.get("date", datetime.now().date().isoformat()),
                "model": self.model_name,
                "daily_requests": "0/0",
                "usage_percentage": "0.0%",
                "remaining_requests": 0,
                "total_tokens_used": 0,
                "quota_warning": False,
                "recent_requests_per_minute": len(self.request_times)
            }

        # 获取当前模型的数据
        model_data = quota_data["models"][self.model_name]
        daily_limit = self.model_limits.get("rpd", 100)
        usage_pct = (model_data["usage"]["requests"] / daily_limit) * 100 if daily_limit > 0 else 0

        # 返回当前模型的配额状态
        status = {
            "date": quota_data["date"],
            "model": self.model_name,
            "daily_requests": f"{model_data['usage']['requests']}/{daily_limit}",
            "usage_percentage": f"{usage_pct:.1f}%",
            "remaining_requests": model_data["remaining"]["requests"],
            "total_tokens_used": model_data["usage"]["total_tokens"],
            "quota_warning": usage_pct > 80,
            "recent_requests_per_minute": len(self.request_times),
            # 新增：返回所有模型的基本使用情况
            "all_models_summary": {
                model: {
                    "requests": data["usage"]["requests"],
                    "total_tokens": data["usage"]["total_tokens"],
                    "remaining_requests": data["remaining"]["requests"]
                } for model, data in quota_data["models"].items()
            }
        }

        if status["quota_warning"]:
            self.print_status(f"配额警告: 已使用{usage_pct:.1f}%，超过80%警戒线", level='warning')

        return status

    def generate_text(self, contents, config=None):
        """
        生成文本，包含配额控制和监控

        Args:
            contents: 输入内容
            config: 生成配置

        Returns:
            Response: API响应对象，或None（如果出错）
        """
        # 记录请求时间
        request_time = time.time()
        self.request_times.append(request_time)
        self.print_status("开始生成文本（带配额控制）", level='info')

        try:
            # 调用父类方法生成文本
            response = super().generate_text(contents, config)

            # 生成后延迟
            self.print_status("生成完成，开始智能延迟", level='info')
            self.smart_sleep()

            # 如果响应正常，计算token消耗并更新配额
            if response is not None:
                self.print_status("计算token消耗并更新配额", level='info')
                token_usage = self.calculate_response_tokens(response)
                self._update_quota_log(token_usage)
                self.print_status("配额更新完成", level='success')
            else:
                self.print_status("响应为空，跳过配额更新", level='warning')

            return response

        except Exception as e:
            self.print_status(f"生成文本失败: {e}", level='error')
            # 即使出错也要延迟，避免频繁重试
            self.smart_sleep()
            return None


class EnhancedGenAI(QuotaControlledGenAI):
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

    # 错误类型分类
    ERROR_TYPES = {
        # 客户端错误 (4xx)
        "INVALID_ARGUMENT": {
            "retryable": False,
            "description": "请求格式错误或参数拼写错误",
            "solution": "检查API参考文档，确认请求格式正确"
        },
        "FAILED_PRECONDITION": {
            "retryable": False,
            "description": "免费层级不支持当前地区",
            "solution": "在Google AI Studio启用付费方案"
        },
        "PERMISSION_DENIED": {
            "retryable": False,
            "description": "API密钥权限不足",
            "solution": "检查API密钥设置和访问权限"
        },
        "NOT_FOUND": {
            "retryable": False,
            "description": "请求的资源不存在",
            "solution": "验证文件路径和API版本参数"
        },
        "RESOURCE_EXHAUSTED": {
            "retryable": True,
            "description": "超出速率限制",
            "solution": "控制请求频率或申请增加配额"
        },
        # 服务器错误 (5xx)
        "INTERNAL": {
            "retryable": True,
            "description": "服务器内部错误",
            "solution": "减少输入长度或切换模型重试"
        },
        "UNAVAILABLE": {
            "retryable": True,
            "description": "服务暂时不可用",
            "solution": "切换到其他模型或稍后重试"
        },
        "DEADLINE_EXCEEDED": {
            "retryable": True,
            "description": "处理超时",
            "solution": "增加客户端超时设置"
        }
    }

    # 模型参数限制
    PARAMETER_LIMITS = {
        "candidates": {"min": 1, "max": 8},
        "temperature": {"min": 0.0, "max": 1.0},
        "top_p": {"min": 0.0, "max": 1.0},
        "top_k": {"min": 1, "max": 40}
    }

    def __init__(self,
                 api_key: Optional[str] = None,
                 model_name: str = "gemini-1.5-flash",
                 log_dir: str = "logs",
                 quota_log_dir: str = "quota_logs",
                 custom_sleep_time: Optional[float] = None,
                 max_retries: int = 3,
                 fallback_models: List[str] = None,
                 verbose: bool = True):

        # 初始化父类
        super().__init__(api_key, model_name, log_dir, quota_log_dir, custom_sleep_time, verbose)

        # 错误处理配置
        self.max_retries = max_retries
        self.fallback_models = fallback_models or ["gemini-2.5-flash-lite", "gemini-2.0-flash"]

        self.print_status(f"增强型GenAI客户端初始化完成，模型: {model_name}, 最大重试次数: {max_retries}", level='info')
        self.print_status(f"回退模型列表: {self.fallback_models}", level='info')

    def _classify_error(self, error: Exception) -> Dict[str, Any]:
        """
        对API错误进行分类，确定错误类型和是否可重试

        Args:
            error: 捕获的异常

        Returns:
            Dict: 包含错误类型、描述、解决方案和是否可重试的信息
        """
        error_str = str(error)
        error_info = {
            "type": "UNKNOWN",
            "retryable": False,
            "description": "未知错误",
            "solution": "检查API文档或联系支持团队",
            "original_error": error_str
        }

        # 检查错误类型
        for error_type, info in self.ERROR_TYPES.items():
            if error_type in error_str:
                error_info.update({
                    "type": error_type,
                    "retryable": info["retryable"],
                    "description": info["description"],
                    "solution": info["solution"]
                })
                self.print_status(f"识别到错误类型: {error_type}, 可重试: {info['retryable']}",
                                  level='warning' if info['retryable'] else 'error')
                break

        # 检查是否为网络错误
        if "ConnectionError" in error_str or "Timeout" in error_str:
            error_info.update({
                "type": "NETWORK_ERROR",
                "retryable": True,
                "description": "网络连接错误",
                "solution": "检查网络连接或稍后重试"
            })
            self.print_status("识别到网络连接错误，可重试", level='warning')

        return error_info

    def _validate_config(self, config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        验证并清理配置参数，确保所有参数在有效范围内

        Args:
            config: 原始配置字典

        Returns:
            Dict: 验证并清理后的配置字典
        """
        if config is None:
            self.print_status("配置为空，使用默认配置", level='info')
            return {}

        validated_config = config.copy()
        self.print_status("开始验证配置参数", level='info')

        # 检查并调整参数值
        for param, limits in self.PARAMETER_LIMITS.items():
            if param in validated_config:
                value = validated_config[param]

                # 检查类型
                if param == "candidates" and not isinstance(value, int):
                    self.print_status(f"参数 {param} 应为整数，当前值: {value}，已调整为默认值1", level='warning')
                    validated_config[param] = 1
                elif param in ["temperature", "top_p", "top_k"] and not isinstance(value, (int, float)):
                    default_values = {"temperature": 0.7, "top_p": 0.95, "top_k": 40}
                    self.print_status(f"参数 {param} 应为数值，当前值: {value}，已调整为默认值{default_values[param]}",
                                      level='warning')
                    validated_config[param] = default_values[param]

                # 检查范围
                if param in validated_config:
                    min_val = limits.get("min")
                    max_val = limits.get("max")

                    if min_val is not None and validated_config[param] < min_val:
                        self.print_status(f"参数 {param} 低于最小值 {min_val}，已调整", level='warning')
                        validated_config[param] = min_val

                    if max_val is not None and validated_config[param] > max_val:
                        self.print_status(f"参数 {param} 超过最大值 {max_val}，已调整", level='warning')
                        validated_config[param] = max_val

        self.print_status("配置参数验证完成", level='success')
        return validated_config

    def _validate_contents(self, contents) -> Any:
        """
        验证并规范化输入内容

        Args:
            contents: 输入内容，可以是字符串、列表或其他类型

        Returns:
            规范化后的内容
        """
        self.print_status("开始验证输入内容", level='info')

        # 如果是None，返回空字符串
        if contents is None:
            self.print_status("输入内容为None，已替换为空字符串", level='warning')
            return ""

        # 如果是字符串，直接返回
        if isinstance(contents, str):
            if len(contents) > 100:
                self.print_status(f"输入内容为字符串，长度: {len(contents)}", level='info')
            else:
                self.print_status(f"输入内容为字符串: '{contents}'", level='info')
            return contents

        # 如果是列表，检查每个元素
        if isinstance(contents, list):
            # 如果是空列表，返回空字符串
            if not contents:
                self.print_status("输入内容为空列表，已替换为空字符串", level='warning')
                return ""

            # 检查列表中的每个元素
            for i, item in enumerate(contents):
                if item is None:
                    self.print_status(f"输入内容列表中第{i + 1}项为None，已替换为空字符串", level='warning')
                    contents[i] = ""

            self.print_status(f"输入内容为列表，包含{len(contents)}个元素", level='info')

        self.print_status("输入内容验证完成", level='success')
        return contents

    def generate_text(self, contents, config: Optional[Dict[str, Any]] = None) -> GenerateContentResponse:
        """
        生成文本，包含增强的错误处理和重试机制

        Args:
            contents: 输入内容
            config: 配置参数

        Returns:
            GenerateContentResponse: 生成的内容响应

        Raises:
            Exception: 如果所有尝试都失败，则抛出带有详细信息的异常
        """
        # 验证和清理输入
        self.print_status("开始增强型文本生成", level='info')
        contents = self._validate_contents(contents)
        config = self._validate_config(config)

        # 记录请求信息
        self.print_status(f"使用模型: {self.model_name}, 最大重试次数: {self.max_retries}", level='info')

        # 重试计数
        retry_count = 0
        last_error = None
        last_error_info = None

        # 重试循环
        while retry_count <= self.max_retries:
            try:
                # 如果不是第一次尝试，增加延迟
                if retry_count > 0:
                    backoff_time = min(2 ** retry_count, 30)  # 指数退避，最多30秒
                    self.print_status(f"第{retry_count}次重试，等待{backoff_time}秒", level='warning')
                    time.sleep(backoff_time)

                # 调用父类方法生成文本
                self.print_status(f"尝试 {retry_count + 1}/{self.max_retries + 1} 开始生成", level='info')
                response = super().generate_text(contents, config)

                # 如果成功，返回
                if response:
                    if retry_count > 0:
                        self.print_status(f"在第{retry_count}次重试后成功生成文本", level='success')
                    else:
                        self.print_status("首次尝试成功生成文本", level='success')
                    return response
                else:
                    self.print_status("生成结果为空，计为失败", level='warning')

            except Exception as e:
                last_error = e
                last_error_info = self._classify_error(e)

                # 记录错误信息
                self.print_status(
                    f"尝试 {retry_count + 1}/{self.max_retries + 1} 失败: "
                    f"{last_error_info['type']} - {last_error_info['description']}",
                    level='error'
                )

                # 如果错误不可重试，立即跳出
                if not last_error_info.get("retryable", False):
                    self.print_status(f"错误不可重试，跳过后续尝试", level='error')
                    break

            retry_count += 1

        # 如果所有重试都失败，尝试回退模型
        if last_error:
            self.print_status("所有重试都失败，尝试回退模型", level='warning')

            # 保存原始模型名称
            original_model = self.model_name

            # 尝试每个回退模型
            for fallback_model in self.fallback_models:
                try:
                    self.print_status(f"尝试使用回退模型: {fallback_model}", level='info')

                    # 临时切换模型
                    self.set_model(fallback_model)

                    # 使用回退模型生成内容
                    response = super().generate_text(contents, config)

                    if response:
                        self.print_status(f"回退模型 {fallback_model} 成功生成内容", level='success')
                        # 恢复原始模型
                        self.set_model(original_model)
                        return response
                    else:
                        self.print_status(f"回退模型 {fallback_model} 返回空响应", level='warning')

                except Exception as e:
                    self.print_status(f"回退模型 {fallback_model} 生成失败: {str(e)}", level='error')

                finally:
                    # 恢复原始模型
                    self.print_status(f"恢复原始模型: {original_model}", level='info')
                    self.set_model(original_model)

        # 如果所有尝试都失败，抛出异常
        error_message = "所有生成尝试都失败"
        if last_error_info:
            error_message = (
                f"生成失败: {last_error_info['type']}\n"
                f"描述: {last_error_info['description']}\n"
                f"解决方案: {last_error_info['solution']}\n"
                f"原始错误: {last_error_info['original_error']}"
            )

        self.print_status("所有生成尝试（包括回退模型）均失败", level='error')
        raise Exception(error_message)

# 使用示例
if __name__ == '__main__':
    if False:
        client = BaseGenAI()

        # 初始化对话历史
        dialog_history = []

        # 用户输入
        user_input = "（测试一个对话流程，我问你问题，你随机给出一个结果）明天天气怎么样？"
        user_part = types.Part.from_text(text=user_input)  # 确保只传递一个参数
        dialog_history.append(types.Content(role='user', parts=[user_part]))

        response = client.generate_text(user_input)
        dialog_history.append(types.Content(role='model', parts=[types.Part.from_text(text=response.text)]))

        # 构建上文
        context = '\n'.join([f"{entry.role}: {entry.parts[0].text}" for entry in dialog_history])

        # 输入历史记录作为上文
        new_user_input = "我应该穿什么衣服？"

        response = client.generate_text(contents=[context, new_user_input])
        print(response)
        print("=" * 10)
        print(response.model_dump_json(indent=2))
        print("=" * 10)
        print(response.text)
        print("=" * 10)
        print(context)

    if False:
        client1 = LoggedGenAI(log_dir="my_logs", model_name="gemini-1.5-flash-8b")
        print(f"Client1 日志文件: {client1.log_file}")

        # 进行对话
        try:
            response1 = client1.generate_text("你好，请介绍一下自己")
            print("Response 1:", response1)

            response2 = client1.generate_text("请解释什么是机器学习")
            print("Response 2:", response2)

        except Exception as e:
            print(f"错误: {e}")

        # 查看会话信息
        print("\n会话信息:")
        print(json.dumps(client1.get_session_info(), indent=2, ensure_ascii=False))

        # 关闭会话
        client1.close_session()

        # 创建另一个客户端（会有不同的日志文件）
        client2 = LoggedGenAI(log_dir="my_logs")
        print(f"\nClient2 日志文件: {client2.log_file}")

        print(f"\nClient1总对话次数: {len(client1.conversation_history)}")
    if False:
        """
         QuotaControlledGenAI 使用示例
         """

        # 1. 基本初始化
        print("=== 1. 初始化客户端 ===")
        client = QuotaControlledGenAI(
            log_dir="my_logs",  # 对话日志目录
            quota_log_dir="my_quotas",  # 配额日志目录
            custom_sleep_time=1.5  # 自定义延迟时间（可选）
        )
        print(f"初始化完成，模型: {client.model_name}")
        print(f"基础延迟时间: {client.base_sleep_time:.2f}s")

        # 2. 查看初始配额状态
        print("\n=== 2. 初始配额状态 ===")
        status = client.get_quota_status()
        for key, value in status.items():
            print(f"{key}: {value}")

        # 3. 进行一些API调用
        print("\n=== 3. 进行API调用 ===")

        questions = [
            "什么是人工智能？",
            "请解释机器学习的基本概念",
            "深度学习和传统机器学习有什么区别？"
        ]

        for i, question in enumerate(questions, 1):
            print(f"\n--- 第{i}个问题 ---")
            print(f"问题: {question}")

            # 估算输入token（可选功能）
            estimated_tokens = client.estimate_tokens(question)
            print(f"估算输入tokens: {estimated_tokens}")

            # 生成回答
            response = client.generate_text(question)

            if response:
                print(f"回答: {response.text[:100]}...")
                # 获取实际token消耗
                token_usage = client.calculate_response_tokens(response)
                print(f"实际token消耗: {token_usage}")
            else:
                print("请求失败")

            # 查看当前配额状态
            current_status = client.get_quota_status()
            print(f"剩余请求: {current_status['remaining_requests']}")
            print(f"使用率: {current_status['usage_percentage']}")

            if current_status['quota_warning']:
                print("⚠️ 配额使用警告: 已超过80%")

        # 4. 最终统计
        print("\n=== 4. 最终统计 ===")
        final_status = client.get_quota_status()
        print("配额使用情况:")
        for key, value in final_status.items():
            print(f"  {key}: {value}")

        # 5. 演示配额文件内容
        print("\n=== 5. 配额文件内容示例 ===")
        try:
            with open(client.quota_file, 'r', encoding='utf-8') as f:
                quota_data = json.load(f)

            print("配额文件结构:")
            print(f"  日期: {quota_data['date']}")
            print(f"  模型: {quota_data['model']}")
            print(f"  总请求数: {quota_data['usage']['requests']}")
            print(f"  总token消耗: {quota_data['usage']['total_tokens']}")
            print(f"  剩余请求: {quota_data['remaining']['requests']}")
            print(f"  记录条数: {len(quota_data['records'])}")

            if quota_data['records']:
                print("\n最后一条记录:")
                last_record = quota_data['records'][-1]
                print(f"  时间: {last_record['timestamp']}")
                print(f"  token使用: {last_record['token_usage']}")
                print(f"  剩余请求: {last_record['remaining_requests']}")

        except Exception as e:
            print(f"读取配额文件失败: {e}")
    if True:
        # 初始化增强型客户端
        client = EnhancedGenAI(
            max_retries=2
        )

        # 测试生成方法
        try:
            response = client.generate_text(
                "请简要介绍一下人工智能的发展历程。",
                config={"temperature": 0.7}
            )
            print(f"生成成功! 回答: {response.text[:150]}...")
        except Exception as e:
            print(f"生成失败: {e}")

        # 测试参数验证
        try:
            response = client.generate_text(
                "解释量子计算的基本原理。",
                config={"temperature": 1.5, "candidates": 10}  # 超出限制的参数
            )
            print(f"参数自动调整成功! 回答: {response.text[:150]}...")
        except Exception as e:
            print(f"生成失败: {e}")
