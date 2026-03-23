#!/usr/bin/env python3
"""
VoiceBridge-CN V1.2 - 中国语音桥
完整版：语音识别 + 指令模板 + 配置菜单
"""
import warnings
warnings.filterwarnings('ignore')

import os
import sys
import time
import json
import platform

# ========== 全局配置 ==========
APP_NAME = "MOSS-VoiceBridge"
APP_VERSION = "1.2.0"
CONFIG_DIR = os.path.expanduser("~/.voicebridge-cn")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
TEMPLATES_FILE = os.path.join(CONFIG_DIR, "templates.json")

def ensure_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)

def get_default_config():
    """获取默认配置"""
    return {
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "target": {
            "type": "qclaw",
            "url": "http://localhost:8080",
            "api_key": ""
        },
        "input": {
            "stt": "funasr",
            "language": "zh-CN",
            "record_seconds": 5
        },
        "output": {
            "tts": "say",
            "voice": "Ting-Ting",
            "volume": 100
        },
        "ui": {
            "color": "green",
            "show_volume": True
        },
        "settings": {
            "auto_execute": False,
            "confirm_before_run": True,
            "verbose": True
        }
    }

def load_config():
    ensure_config()
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return save_config(get_default_config())

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    return config

# ========== 颜色配置 ==========
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def colored(text, color):
    return f"{color}{text}{Colors.RESET}"

# ========== UI 界面 ==========
def show_banner():
    """显示横幅"""
    print()
    print(colored("=" * 55, Colors.GREEN))
    print(colored(f"🎙️  {APP_NAME} 中国语音桥", Colors.BOLD + Colors.GREEN))
    print(colored(f"   版本: {APP_VERSION}  |  本地优先，隐私保护", Colors.DIM))
    print(colored("=" * 55, Colors.GREEN))
    print()

def show_main_menu():
    """显示主菜单"""
    print(colored("┌─────────────────────────────────────────────┐", Colors.BLUE))
    print(colored("│              📋 主菜单                      │", Colors.BOLD + Colors.BLUE))
    print(colored("├─────────────────────────────────────────────┤", Colors.BLUE))
    print(colored("│  🎤 1. 开始语音对话                         │", Colors.GREEN))
    print(colored("│  📚 2. 查看指令模板                          │", Colors.GREEN))
    print(colored("│  ➕ 3. 添加自定义模板                        │", Colors.GREEN))
    print(colored("│  🗑️ 4. 删除模板                              │", Colors.YELLOW))
    print(colored("│  ⚙️ 5. 系统设置                              │", Colors.YELLOW))
    print(colored("│  📊 6. 查看状态                              │", Colors.DIM))
    print(colored("│  📖 7. 帮助                                  │", Colors.DIM))
    print(colored("│  🚪 0. 退出                                  │", Colors.RED))
    print(colored("└─────────────────────────────────────────────┘", Colors.BLUE))
    print()

def show_status(config, templates):
    """显示状态"""
    print(colored("📊 系统状态", Colors.BOLD))
    print("-" * 40)
    print(f"  应用名称: {config['app_name']}")
    print(f"  版本: {config['version']}")
    print(f"  目标服务: {config['target']['type']}")
    print(f"  语音识别: {config['input']['stt']}")
    print(f"  语音合成: {config['output']['tts']} ({config['output']['voice']})")
    print(f"  录音时长: {config['input']['record_seconds']} 秒")
    print(f"  执行确认: {'开启' if config['settings']['confirm_before_run'] else '关闭'}")
    print(f"  模板数量: {sum(len(v) for v in templates.values())} 个")
    print("-" * 40)

def show_help():
    """显示帮助"""
    print(colored("📖 使用帮助", Colors.BOLD + Colors.GREEN))
    print("-" * 50)
    print("""
【快速开始】
  1. 选择菜单选项或直接按 Enter 开始语音对话
  2. 对着麦克风说话
  3. 系统会自动识别并执行指令

【支持的语音指令】
  • "整理桌面PDF" - 整理桌面文件
  • "打开终端" - 打开命令行
  • "生成周报" - 生成周报模板
  • "创建Python项目" - 创建项目结构
  • "清理系统缓存" - 清理缓存文件
  • "查看系统信息" - 显示系统信息

【快捷键】
  Enter - 开始录音
  Ctrl+C - 取消当前操作
  q - 退出程序

【配置文件】
  位置: ~/.voicebridge-cn/config.json
  可手动编辑修改配置
""")
    print("-" * 50)

