package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Server;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * Tache récupération des données ratées dans le passé (pour causes diverses et variées)
 * <p>
 * Created by IFPEN on 20/02/2019.
 */
public class BackgroundRetrieveTask extends AbstractTask<LocalDateTime> {
    protected Logger log = LoggerFactory.getLogger(BackgroundRetrieveTask.class);

    private Server server;

    public BackgroundRetrieveTask(Server server) {
        super();
        this.server = server;
        log.debug("new {}", toString());
    }

    @Override
    public LocalDateTime runTask() {
        if (!server.getHealth().get()) {
            log.debug("server {} in bad health (previous extraction was in error)... background retrieve task cancelled, sleeping {}s", server.getName(), getPeriod());
            try {
                // waiting for a moment to limit number of preceding log
                Thread.sleep(TimeUnit.MILLISECONDS.convert(getPeriod(), getTimeUnit()));
            } catch (InterruptedException e) {
                log.error("background task wait for server {} to recover good health has been interrupted, reason {}", server.getName(), e.getMessage());
            }
            return null;
        }
        LocalDateTime firstError = server.firstBadRetrieveDateTime();
        if (firstError == null) {
            log.debug("no extraction missing for server {}... background retrieve task cancelled", server.getName());
            return null;
        }
        LocalDateTime extractionDateTime = new ExtractTask(server, firstError, ExtractTask.ExtractMode.BACKGROUND_RETRIEVE).runTask();
        LogDAO.computeHourStat(server.getName(), extractionDateTime);
        LogDAO.computeDayStat(server.getName(), extractionDateTime.toLocalDate());
        return extractionDateTime;
    }

    @Override
    public String toString() {
        return "retrieve data task in background for server " + server.getName();
    }

    @Override
    public long computeInitialDelay() {
        // on fait démarrer la tache 3 min après le service
        return 3 * 60;
    }

    @Override
    public long getPeriod() {
        return Singleton.getInstance().getConfiguration().getAutomaticDataRetrieveDelay();
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }
}
