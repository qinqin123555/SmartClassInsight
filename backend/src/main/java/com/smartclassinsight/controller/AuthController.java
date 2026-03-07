package com.smartclassinsight.controller;

import com.smartclassinsight.entity.User;
import com.smartclassinsight.repo.UserRepository;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/auth")
public class AuthController {
  private final UserRepository users;
  private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();
  public AuthController(UserRepository users) { this.users = users; }
  @PostMapping("/register")
  public ResponseEntity<?> register(@RequestBody Map<String, String> payload) {
    String username = payload.getOrDefault("username", "").trim();
    String password = payload.getOrDefault("password", "");
    if (username.isEmpty() || password.length() < 6) return ResponseEntity.badRequest().body(Map.of("error", "invalid"));
    if (users.existsByUsername(username)) return ResponseEntity.badRequest().body(Map.of("error", "exists"));
    User u = new User();
    u.setUsername(username);
    u.setPasswordHash(encoder.encode(password));
    u.setRole("USER");
    u.setCreatedAt(System.currentTimeMillis());
    users.save(u);
    return ResponseEntity.ok(Map.of("ok", true));
  }
  @PostMapping("/login")
  public ResponseEntity<?> login(@RequestBody Map<String, String> payload) {
    String username = payload.getOrDefault("username", "");
    String password = payload.getOrDefault("password", "");
    User u = users.findByUsername(username).orElse(null);
    if (u == null || !encoder.matches(password, u.getPasswordHash())) return ResponseEntity.status(401).body(Map.of("error", "unauthorized"));
    String token = "token-" + username;
    Map<String, Object> res = new HashMap<>();
    res.put("token", token);
    res.put("username", username);
    return ResponseEntity.ok(res);
  }
}
