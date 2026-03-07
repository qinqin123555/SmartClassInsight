package com.smartclassinsight.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "detect.python")
public class DetectProperties {
  private boolean enabled = false;
  private String command = "";

  public boolean isEnabled() { return enabled; }
  public void setEnabled(boolean enabled) { this.enabled = enabled; }

  public String getCommand() { return command; }
  public void setCommand(String command) { this.command = command; }
}
