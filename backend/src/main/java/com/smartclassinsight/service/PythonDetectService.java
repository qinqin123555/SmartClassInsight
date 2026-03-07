package com.smartclassinsight.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URI;
import java.util.Map;
import com.fasterxml.jackson.databind.ObjectMapper;

@Service
public class PythonDetectService {
  private static final Logger log = LoggerFactory.getLogger(PythonDetectService.class);

  @Value("${detect.python.service.url:http://localhost:5001}")
  private String serviceUrl;

  private final RestTemplate restTemplate = new RestTemplate();

  public interface VideoFrameCallback {
    void onFrame(Map<String, Object> frameData);
    void onComplete();
    void onError(String error);
  }

  public String detect(File image) throws Exception {
    log.info("Detecting image: {} using service: {}", image.getName(), serviceUrl);
    try {
      HttpHeaders headers = new HttpHeaders();
      headers.setContentType(MediaType.MULTIPART_FORM_DATA);

      MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
      body.add("image", new FileSystemResource(image));

      HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
      ResponseEntity<Map> response = restTemplate.postForEntity(serviceUrl + "/detect", request, Map.class);

      if (response.getStatusCode() == HttpStatus.OK && response.getBody() != null) {
        String label = (String) response.getBody().get("label");
        log.info("Detection result: {}", label);
        return label;
      }
      throw new Exception("Detection failed with status: " + response.getStatusCode());
    } catch (Exception e) {
      log.error("Detection failed for {}: {}", image.getName(), e.getMessage(), e);
      throw e;
    }
  }

  public Map<String, Object> detectWithDetails(File image) throws Exception {
    log.info("Detecting image with details: {} using service: {}", image.getName(), serviceUrl);
    try {
      HttpHeaders headers = new HttpHeaders();
      headers.setContentType(MediaType.MULTIPART_FORM_DATA);

      MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
      body.add("image", new FileSystemResource(image));

      HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);
      ResponseEntity<Map> response = restTemplate.postForEntity(serviceUrl + "/detect", request, Map.class);

      if (response.getStatusCode() == HttpStatus.OK) {
        log.info("Detection successful: {}", response.getBody());
        return response.getBody();
      }
      throw new Exception("Detection failed with status: " + response.getStatusCode());
    } catch (Exception e) {
      log.error("Detection with details failed for {}: {}", image.getName(), e.getMessage(), e);
      throw e;
    }
  }

  public void detectVideoStream(File video, int skipFrames, VideoFrameCallback callback) {
    log.info("Starting video stream detection: {} using service: {}", video.getName(), serviceUrl);
    
    try {
      HttpHeaders headers = new HttpHeaders();
      headers.setContentType(MediaType.MULTIPART_FORM_DATA);
      headers.setAccept(java.util.Collections.singletonList(MediaType.TEXT_EVENT_STREAM));

      MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
      body.add("video", new FileSystemResource(video));
      body.add("skip_frames", String.valueOf(skipFrames));

      HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
      
      log.info("Sending request to: {}", serviceUrl + "/detect/video");
      log.info("Request headers: {}", headers);
      
      // 使用RestTemplate的execute方法来处理流式响应
      restTemplate.execute(
        URI.create(serviceUrl + "/detect/video"),
        HttpMethod.POST,
        new org.springframework.web.client.RequestCallback() {
          @Override
          public void doWithRequest(org.springframework.http.client.ClientHttpRequest request) throws IOException {
            log.info("Writing request to server...");
            request.getHeaders().putAll(headers);
            // 写入请求体
            new org.springframework.http.converter.FormHttpMessageConverter().write(requestEntity.getBody(), MediaType.MULTIPART_FORM_DATA, request);
            log.info("Request written successfully");
          }
        },
        responseExtractor -> {
          log.info("Response received, status: {}", responseExtractor.getStatusCode());
          log.info("Response headers: {}", responseExtractor.getHeaders());
          
          try (BufferedReader reader = new BufferedReader(new InputStreamReader(responseExtractor.getBody()))) {
            String line;
            int lineCount = 0;
            int frameCount = 0;
            StringBuilder eventBuilder = new StringBuilder();
            while ((line = reader.readLine()) != null) {
              lineCount++;
              log.debug("Read line {}: {}", lineCount, line);
              eventBuilder.append(line).append("\n");
              if (line.isEmpty() && eventBuilder.length() > 1) {
                // 当遇到空行时，解析完整的SSE事件
                try {
                  String eventData = eventBuilder.toString();
                  // 提取data部分
                  String[] eventLines = eventData.split("\n");
                  String dataLine = null;
                  for (String eventLine : eventLines) {
                    if (eventLine.startsWith("data: ")) {
                      dataLine = eventLine.substring(6);
                      break;
                    }
                  }
                  if (dataLine != null) {
                    // 解析JSON数据
                    ObjectMapper mapper = new ObjectMapper();
                    Map<String, Object> frameData = mapper.readValue(dataLine, Map.class);
                    callback.onFrame(frameData);
                    frameCount++;
                    if (frameCount % 10 == 0) {
                      log.info("Sent frame data: {}, total: {}", lineCount, frameCount);
                    }
                  }
                } catch (Exception e) {
                  log.error("Error processing SSE event: {}", e.getMessage());
                }
                eventBuilder.setLength(0);
              }
              if (lineCount % 100 == 0) {
                log.info("Read {} lines from response", lineCount);
              }
            }
            log.info("Total lines read: {}, total frames sent: {}", lineCount, frameCount);
          } catch (Exception e) {
            log.error("Error reading response: {}", e.getMessage(), e);
            callback.onError(e.getMessage());
          } finally {
            callback.onComplete();
            log.info("Video detection completed");
          }
          return null;
        }
      );
    } catch (Exception e) {
      log.error("Video stream detection failed for {}: {}", video.getName(), e.getMessage(), e);
      callback.onError(e.getMessage());
    }
  }

  public boolean isHealthy() {
    try {
      log.debug("Checking health of service: {}", serviceUrl);
      ResponseEntity<Map> response = restTemplate.getForEntity(serviceUrl + "/health", Map.class);
      boolean healthy = response.getStatusCode() == HttpStatus.OK;
      log.info("Service health check: {} - {}", serviceUrl, healthy ? "OK" : "FAILED");
      return healthy;
    } catch (Exception e) {
      log.warn("Service health check failed for {}: {}", serviceUrl, e.getMessage());
      return false;
    }
  }
}
