package com.example.api;

import com.example.api.ReviewRepository.BreakdownRow;
import com.example.api.ReviewRepository.ConfusionCell;
import com.example.api.ReviewRepository.PredictionRow;
import com.example.api.ReviewRepository.RunSummary;
import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api")
public class ReviewController {

    private static final List<String> SETS = List.of("gold", "held_out");
    private static final List<String> LANGUAGES = List.of("en", "es", "fr");

    private final ReviewRepository repo;

    public ReviewController(ReviewRepository repo) {
        this.repo = repo;
    }

    @GetMapping("/runs")
    public List<RunSummary> runs() {
        return repo.runs();
    }

    @GetMapping("/runs/{runId}/predictions")
    public List<PredictionRow> predictions(@PathVariable String runId,
                                           @RequestParam(required = false) String set,
                                           @RequestParam(required = false) String language,
                                           @RequestParam(defaultValue = "false") boolean errorsOnly) {
        checkRun(runId);
        checkAllowed("set", set, SETS);
        checkAllowed("language", language, LANGUAGES);
        return repo.predictions(runId, set, language, errorsOnly);
    }

    @GetMapping("/runs/{runId}/confusion")
    public List<ConfusionCell> confusion(@PathVariable String runId,
                                         @RequestParam(required = false) String set) {
        checkRun(runId);
        checkAllowed("set", set, SETS);
        return repo.confusion(runId, set);
    }

    /** by=language breaks accuracy down by language; by=intent breaks it down by gold intent. */
    @GetMapping("/runs/{runId}/breakdown")
    public List<BreakdownRow> breakdown(@PathVariable String runId,
                                        @RequestParam String by,
                                        @RequestParam(required = false) String set) {
        checkRun(runId);
        checkAllowed("set", set, SETS);
        String column = switch (by) {
            case "language" -> "language";
            case "intent" -> "gold";
            default -> throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "by must be language or intent");
        };
        return repo.breakdown(runId, set, column);
    }

    private void checkRun(String runId) {
        if (!repo.runExists(runId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "unknown run: " + runId);
        }
    }

    private static void checkAllowed(String name, String value, List<String> allowed) {
        if (value != null && !allowed.contains(value)) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, name + " must be one of " + allowed);
        }
    }
}
