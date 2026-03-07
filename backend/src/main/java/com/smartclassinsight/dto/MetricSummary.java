package com.smartclassinsight.dto;

import java.util.List;

public class MetricSummary {
  private long serviceCount;
  private String mostReadTitle;
  private double avgDetectionMs;
  private long userCount;
  private List<Integer> last5DaysCounts;

  public long getServiceCount() { return serviceCount; }
  public void setServiceCount(long v) { this.serviceCount = v; }
  public String getMostReadTitle() { return mostReadTitle; }
  public void setMostReadTitle(String v) { this.mostReadTitle = v; }
  public double getAvgDetectionMs() { return avgDetectionMs; }
  public void setAvgDetectionMs(double v) { this.avgDetectionMs = v; }
  public long getUserCount() { return userCount; }
  public void setUserCount(long v) { this.userCount = v; }
  public List<Integer> getLast5DaysCounts() { return last5DaysCounts; }
  public void setLast5DaysCounts(List<Integer> v) { this.last5DaysCounts = v; }
}
