#!/usr/bin/env python3
"""
PharmaSim 视频制作系统演示
快速演示系统的核心功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from voice_generator import VoiceGenerator
from audio_processor import AudioProcessor

async def demo_voice_generation():
    """演示语音生成功能"""
    print("\n🎤 演示语音生成功能")
    print("=" * 50)
    
    generator = VoiceGenerator()
    
    # 演示文本
    demo_texts = [
        ("PharmaSim. AI-Powered Drug Launch Simulation.", "en-US-GuyNeural"),
        ("Ninety percent of drug launches underperform expectations.", "en-US-JennyNeural"),
        ("What if you could simulate the entire market first?", "en-GB-RyanNeural"),
    ]
    
    print("生成演示语音文件...")
    
    for i, (text, voice) in enumerate(demo_texts, 1):
        output_file = f"demo_voice_{i}.mp3"
        print(f"\n{i}. 生成语音: {voice}")
        print(f"   文本: {text}")
        
        try:
            await generator.generate_voice(text, voice, output_file)
            print(f"   ✅ 成功: {output_file}")
        except Exception as e:
            print(f"   ❌ 失败: {e}")
    
    print(f"\n✅ 语音生成演示完成")

def demo_audio_processing():
    """演示音频处理功能"""
    print("\n🎵 演示音频处理功能")
    print("=" * 50)
    
    processor = AudioProcessor()
    
    # 检查演示文件是否存在
    demo_files = ["demo_voice_1.mp3", "demo_voice_2.mp3", "demo_voice_3.mp3"]
    existing_files = [f for f in demo_files if Path(f).exists()]
    
    if not existing_files:
        print("⚠️ 没有找到演示语音文件，跳过音频处理演示")
        return
    
    print("处理演示音频文件...")
    
    # 1. 获取音频信息
    print("\n1. 获取音频信息")
    for file in existing_files[:1]:  # 只处理第一个文件
        try:
            duration = processor.get_duration(file)
            print(f"   文件: {file}")
            print(f"   时长: {duration:.2f}秒")
        except Exception as e:
            print(f"   ❌ 获取信息失败: {e}")
    
    # 2. 调整音量
    print("\n2. 调整音量")
    if existing_files:
        input_file = existing_files[0]
        output_file = "demo_volume_adjusted.mp3"
        try:
            processor.adjust_volume(input_file, output_file, 1.5)
            print(f"   ✅ 音量调整完成: {output_file}")
        except Exception as e:
            print(f"   ❌ 音量调整失败: {e}")
    
    # 3. 混合音频
    print("\n3. 混合多个音频")
    if len(existing_files) >= 2:
        output_file = "demo_mixed.mp3"
        try:
            processor.mix_audio_files(existing_files[:2], output_file, [1.0, 0.8])
            print(f"   ✅ 音频混合完成: {output_file}")
        except Exception as e:
            print(f"   ❌ 音频混合失败: {e}")
    
    # 4. 生成程序化音乐
    print("\n4. 生成程序化音乐")
    music_file = "demo_background_music.mp3"
    try:
        processor.generate_procedural_music(music_file, duration=15, volume=0.12)
        print(f"   ✅ 背景音乐生成完成: {music_file}")
    except Exception as e:
        print(f"   ❌ 背景音乐生成失败: {e}")
    
    print(f"\n✅ 音频处理演示完成")

def show_system_info():
    """显示系统信息"""
    print("\n📊 系统信息")
    print("=" * 50)
    
    # 检查依赖
    print("检查系统依赖...")
    
    dependencies = [
        ("Python3", "python3 --version"),
        ("FFmpeg", "ffmpeg -version | head -1"),
        ("Edge TTS", "pip3 show edge-tts | grep Version"),
        ("PyYAML", "pip3 show pyyaml | grep Version"),
    ]
    
    for name, command in dependencies:
        try:
            result = os.popen(command).read().strip()
            if result:
                print(f"   ✅ {name}: {result}")
            else:
                print(f"   ⚠️ {name}: 未安装")
        except:
            print(f"   ❌ {name}: 检查失败")
    
    # 显示可用语音
    print("\n可用语音列表:")
    generator = VoiceGenerator()
    generator.list_voices()

async def main():
    """主演示函数"""
    print("🎬 PharmaSim 视频制作系统演示")
    print("=" * 50)
    print("本演示将展示系统的核心功能:")
    print("1. 语音合成")
    print("2. 音频处理")
    print("3. 系统信息")
    
    # 切换到脚本目录
    os.chdir(Path(__file__).parent)
    
    try:
        # 显示系统信息
        show_system_info()
        
        # 演示语音生成
        await demo_voice_generation()
        
        # 演示音频处理
        demo_audio_processing()
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        print("\n生成的文件:")
        
        # 列出生成的文件
        demo_files = [
            "demo_voice_1.mp3",
            "demo_voice_2.mp3", 
            "demo_voice_3.mp3",
            "demo_volume_adjusted.mp3",
            "demo_mixed.mp3",
            "demo_background_music.mp3"
        ]
        
        for file in demo_files:
            if Path(file).exists():
                size = Path(file).stat().st_size
                print(f"   📁 {file} ({size:,} bytes)")
        
        print("\n💡 下一步:")
        print("   1. 查看Web界面: ./run.sh web")
        print("   2. 生成自定义语音: ./run.sh voice --text \"你的文本\"")
        print("   3. 制作完整视频: ./run.sh video --quality h")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())