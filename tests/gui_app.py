"""
爱蜜莉雅技能包 - GUI 测试控制台
基于 tkinter，集成测试运行、场景预览、报告管理
"""

import os
import re
import sys
import json
import shlex
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path

# ── 路径常量 ────────────────────────────────────────────
TESTS_DIR = Path(__file__).parent
PROJECT_DIR = TESTS_DIR.parent
QUESTIONS_DIR = TESTS_DIR / "questions"
RESULTS_DIR = TESTS_DIR / "results"
ENV_FILE = TESTS_DIR / ".env"
PYTHON_EXE = TESTS_DIR / "venv" / "Scripts" / "python.exe"
TEST_RUNNER = TESTS_DIR / "test_integration.py"
CHAT_SCRIPT = TESTS_DIR / "chat.py"


# ── .env 配置读写 ───────────────────────────────────────
def load_env():
    """从 .env 读取配置，返回 dict"""
    cfg = {"API_BASE_URL": "", "API_KEY": "", "API_MODEL": "", "API_TEMPERATURE": "0.5"}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                k, v = k.strip(), v.strip()
                if k in cfg:
                    cfg[k] = v
    return cfg


def save_env(cfg: dict):
    """保存配置到 .env，保留原有注释"""
    lines = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()

    new_lines = []
    written_keys = set()
    for line in lines:
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            k = stripped.split("=", 1)[0].strip()
            if k in cfg:
                new_lines.append(f"{k}={cfg[k]}")
                written_keys.add(k)
                continue
        new_lines.append(line)

    # 追加未写入的 key
    for k, v in cfg.items():
        if k not in written_keys:
            new_lines.append(f"{k}={v}")

    ENV_FILE.write_text("\n".join(new_lines), encoding="utf-8")


# ── 场景加载 ────────────────────────────────────────────
def load_scenes():
    """扫描 questions/ 下 scene_*.json，返回 {场景名: {file, cases, ...}}"""
    scenes = {}
    for f in sorted(QUESTIONS_DIR.glob("scene_*.json")):
        data = json.loads(f.read_text(encoding="utf-8"))
        name = data.get("scene", f.stem)
        cases = []
        for c in data.get("cases", []):
            qs = [m["content"] for m in c.get("messages", []) if m["role"] == "user"]
            cases.append({
                "id": c["id"],
                "title": c.get("title", ""),
                "questions": qs,
                "keywords": c.get("expected_keywords", []),
                "metrics": c.get("metrics_focus", []),
            })
        scenes[name] = {"file": f, "cases": cases}
    return scenes


def get_next_report_num():
    """返回 results/ 下 .txt 文件数 + 1"""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    count = len(list(RESULTS_DIR.glob("测试*.txt")))
    return count + 1


