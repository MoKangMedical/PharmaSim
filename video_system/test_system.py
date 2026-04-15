#!/usr/bin/env python3
"""
系统完整性测试
验证所有组件是否正常工作
"""

import sys
import os
from pathlib import Path

def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import yaml
        print("   ✅ PyYAML")
    except ImportError:
        print("   ❌ PyYAML 未安装")
        return False
    
    try:
        import edge_tts
        print("   ✅ Edge TTS")
    except ImportError:
        print("   ❌ Edge TTS 未安装")
        return False
    
    # 测试ffmpeg
    try:
        import subprocess
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ FFmpeg")
        else:
            print("   ❌ FFmpeg 未正确安装")
            return False
    except FileNotFoundError:
        print("   ❌ FFmpeg 未安装")
        return False
    
    return True

def test_files():
    """测试必要文件是否存在"""
    print("\n📁 测试文件完整性...")
    
    required_files = [
        "config.yaml",
        "voice_generator.py",
        "audio_processor.py",
        "video_production.py",
        "web_interface.html",
        "run.sh",
        "README.md"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} 不存在")
            all_exist = False
    
    return all_exist

def test_voice_generator():
    """测试语音生成器"""
    print("\n🎤 测试语音生成器...")
    
    try:
        from voice_generator import VoiceGenerator
        generator = VoiceGenerator()
        
        # 测试语音列表
        voices = generator.RECOMMENDED_VOICES
        if len(voices) > 0:
            print(f"   ✅ 语音列表: {len(voices)} 种语音")
        else:
            print("   ❌ 语音列表为空")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ 语音生成器测试失败: {e}")
        return False

def test_audio_processor():
    """测试音频处理器"""
    print("\n🎵 测试音频处理器...")
    
    try:
        from audio_processor import AudioProcessor
        processor = AudioProcessor()
        
        # 测试配置
        if processor.default_codec == "libmp3lame":
            print("   ✅ 默认编码器: libmp3lame")
        else:
            print(f"   ⚠️ 默认编码器: {processor.default_codec}")
        
        return True
    except Exception as e:
        print(f"   ❌ 音频处理器测试失败: {e}")
        return False

def test_config():
    """测试配置文件"""
    print("\n⚙️ 测试配置文件...")
    
    try:
        import yaml
        with open("config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查主要配置节
        required_sections = ['video', 'voices', 'narration', 'music', 'mixing']
        all_exist = True
        
        for section in required_sections:
            if section in config:
                print(f"   ✅ 配置节: {section}")
            else:
                print(f"   ❌ 缺少配置节: {section}")
                all_exist = False
        
        return all_exist
    except Exception as e:
        print(f"   ❌ 配置文件测试失败: {e}")
        return False

def test_web_interface():
    """测试Web界面"""
    print("\n🌐 测试Web界面...")
    
    try:
        with open("web_interface.html", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        checks = [
            ("PharmaSim 视频制作系统", "标题"),
            ("语音合成", "语音标签"),
            ("音乐生成", "音乐标签"),
            ("视频制作", "视频标签"),
            ("批量处理", "批量标签")
        ]
        
        all_found = True
        for text, desc in checks:
            if text in content:
                print(f"   ✅ {desc}: {text}")
            else:
                print(f"   ❌ 未找到: {desc}")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"   ❌ Web界面测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🧪 PharmaSim 视频制作系统 - 完整性测试")
    print("=" * 50)
    
    # 切换到脚本目录
    os.chdir(Path(__file__).parent)
    
    tests = [
        ("模块导入", test_imports),
        ("文件完整性", test_files),
        ("语音生成器", test_voice_generator),
        ("音频处理器", test_audio_processor),
        ("配置文件", test_config),
        ("Web界面", test_web_interface)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统完整可用。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关组件。")
        return 1

if __name__ == "__main__":
    exit(main())