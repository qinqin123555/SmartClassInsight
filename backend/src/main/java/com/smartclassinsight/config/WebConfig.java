package com.smartclassinsight.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import java.io.File;

@Configuration
public class WebConfig implements WebMvcConfigurer {
  
  @Override
  public void addResourceHandlers(ResourceHandlerRegistry registry) {
    // 配置静态资源映射，使上传的图片可以通过URL访问
    String uploadPath = new File(System.getProperty("user.dir"), "data/uploads").getAbsolutePath();
    registry.addResourceHandler("/api/uploads/**")
            .addResourceLocations("file:" + uploadPath + "/");
  }
}
