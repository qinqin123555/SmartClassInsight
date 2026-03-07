package com.smartclassinsight.controller;

import com.smartclassinsight.dto.MetricSummary;
import com.smartclassinsight.service.RecordsService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/metrics")
public class MetricsController {
  private final RecordsService service;
  public MetricsController(RecordsService service) { this.service = service; }
  @GetMapping("/summary")
  public ResponseEntity<MetricSummary> summary() {
    MetricSummary s = new MetricSummary();
    s.setServiceCount(service.totalCount());
    s.setMostReadTitle(service.mostCommonResult());
    s.setAvgDetectionMs(service.avgDetectionMsMock());
    s.setUserCount(service.userCountMock());
    s.setLast5DaysCounts(service.last5DaysCounts("VIDEO"));
    return ResponseEntity.ok(s);
  }
}
