package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Server;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.TimeUnit;

/**
 * Tache de creation des stats horaires :
 * - combien de requêtes effectuées, combien d'extraction réussies, de transferts de fichiers
 * - alimentation de la table log_hour
 * <p>
 * Created by IFPEN on 20/02/2019.
 */
public class HourlyStatTask extends AbstractTask<LocalDateTime> {
    protected Logger log = LoggerFactory.getLogger(HourlyStatTask.class);

    private LocalDateTime hour;

    public HourlyStatTask() {
        super();
        log.debug("new {}", toString());
    }

    @Override
    public LocalDateTime runTask() {
        // la tache démarre à l'heure plus quelques minutes on fait les stats sur l'heure précédente
        hour = LocalDateTime.now().truncatedTo(ChronoUnit.HOURS).plusMinutes(5).minusHours(1);
        for (Server server : Singleton.getInstance().getServers()) {
            LocalDateTime t0 = LocalDateTime.now();
            LogDAO.computeHourStat(server.getName(), hour);
            log.info("end of hourly stat computation for {} at {} in {}s", server.getName(), hour, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        }
        return hour;
    }

    @Override
    public String toString() {
        if (hour == null)
            return "hourly stat computation task in background";
        else
            return "hourly stat computation task for " + hour;
    }

    @Override
    public long computeInitialDelay() {
        // on démarre à l'heure + 5 min
        LocalDateTime nextHour = LocalDateTime.now().truncatedTo(ChronoUnit.HOURS).plusHours(1);
        return ChronoUnit.SECONDS.between(LocalDateTime.now(), nextHour.plusMinutes(5));
    }

    @Override
    public long getPeriod() {
        return 60 * 60;
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }
}
