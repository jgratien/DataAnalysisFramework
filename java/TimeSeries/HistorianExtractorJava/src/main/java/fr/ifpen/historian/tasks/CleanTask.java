package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.RetentionPeriods;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * Tache de ménage des stats journalières, horaires, des rapports d'extraction et des fichiers
 * <p>
 * Created by IFPEN on 20/02/2019.
 */
public class CleanTask extends AbstractTask<Integer> {
    private static final DateTimeFormatter FILE_DATE_FMT = DateTimeFormatter.ofPattern("-yyyyMMdd");

    protected Logger log = LoggerFactory.getLogger(CleanTask.class);

    public CleanTask() {
        super();
        log.debug("new {}", toString());
    }

    @Override
    public Integer runTask() {
        LocalDateTime t0 = LocalDateTime.now();
        RetentionPeriods periods = Singleton.getInstance().getConfiguration().getRetentionPeriods();
        log.debug("clean task starting, deleting entries older than {}", periods);
        log.debug("clean task, deleting db entries older than {}", periods.lastDbDate());
        LogDAO.deleteStats(periods.lastDbDate());
        log.debug("clean task, deleting data file older than {}", periods.lastFilesDate());
        deleteOldFiles(periods.lastFilesDate());
        log.info("end of logs, stats and files cleaning. DB entries older than {} and files older than {} have been deleted in {}s",
                periods.lastDbDate(), periods.lastFilesDate(), ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        return 1;
    }

    private void deleteFile(Path file) {
        try {
            if (!Files.isDirectory(file)) {
                if (debug) {
                    log.info("debug mode simulating delete {}", file);
                } else {
                    Files.deleteIfExists(file);
                    log.debug("{} deleted successfully", file);
                }
            } else {
                log.warn("invalid file to delete {}", file);
            }
        } catch (IOException e) {
            log.error("unable to delete old file {} : {}", file, e.getMessage());
        }
    }

    private void deleteOldFiles(LocalDate lastFileDate) {
        Path dataPath = Singleton.getInstance().getConfiguration().dataDirectoryAsPath();
        List<String> validDates = new ArrayList<>();
        for (LocalDate day = lastFileDate; day.isBefore(LocalDate.now()); day = day.plusDays(1))
            validDates.add(day.plusDays(1).format(FILE_DATE_FMT));
        try {
            log.debug("Repertoire={}", dataPath);
            Files.list(dataPath)
                    .filter(Files::isRegularFile)
                    .filter(f -> f.getFileName().toString().endsWith(".csv"))
                    .filter(f -> f.getFileName().toString().startsWith("dataHistorian-"))
                    .filter(f -> !validDates.stream().anyMatch(d -> f.getFileName().toString().contains(d)))
                    .forEach(this::deleteFile);
        } catch (IOException e) {
            log.error("unable to list old data files to delete in directory {} : {}", dataPath, e.getMessage());
        }
    }

    @Override
    public String toString() {
        return "daily clean task in background";
    }

    @Override
    public long computeInitialDelay() {
        // prochaine heure
        LocalDateTime nextRun = LocalDateTime.now().truncatedTo(ChronoUnit.HOURS).plusHours(1);
        // on démarre à 0h30, 3h30, 6h30, 9h30, 12h30, 15h30, 18h30, 21h30
        while (nextRun.getHour() % 3 != 0) {
            nextRun = nextRun.plusHours(1);
        }
        // on fait démarrer la tache à la période suivante à la demi
        return ChronoUnit.SECONDS.between(LocalDateTime.now(), nextRun.plusMinutes(30));
    }

    @Override
    public long getPeriod() {
        // tourne toutes les 3 heures
        return 3 * 60 * 60;
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }
}
