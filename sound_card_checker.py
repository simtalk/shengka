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
import sys


def safe_decode(output):
    """安全解码，解决中文乱码问题"""
    if output is None:
        return ""
    if isinstance(output, str):
        return output
    # 尝试多种编码
    for encoding in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'cp936']:
        try:
            return output.decode(encoding)
        except:
            try:
                return output.decode('utf-8', errors='replace')
            except:
                pass
    return str(output)


def run_command(cmd):
    """安全执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        # 清理可能的乱码字符
        output = result.stdout
        if output:
            # 移除控制字符和非法字符
            output = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', output)
            # 移除常见的Unicode替换字符
            output = output.replace('\ufffd', '')
            output = output.replace('\u2588', '')  # █
            output = output.replace('\u2502', '|')  # │
            output = output.replace('\u251c', '+')  # ├
            output = output.replace('\u2514', '+')  # └
            output = output.replace('\u2524', '+')  # ┤
            output = output.replace('\u253c', '+')  # ┼
            output = output.replace('\u2500', '-')  # ─
            output = output.replace('\u2551', '|')  # ║
            output = output.replace('\u256d', '+')  # ╭
            output = output.replace('\u256e', '+')  # ╮
            output = output.replace('\u256f', '+')  # ╯
            output = output.replace('\u2570', '+')  # ╰
        return output
    except Exception as e:
        return ""


def clean_text(text):
    """清理文本中的乱码字符"""
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    text = text.replace('\ufffd', '')
    text = text.replace('\u2588', '')
    text = text.replace('\u2502', '|')
    text = text.replace('\u251c', '+')
    text = text.replace('\u2514', '+')
    text = text.replace('\u2524', '+')
    text = text.replace('\u253c', '+')
    text = text.replace('\u2500', '-')
    text = text.replace('\u2551', '|')
    return text


class SoundCardChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("声卡检测 V1.0 - 知一科技")
        self.root.geometry("750x600")
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
        columns = ("类型", "项目", "信息")
        self.tree = ttk.Treeview(result_frame, columns=columns, show="headings", height=18)
        
        self.tree.heading("类型", text="类型")
        self.tree.heading("项目", text="项目")
        self.tree.heading("信息", text="信息")
        
        self.tree.column("类型", width=100, anchor="center")
        self.tree.column("项目", width=180, anchor="w")
        self.tree.column("信息", width=420, anchor="w")
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 样式
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Microsoft YaHei", 11, "bold"))
        style.configure("Treeview", font=("Microsoft YaHei", 10), rowheight=26)
        
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
            results.append(("系统信息", "操作系统", platform.system() + " " + platform.release()))
            results.append(("系统信息", "操作系统版本", platform.version()))
            results.append(("系统信息", "机器类型", platform.machine()))
            results.append(("系统信息", "处理器", platform.processor()))
            
            # Windows系统使用wmic命令
            if platform.system() == "Windows":
                results.extend(self.get_windows_sound_info())
            else:
                results.append(("状态", "系统", "当前仅支持Windows系统"))
            
        except Exception as e:
            results.append(("错误", "检测异常", str(e)))
        
        # 在主线程更新UI
        self.root.after(0, lambda: self.update_results(results))
    
    def get_windows_sound_info(self):
        """获取Windows声卡信息"""
        results = []
        
        try:
            # 使用AudioDeviceCmdlets或直接使用Windows API获取音频设备
            # 获取所有音频终结点设备（播放设备）
            playback_cmd = '''powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $devices = [System.Windows.Forms.SystemInformation]::Audio; if($devices) { Write-Output ('Speaker: ' + $devices.Speakers) }"'''
            
            # 使用WMI获取更详细的音频设备信息
            all_output = run_command(
                'powershell -Command "Get-WmiObject Win32_SoundDevice | Format-List"'
            )
            
            # 获取音频渲染设备（播放）
            render_output = run_command(
                '''powershell -Command "
                    try {
                        Add-Type -Path '$env:SystemRoot\\System32\\AudioEndpointBuilder.dll' -ErrorAction SilentlyContinue
                    } catch {}
                    $sessions = Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Render' -ErrorAction SilentlyContinue
                    if ($sessions) {
                        Get-ChildItem -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Render' -Recurse | ForEach-Object {
                            $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
                            if ($props -and $props.DeviceName) {
                                Write-Output ('Name: ' + $props.DeviceName)
                                Write-Output ('State: ' + $props.State)
                            }
                        }
                    }
                "'''
            )
            
            # 获取音频捕获设备（录音）
            capture_output = run_command(
                '''powershell -Command "
                    $sessions = Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Capture' -ErrorAction SilentlyContinue
                    if ($sessions) {
                        Get-ChildItem -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\MMDevices\\Audio\\Capture' -Recurse | ForEach-Object {
                            $props = Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue
                            if ($props -and $props.DeviceName) {
                                Write-Output ('Name: ' + $props.DeviceName)
                                Write-Output ('State: ' + $props.State)
                            }
                        }
                    }
                "'''
            )
            
            # 解析播放设备 - 区分扬声器和耳机
            if render_output and render_output.strip():
                results.extend(self.parse_audio_devices(render_output, "🔊 扬声器/耳机"))
            elif all_output:
                results.extend(self.parse_devices(all_output, "🔊 扬声器/耳机"))
            
            # 解析录音设备
            if capture_output and capture_output.strip():
                results.extend(self.parse_audio_devices(capture_output, "🎤 录音设备"))
            
            # 如果没有找到任何设备，使用WMI获取全部
            if not results and all_output:
                results.extend(self.parse_devices(all_output, "🔊 音频设备"))
            
            if not results:
                results.append(("状态", "检测结果", "未检测到声卡设备"))
            
        except Exception as e:
            results.append(("错误", "获取失败", str(e)))
        
        # 获取音频驱动信息 - 只获取设备名称，简化输出
        try:
            driver_output = run_command(
                '''powershell -Command "Get-WmiObject Win32_SoundDevice | Select-Object Name, Status | Format-Table -AutoSize"'''
            )
            if driver_output and driver_output.strip():
                # 只保留干净的行
                for line in driver_output.strip().split('\n'):
                    cleaned = clean_text(line).strip()
                    if cleaned and 'Name' not in cleaned and cleaned != '':
                        results.append(("驱动信息", "驱动", cleaned))
        except:
            pass
        
        return results
    
    def parse_devices(self, output, device_type):
        """解析设备信息"""
        results = []
        if not output:
            return results
            
        lines = output.strip().split('\n')
        current_device = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_device:
                    name = clean_text(current_device.get('Name', '未知设备'))
                    device_id = clean_text(current_device.get('DeviceID', current_device.get('PSPath', '')))
                    status = clean_text(current_device.get('Status', current_device.get('State', '未知')))
                    manufacturer = clean_text(current_device.get('Manufacturer', current_device.get('PSParentPath', '').split('\\')[-1] if current_device.get('PSParentPath') else '未知'))
                    
                    results.append((device_type, "设备名称", name))
                    results.append((device_type, "设备ID", device_id))
                    results.append((device_type, "状态", status))
                    results.append((device_type, "制造商", manufacturer))
                    current_device = {}
            else:
                if ':' in line:
                    key, value = line.split(':', 1)
                    current_device[key.strip()] = value.strip()
        
        # 处理最后一个设备
        if current_device:
            name = clean_text(current_device.get('Name', '未知设备'))
            device_id = clean_text(current_device.get('DeviceID', current_device.get('PSPath', '')))
            status = clean_text(current_device.get('Status', current_device.get('State', '未知')))
            manufacturer = clean_text(current_device.get('Manufacturer', current_device.get('PSParentPath', '').split('\\')[-1] if current_device.get('PSParentPath') else '未知'))
            
            results.append((device_type, "设备名称", name))
            results.append((device_type, "设备ID", device_id))
            results.append((device_type, "状态", status))
            results.append((device_type, "制造商", manufacturer))
        
        return results
    
    def parse_audio_devices(self, output, device_type):
        """解析音频设备信息（从注册表获取）"""
        results = []
        if not output:
            return results
        
        lines = output.strip().split('\n')
        device_count = 0
        current_name = ""
        current_state = ""
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                value = clean_text(value.strip())
                if key == 'Name' and value:
                    current_name = value
                elif key == 'State' and value:
                    current_state = value
            elif not line and current_name:
                # 空行表示一个设备结束
                device_count += 1
                results.append((device_type, f"设备{device_count}", current_name))
                results.append((device_type, "状态", current_state if current_state else "未知"))
                current_name = ""
                current_state = ""
        
        # 处理最后一个设备
        if current_name:
            device_count += 1
            results.append((device_type, f"设备{device_count}", current_name))
            results.append((device_type, "状态", current_state if current_state else "未知"))
        
        return results
    
    def update_results(self, results):
        """更新结果显示"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for item_type, key, value in results:
            # 清理所有文本
            item_type = clean_text(item_type)
            key = clean_text(key)
            value = clean_text(value)
            
            tags = ()
            if "状态" in key and value == "OK":
                tags = ("success",)
            elif "错误" in item_type:
                tags = ("error",)
            
            self.tree.insert("", tk.END, values=(item_type, key, value), tags=tags)
        
        # 配置标签颜色
        self.tree.tag_configure("success", foreground="#27ae60")
        self.tree.tag_configure("error", foreground="#e74c3c")
        
        # 统计设备数量
        speakers = len([v for v in results if v[0] == "🔊 扬声器/耳机"])
        recorders = len([v for v in results if v[0] == "🎤 录音设备"])
        audio_devices = len([v for v in results if v[0] == "🔊 音频设备"])
        
        if speakers > 0 or recorders > 0:
            device_info = f"检测完成：扬声器/耳机 {speakers//2} 个，录音设备 {recorders//2} 个"
        elif audio_devices > 0:
            device_info = f"检测完成：共发现 {audio_devices//4} 个音频设备"
        else:
            device_info = "检测完成"
        
        self.scan_btn.config(state="normal", text="🔍 一键检测声卡信息")
        self.status_label.config(text=device_info)
    
    def show_about(self):
        """显示关于对话框"""
        about_window = tk.Toplevel(self.root)
        about_window.title("关于 - 声卡检测 V1.0")
        about_window.geometry("450x420")
        about_window.resizable(False, False)
        about_window.configure(bg="#f0f0f0")
        about_window.transient(self.root)
        about_window.grab_set()
        
        # 居中显示
        about_window.update_idletasks()
        x = (about_window.winfo_screenwidth() - 450) // 2
        y = (about_window.winfo_screenheight() - 420) // 2
        about_window.geometry(f"450x420+{x}+{y}")
        
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
• 区分扬声器和录音设备
• 微信：Hello-byte"""
        
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