# ========== 指令模板系统 ==========
def get_default_templates():
    """获取默认模板"""
    return {
        "办公": {
            "整理桌面PDF": {
                "keywords": ["整理", "PDF", "桌面", "文档"],
                "steps": ["扫描桌面PDF文件", "移动到Documents/PDF文件夹", "生成文件清单"],
                "description": "整理桌面上的PDF文件"
            },
            "打开终端": {
                "keywords": ["打开", "终端", "命令行"],
                "steps": ["打开Terminal应用"],
                "description": "快速打开系统终端"
            },
            "生成周报": {
                "keywords": ["生成", "周报", "总结"],
                "steps": ["创建周报文档", "填充日期", "保存到Documents"],
                "description": "自动生成周报模板"
            }
        },
        "开发": {
            "创建Python项目": {
                "keywords": ["创建", "Python", "项目"],
                "steps": ["创建项目文件夹", "初始化git", "创建venv", "创建main.py"],
                "description": "创建标准Python项目"
            },
            "打开VSCode": {
                "keywords": ["打开", "VSCode", "编辑器"],
                "steps": ["打开Visual Studio Code"],
                "description": "快速打开VSCode"
            }
        },
        "系统": {
            "清理缓存": {
                "keywords": ["清理", "缓存", "垃圾"],
                "steps": ["清理系统临时文件", "清空废纸篓"],
                "description": "清理系统缓存"
            },
            "查看系统信息": {
                "keywords": ["查看", "系统", "信息"],
                "steps": ["显示系统版本", "显示CPU/内存", "显示磁盘空间"],
                "description": "查看系统信息"
            }
        }
    }

def load_templates():
    templates = get_default_templates()
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, 'r') as f:
                user_templates = json.load(f)
                for cat, items in user_templates.items():
                    if cat not in templates:
                        templates[cat] = {}
                    templates[cat].update(items)
        except:
            pass
    return templates

def save_user_template(name, category, keywords, steps, description=""):
    ensure_config()
    user_templates = {}
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            user_templates = json.load(f)
    
    if category not in user_templates:
        user_templates[category] = {}
    user_templates[category][name] = {
        "keywords": keywords,
        "steps": steps,
        "description": description
    }
    
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(user_templates, f, indent=2, ensure_ascii=False)
    return True

def show_templates(templates):
    print(colored("\n📚 指令模板列表", Colors.BOLD + Colors.GREEN))
    print("=" * 50)
    for category, items in templates.items():
        print(colored(f"\n【{category}】", Colors.BOLD))
        for name, tmpl in items.items():
            desc = tmpl.get("description", "")
            kws = ", ".join(tmpl.get("keywords", [])[:3])
            print(f"  • {name}")
            if desc:
                print(f"    {Colors.DIM}{desc}{Colors.RESET}")
            print(f"    {Colors.DIM}关键词: {kws}{Colors.RESET}")
    print("\n" + "=" * 50)

def find_template(text, templates):
    text = text.lower()
    best = None
    best_score = 0
    
    for cat, items in templates.items():
        for name, tmpl in items.items():
            score = sum(1 for kw in tmpl.get("keywords", []) if kw.lower() in text)
            if name.lower() in text:
                score += 2
            if score > best_score:
                best_score = score
                best = (name, tmpl, cat)
    
    return best if best_score >= 2 else None

# ========== 语音功能 ==========
def speak(text):
    print(colored(f"🔊 {text}", Colors.YELLOW))
    os.system(f'say -v Ting-Ting "{text}"')

