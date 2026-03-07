package com.smartclassinsight.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/users")
public class UserController {
  @GetMapping("")
  public ResponseEntity<List<Map<String, Object>>> list() {
    Map<String, Object> u = new HashMap<>();
    u.put("id", 1);
    u.put("username", "admin");
    u.put("role", "ADMIN");
    return ResponseEntity.ok(List.of(u));
  }
  @PostMapping("")
  public ResponseEntity<Map<String, Object>> create(@RequestBody Map<String, Object> payload) {
    payload.put("id", 2);
    return ResponseEntity.ok(payload);
  }
}
