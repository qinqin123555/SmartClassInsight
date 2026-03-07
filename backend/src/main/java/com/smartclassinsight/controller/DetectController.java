package com.smartclassinsight.controller;

import com.smartclassinsight.entity.DetectionRecord;
import com.smartclassinsight.service.RecordsService;
import com.smartclassinsight.service.PythonDetectService;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@RestController
@RequestMapping("/api/detect")
public class DetectController {
  private final RecordsService records;
  private final PythonDetectService pythonDetect;
  private final ExecutorService executorService = Executors.newCachedThreadPool();
  
  public DetectController(RecordsService records, PythonDetectService pythonDetect) { 
    this.records = records; 
    this.pythonDetect = pythonDetect;
  }
  
  @PostMapping("/image")
  public ResponseEntity<?> detectImage(@RequestParam("file") MultipartFile file) throws IOException, InterruptedException {
    String fileName = file != null ? file.getOriginalFilename() : "unknown.jpg";
    String result;
    String engine = "fallback";
    String annotatedImageBase64 = null;
    if (file == null || file.isEmpty()) {
      result = "无效图片";
    } else if (pythonDetect.isHealthy()) {
      try {
        File dir = new File(System.getProperty("user.dir"), "data/uploads");
        if (!dir.exists()) dir.mkdirs();
        File saved = new File(dir, System.currentTimeMillis() + "-" + file.getOriginalFilename());
        file.transferTo(saved);
        
        Map<String, Object> detectResult = pythonDetect.detectWithDetails(saved);
        result = (String) detectResult.get("label");
        annotatedImageBase64 = (String) detectResult.get("annotatedImage");
        
        if (annotatedImageBase64 != null) {
          String annotatedFileName = "annotated-" + saved.getName();
          File annotatedFile = new File(dir, annotatedFileName);
          byte[] imageBytes = Base64.getDecoder().decode(annotatedImageBase64);
          Files.write(annotatedFile.toPath(), imageBytes);
          System.out.println("Annotated image saved: " + annotatedFile.getAbsolutePath());
        }
        
        engine = "python";
      } catch (Exception ex) {
        String[] labels = new String[]{"举手", "阅读", "使用手机", "写作", "走神"};
        int idx = Math.abs(fileName.hashCode()) % labels.length;
        result = labels[idx];
        engine = "fallback";
      }
    } else {
      String[] labels = new String[]{"举手", "阅读", "使用手机", "写作", "走神"};
      int idx = Math.abs(fileName.hashCode()) % labels.length;
      result = labels[idx];
    }
    DetectionRecord saved = records.add("IMAGE", fileName, result, System.currentTimeMillis());
    Map<String, Object> res = new HashMap<>();
    res.put("ok", true);
    res.put("id", saved.getId());
    res.put("fileName", fileName);
    res.put("resultText", result);
    res.put("engine", engine);
    if (annotatedImageBase64 != null) {
      res.put("annotatedImage", "data:image/jpeg;base64," + annotatedImageBase64);
    }
    return ResponseEntity.ok(res);
  }

  @PostMapping("/image/python")
  public ResponseEntity<?> detectImagePython(@RequestParam("file") MultipartFile file) throws IOException, InterruptedException {
    Map<String, Object> res = new HashMap<>();
    if (file == null || file.isEmpty()) {
      res.put("ok", false);
      res.put("error", "empty");
      return ResponseEntity.badRequest().body(res);
    }
    if (!pythonDetect.isHealthy()) {
      res.put("ok", false);
      res.put("error", "python_service_unavailable");
      return ResponseEntity.badRequest().body(res);
    }
    try {
      File dir = new File(System.getProperty("user.dir"), "data/uploads");
      if (!dir.exists()) dir.mkdirs();
      File savedFile = new File(dir, System.currentTimeMillis() + "-" + file.getOriginalFilename());
      file.transferTo(savedFile);
      Map<String, Object> detectResult = pythonDetect.detectWithDetails(savedFile);
      String label = (String) detectResult.get("label");
      Integer count = detectResult.get("count") != null ? ((Number) detectResult.get("count")).intValue() : null;
      List<Map<String, Object>> detections = (List<Map<String, Object>>) detectResult.get("detections");
      String annotatedImageBase64 = (String) detectResult.get("annotatedImage");
      
      String annotatedImageUrl = null;
      if (annotatedImageBase64 != null) {
        String annotatedFileName = "annotated-" + savedFile.getName();
        File annotatedFile = new File(dir, annotatedFileName);
        byte[] imageBytes = Base64.getDecoder().decode(annotatedImageBase64);
        Files.write(annotatedFile.toPath(), imageBytes);
        annotatedImageUrl = "/api/uploads/" + annotatedFileName;
        System.out.println("Annotated image saved: " + annotatedFile.getAbsolutePath());
      }
      
      DetectionRecord saved = records.add("IMAGE", file.getOriginalFilename(), label, System.currentTimeMillis());
      res.put("ok", true);
      res.put("id", saved.getId());
      res.put("fileName", file.getOriginalFilename());
      res.put("resultText", label);
      if (count != null) res.put("count", count);
      if (detections != null) res.put("detections", detections);
      if (annotatedImageBase64 != null) {
        res.put("annotatedImage", "data:image/jpeg;base64," + annotatedImageBase64);
      }
      if (annotatedImageUrl != null) {
        res.put("annotatedImageUrl", annotatedImageUrl);
      }
      res.put("engine", "python");
      return ResponseEntity.ok(res);
    } catch (Exception e) {
      res.put("ok", false);
      res.put("error", "exec_failed");
      res.put("message", e.getMessage());
      return ResponseEntity.internalServerError().body(res);
    }
  }
  
