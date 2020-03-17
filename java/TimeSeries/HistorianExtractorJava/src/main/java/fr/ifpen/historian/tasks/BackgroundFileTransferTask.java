package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.domain.Server;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * Tache de renvoi des fichiers non transférés dans le passé (pour causes diverses et variées)
 * <p>
 * Created by IFPEN on 20/02/2019.
 */
public class BackgroundFileTransferTask extends AbstractTask<Integer> {
    protected Logger log = LoggerFactory.getLogger(BackgroundFileTransferTask.class);

    private Server server;

    public BackgroundFileTransferTask(Server server) {
        super();
        this.server = server;
        log.debug("new {}", toString());
    }

    @Override
    public Integer runTask() throws InterruptedException {
        Report firstBadTransfer = server.firstBadFileTransferReport();
        if (firstBadTransfer == null) {
            log.debug("no file transfer missing for server {}... background file transfer task cancelled", server.getName());
            return null;
        }
        LocalDateTime transferTime = new FileTransfer(firstBadTransfer).execute();
        if (transferTime != null) {
            LogDAO.computeHourStat(server.getName(), transferTime);
            LogDAO.computeDayStat(server.getName(), transferTime.toLocalDate());
        }
        return transferTime == null ? 0 : 1;
    }

    @Override
    public String toString() {
        return "file transfer task in background for server " + server.getName();
    }

    @Override
    public long computeInitialDelay() {
        // on fait démarrer la tache 4 min après le service
        return 4 * 60;
    }

    @Override
    public long getPeriod() {
        return Singleton.getInstance().getConfiguration().getAutomaticFileTransferDelay();
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }
}
