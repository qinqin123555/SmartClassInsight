package com.smartclassinsight.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "users", indexes = @Index(name = "idx_users_username", columnList = "username", unique = true))
public class User {
  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;
  @Column(nullable = false, unique = true, length = 64)
  private String username;
  @Column(nullable = false)
  private String passwordHash;
  @Column(nullable = false, length = 16)
  private String role;
  @Column(nullable = false)
  private Long createdAt;
  public Long getId() { return id; }
  public void setId(Long id) { this.id = id; }
  public String getUsername() { return username; }
  public void setUsername(String username) { this.username = username; }
  public String getPasswordHash() { return passwordHash; }
  public void setPasswordHash(String passwordHash) { this.passwordHash = passwordHash; }
  public String getRole() { return role; }
  public void setRole(String role) { this.role = role; }
  public Long getCreatedAt() { return createdAt; }
  public void setCreatedAt(Long createdAt) { this.createdAt = createdAt; }
}
