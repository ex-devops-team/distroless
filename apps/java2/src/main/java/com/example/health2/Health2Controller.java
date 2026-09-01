package com.example.health2;

import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class Health2Controller {
  @GetMapping("/health")
  public Map<String, String> health() {
    return Map.of("status", "ok", "language", "java", "stack", "spring-boot", "app", "health2");
  }
}
