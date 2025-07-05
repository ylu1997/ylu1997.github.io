import tkinter as tk
from tkinter import messagebox, scrolledtext
from BibConverter import BibConverter


class ConvertGUI:
    """BibTeX转换器图形界面类"""

    def __init__(self, root):
        self.root = root
        self.converter = BibConverter()

        # 设置窗口属性
        self.setup_window()

        # 创建界面
        self.create_widgets()

        # 加载示例数据
        self.load_sample_data()

    def setup_window(self):
        """设置窗口属性"""
        self.root.title("BibTeX 转换器 (支持批量处理)")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)

        # 设置窗口居中
        self.center_window()

    def center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()
        width = 900
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        self.create_title()

        # 输入区域
        self.create_input_area()

        # 按钮区域
        self.create_button_area()

        # 输出区域
        self.create_output_area()

        # 状态栏
        self.create_status_bar()

    def create_title(self):
        """创建标题"""
        title_label = tk.Label(
            self.root,
            text="BibTeX 转 addliterature 格式转换器",
            font=("Arial", 16, "bold"),
            pady=10,
            fg="#2c3e50"
        )
        title_label.pack()

        # 添加批量处理说明
        subtitle_label = tk.Label(
            self.root,
            text="支持单个或多个BibTeX条目的批量转换",
            font=("Arial", 10),
            fg="#7f8c8d"
        )
        subtitle_label.pack()

    def create_input_area(self):
        """创建输入区域"""
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        input_label = tk.Label(
            input_frame,
            text="请粘贴BibTeX内容（支持多个条目）：",
            font=("Arial", 12),
            anchor="w",
            fg="#34495e"
        )
        input_label.pack(fill=tk.X, pady=(0, 5))

        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=12,
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)

    def create_button_area(self):
        """创建按钮区域"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=15)

        # 转换按钮
        self.convert_btn = tk.Button(
            button_frame,
            text="🔄 批量转换",
            command=self.convert_bib,
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.convert_btn.pack(side=tk.LEFT, padx=5)

        # 清空按钮
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ 清空",
            command=self.clear_all,
            font=("Arial", 12),
            bg="#e74c3c",
            fg="white",
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        # 复制结果按钮
        self.copy_btn = tk.Button(
            button_frame,
            text="📋 复制结果",
            command=self.copy_result,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.copy_btn.pack(side=tk.LEFT, padx=5)

        # 验证按钮
        validate_btn = tk.Button(
            button_frame,
            text="✓ 验证格式",
            command=self.validate_format,
            font=("Arial", 12),
            bg="#f39c12",
            fg="white",
            padx=25,
            pady=8,
            relief=tk.FLAT,
            cursor="hand2"
        )
        validate_btn.pack(side=tk.LEFT, padx=5)

    def create_output_area(self):
        """创建输出区域"""
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        output_label = tk.Label(
            output_frame,
            text="转换结果：",
            font=("Arial", 12),
            anchor="w",
            fg="#34495e"
        )
        output_label.pack(fill=tk.X, pady=(0, 5))

        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=10,
            font=("Consolas", 10),
            bg="#f8f9fa",
            wrap=tk.WORD,
            relief=tk.SOLID,
            borderwidth=1
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_var = tk.StringVar()
        self.status_var.set("就绪 - 支持批量处理")

        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_sample_data(self):
        """加载示例数据（包含多个条目）"""
        sample_text = """@article{Kuronya2014LocalPO,
title={Local positivity of linear series on surfaces},
author={Alex Kuronya and Victor Lozovanu},
journal={arXiv: Algebraic Geometry},
year={2014},
url={https://api.semanticscholar.org/CorpusID:119288694}
}

@article{Smith2020TestArticle,
title={Another Test Article for Batch Processing},
author={John Smith and Jane Doe},
journal={Test Journal of Mathematics},
year={2020}
}"""
        self.input_text.insert("1.0", sample_text)

    def convert_bib(self):
        """转换按钮点击事件（支持批量处理）"""
        try:
            # 获取输入内容
            input_content = self.input_text.get("1.0", tk.END).strip()

            if not input_content:
                messagebox.showwarning("警告", "请先输入BibTeX内容！")
                return

            # 更新状态和按钮
            self.status_var.set("正在批量转换...")
            self.convert_btn.config(state=tk.DISABLED)
            self.root.update()

            # 执行批量转换
            success_results, error_messages = self.converter.convert_multiple_bibs(input_content)

            # 清空输出区域
            self.output_text.delete("1.0", tk.END)

            # 只显示转换结果，每个结果一行
            if success_results:
                for result in success_results:
                    self.output_text.insert(tk.END, result + "\n")

            # 如果有错误，在结果后面显示错误信息
            if error_messages:
                if success_results:
                    self.output_text.insert(tk.END, "\n")  # 空行分隔

                self.output_text.insert(tk.END, "错误信息:\n")
                for error in error_messages:
                    self.output_text.insert(tk.END, f"{error}\n")

            # 更新状态
            if success_results and not error_messages:
                self.status_var.set(f"批量转换成功！共 {len(success_results)} 个条目")
                messagebox.showinfo("成功", f"批量转换完成！\n成功转换 {len(success_results)} 个条目。")
            elif success_results and error_messages:
                self.status_var.set(f"部分转换成功：{len(success_results)} 成功，{len(error_messages)} 失败")
                messagebox.showwarning("部分成功",
                                       f"批量转换部分完成：\n✅ 成功：{len(success_results)} 个条目\n❌ 失败：{len(error_messages)} 个条目\n\n详细信息请查看结果区域。")
            else:
                self.status_var.set("批量转换失败")
                messagebox.showerror("失败", "所有条目转换都失败了，请检查BibTeX格式。")

        except Exception as e:
            # 显示错误对话框
            messagebox.showerror("转换错误", f"批量转换失败：\n\n{str(e)}")
            self.status_var.set("批量转换失败")

        finally:
            # 恢复按钮状态
            self.convert_btn.config(state=tk.NORMAL)

    def validate_format(self):
        """验证BibTeX格式（支持批量）"""
        input_content = self.input_text.get("1.0", tk.END).strip()

        if not input_content:
            messagebox.showwarning("警告", "请先输入BibTeX内容！")
            return

        is_valid, message = self.converter.validate_bib_format(input_content)

        if is_valid:
            messagebox.showinfo("验证结果", f"✓ BibTeX格式正确！\n{message}")
            self.status_var.set("格式验证通过")
        else:
            messagebox.showerror("验证结果", f"✗ BibTeX格式错误：\n\n{message}")
            self.status_var.set("格式验证失败")

    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.status_var.set("已清空 - 支持批量处理")

    def copy_result(self):
        """复制结果到剪贴板"""
        try:
            result = self.output_text.get("1.0", tk.END).strip()
            if not result:
                messagebox.showwarning("警告", "没有可复制的结果！")
                return

            # 复制到剪贴板
            self.root.clipboard_clear()
            self.root.clipboard_append(result)
            self.root.update()

            self.status_var.set("批量结果已复制到剪贴板")
            messagebox.showinfo("成功", "批量转换结果已复制到剪贴板！")

        except Exception as e:
            messagebox.showerror("错误", f"复制失败：{str(e)}")


def main():
    """主函数"""
    root = tk.Tk()
    app = ConvertGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()