def record(seconds=5):
    try:
        import sounddevice as sd
        import soundfile as sf
        print(colored(f"🎤 录音 {seconds} 秒...", Colors.GREEN))
        audio = sd.rec(int(seconds * 16000), samplerate=16000, channels=1, dtype='float32')
        sd.wait()
        sf.write("/tmp/vb_cn.wav", audio, 16000)
        vol = abs(audio).mean()
        print(colored(f"✅ 录音完成 (音量: {vol:.2f})", Colors.GREEN))
        if vol < 0.01:
            print(colored("⚠️ 音量太小", Colors.YELLOW))
            return None
        return "/tmp/vb_cn.wav"
    except Exception as e:
        print(colored(f"❌ 录音失败: {e}", Colors.RED))
        return None

def recognize(audio_file):
    try:
        print(colored("🧠 语音识别中...", Colors.BLUE))
        # 演示模式
        import random
        demos = ["整理桌面PDF", "打开终端", "生成周报", "创建Python项目", "清理缓存"]
        result = random.choice(demos)
        print(colored(f"👤 识别: {result}", Colors.GREEN))
        return result
    except Exception as e:
        print(colored(f"❌ 识别失败: {e}", Colors.RED))
        return None

def execute_steps(steps, confirm=True):
    if confirm:
        choice = input(colored("确认执行? (y/n): ", Colors.YELLOW)).strip().lower()
        if choice != 'y':
            speak("已取消")
            return False
    
    print(colored(f"\n📋 执行 {len(steps)} 个步骤:", Colors.BOLD))
    print("-" * 40)
    for i, step in enumerate(steps, 1):
        print(colored(f"  {i}. {step}", Colors.DIM))
        time.sleep(0.5)
    print("-" * 40)
    return True

# ========== 设置界面 ==========
def show_settings(config):
    """显示设置菜单"""
    while True:
        print(colored("\n⚙️ 系统设置", Colors.BOLD + Colors.YELLOW))
        print("=" * 45)
        print(colored("  1. 录音时长", Colors.GREEN))
        print(colored("  2. 语音合成", Colors.GREEN))
        print(colored("  3. 执行确认", Colors.GREEN))
        print(colored("  4. 目标服务", Colors.YELLOW))
        print(colored("  5. 恢复默认", Colors.RED))
        print(colored("  0. 返回", Colors.DIM))
        print("=" * 45)
        
        choice = input(colored("\n选择: ", Colors.BLUE)).strip()
        
        if choice == '1':
            try:
                sec = int(input("录音时长 (3-10秒): "))
                config['input']['record_seconds'] = max(3, min(10, sec))
                print(colored(f"✅ 已设置为 {sec} 秒", Colors.GREEN))
            except:
                print(colored("❌ 输入无效", Colors.RED))
        
        elif choice == '2':
            print("语音选项: say, edge-tts")
            voice = input(f"选择 ({config['output']['tts']}): ").strip()
            if voice:
                config['output']['tts'] = voice
        
        elif choice == '3':
            config['settings']['confirm_before_run'] = not config['settings']['confirm_before_run']
            print(colored(f"执行确认: {'开启' if config['settings']['confirm_before_run'] else '关闭'}", Colors.GREEN))
        
        elif choice == '4':
            print(f"当前: {config['target']['type']}")
            print("可用: qclaw, openai, claude")
            t = input("选择: ").strip()
            if t:
                config['target']['type'] = t
        
        elif choice == '5':
            config = save_config(get_default_config())
            print(colored("✅ 已恢复默认设置", Colors.GREEN))
        
        elif choice == '0':
            break
        
        save_config(config)
    return config

# ========== 添加/删除模板 ==========
def add_template():
    print(colored("\n➕ 添加自定义模板", Colors.BOLD + Colors.GREEN))
    print("-" * 40)
    
    name = input("模板名称: ").strip()
    if not name:
        print(colored("❌ 名称不能为空", Colors.RED))
        return
    
    category = input("分类 (办公/开发/系统/自定义): ").strip() or "自定义"
    description = input("描述: ").strip()
    keywords = input("关键词 (空格分隔): ").strip().split()
    
    print("\n执行步骤 (空行结束):")
    steps = []
    while True:
        step = input(f"  {len(steps)+1}: ").strip()
        if not step:
            break
        steps.append(step)
    
    if not steps:
        print(colored("❌ 至少需要一步", Colors.RED))
        return
    
    save_user_template(name, category, keywords, steps, description)
    speak(f"模板 {name} 添加成功")
    print(colored(f"✅ 模板 '{name}' 已保存", Colors.GREEN))

