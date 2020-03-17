package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.domain.Server;

import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.stream.Collectors;

/**
 * Created by IFPEN on 20/02/2019.
 */
public class RetryExtractTask extends AbstractRetryTask {

    public RetryExtractTask(Server server, LocalDateTime start, LocalDateTime end, Boolean force) {
        super(server, start, end, force, Singleton.getInstance().getConfiguration().getParallelRetrieveRequests(), 300);
        log.debug("new {}", toString());
    }

    @Override
    public List<Callable<LocalDateTime>> getTasks() {
        // liste des extractions à rejouer !
        return server.retrieveDateTimes(start, end, force)
                .stream()
                .map(dt -> new ExtractTask(server, dt, ExtractTask.ExtractMode.RETRY))
                .collect(Collectors.toList());
    }

    @Override
    public String toString() {
        String name = "retrieve data task";
        if (server != null) name += " for " + server.getName();
        if (start != null) name += " from " + start;
        if (end != null) name += " to " + end;
        return name;
    }

    @Override
    public long computeInitialDelay() {
        // on fait démarrer la tache tout de suite (5s)
        return 5;
    }

    @Override
    public long getPeriod() {
        return Singleton.getInstance().getConfiguration().getAutomaticDataRetrieveDelay();
    }
}
