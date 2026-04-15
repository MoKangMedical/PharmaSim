# 🎬 视频和语音制作系统 - 快速使用指南

## 🚀 5分钟快速开始

### 1. 进入系统目录
```bash
cd ~/Desktop/PharmaSim/video_system
```

### 2. 生成第一个语音
```bash
./run.sh voice --text "Hello, this is PharmaSim" --voice en-US-GuyNeural
```

### 3. 启动Web界面
```bash
./run.sh web
```

## 🎤 语音生成

### 基本用法
```bash
# 英语语音
python3 voice_generator.py --text "Your text here" --voice en-US-GuyNeural

# 中文语音
python3 voice_generator.py --text "你好世界" --voice zh-CN-YunxiNeural

# 列出所有可用语音
python3 voice_generator.py --list-voices
```

### 推荐语音
| 语音 | 风格 | 适用场景 |
|------|------|----------|
| en-US-GuyNeural | 深沉、权威 | 企业宣传 |
| en-US-JennyNeural | 清晰、专业 | 通用解说 |
| en-GB-RyanNeural | 纪录片风格 | 科学内容 |
| en-US-AriaNeural | 表达丰富 | 故事叙述 |

## 🎵 音频处理

### 常用操作
```bash
# 转换格式
python3 audio_processor.py convert input.mp3 output.wav

# 调整音量 (1.5倍)
python3 audio_processor.py volume input.mp3 output.mp3 1.5

# 混合音频
python3 audio_processor.py mix input1.mp3 input2.mp3 output.mp3

# 生成背景音乐
python3 audio_processor.py music background.mp3 --duration 60
```

## 🎬 视频制作

### 完整流程
```bash
# 高质量视频制作
python3 video_production.py --quality h

# 仅生成语音
python3 video_production.py --voice-only

# 仅生成音乐
python3 video_production.py --music-only
```

## ⚙️ 配置文件

### 主要配置 (config.yaml)
```yaml
# 语音配置
voices:
  primary:
    id: "en-US-GuyNeural"
    rate: "-5%"
    pitch: "-2Hz"

# 音乐配置
music:
  cinematic:
    frequencies: [130.81, 164.81, 196.00, 261.63]
    volume: 0.12

# 混合配置
mixing:
  voice_volume: 2.5
  music_volume: 0.15
```

## 🔧 故障排除

### 常见问题
1. **Edge TTS失败** - 检查网络，使用代理
2. **FFmpeg错误** - 检查文件路径和格式
3. **Manim渲染失败** - 使用Python 3.10+

### 获取帮助
```bash
# 查看帮助
./run.sh help

# 运行测试
python3 test_system.py

# 运行演示
python3 demo.py
```

## 📚 更多资源

- **详细文档**: README.md
- **项目总结**: PROJECT_SUMMARY.md
- **实现报告**: IMPLEMENTATION_COMPLETE.md
- **状态报告**: FINAL_STATUS_REPORT.md

## 🎯 使用技巧

1. **语音选择** - 根据内容风格选择合适的语音
2. **音量平衡** - 语音2.0-3.0，音乐0.1-0.2
3. **质量选择** - 预览用低质量，最终用高质量
4. **批量处理** - 使用批处理功能提高效率

---

**系统状态**: ✅ 完全可用  
**最后更新**: 2025年4月14日