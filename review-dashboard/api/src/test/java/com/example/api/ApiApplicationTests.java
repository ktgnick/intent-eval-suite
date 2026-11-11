package com.example.api;

import static org.assertj.core.api.Assertions.assertThat;

import com.example.api.ReviewRepository.RunSummary;
import java.util.Map;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

/** Checks the seeded data against the results recorded in the two projects. */
@SpringBootTest
class ApiApplicationTests {

    @Autowired
    ReviewRepository repo;

    @Test
    void runSummariesMatchRecordedResults() {
        Map<String, RunSummary> runs = repo.runs().stream()
                .collect(Collectors.toMap(RunSummary::id, r -> r));

        assertThat(runs.get("model_a").total()).isEqualTo(36);
        assertThat(runs.get("model_a").correct()).isEqualTo(27);
        assertThat(runs.get("model_b").correct()).isEqualTo(34);
        assertThat(runs.get("haiku_gold").correct()).isEqualTo(36);
        assertThat(runs.get("haiku_held_out").total()).isEqualTo(15);
        assertThat(runs.get("haiku_held_out").correct()).isEqualTo(15);
    }

    @Test
    void errorsOnlyReturnsOnlyWrongRows() {
        assertThat(repo.predictions("model_a", null, null, true))
                .hasSize(36 - 27)
                .allMatch(row -> !row.correct());
    }
}
