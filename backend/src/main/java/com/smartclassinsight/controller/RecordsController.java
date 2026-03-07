package com.smartclassinsight.controller;

import com.smartclassinsight.entity.DetectionRecord;
import com.smartclassinsight.service.RecordsService;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/records")
public class RecordsController {
  private final RecordsService service;
  public RecordsController(RecordsService service) { this.service = service; }
  @GetMapping("/images")
  public ResponseEntity<?> imageRecords(@RequestParam(defaultValue = "0") int page,
                                        @RequestParam(defaultValue = "10") int size) {
    Page<DetectionRecord> p = service.pageByType("IMAGE", page, size);
    return ResponseEntity.ok(pageWrap(p));
  }
  @GetMapping("/videos")
  public ResponseEntity<?> videoRecords(@RequestParam(defaultValue = "0") int page,
                                        @RequestParam(defaultValue = "10") int size) {
    Page<DetectionRecord> p = service.pageByType("VIDEO", page, size);
    return ResponseEntity.ok(pageWrap(p));
  }
  @PostMapping("")
  public ResponseEntity<DetectionRecord> addRecord(@RequestBody Map<String, Object> payload) {
    String type = String.valueOf(payload.getOrDefault("type", "IMAGE"));
    String fileName = String.valueOf(payload.getOrDefault("fileName", ""));
    String resultText = String.valueOf(payload.getOrDefault("resultText", ""));
    long ts = payload.get("ts") == null ? System.currentTimeMillis() : Long.parseLong(String.valueOf(payload.get("ts")));
    return ResponseEntity.ok(service.add(type, fileName, resultText, ts));
  }
  private Map<String, Object> pageWrap(Page<DetectionRecord> p) {
    Map<String, Object> m = new HashMap<>();
    m.put("items", p.getContent());
    m.put("page", p.getNumber());
    m.put("size", p.getSize());
    m.put("totalElements", p.getTotalElements());
    m.put("totalPages", p.getTotalPages());
    return m;
  }
}
