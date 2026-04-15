#!/usr/bin/env python3
"""
音频处理工具
基于ffmpeg的音频处理工具集
"""

import subprocess
import argparse
from pathlib import Path
from typing import List, Optional, Dict
import json
import yaml

class AudioProcessor:
    """音频处理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path) if config_path else {}
        self.default_codec = "libmp3lame"
        self.default_bitrate = "192k"
    
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _run_ffmpeg(self, cmd: str, check: bool = True) -> subprocess.CompletedProcess:
        """运行ffmpeg命令"""
        try:
            return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg错误: {e}")
            print(f"命令: {cmd}")
            if e.stderr:
                print(f"错误信息: {e.stderr}")
            raise
    
    def get_audio_info(self, audio_file: str) -> Dict:
        """获取音频文件信息"""
        cmd = f'ffprobe -v quiet -print_format json -show_format -show_streams "{audio_file}"'
        result = self._run_ffmpeg(cmd)
        return json.loads(result.stdout)
    
    def get_duration(self, audio_file: str) -> float:
        """获取音频时长（秒）"""
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{audio_file}"'
        result = self._run_ffmpeg(cmd)
        return float(result.stdout.strip())
    
    def convert_format(self, input_file: str, output_file: str, 
                      codec: Optional[str] = None, bitrate: Optional[str] = None) -> Path:
        """转换音频格式"""
        if codec is None:
            codec = self.default_codec
        if bitrate is None:
            bitrate = self.default_bitrate
        
        cmd = f'ffmpeg -y -i "{input_file}" -codec:a {codec} -b:a {bitrate} "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 格式转换完成: {input_file} -> {output_file}")
        return Path(output_file)
    
    def adjust_volume(self, input_file: str, output_file: str, volume_factor: float = 1.5) -> Path:
        """调整音量"""
        cmd = f'ffmpeg -y -i "{input_file}" -af "volume={volume_factor}" -c:a {self.default_codec} -b:a {self.default_bitrate} "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 音量调整完成: {volume_factor}x")
        return Path(output_file)
    
    def trim_audio(self, input_file: str, output_file: str, 
                  start: float = 0, duration: Optional[float] = None) -> Path:
        """裁剪音频"""
        if duration:
            cmd = f'ffmpeg -y -i "{input_file}" -ss {start} -t {duration} -c:a copy "{output_file}"'
        else:
            cmd = f'ffmpeg -y -i "{input_file}" -ss {start} -c:a copy "{output_file}"'
        
        self._run_ffmpeg(cmd)
        print(f"✅ 音频裁剪完成: {start}s" + (f" - {start + duration}s" if duration else " - 结尾"))
        return Path(output_file)
    
    def pad_audio(self, input_file: str, output_file: str, target_duration: float) -> Path:
        """填充音频到指定时长"""
        cmd = f'ffmpeg -y -i "{input_file}" -af "apad=whole_dur={target_duration}" -c:a copy "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 音频填充完成: {target_duration}s")
        return Path(output_file)
    
    def mix_audio_files(self, input_files: List[str], output_file: str, 
                       volumes: Optional[List[float]] = None, normalize: bool = True) -> Path:
        """混合多个音频文件"""
        if volumes is None:
            volumes = [1.0] * len(input_files)
        
        # 构建输入参数
        inputs = " ".join([f'-i "{f}"' for f in input_files])
        
        # 构建滤镜
        filter_parts = []
        for i, vol in enumerate(volumes):
            filter_parts.append(f"[{i}:a]volume={vol}[a{i}]")
        
        mix_inputs = "".join([f"[a{i}]" for i in range(len(input_files))])
        filter_parts.append(f"{mix_inputs}amix=inputs={len(input_files)}:duration=longest:normalize={1 if normalize else 0}[a]")
        
        filter_complex = ";".join(filter_parts)
        
        cmd = f'ffmpeg -y {inputs} -filter_complex "{filter_complex}" -map "[a]" -c:a {self.default_codec} -b:a {self.default_bitrate} "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 音频混合完成: {len(input_files)} 个文件")
        return Path(output_file)
    
    def concatenate_audio(self, input_files: List[str], output_file: str) -> Path:
        """连接多个音频文件"""
        # 创建临时文件列表
        list_file = Path("temp_concat.txt")
        with open(list_file, 'w') as f:
            for audio_file in input_files:
                f.write(f"file '{audio_file}'\n")
        
        cmd = f'ffmpeg -y -f concat -safe 0 -i "{list_file}" -c:a copy "{output_file}"'
        self._run_ffmpeg(cmd)
        
        # 清理临时文件
        list_file.unlink()
        
        print(f"✅ 音频连接完成: {len(input_files)} 个文件")
        return Path(output_file)
    
    def generate_silence(self, output_file: str, duration: float) -> Path:
        """生成静音文件"""
        cmd = f'ffmpeg -y -f lavfi -i anullsrc=r=44100:cl=stereo -t {duration} -c:a {self.default_codec} -b:a {self.default_bitrate} "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 静音生成完成: {duration}s")
        return Path(output_file)
    
    def add_fade_effects(self, input_file: str, output_file: str, 
                        fade_in: float = 0, fade_out: float = 0) -> Path:
        """添加淡入淡出效果"""
        filters = []
        if fade_in > 0:
            filters.append(f"afade=t=in:d={fade_in}")
        if fade_out > 0:
            duration = self.get_duration(input_file)
            filters.append(f"afade=t=out:st={duration - fade_out}:d={fade_out}")
        
        filter_str = ",".join(filters) if filters else "anull"
        
        cmd = f'ffmpeg -y -i "{input_file}" -af "{filter_str}" -c:a copy "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 淡入淡出效果添加完成")
        return Path(output_file)
    
    def generate_procedural_music(self, output_file: str, duration: float = 60,
                                 frequencies: List[float] = [130.81, 164.81, 196.00],
                                 volume: float = 0.15) -> Path:
        """生成程序化背景音乐"""
        # 构建输入
        inputs = []
        for i, freq in enumerate(frequencies):
            inputs.append(f'-f lavfi -i "sine=frequency={freq}:duration={duration}"')
        
        # 混合滤镜
        mix_inputs = "".join([f"[{i}:a]" for i in range(len(frequencies))])
        filter_complex = f"{mix_inputs}amix=inputs={len(frequencies)}:duration=shortest,"
        filter_complex += f"lowpass=f=800,volume={volume},"
        filter_complex += f"afade=t=in:d=2,afade=t=out:st={duration - 3}:d=3[a]"
        
        cmd = f'ffmpeg -y {" ".join(inputs)} -filter_complex "{filter_complex}" -map "[a]" -c:a {self.default_codec} -b:a {self.default_bitrate} "{output_file}"'
        self._run_ffmpeg(cmd)
        
        print(f"✅ 程序化音乐生成完成: {duration}s")
        return Path(output_file)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="音频处理工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 信息命令
    info_parser = subparsers.add_parser("info", help="获取音频文件信息")
    info_parser.add_argument("input", help="输入音频文件")
    
    # 转换命令
    convert_parser = subparsers.add_parser("convert", help="转换音频格式")
    convert_parser.add_argument("input", help="输入文件")
    convert_parser.add_argument("output", help="输出文件")
    convert_parser.add_argument("--codec", default="libmp3lame", help="音频编码器")
    convert_parser.add_argument("--bitrate", default="192k", help="音频比特率")
    
    # 音量调整命令
    volume_parser = subparsers.add_parser("volume", help="调整音量")
    volume_parser.add_argument("input", help="输入文件")
    volume_parser.add_argument("output", help="输出文件")
    volume_parser.add_argument("factor", type=float, help="音量因子 (例如: 1.5)")
    
    # 裁剪命令
    trim_parser = subparsers.add_parser("trim", help="裁剪音频")
    trim_parser.add_argument("input", help="输入文件")
    trim_parser.add_argument("output", help="输出文件")
    trim_parser.add_argument("--start", type=float, default=0, help="开始时间(秒)")
    trim_parser.add_argument("--duration", type=float, help="持续时间(秒)")
    
    # 混合命令
    mix_parser = subparsers.add_parser("mix", help="混合多个音频")
    mix_parser.add_argument("input", nargs="+", help="输入文件列表")
    mix_parser.add_argument("output", help="输出文件")
    mix_parser.add_argument("--volumes", nargs="+", type=float, help="音量列表")
    mix_parser.add_argument("--no-normalize", action="store_true", help="禁用标准化")
    
    # 连接命令
    concat_parser = subparsers.add_parser("concat", help="连接多个音频")
    concat_parser.add_argument("input", nargs="+", help="输入文件列表")
    concat_parser.add_argument("output", help="输出文件")
    
    # 静音命令
    silence_parser = subparsers.add_parser("silence", help="生成静音")
    silence_parser.add_argument("output", help="输出文件")
    silence_parser.add_argument("duration", type=float, help="持续时间(秒)")
    
    # 淡入淡出命令
    fade_parser = subparsers.add_parser("fade", help="添加淡入淡出效果")
    fade_parser.add_argument("input", help="输入文件")
    fade_parser.add_argument("output", help="输出文件")
    fade_parser.add_argument("--fade-in", type=float, default=0, help="淡入时间(秒)")
    fade_parser.add_argument("--fade-out", type=float, default=0, help="淡出时间(秒)")
    
    # 音乐生成命令
    music_parser = subparsers.add_parser("music", help="生成程序化音乐")
    music_parser.add_argument("output", help="输出文件")
    music_parser.add_argument("--duration", type=float, default=60, help="持续时间(秒)")
    music_parser.add_argument("--frequencies", nargs="+", type=float, default=[130.81, 164.81, 196.00], help="频率列表")
    music_parser.add_argument("--volume", type=float, default=0.15, help="音量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    processor = AudioProcessor()
    
    try:
        if args.command == "info":
            info = processor.get_audio_info(args.input)
            duration = processor.get_duration(args.input)
            print(f"📁 文件: {args.input}")
            print(f"⏱️ 时长: {duration:.2f}秒")
            print(f"📊 格式信息: {json.dumps(info, indent=2)}")
            
        elif args.command == "convert":
            processor.convert_format(args.input, args.output, args.codec, args.bitrate)
            
        elif args.command == "volume":
            processor.adjust_volume(args.input, args.output, args.factor)
            
        elif args.command == "trim":
            processor.trim_audio(args.input, args.output, args.start, args.duration)
            
        elif args.command == "mix":
            volumes = args.volumes if args.volumes else None
            processor.mix_audio_files(args.input, args.output, volumes, not args.no_normalize)
            
        elif args.command == "concat":
            processor.concatenate_audio(args.input, args.output)
            
        elif args.command == "silence":
            processor.generate_silence(args.output, args.duration)
            
        elif args.command == "fade":
            processor.add_fade_effects(args.input, args.output, args.fade_in, args.fade_out)
            
        elif args.command == "music":
            processor.generate_procedural_music(args.output, args.duration, args.frequencies, args.volume)
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())