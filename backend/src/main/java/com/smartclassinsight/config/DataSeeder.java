package com.smartclassinsight.config;

import com.smartclassinsight.entity.DetectionRecord;
import com.smartclassinsight.repo.DetectionRecordRepository;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class DataSeeder implements ApplicationRunner {
  private final DetectionRecordRepository repo;
  public DataSeeder(DetectionRecordRepository repo) { this.repo = repo; }
  @Override
  public void run(ApplicationArguments args) {
    if (repo.count() > 0) return;
    long now = System.currentTimeMillis();
    List<DetectionRecord> seed = List.of(
        make("IMAGE", "class_img_01.jpg", "举手", now - 1000L * 60 * 60 * 24 * 1),
        make("IMAGE", "class_img_02.jpg", "使用手机", now - 1000L * 60 * 60 * 24 * 2),
        make("VIDEO", "class_01.mp4", "阅读", now - 1000L * 60 * 60 * 24 * 3),
        make("VIDEO", "class_02.mp4", "写作", now - 1000L * 60 * 60 * 24 * 1),
        make("VIDEO", "class_03.mp4", "举手", now - 1000L * 60 * 60 * 24 * 0)
    );
    repo.saveAll(seed);
  }
  private DetectionRecord make(String type, String file, String result, long ts) {
    DetectionRecord r = new DetectionRecord();
    r.setType(type);
    r.setFileName(file);
    r.setResultText(result);
    r.setTs(ts);
    return r;
  }
}
