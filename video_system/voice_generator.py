#!/usr/bin/env python3
"""
语音合成工具
基于Edge TTS的高质量语音生成
"""

import asyncio
import edge_tts
import argparse
import yaml
from pathlib import Path
from typing import Optional, Dict, List
import time

class VoiceGenerator:
    """语音生成器"""
    
    # 推荐的语音列表
    RECOMMENDED_VOICES = {
        "en-US-GuyNeural": "Deep, authoritative male - Corporate/tech promos",
        "en-US-JennyNeural": "Clear professional female - General narration",
        "en-US-AriaNeural": "Expressive female - Storytelling, emotional",
        "en-GB-RyanNeural": "British male - Documentary/science style",
        "en-US-AndrewMultilingualNeural": "Polished news-style male",
        "zh-CN-YunxiNeural": "Chinese male - 温暖、自然",
        "zh-CN-XiaoxiaoNeural": "Chinese female - 温柔、亲切",
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.voices_dir = Path("voices")
        self.voices_dir.mkdir(exist_ok=True)
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def generate_voice(self, text: str, voice_id: str = "en-US-GuyNeural", 
                           output_file: Optional[str] = None, rate: str = "-5%", 
                           pitch: str = "-2Hz", retry_attempts: int = 3) -> Path:
        """生成单个语音文件"""
        
        if output_file is None:
            output_file = f"voices/voice_{int(time.time())}.mp3"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🎤 生成语音: {voice_id}")
        print(f"📝 文本: {text[:50]}...")
        
        for attempt in range(retry_attempts):
            try:
                communicate = edge_tts.Communicate(text, voice_id, rate=rate, pitch=pitch)
                await communicate.save(str(output_path))
                print(f"✅ 语音生成成功: {output_path}")
                return output_path
                
            except Exception as e:
                print(f"⚠️ 尝试 {attempt + 1} 失败: {e}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(2)
                else:
                    print(f"❌ 语音生成最终失败")
                    raise
    
    async def generate_batch(self, texts: List[str], voice_id: str = "en-US-GuyNeural",
                           output_dir: str = "voices", delay: float = 1.0) -> List[Path]:
        """批量生成语音文件"""
        print(f"🎵 批量生成 {len(texts)} 个语音文件...")
        
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(exist_ok=True)
        
        generated_files = []
        
        for i, text in enumerate(texts):
            output_file = output_dir_path / f"voice_{i+1:02d}.mp3"
            
            try:
                await self.generate_voice(text, voice_id, str(output_file))
                generated_files.append(output_file)
            except Exception as e:
                print(f"❌ 生成失败 {i+1}: {e}")
            
            # 批处理延迟
            if i < len(texts) - 1:
                await asyncio.sleep(delay)
        
        print(f"✅ 批量生成完成: {len(generated_files)}/{len(texts)}")
        return generated_files
    
    async def generate_with_ssml(self, ssml_text: str, voice_id: str = "en-US-GuyNeural",
                                output_file: Optional[str] = None) -> Path:
        """使用SSML生成语音（更精细的控制）"""
        
        if output_file is None:
            output_file = f"voices/ssml_voice_{int(time.time())}.mp3"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🎭 使用SSML生成语音: {voice_id}")
        
        try:
            communicate = edge_tts.Communicate(ssml_text, voice_id)
            await communicate.save(str(output_path))
            print(f"✅ SSML语音生成成功: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ SSML语音生成失败: {e}")
            raise
    
    def list_voices(self):
        """列出推荐的语音"""
        print("\n🎤 推荐语音列表:")
        print("=" * 60)
        
        for voice_id, description in self.RECOMMENDED_VOICES.items():
            print(f"{voice_id:35} | {description}")
        
        print("\n💡 使用示例:")
        print('python voice_generator.py --text "Hello World" --voice en-US-GuyNeural')
        print('python voice_generator.py --ssml "<speak>Hello <break time=\"500ms\"/> World</speak>"')

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="语音合成工具")
    parser.add_argument("--text", type=str, help="要转换的文本")
    parser.add_argument("--ssml", type=str, help="SSML格式的文本")
    parser.add_argument("--voice", default="en-US-GuyNeural", help="语音ID")
    parser.add_argument("--output", "-o", help="输出文件路径")
    parser.add_argument("--rate", default="-5%", help="语速调整 (例如: -10%, +5%)")
    parser.add_argument("--pitch", default="-2Hz", help="音调调整 (例如: -5Hz, +3Hz)")
    parser.add_argument("--list-voices", action="store_true", help="列出推荐语音")
    parser.add_argument("--batch", nargs="+", help="批量生成语音")
    parser.add_argument("--config", help="配置文件路径")
    
    args = parser.parse_args()
    
    generator = VoiceGenerator(args.config)
    
    if args.list_voices:
        generator.list_voices()
        return
    
    if args.ssml:
        # SSML模式
        await generator.generate_with_ssml(args.ssml, args.voice, args.output)
    elif args.batch:
        # 批量模式
        await generator.generate_batch(args.batch, args.voice)
    elif args.text:
        # 单文本模式
        await generator.generate_voice(args.text, args.voice, args.output, args.rate, args.pitch)
    else:
        print("❌ 请提供要转换的文本 (--text) 或 SSML (--ssml)")
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())