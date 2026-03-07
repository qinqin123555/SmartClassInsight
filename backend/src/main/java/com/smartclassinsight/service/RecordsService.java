package com.smartclassinsight.service;

import com.smartclassinsight.entity.DetectionRecord;
import com.smartclassinsight.repo.DetectionRecordRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.ZoneId;
import java.util.ArrayList;
import java.util.List;

@Service
public class RecordsService {
  private final DetectionRecordRepository repo;
  public RecordsService(DetectionRecordRepository repo) { this.repo = repo; }
  public Page<DetectionRecord> pageByType(String type, int page, int size) {
    return repo.findByTypeOrderByTsDesc(type, PageRequest.of(page, size));
  }
  public DetectionRecord add(String type, String fileName, String resultText, long ts) {
    DetectionRecord r = new DetectionRecord();
    r.setType(type);
    r.setFileName(fileName);
    r.setResultText(resultText);
    r.setTs(ts);
    return repo.save(r);
  }
  public List<Integer> last5DaysCounts(String type) {
    List<Integer> res = new ArrayList<>();
    ZoneId zone = ZoneId.systemDefault();
    for (int i = 4; i >= 0; i--) {
      LocalDate day = LocalDate.now().minusDays(i);
      long start = day.atStartOfDay(zone).toInstant().toEpochMilli();
      long end = day.plusDays(1).atStartOfDay(zone).toInstant().toEpochMilli() - 1;
      long c = repo.countBetweenTsAndType(start, end, type);
      res.add((int) c);
    }
    return res;
  }
  public long totalCount() { return repo.count(); }
  public long userCountMock() { return 256; }
  public double avgDetectionMsMock() { return 842.5; }
  public String mostCommonResult() {
    // naive: read first page and return resultText, replace with real aggregation
    Page<DetectionRecord> p = repo.findByTypeOrderByTsDesc("VIDEO", PageRequest.of(0, 1));
    if (p.hasContent()) return p.getContent().get(0).getResultText();
    return "N/A";
  }
}
