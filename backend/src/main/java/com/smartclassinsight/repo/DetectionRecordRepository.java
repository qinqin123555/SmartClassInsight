package com.smartclassinsight.repo;

import com.smartclassinsight.entity.DetectionRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

public interface DetectionRecordRepository extends JpaRepository<DetectionRecord, Long> {
  Page<DetectionRecord> findByTypeOrderByTsDesc(String type, Pageable pageable);
  long countByType(String type);
  @Query("select count(r) from DetectionRecord r where r.ts between ?1 and ?2 and r.type = ?3")
  long countBetweenTsAndType(long startTs, long endTs, String type);
}
