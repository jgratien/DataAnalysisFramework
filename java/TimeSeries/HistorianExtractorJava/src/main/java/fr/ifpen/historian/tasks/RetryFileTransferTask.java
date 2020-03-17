package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Server;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.stream.Collectors;

/**
 * Created by IFPEN on 20/02/2019.
 */
public class RetryFileTransferTask extends AbstractRetryTask {

    public RetryFileTransferTask(Server server, LocalDateTime start, LocalDateTime end, Boolean force) {
        super(server, start, end, force, 1, 30);
    }

    @Override
    public List<Callable<LocalDateTime>> getTasks() {
        // transfer files
        return LogDAO.listReports(server.getName(), start, end)
                .stream()
                .filter(r -> Objects.nonNull(r.getDataFile()) && (!r.getFileTransferSuccess() || force))
                .limit(Singleton.getInstance().getConfiguration().getMaxRetrieveRequests())
                .map(FileTransfer::new)
                .map(FileTransfer::toTask)
                .collect(Collectors.toList());
    }

    @Override
    public String toString() {
        String name = "retry file transfer task";
        if (server != null) name += " for " + server.getName();
        if (start != null) name += " from " + start;
        if (end != null) name += " to " + end;
        return name;
    }

    @Override
    public long computeInitialDelay() {
        // on fait démarrer la tache tout de suite (10s)
        return 10;
    }

    @Override
    public long getPeriod() {
        return Singleton.getInstance().getConfiguration().getAutomaticFileTransferDelay();
    }
}
