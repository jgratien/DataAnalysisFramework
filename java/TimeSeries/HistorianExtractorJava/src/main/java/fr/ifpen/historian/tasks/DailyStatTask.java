package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.LogStat;
import fr.ifpen.historian.domain.Server;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Date;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * Tache de creation des stats journalières :
 * - combien d'heures traitées, combien d'extraction réussies, de transferts de fichiers
 * - alimentation de la table log_day
 * <p>
 * Created by IFPEN on 20/02/2019.
 */
public class DailyStatTask extends AbstractTask<Integer> {
    protected Logger log = LoggerFactory.getLogger(DailyStatTask.class);

    public DailyStatTask() {
        super();
        log.debug("new {}", toString());
    }

    @Override
    public Integer runTask() {
        // calcul des stats de la veille (on démarre à 0h15)
        for (Server server : Singleton.getInstance().getServers()) {
            LogDAO.computeDayStat(server.getName(), LocalDate.now().minusDays(1));
        }
        // on recalcule l'ensemble des stats à chaque fois (1 fois par jour et à minuit, ça doit passer et ça permet d'être sûr qu'on a des stats pour tout) !
        computeMissingStats();
        return 1;
    }

    private void computeMissingStats() {
        LocalDate end = LocalDate.now().minusDays(1);
        LocalDate start = Singleton.getInstance().getConfiguration().getRetentionPeriods().lastDbDate();
        for (Server server : Singleton.getInstance().getServers()) {
            LocalDateTime t0 = LocalDateTime.now();
            // recalcul des heures manquantes
            computeMissingHourStats(server.getName(), start.atStartOfDay(), end.plusDays(1).atStartOfDay());
            // recalcul des jours manquants
            computeMissingDayStats(server.getName(), start, end);
            log.info("end of daily and hourly stat computation for {}, from {} to {} in {}s",
                    server.getName(), start, end, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        }
    }

    private void computeMissingDayStats(String server, LocalDate start, LocalDate end) {
        int nbMaxDays = Singleton.getInstance().getConfiguration().getRetentionPeriods().getDb();
        // on calcule d'abord la liste des jours
        List<LocalDate> days = new ArrayList<>(nbMaxDays);
        for (LocalDate day = start; day.isBefore(end); day = day.plusDays(1)) {
            days.add(day);
        }
        // stats existantes
        List<LogStat> dayStats = LogDAO.listDayStat(server, start, days.size());
        if (dayStats != null && !dayStats.isEmpty()) {
            // on retire les stats existantes
            List<LocalDate> treated = dayStats
                    .stream()
                    .map(LogStat::getDay)
                    .map(Date::toLocalDate)
                    .collect(Collectors.toList());
            days.removeAll(treated);
        }
        // on calcule ce qui manque
        days.forEach(day -> LogDAO.computeDayStat(server, day));
        log.debug("{} / {} missing days stats have been calculated", days.size(), nbMaxDays);
    }

    private void computeMissingHourStats(String server, LocalDateTime start, LocalDateTime end) {
        int nbHoursMax = Singleton.getInstance().getConfiguration().getRetentionPeriods().getDb() * 24;
        // on calcule d'abord la liste des heures
        List<LocalDateTime> hours = new ArrayList<>(nbHoursMax);
        for (LocalDateTime hour = start; hour.isBefore(end); hour = hour.plusHours(1)) {
            hours.add(hour);
        }
        // stats existantes
        List<LogStat> hourStats = LogDAO.listHourStat(server, end, nbHoursMax);
        if (hourStats != null && !hourStats.isEmpty()) {
            // on retire les stats existantes
            List<LocalDateTime> treated = hourStats
                    .stream()
                    .map(LogStat::getHour)
                    .map(Timestamp::toLocalDateTime)
                    .collect(Collectors.toList());
            hours.removeAll(treated);
        }
        // on calcule ce qui manque
        hours.forEach(hour -> LogDAO.computeHourStat(server, hour));
        log.debug("{} / {} missing hours stats have been calculated", hours.size(), nbHoursMax);
    }

    @Override
    public String toString() {
        return "daily stat computation task in background";
    }

    @Override
    public long computeInitialDelay() {
        LocalDateTime nextDay = LocalDateTime.now().truncatedTo(ChronoUnit.DAYS).plusDays(1);
        // on fait démarrer la tache au jour suivant à minuit 15 min
        return ChronoUnit.SECONDS.between(LocalDateTime.now(), nextDay.plusMinutes(15));
    }

    @Override
    public long getPeriod() {
        return 24 * 60 * 60;
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }
}
