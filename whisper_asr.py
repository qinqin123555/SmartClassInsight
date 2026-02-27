import os
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception:
    WHISPER_AVAILABLE = False
try:
    from opencc import OpenCC
    OPENCC_AVAILABLE = True
    _cc = OpenCC('t2s')
except Exception:
    OPENCC_AVAILABLE = False
try:
    import imageio_ffmpeg
    IMAGEIO_FFMPEG_AVAILABLE = True
except Exception:
    IMAGEIO_FFMPEG_AVAILABLE = False

class ASRResult:
    def __init__(self, text, start_time, end_time, confidence=0.0):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.confidence = confidence
    def __str__(self):
        return f"[{self.start_time:.2f}s-{self.end_time:.2f}s] {self.text}"

class WhisperModule(QObject):
    result_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str)
    def __init__(self, model_size="base", language="zh"):
        super().__init__()
        self.language = language
        self.results = []
        self.model = None
        if not WHISPER_AVAILABLE:
            self.status_changed.emit("错误: 缺少whisper库")
    def load(self, model_size="base"):
        if WHISPER_AVAILABLE and self.model is None:
            try:
                self.model = whisper.load_model(model_size)
            except Exception as e:
                self.status_changed.emit(f"加载模型失败: {e}")
    def transcribe_audio(self, audio_path):
        self.results = []
        if not WHISPER_AVAILABLE:
            return []
        if self.model is None:
            self.load()
        try:
            r = self.model.transcribe(audio_path, language=self.language, verbose=False, word_timestamps=False)
            text = r.get("text", "")
            if OPENCC_AVAILABLE:
                text = _cc.convert(text)
            segs = r.get("segments", []) or []
            if segs:
                for s in segs:
                    st = float(s.get("start", 0.0))
                    et = float(s.get("end", st))
                    t = s.get("text", "")
                    if OPENCC_AVAILABLE:
                        t = _cc.convert(t)
                    res = ASRResult(t, st, et)
                    self.results.append(res)
                    self.result_ready.emit(res)
            elif text:
                res = ASRResult(text, 0.0, 0.0)
                self.results.append(res)
                self.result_ready.emit(res)
            self.status_changed.emit(f"识别完成: {len(self.results)}")
            return self.results
        except Exception as e:
            self.status_changed.emit(f"识别失败: {e}")
            return []
    def transcribe_video(self, video_path):
        self.results = []
        self.status_changed.emit(f"处理视频: {video_path}")
        temp_audio_path = "temp_whisper_audio.wav"
        try:
            if IMAGEIO_FFMPEG_AVAILABLE:
                exe = imageio_ffmpeg.get_ffmpeg_exe()
                import subprocess
                cmd = [exe, "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", temp_audio_path]
                r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if r.returncode != 0 or not os.path.exists(temp_audio_path):
                    self.status_changed.emit("错误: 无法从视频提取音频")
                    return []
            else:
                self.status_changed.emit("错误: 缺少FFmpeg支持")
                return []
            res = self.transcribe_audio(temp_audio_path)
            if os.path.exists(temp_audio_path):
                try:
                    os.remove(temp_audio_path)
                except Exception:
                    pass
            return res
        except Exception as e:
            self.status_changed.emit(f"处理视频失败: {e}")
            return []
    def export_results(self, output_path):
        try:
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(["开始时间(秒)", "结束时间(秒)", "识别文本"])
                for r in self.results:
                    w.writerow([f"{r.start_time:.2f}", f"{r.end_time:.2f}", r.text])
            self.status_changed.emit(f"结果已导出: {output_path}")
            return True
        except Exception as e:
            self.status_changed.emit(f"导出失败: {e}")
            return False

class WhisperIntegrator:
    def __init__(self, model_size="base", language="zh"):
        self.module = WhisperModule(model_size=model_size, language=language)
    def connect_signals(self, result_callback=None, status_callback=None):
        if result_callback:
            self.module.result_ready.connect(result_callback)
        if status_callback:
            self.module.status_changed.connect(status_callback)
    def process_video(self, video_path):
        t = threading.Thread(target=self.module.transcribe_video, args=(video_path,), daemon=True)
        t.start()
    def export_results(self, output_path):
        return self.module.export_results(output_path)
    def get_results(self):
        return self.module.results
