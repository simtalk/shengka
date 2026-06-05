"""
声卡检测V1.0 - 知一科技
一款简单易用的声卡信息检测工具
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform
import subprocess
import re
import threading


class SoundCardChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("声卡检测 V1.0 - 知一科技")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        self.setup_ui()
    
    def setup_ui(self):
        # 标题
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🎧 声卡检测 V1.0", 
            font=("Microsoft YaHei", 20, "bold"),
            fg="white", 
            bg="#2c3e50"
        )
        title_label.pack(pady=15)
        
        # 子标题
        subtitle_label = tk.Label(
            title_frame, 
            text="知一科技出品", 
            font=("Microsoft YaHei", 10),
            fg="#bdc3c7", 
            bg="#2c3e50"
        )
        subtitle_label.pack()
        
        # 按钮区域
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        self.scan_btn = tk.Button(
            btn_frame,
            text="🔍 一键检测声卡信息",
            font=("Microsoft YaHei", 14),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.start_scan
        )
        self.scan_btn.pack(side=tk.LEFT, padx=10)
        
        self.about_btn = tk.Button(
            btn_frame,
            text="ℹ️ 关于",
            font=("Microsoft YaHei", 14),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.show_about
        )
        self.about_btn.pack(side=tk.LEFT, padx=10)
        
        # 结果显示区域
        result_frame = tk.Frame(self.root, bg="white", bd=2, relief=tk.SUNKEN)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建Treeview显示结果
        columns = ("项目", "信息")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("项目", text="项目")
        self.tree.heading("信息", text="信息")
        
        self.tree.column("项目", width=200, anchor="w")
        self.tree.column("信息", width=450, anchor="w")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 样式
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 11, "bold"))
        style.configure("Treeview", font=("Microsoft YaHei", 10), rowheight=28)
        
        # 状态栏
        self.status_label = tk.Label(
            self.root, 
            text="就绪", 
            font=("Microsoft YaHei", 9),
            bg="#ecf0f1",
            anchor="w"
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    def start_scan(self):
        """启动扫描线程"""
        self.scan_btn.config(state="disabled", text="检测中...")
        self.status_label.config(text="正在检测声卡信息...")
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        thread = threading.Thread(target=self.scan_sound_card, daemon=True)
        thread.start()
    
    def scan_sound_card(self):
        """扫描声卡信息"""
        results = []
        
        try:
            # 获取系统信息
            results.append(("操作系统", platform.system() + " " + platform.release()))
            results.append(("操作系统版本", platform.version()))
            results.append(("机器类型", platform.machine()))
            results.append(("处理器", platform.processor()))
            
            # Windows系统使用wmic命令
            if platform.system() == "Windows":
                results.extend(self.get_windows_sound_info())
            else:
                results.append(("状态", "当前仅支持Windows系统"))
            
        except Exception as e:
            results.append(("错误", str(e)))
        
        # 在主线程更新UI
        self.root.after(0, lambda: self.update_results(results))
    
    def get_windows_sound_info(self):
        """获取Windows声卡信息"""
        results = []
        
        try:
            # 获取音频设备信息
            output = subprocess.check_output(
                "powershell -Command \"Get-WmiObject Win32_SoundDevice | Select-Object Name, DeviceID, Status, Manufacturer, ProductName | Format-List\"",
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if output:
                lines = output.strip().split('\n')
                device_count = 0
                current_device = {}
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        if current_device:
                            device_count += 1
                            prefix = f"声卡{device_count}"
                            results.append((f"{prefix}名称", current_device.get('Name', '未知')))
                            results.append((f"{prefix}设备ID", current_device.get('DeviceID', '未知')))
                            results.append((f"{prefix}状态", current_device.get('Status', '未知')))
                            results.append((f"{prefix}制造商", current_device.get('Manufacturer', '未知')))
                            results.append((f"{prefix}产品名称", current_device.get('ProductName', '未知')))
                            current_device = {}
                    else:
                        if ':' in line:
                            key, value = line.split(':', 1)
                            current_device[key.strip()] = value.strip()
                
                # 处理最后一个设备
                if current_device:
                    device_count += 1
                    prefix = f"声卡{device_count}"
                    results.append((f"{prefix}名称", current_device.get('Name', '未知')))
                    results.append((f"{prefix}设备ID", current_device.get('DeviceID', '未知')))
                    results.append((f"{prefix}状态", current_device.get('Status', '未知')))
                    results.append((f"{prefix}制造商", current_device.get('Manufacturer', '未知')))
                    results.append((f"{prefix}产品名称", current_device.get('ProductName', '未知')))
                
                if device_count == 0:
                    results.append(("状态", "未检测到声卡设备"))
            
        except subprocess.CalledProcessError:
            results.append(("状态", "无法获取声卡信息"))
        except Exception as e:
            results.append(("错误", str(e)))
        
        # 获取音频控制器信息
        try:
            output = subprocess.check_output(
                "powershell -Command \"Get-WmiObject Win32_OperatingSystem | Select-Object Caption, OSArchitecture, Version | Format-List\"",
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
        except:
            pass
        
        # 获取声卡驱动信息
        try:
            driver_output = subprocess.check_output(
                "powershell -Command \"driverquery /FO LIST /SI | Select-String -Pattern 'audio|Audio|sound|Sound|声卡'\"",
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if driver_output.strip():
                results.append(("相关驱动", driver_output.strip().replace('\n', ' | ')))
        except:
            pass
        
        # 获取播放设备
        try:
            playback = subprocess.check_output(
                "powershell -Command \"Get-WmiObject Win32_LogicalSoundDevice | Select-Object ProductName, DeviceID | Format-List\"",
                shell=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if playback and "ProductName" in playback:
                lines = playback.strip().split('\n')
                for line in lines:
                    if 'ProductName' in line or 'DeviceID' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            results.append(("播放设备" if 'ProductName' in line else "设备ID", parts[1].strip()))
        except:
            pass
        
        return results
    
    def update_results(self, results):
        """更新结果显示"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, (key, value) in enumerate(results):
            tags = ()
            if "状态" in key and value == "OK":
                tags = ("success",)
            elif "错误" in key:
                tags = ("error",)
            
            self.tree.insert("", tk.END, values=(key, value), tags=tags)
        
        # 配置标签颜色
        self.tree.tag_configure("success", foreground="#27ae60")
        self.tree.tag_configure("error", foreground="#e74c3c")
        
        self.scan_btn.config(state="normal", text="🔍 一键检测声卡信息")
        self.status_label.config(text=f"检测完成，共发现 {len([k for k,v in results if '声卡' in k])} 个声卡设备")
    
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于 - 声卡检测 V1.0")
        about_window.geometry("450x400")
        about_window.resizable(False, False)
        about_window.configure(bg="#f0f0f0")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 居中显示
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - 450) // 2
        y = (about_window.winfo_screenheight() - 400) // 2
        about_window.geometry(f"450x400+{x}+{y}")
        
        # 关于内容
        content_frame = tk.Frame(about_window, bg="white", bd=2, relief=tk.RAISED)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Logo/图标区域
        icon_label = tk.Label(
            content_frame,
            text="🎧",
            font=("Arial", 50),
            bg="white"
        )
        icon_label.pack(pady=(20, 10))
        
        # 软件名称
        name_label = tk.Label(
            content_frame,
            text="声卡检测 V1.0",
            font=("Microsoft YaHei", 18, "bold"),
            bg="white",
            fg="#2c3e50"
        )
        name_label.pack()
        
        # 公司名称
        company_label = tk.Label(
            content_frame,
            text="知一科技",
            font=("Microsoft YaHei", 12),
            bg="white",
            fg="#7f8c8d"
        )
        company_label.pack(pady=(5, 15))
        
        # 分隔线
        tk.Frame(content_frame, height=2, bg="#bdc3c7").pack(fill=tk.X, padx=30)
        
        # 功能介绍
        intro_text = """一款简单易用的声卡信息检测工具

主要功能：
• 一键检测本机声卡设备
• 查看声卡驱动名称和状态
• 显示设备详细信息
• 支持Windows系统"""
        
        intro_label = tk.Label(
            content_frame,
            text=intro_text,
            font=("Microsoft YaHei", 10),
            bg="white",
            fg="#34495e",
            justify=tk.LEFT
        )
        intro_label.pack(pady=15, padx=20)
        
        # 分隔线
        tk.Frame(content_frame, height=2, bg="#bdc3c7").pack(fill=tk.X, padx=30)
        
        # 反馈信息
        feedback_label = tk.Label(
            content_frame,
            text="反馈微信：Hello-byte",
            font=("Microsoft YaHei", 11, "bold"),
            bg="white",
            fg="#3498db"
        )
        feedback_label.pack(pady=15)
        
        # 版权信息
        copyright_label = tk.Label(
            content_frame,
            text="© 2024 知一科技 版权所有",
            font=("Microsoft YaHei", 9),
            bg="white",
            fg="#95a5a6"
        )
        copyright_label.pack(pady=(0, 15))
        
        # 关闭按钮
        close_btn = tk.Button(
            about_window,
            text="关闭",
            font=("Microsoft YaHei", 11),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            relief=tk.FLAT,
            padx=30,
            pady=5,
            cursor="hand2",
            command=about_window.destroy
        )
        close_btn.pack(pady=(0, 15))


def main():
    root = tk.Tk()
    
    # 设置窗口图标（如果可用）
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = SoundCardChecker(root)
    root.mainloop()


if __name__ == "__main__":
    main()