# ── 主应用 ──────────────────────────────────────────────
class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("爱蜜莉雅技能包 - 测试控制台")
        root.geometry("900x720")
        root.minsize(800, 600)

        self.env_cfg = load_env()
        self.scenes = load_scenes()
        self.process = None
        self.running = False

        self._build_ui()
        self._refresh_scene_preview()

    # ── UI 构建 ─────────────────────────────────────────
    def _build_ui(self):
        root = self.root
        style = ttk.Style()
        style.theme_use("clam")

        # 主容器
        main = ttk.Frame(root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ── 行0: API 配置 ──
        cfg_frame = ttk.LabelFrame(main, text="API 配置", padding=5)
        cfg_frame.pack(fill=tk.X, pady=(0, 6))

        fld = {}
        for i, (key, label) in enumerate([("API_BASE_URL", "端点"), ("API_KEY", "Key"),
                                           ("API_MODEL", "模型"), ("API_TEMPERATURE", "温度")]):
            ttk.Label(cfg_frame, text=label + ":", width=5).grid(row=0, column=i * 2, sticky="e", padx=(2, 2))
            val = self.env_cfg.get(key, "")
            if key == "API_KEY" and val:
                display = val[:4] + "●●●●" if len(val) > 4 else "●●●●"
            else:
                display = val
            var = tk.StringVar(value=display)
            entry = ttk.Entry(cfg_frame, textvariable=var, width=20)
            entry.grid(row=0, column=i * 2 + 1, padx=(0, 6))
            fld[key] = (entry, var)
        self._cfg_fields = fld

        edit_btn = ttk.Button(cfg_frame, text="保存配置", command=self._save_config)
        edit_btn.grid(row=0, column=8, padx=4)

        # ── 行1: 测试模式 + 场景选择 ──
        mode_frame = ttk.Frame(main)
        mode_frame.pack(fill=tk.X, pady=(0, 4))

        self._mode_var = tk.StringVar(value="all")
        ttk.Radiobutton(mode_frame, text="全部场景", variable=self._mode_var,
                        value="all", command=self._on_mode_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="单场景", variable=self._mode_var,
                        value="single", command=self._on_mode_change).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(mode_frame, text="自由输入", variable=self._mode_var,
                        value="free", command=self._on_mode_change).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Label(mode_frame, text="  场景:").pack(side=tk.LEFT, padx=(10, 2))
        self._scene_var = tk.StringVar()
        self._scene_combo = ttk.Combobox(mode_frame, textvariable=self._scene_var,
                                          state="readonly", width=18)
        self._scene_combo["values"] = list(self.scenes.keys())
        if self.scenes:
            self._scene_combo.current(0)
        self._scene_combo.pack(side=tk.LEFT, padx=2)
        self._scene_combo.bind("<<ComboboxSelected>>", lambda e: self._refresh_scene_preview())

        self._btn_open_json = ttk.Button(mode_frame, text="打开问题集文件",
                                         command=self._open_scene_json)
        # 初始隐藏（仅在单场景模式显示）

        self._btn_start = ttk.Button(mode_frame, text="▶ 开始测试", command=self._start_test)
        self._btn_start.pack(side=tk.RIGHT, padx=4)

        # ── 行2: 可拖拽分隔预览区 + 终端区 ──
        pane = ttk.PanedWindow(main, orient=tk.VERTICAL)
        pane.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        # 预览区
        preview_frame = ttk.LabelFrame(pane, text="场景问题预览", padding=5)
        pane.add(preview_frame, weight=1)

        self._preview_text = scrolledtext.ScrolledText(preview_frame, wrap=tk.WORD,
                                                        font=("Microsoft YaHei", 9))
        self._preview_text.pack(fill=tk.BOTH, expand=True)

        open_json_btn = ttk.Button(preview_frame, text="打开场景 JSON 文件",
                                   command=self._open_scene_json)
        open_json_btn.pack(anchor="e", pady=(2, 0))

        # 终端输出区
        term_frame = ttk.LabelFrame(pane, text="终端输出", padding=5)
        pane.add(term_frame, weight=3)

        self._term = tk.Text(term_frame, wrap=tk.WORD, state=tk.DISABLED,
                              bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10),
                              insertbackground="white")
        term_scroll = ttk.Scrollbar(term_frame, command=self._term.yview)
        self._term.configure(yscrollcommand=term_scroll.set)
        self._term.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        term_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 状态栏
        self._status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main, textvariable=self._status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self._on_mode_change()

    # ── 终端输出 ─────────────────────────────────────────
    def _term_log(self, msg: str):
        self._term.configure(state=tk.NORMAL)
        self._term.insert(tk.END, msg)
        self._term.see(tk.END)
        self._term.configure(state=tk.DISABLED)

    def _term_clear(self):
        self._term.configure(state=tk.NORMAL)
        self._term.delete("1.0", tk.END)
        self._term.configure(state=tk.DISABLED)

    # ── 模式切换 ─────────────────────────────────────────
    def _on_mode_change(self):
        mode = self._mode_var.get()
        if mode == "single":
            self._scene_combo.configure(state="readonly")
            self._btn_open_json.pack(side=tk.LEFT, padx=2, before=self._btn_start)
            self._btn_start.configure(text="▶ 开始测试")
        elif mode == "all":
            self._scene_var.set("全部场景")
            self._scene_combo.configure(state="disabled")
            self._btn_open_json.pack_forget()
            self._btn_start.configure(text="▶ 开始全量测试")
        else:
            self._scene_var.set("")
            self._scene_combo.configure(state="disabled")
            self._btn_open_json.pack_forget()
            self._btn_start.configure(text="▶ 开始自由对话")
        self._refresh_scene_preview()

    # ── 场景预览 ─────────────────────────────────────────
    def _refresh_scene_preview(self):
        mode = self._mode_var.get()
        self._preview_text.configure(state=tk.NORMAL)
        self._preview_text.delete("1.0", tk.END)

        if mode == "all":
            total = 0
            for name, sc in self.scenes.items():
                self._preview_text.insert(tk.END, f"【{name}】{len(sc['cases'])} 个用例\n")
                for c in sc["cases"]:
                    q_preview = c["questions"][0] if c["questions"] else ""
                    if len(q_preview) > 60:
                        q_preview = q_preview[:57] + "..."
                    self._preview_text.insert(tk.END, f"  {c['id']} - {c['title']}\n")
                    self._preview_text.insert(tk.END, f"    Q: {q_preview}\n")
                    self._preview_text.insert(tk.END, f"    关键词: {', '.join(c['keywords'])}\n")
                total += len(sc["cases"])
                self._preview_text.insert(tk.END, "\n")
            self._preview_text.insert(tk.END, f"共 {len(self.scenes)} 个场景, {total} 个用例\n")

        elif mode == "single":
            name = self._scene_var.get()
            if name and name in self.scenes:
                sc = self.scenes[name]
                for c in sc["cases"]:
                    self._preview_text.insert(tk.END, f"▸ {c['id']} - {c['title']}  [{', '.join(c['metrics'])}]\n")
                    for i, q in enumerate(c["questions"]):
                        self._preview_text.insert(tk.END, f"    Q{i+1}: {q}\n")
                    self._preview_text.insert(tk.END, f"    关键词 ({len(c['keywords'])}): {', '.join(c['keywords'])}\n\n")
            else:
                self._preview_text.insert(tk.END, "请选择一个场景")
        else:
            self._preview_text.insert(tk.END,
                "自由输入模式：将弹出独立命令行窗口，与爱蜜莉雅实时对话。\n"
                "输入 /exit 或按 Ctrl+C 退出。\n\n"
                "注意：自由输入不生成测试报告。"
            )

        self._preview_text.configure(state=tk.DISABLED)

    # ── 配置保存 ─────────────────────────────────────────
    def _save_config(self):
        cfg = {}
        for key, (entry, var) in self._cfg_fields.items():
            val = var.get().strip()
            # Key 脱敏恢复：如果用户没改显示值，用回原始值
            if key == "API_KEY":
                orig = self.env_cfg.get("API_KEY", "")
                if val and val.endswith("●●●●") and orig:
                    val = orig
            cfg[key] = val

        save_env(cfg)
        self.env_cfg = cfg
        self._status_var.set("配置已保存")
        messagebox.showinfo("提示", "配置已保存到 .env")

    # ── 打开场景 JSON ────────────────────────────────────
    def _open_scene_json(self):
        name = self._scene_var.get()
        if name and name in self.scenes:
            os.startfile(str(self.scenes[name]["file"]))
        else:
            # 全量模式打开 config.json
            cfg_path = QUESTIONS_DIR / "config.json"
            if cfg_path.exists():
                os.startfile(str(cfg_path))

    # ── 开始测试 ─────────────────────────────────────────
    def _start_test(self):
        if self.running:
            messagebox.showwarning("提示", "测试正在运行中，请等待完成")
            return

        mode = self._mode_var.get()
        self._term_clear()
        self._term_log(f"══════════════════════════════════════\n")
        self._term_log(f"  爱蜜莉雅技能包 - 测试控制台\n")
        self._term_log(f"══════════════════════════════════════\n\n")

        if mode == "free":
            self._start_free_chat()
            return

        # 验证 Python 解释器
        if not PYTHON_EXE.exists():
            messagebox.showerror("错误", f"未找到 Python 解释器:\n{PYTHON_EXE}")
            return

        # 生成报告编号
        num = get_next_report_num()
        report_name = f"测试{num}.txt"
        report_path = RESULTS_DIR / report_name

        # 构建命令
        cmd = [str(PYTHON_EXE), str(TEST_RUNNER), "-o", report_name]
        if mode == "single":
            name = self._scene_var.get()
            if not name:
                messagebox.showwarning("提示", "请选择一个测试场景")
                return
            # 用文件名关键词匹配：找场景名对应的 scene_xxx.json
            scene_key = self._get_scene_key(name)
            if scene_key:
                cmd.extend(["--scene", scene_key])

        self._status_var.set(f"测试运行中...")
        self._btn_start.configure(state=tk.DISABLED)
        self.running = True

        def target():
            path = str(report_path)
            self._term_log(f"> {' '.join(cmd)}\n\n")

            try:
                # 创建时不打印到控制台的标志
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(TESTS_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    startupinfo=startupinfo,
                )

                for line in self.process.stdout:
                    self._term_log(line)

                self.process.wait()
                rc = self.process.returncode
                self.process = None

                self._term_log(f"\n{'='*60}\n")
                self._term_log(f"  退出码: {rc}\n")
                if rc == 0 and Path(path).exists():
                    self._term_log(f"  报告已生成: {path}\n")
                    self._term_log(f"\n正在打开报告...\n")
                    self.root.after(200, lambda: os.startfile(path))
                else:
                    self._term_log(f"  报告未生成，请检查错误信息\n")
                self._term_log(f"{'='*60}\n")

            except Exception as e:
                self._term_log(f"\n[错误] {e}\n")

            finally:
                self.root.after(0, self._on_test_done)

        threading.Thread(target=target, daemon=True).start()

    def _start_free_chat(self):
        if not PYTHON_EXE.exists():
            messagebox.showerror("错误", f"未找到 Python 解释器:\n{PYTHON_EXE}")
            return
        # 弹出独立命令行窗口
        chat_cmd = f'start "爱蜜莉雅 - 对话" cmd /k "cd /d {TESTS_DIR} && {PYTHON_EXE} {CHAT_SCRIPT}"'
        self._term_log(f"启动自由对话窗口...\n")
        subprocess.Popen(chat_cmd, shell=True)
        self._status_var.set("已启动独立对话窗口")

    def _get_scene_key(self, scene_name: str) -> str:
        """场景名 → 文件名关键词"""
        mapping = {
            "日常闲聊": "daily",
            "核心话题触发": "core",
            "情绪响应测试": "emotion",
            "人际关系测试": "relations",
            "多轮记忆保持": "memory",
            "安全对抗测试": "safety",
            "OOC检测": "ooc",
        }
        return mapping.get(scene_name, "")

    def _on_test_done(self):
        self.running = False
        self._btn_start.configure(state=tk.NORMAL)
        self._status_var.set("测试完成")


# ── 入口 ─────────────────────────────────────────────────
def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