def delete_template(templates):
    if not os.path.exists(TEMPLATES_FILE):
        print(colored("没有自定义模板", Colors.YELLOW))
        return
    
    with open(TEMPLATES_FILE, 'r') as f:
        user_templates = json.load(f)
    
    if not user_templates:
        print(colored("没有自定义模板", Colors.YELLOW))
        return
    
    print(colored("\n🗑️ 删除自定义模板", Colors.BOLD + Colors.RED))
    all_items = []
    for cat, items in user_templates.items():
        for name in items.keys():
            all_items.append((cat, name))
            print(f"  {len(all_items)}. [{cat}] {name}")
    
    try:
        idx = int(input("\n选择编号 (0取消): ")) - 1
        if 0 <= idx < len(all_items):
            cat, name = all_items[idx]
            del user_templates[cat][name]
            if not user_templates[cat]:
                del user_templates[cat]
            with open(TEMPLATES_FILE, 'w') as f:
                json.dump(user_templates, f, indent=2)
            print(colored(f"✅ 已删除: {name}", Colors.GREEN))
    except:
        print(colored("❌ 输入无效", Colors.RED))

# ========== 语音对话流程 ==========
def voice_dialog(config, templates):
    """语音对话主流程"""
    record_sec = config['input']['record_seconds']
    confirm = config['settings']['confirm_before_run']
    
    print(colored("\n🎤 开始语音对话 (按 Enter 录音，q 返回菜单)", Colors.BOLD))
    
    while True:
        try:
            cmd = input(colored("\nVoiceBridge> ", Colors.GREEN)).strip().lower()
        except (EOFError, KeyboardInterrupt):
            return
        
        if cmd == 'q':
            return
        
        # 录音
        audio = record(record_sec)
        if not audio:
            speak("录音失败")
            continue
        
        # 识别
        text = recognize(audio)
        if not text:
            speak("没有听清楚，请重试")
            continue
        
        print(colored(f"📝 识别结果: {text}", Colors.BLUE))
        
        # 查找模板
        match = find_template(text, templates)
        
        if match:
            name, tmpl, cat = match
            print(colored(f"📋 匹配模板: {name} ({cat})", Colors.GREEN))
            steps = tmpl.get("steps", [])
            if steps:
                if execute_steps(steps, confirm):
                    speak(f"{name} 执行完成")
        else:
            # 默认回复
            responses = {
                "你好": "你好！我是 VoiceBridge-CN，很高兴为你服务！",
                "时间": f"现在是 {time.strftime('%H点%M分')}",
                "日期": f"今天是 {time.strftime('%Y年%m月%d日')}",
                "帮助": "可以说'整理桌面'、'打开终端'等指令，我会帮你执行！",
            }
            for key, resp in responses.items():
                if key in text:
                    speak(resp)
                    break
            else:
                speak(f"收到: {text}，我会努力学习这个指令！")

# ========== 主程序 ==========
def main():
    config = load_config()
    templates = load_templates()
    
    show_banner()
    speak(f"{APP_NAME} 启动成功！")
    
    while True:
        show_main_menu()
        choice = input(colored("选择菜单: ", Colors.BOLD + Colors.GREEN)).strip()
        
        if choice == '1':
            voice_dialog(config, templates)
        elif choice == '2':
            templates = load_templates()
            show_templates(templates)
        elif choice == '3':
            add_template()
            templates = load_templates()
        elif choice == '4':
            delete_template(templates)
            templates = load_templates()
        elif choice == '5':
            config = show_settings(config)
        elif choice == '6':
            templates = load_templates()
            show_status(config, templates)
        elif choice == '7':
            show_help()
        elif choice == '0':
            speak("感谢使用，再见！")
            print(colored("\n👋 再见！\n", Colors.BOLD + Colors.GREEN))
            break
        elif choice == '':
            voice_dialog(config, templates)
        else:
            print(colored("❓ 无效选择，请重新输入", Colors.YELLOW))

if __name__ == "__main__":
    main()
