package fr.ifpen.historian.config;

import java.time.LocalDate;

/**
 * Retention periods in days
 * <p>
 * Created by IFPEN on 27/03/2019.
 */
public class RetentionPeriods {
    private Integer files;
    private Integer db;

    public RetentionPeriods() {
    }

    public Integer getFiles() {
        return files;
    }

    public void setFiles(Integer files) {
        this.files = files;
    }

    public LocalDate lastFilesDate() {
        return LocalDate.now().minusDays(files);
    }

    public Integer getDb() {
        return db;
    }

    public void setDb(Integer db) {
        this.db = db;
    }

    public LocalDate lastDbDate() {
        return LocalDate.now().minusDays(db);
    }

    public LocalDate lastFullDataDate() {
        return LocalDate.now().minusDays(Math.min(db, files));
    }

    @Override
    public String toString() {
        return "RetentionPeriods{" +
                "files=" + files +
                ", db=" + db +
                '}';
    }
}
