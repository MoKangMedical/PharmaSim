#!/bin/bash
# PharmaSim 视频制作系统启动脚本

echo "🚀 启动PharmaSim视频制作系统"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
python3 -c "import edge_tts, yaml" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ 正在安装依赖..."
    pip3 install edge-tts pyyaml
fi

# 检查ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ 未找到ffmpeg，请先安装ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Ubuntu: sudo apt install ffmpeg"
    exit 1
fi

# 检查manim
if ! python3 -c "import manim" 2>/dev/null; then
    echo "⚠️ 未找到manim，请安装manim:"
    echo "   pip3 install manim"
    echo "   或使用Python 3.12: /opt/homebrew/bin/python3.12 -m pip install manim"
fi

echo ""
echo "🎬 可用功能:"
echo "1. 语音生成 (voice_generator.py)"
echo "2. 音频处理 (audio_processor.py)"
echo "3. 视频制作 (video_production.py)"
echo "4. Web界面 (web_interface.html)"
echo ""

# 解析命令行参数
case "${1:-}" in
    "voice")
        echo "🎤 启动语音生成器..."
        python3 voice_generator.py "${@:2}"
        ;;
    "audio")
        echo "🎵 启动音频处理器..."
        python3 audio_processor.py "${@:2}"
        ;;
    "video")
        echo "🎬 启动视频制作..."
        python3 video_production.py "${@:2}"
        ;;
    "web")
        echo "🌐 启动Web界面..."
        if command -v open &> /dev/null; then
            open web_interface.html
        elif command -v xdg-open &> /dev/null; then
            xdg-open web_interface.html
        else:
            echo "请手动打开: web_interface.html"
        fi
        ;;
    "help"|"-h"|"--help")
        echo "📖 使用说明:"
        echo ""
        echo "语音生成:"
        echo "  ./run.sh voice --text \"Hello World\" --voice en-US-GuyNeural"
        echo "  ./run.sh voice --list-voices"
        echo ""
        echo "音频处理:"
        echo "  ./run.sh audio convert input.mp3 output.wav"
        echo "  ./run.sh audio volume input.mp3 output.mp3 1.5"
        echo "  ./run.sh audio mix input1.mp3 input2.mp3 output.mp3"
        echo ""
        echo "视频制作:"
        echo "  ./run.sh video --quality h"
        echo "  ./run.sh video --voice-only"
        echo "  ./run.sh video --music-only"
        echo ""
        echo "Web界面:"
        echo "  ./run.sh web"
        echo ""
        ;;
    *)
        echo "💡 使用 './run.sh help' 查看帮助"
        echo ""
        echo "快速开始:"
        echo "  ./run.sh voice --text \"PharmaSim AI-Powered Drug Launch Simulation\""
        echo "  ./run.sh web"
        echo ""
        ;;
esac