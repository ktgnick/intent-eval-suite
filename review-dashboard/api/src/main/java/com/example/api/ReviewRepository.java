package com.example.api;

import java.util.ArrayList;
import java.util.List;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

/** SQL over the scored view. All user-supplied values are bound as parameters. */
@Repository
public class ReviewRepository {

    /** accuracy is a real field so it appears in the JSON response. */
    public record RunSummary(String id, String label, String description, int total, int correct, double accuracy) {
        static RunSummary of(String id, String label, String description, int total, int correct) {
            double accuracy = total == 0 ? 0 : (double) correct / total;
            return new RunSummary(id, label, description, total, correct, accuracy);
        }
    }

    public record PredictionRow(String exampleId, String language, String setName, String text,
                                String gold, String pred, boolean correct, String reason) {}

    public record ConfusionCell(String gold, String pred, int count) {}

    public record BreakdownRow(String key, int total, int correct, double accuracy) {
        static BreakdownRow of(String key, int total, int correct) {
            double accuracy = total == 0 ? 0 : (double) correct / total;
            return new BreakdownRow(key, total, correct, accuracy);
        }
    }

    private final JdbcTemplate jdbc;

    public ReviewRepository(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    public List<RunSummary> runs() {
        return jdbc.query("""
                SELECT r.id, r.label, r.description,
                       COUNT(s.example_id) AS total,
                       COALESCE(SUM(CASE WHEN s.correct THEN 1 ELSE 0 END), 0) AS correct
                FROM runs r
                LEFT JOIN scored s ON s.run_id = r.id
                GROUP BY r.id, r.label, r.description
                ORDER BY r.id
                """,
                (rs, i) -> RunSummary.of(rs.getString("id"), rs.getString("label"),
                        rs.getString("description"), rs.getInt("total"), rs.getInt("correct")));
    }

    public List<PredictionRow> predictions(String runId, String set, String language, boolean errorsOnly) {
        StringBuilder sql = new StringBuilder("""
                SELECT s.example_id, s.language, s.set_name, s.text, s.gold, s.pred, s.correct, p.reason
                FROM scored s
                JOIN predictions p ON p.run_id = s.run_id AND p.example_id = s.example_id
                WHERE s.run_id = ?
                """);
        List<Object> args = new ArrayList<>();
        args.add(runId);
        if (set != null) {
            sql.append(" AND s.set_name = ?");
            args.add(set);
        }
        if (language != null) {
            sql.append(" AND s.language = ?");
            args.add(language);
        }
        if (errorsOnly) {
            sql.append(" AND s.correct = FALSE");
        }
        sql.append(" ORDER BY s.example_id");
        return jdbc.query(sql.toString(), (rs, i) -> new PredictionRow(
                rs.getString("example_id"), rs.getString("language"), rs.getString("set_name"),
                rs.getString("text"), rs.getString("gold"), rs.getString("pred"),
                rs.getBoolean("correct"), rs.getString("reason")), args.toArray());
    }

    public List<ConfusionCell> confusion(String runId, String set) {
        StringBuilder sql = new StringBuilder("SELECT gold, pred, COUNT(*) AS n FROM scored WHERE run_id = ?");
        List<Object> args = new ArrayList<>();
        args.add(runId);
        if (set != null) {
            sql.append(" AND set_name = ?");
            args.add(set);
        }
        sql.append(" GROUP BY gold, pred ORDER BY gold, pred");
        return jdbc.query(sql.toString(), (rs, i) -> new ConfusionCell(
                rs.getString("gold"), rs.getString("pred"), rs.getInt("n")), args.toArray());
    }

    /** column must be a fixed column name chosen by the controller, never user text. */
    public List<BreakdownRow> breakdown(String runId, String set, String column) {
        String sql = "SELECT " + column + " AS k, COUNT(*) AS total, "
                + "SUM(CASE WHEN correct THEN 1 ELSE 0 END) AS correct "
                + "FROM scored WHERE run_id = ?"
                + (set == null ? "" : " AND set_name = ?")
                + " GROUP BY " + column + " ORDER BY " + column;
        List<Object> args = new ArrayList<>();
        args.add(runId);
        if (set != null) {
            args.add(set);
        }
        return jdbc.query(sql, (rs, i) -> BreakdownRow.of(
                rs.getString("k"), rs.getInt("total"), rs.getInt("correct")), args.toArray());
    }

    public boolean runExists(String runId) {
        Integer n = jdbc.queryForObject("SELECT COUNT(*) FROM runs WHERE id = ?", Integer.class, runId);
        return n != null && n > 0;
    }
}
