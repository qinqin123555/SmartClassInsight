package com.smartclassinsight.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "detection_records")
public class DetectionRecord {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @Column(nullable = false, length = 16)
  private String type; // IMAGE or VIDEO
  @Column(nullable = false)
  private String fileName;
  @Column(nullable = false)
  private String resultText;
  @Column(nullable = false)
  private Long ts;
  public Long getId() { return id; }
  public void setId(Long id) { this.id = id; }
  public String getType() { return type; }
  public void setType(String type) { this.type = type; }
  public String getFileName() { return fileName; }
  public void setFileName(String fileName) { this.fileName = fileName; }
  public String getResultText() { return resultText; }
  public void setResultText(String resultText) { this.resultText = resultText; }
  public Long getTs() { return ts; }
  public void setTs(Long ts) { this.ts = ts; }
}