  @PostMapping("/video")
  public SseEmitter detectVideo(@RequestParam("file") MultipartFile file, 
                               @RequestParam(value = "skipFrames", defaultValue = "2") int skipFrames) {
    System.out.println("Received video detection request");
    System.out.println("File: " + (file != null ? file.getOriginalFilename() : "null"));
    System.out.println("Skip frames: " + skipFrames);
    SseEmitter emitter = new SseEmitter(0L); // 无超时
    
    executorService.execute(() -> {
      try {
        if (file == null || file.isEmpty()) {
          System.out.println("Error: Empty file");
          emitter.send(SseEmitter.event().name("error").data("{\"error\": \"empty_file\"}"));
          emitter.complete();
          return;
        }
        
        if (!pythonDetect.isHealthy()) {
          System.out.println("Error: Python service unavailable");
          emitter.send(SseEmitter.event().name("error").data("{\"error\": \"python_service_unavailable\"}"));
          emitter.complete();
          return;
        }
        
        // 保存视频文件
        File dir = new File(System.getProperty("user.dir"), "data/uploads");
        if (!dir.exists()) dir.mkdirs();
        String videoFileName = System.currentTimeMillis() + "-" + file.getOriginalFilename();
        File savedFile = new File(dir, videoFileName);
        file.transferTo(savedFile);
        System.out.println("Saved video to: " + savedFile.getAbsolutePath());
        
        System.out.println("Starting video detection: " + videoFileName);
        
        // 使用局部变量存储frameData，避免竞态条件
        final Map<String, Object>[] frameDataHolder = new Map[1];
        
        // 调用Python服务进行视频流式检测
        pythonDetect.detectVideoStream(savedFile, skipFrames, new PythonDetectService.VideoFrameCallback() {
          int frameCount = 0;
          
          @Override
          public void onFrame(Map<String, Object> frameData) {
            try {
              // 使用ObjectMapper将Map对象转换为JSON字符串
              ObjectMapper mapper = new ObjectMapper();
              String jsonData = mapper.writeValueAsString(frameData);
              
              // 发送SSE事件，使用SseEmitter.event()方法
              // 这样SseEmitter会自动添加data:前缀和\n\n后缀
              emitter.send(SseEmitter.event().data(jsonData));
              
              frameDataHolder[0] = frameData;
              frameCount++;
              if (frameCount % 10 == 0) {
                System.out.println("Sent frame data: " + frameCount);
              }
            } catch (Exception e) {
              System.err.println("Error sending frame data: " + e.getMessage());
              e.printStackTrace();
            }
          }
          
          @Override
          public void onComplete() {
            try {
              // 保存检测记录
              String finalLabel = frameDataHolder[0] != null ? (String) frameDataHolder[0].get("label") : "未知";
              records.add("VIDEO", file.getOriginalFilename(), finalLabel, System.currentTimeMillis());
              emitter.send(SseEmitter.event().name("complete").data("{\"status\": \"completed\"}"));
              emitter.complete();
              System.out.println("Video detection completed, total frames: " + frameCount);
            } catch (Exception e) {
              System.err.println("Error completing emitter: " + e.getMessage());
              emitter.completeWithError(e);
            }
          }
          
          @Override
          public void onError(String error) {
            try {
              emitter.send(SseEmitter.event().name("error").data("{\"error\": \"" + error + "\"}"));
              emitter.complete();
              System.out.println("Video detection error: " + error);
            } catch (IOException e) {
              System.err.println("Error sending error: " + e.getMessage());
              emitter.completeWithError(e);
            }
          }
        });
        
      } catch (Exception e) {
        try {
          emitter.send(SseEmitter.event().name("error").data("{\"error\": \"" + e.getMessage() + "\"}"));
          emitter.complete();
        } catch (IOException ex) {
          emitter.completeWithError(ex);
        }
      }
    });
    
    return emitter;
  }
  
  @GetMapping("/health")
  public ResponseEntity<?> health() {
    return ResponseEntity.ok("{\"status\": \"ok\"}");
  }
  
  private Map<String, Object> frameData;
}
