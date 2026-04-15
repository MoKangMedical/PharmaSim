#!/usr/bin/env python3
"""
PharmaSim Video Production System
视频和语音能力系统 - 主控制脚本
"""

import asyncio
import subprocess
import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
import edge_tts
import time

class VideoProductionSystem:
    """视频制作系统主类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.base_dir = Path(__file__).parent
        self.output_dir = self.base_dir / "output"
        self.voices_dir = self.base_dir / "voices"
        self.music_dir = self.base_dir / "music"
        
        # 创建必要目录
        self.output_dir.mkdir(exist_ok=True)
        self.voices_dir.mkdir(exist_ok=True)
        self.music_dir.mkdir(exist_ok=True)
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def generate_voiceover(self, scene_name: str, text: str, voice_id: str = None) -> Path:
        """为单个场景生成语音"""
        if voice_id is None:
            voice_id = self.config['voices']['primary']['id']
        
        voice_config = self.config['voices']['primary']
        output_file = self.voices_dir / f"{scene_name}_{voice_id}.mp3"
        
        print(f"🎤 生成语音: {scene_name} ({voice_id})")
        
        for attempt in range(self.config['tts']['retry_attempts']):
            try:
                communicate = edge_tts.Communicate(
                    text, 
                    voice_id,
                    rate=voice_config['rate'],
                    pitch=voice_config['pitch']
                )
                await communicate.save(str(output_file))
                print(f"✅ 语音生成成功: {output_file}")
                return output_file
                
            except Exception as e:
                print(f"⚠️ 尝试 {attempt + 1} 失败: {e}")
                if attempt < self.config['tts']['retry_attempts'] - 1:
                    await asyncio.sleep(self.config['tts']['retry_delay'])
                else:
                    print(f"❌ 语音生成最终失败: {scene_name}")
                    raise
    
    async def generate_all_voiceovers(self) -> Dict[str, Path]:
        """为所有场景生成语音"""
        print("\n🎙️ 开始生成所有场景语音...")
        
        voice_files = {}
        narration = self.config['narration']
        
        for scene_key, text in narration.items():
            scene_name = scene_key.replace('scene', 'Scene')
            voice_file = await self.generate_voiceover(scene_name, text)
            voice_files[scene_name] = voice_file
            
            # 批处理延迟
            await asyncio.sleep(self.config['tts']['batch_delay'])
        
        print(f"✅ 所有语音生成完成: {len(voice_files)} 个文件")
        return voice_files
    
    def generate_background_music(self) -> Path:
        """生成背景音乐"""
        print("\n🎵 生成背景音乐...")
        
        music_config = self.config['music']['cinematic']
        output_file = self.music_dir / "background_music.mp3"
        
        if not music_config['enabled']:
            print("⚠️ 背景音乐已禁用")
            return None
        
        # 构建ffmpeg命令
        frequencies = music_config['frequencies']
        duration = music_config['duration']
        
        # 创建正弦波输入
        inputs = []
        for i, freq in enumerate(frequencies):
            inputs.append(f'-f lavfi -i "sine=frequency={freq}:duration={duration}"')
        
        # 混合滤镜
        filter_complex = f"[0][1][2][3]amix=inputs=4:duration=shortest,"
        filter_complex += f"lowpass=f=600,highpass=f=80,"
        filter_complex += f"volume={music_config['volume']},"
        filter_complex += f"afade=t=in:d={music_config['fade_in']},afade=t=out:st={duration - music_config['fade_out']}:d={music_config['fade_out']},"
        filter_complex += f"tremolo=f=0.5:d=0.2,"
        filter_complex += f"aecho=0.8:0.7:{music_config['echo']}[a]"
        
        cmd = f'ffmpeg -y {" ".join(inputs)} '
        cmd += f'-filter_complex "{filter_complex}" '
        cmd += f'-map "[a]" -codec:a libmp3lame -qscale:a 2 "{output_file}"'
        
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print(f"✅ 背景音乐生成成功: {output_file}")
            return output_file
        except subprocess.CalledProcessError as e:
            print(f"❌ 背景音乐生成失败: {e}")
            return None
    
    def render_manim_scenes(self, quality: str = "l") -> List[Path]:
        """渲染Manim场景"""
        print(f"\n🎬 渲染Manim场景 (质量: {quality})...")
        
        script_path = self.base_dir.parent / "video" / "script.py"
        scenes = [scene['name'] for scene in self.config['scenes']]
        
        rendered_files = []
        
        for scene in scenes:
            print(f"🎥 渲染: {scene}")
            
            # 使用Python 3.12运行manim
            cmd = f'/opt/homebrew/bin/python3.12 -m manim -q{quality} "{script_path}" {scene}'
            
            try:
                subprocess.run(cmd, shell=True, check=True, capture_output=True)
                # manim默认输出到media/videos/script/目录
                video_dir = self.base_dir.parent / "video" / "media" / "videos" / "script" / f"480p15"
                if quality == "h":
                    video_dir = self.base_dir.parent / "video" / "media" / "videos" / "script" / "1080p60"
                
                video_file = video_dir / f"{scene}.mp4"
                if video_file.exists():
                    rendered_files.append(video_file)
                    print(f"✅ 场景渲染完成: {scene}")
                else:
                    print(f"⚠️ 未找到渲染文件: {video_file}")
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ 场景渲染失败 {scene}: {e}")
        
        print(f"✅ 场景渲染完成: {len(rendered_files)}/{len(scenes)}")
        return rendered_files
    
    def mix_audio_video(self, video_files: List[Path], voice_files: Dict[str, Path], music_file: Optional[Path]) -> Path:
        """混合音频和视频"""
        print("\n🎧 混合音频和视频...")
        
        # 1. 为每个场景添加语音
        scenes_with_audio = []
        for video_file in video_files:
            scene_name = video_file.stem
            if scene_name in voice_files:
                voice_file = voice_files[scene_name]
                output_file = self.output_dir / f"{scene_name}_with_voice.mp4"
                
                # 获取视频时长
                duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_file}"'
                duration = float(subprocess.run(duration_cmd, shell=True, capture_output=True, text=True).stdout.strip())
                
                # 添加语音到视频
                mix_cmd = f'''ffmpeg -y -i "{video_file}" -i "{voice_file}" \
                    -filter_complex "[1:a]atrim=0:{duration},asetpts=PTS-STARTPTS,volume={self.config['mixing']['voice_volume']}[a]" \
                    -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 \
                    -shortest "{output_file}" 2>/dev/null'''
                
                try:
                    subprocess.run(mix_cmd, shell=True, check=True)
                    scenes_with_audio.append(output_file)
                    print(f"✅ 语音添加完成: {scene_name}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ 语音添加失败 {scene_name}: {e}")
                    scenes_with_audio.append(video_file)  # 使用原始视频
            else:
                scenes_with_audio.append(video_file)
        
        # 2. 合并所有场景
        concat_file = self.output_dir / "concat.txt"
        with open(concat_file, 'w') as f:
            for scene_file in scenes_with_audio:
                f.write(f"file '{scene_file}'\n")
        
        merged_video = self.output_dir / "merged_no_music.mp4"
        concat_cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{merged_video}"'
        
        try:
            subprocess.run(concat_cmd, shell=True, check=True)
            print("✅ 场景合并完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 场景合并失败: {e}")
            return None
        
        # 3. 添加背景音乐
        if music_file and music_file.exists():
            final_video = self.output_dir / self.config['output']['final']
            
            music_cmd = f'''ffmpeg -y -i "{merged_video}" -i "{music_file}" \
                -filter_complex "[0:a]volume={self.config['mixing']['voice_volume']}[voice];[1:a]volume={self.config['music']['cinematic']['volume']}[music];[voice][music]amix=inputs=2:duration=shortest:normalize=0[a]" \
                -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k "{final_video}"'''
            
            try:
                subprocess.run(music_cmd, shell=True, check=True)
                print(f"✅ 最终视频生成完成: {final_video}")
                return final_video
            except subprocess.CalledProcessError as e:
                print(f"❌ 背景音乐添加失败: {e}")
                return merged_video
        else:
            print("⚠️ 无背景音乐，使用合并视频")
            return merged_video
    
    async def run_production(self, quality: str = "l"):
        """运行完整制作流程"""
        print("🚀 开始PharmaSim视频制作流程")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # 1. 生成语音
            voice_files = await self.generate_all_voiceovers()
            
            # 2. 生成背景音乐
            music_file = self.generate_background_music()
            
            # 3. 渲染Manim场景
            video_files = self.render_manim_scenes(quality)
            
            if not video_files:
                print("❌ 没有成功渲染的场景")
                return None
            
            # 4. 混合音频和视频
            final_video = self.mix_audio_video(video_files, voice_files, music_file)
            
            elapsed = time.time() - start_time
            print("\n" + "=" * 50)
            print(f"🎉 视频制作完成!")
            print(f"📁 输出文件: {final_video}")
            print(f"⏱️ 总耗时: {elapsed:.1f}秒")
            
            return final_video
            
        except Exception as e:
            print(f"❌ 制作流程失败: {e}")
            raise

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PharmaSim视频制作系统")
    parser.add_argument("--config", default="config.yaml", help="配置文件路径")
    parser.add_argument("--quality", choices=["l", "m", "h", "p", "k"], default="l", 
                       help="渲染质量 (l=低, m=中, h=高, p=1080p, k=4K)")
    parser.add_argument("--voice-only", action="store_true", help="仅生成语音")
    parser.add_argument("--music-only", action="store_true", help="仅生成音乐")
    parser.add_argument("--render-only", action="store_true", help="仅渲染场景")
    
    args = parser.parse_args()
    
    # 切换到脚本目录
    os.chdir(Path(__file__).parent)
    
    system = VideoProductionSystem(args.config)
    
    if args.voice_only:
        await system.generate_all_voiceovers()
    elif args.music_only:
        system.generate_background_music()
    elif args.render_only:
        system.render_manim_scenes(args.quality)
    else:
        await system.run_production(args.quality)

if __name__ == "__main__":
    asyncio.run(main())