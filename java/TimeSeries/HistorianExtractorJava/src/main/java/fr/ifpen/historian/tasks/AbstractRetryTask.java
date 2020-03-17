package fr.ifpen.historian.tasks;

import fr.ifpen.historian.ShutdownExecutor;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

/**
 * Created by IFPEN on 20/02/2019.
 */
public abstract class AbstractRetryTask extends AbstractTask<Integer> implements Stoppable {
    protected Logger log = LoggerFactory.getLogger(AbstractRetryTask.class);

    protected ExecutorService executor;
    protected Server server;
    protected LocalDateTime start;
    protected LocalDateTime end;
    protected int timeOut;
    protected boolean force;

    protected AbstractRetryTask(Server server, LocalDateTime start, LocalDateTime end, boolean force, int poolSize, int timeOut) {
        super();
        this.server = server;
        this.start = start;
        this.end = end;
        this.force = force;
        this.timeOut = timeOut;
        this.executor = Executors.newWorkStealingPool(poolSize);
        Runtime.getRuntime().addShutdownHook(new ShutdownExecutor(this));
    }

    protected abstract List<Callable<LocalDateTime>> getTasks();

    @Override
    public Integer runTask() throws InterruptedException {
        // taches de "retry" (extraction des données ou transfert de fichiers)
        List<Callable<LocalDateTime>> tasks = getTasks();
        if (tasks.isEmpty()) return 0;
        log.debug("{} tasks(s) will be launched", tasks.size());
        List<LocalDateTime> extractionTimes = executor.invokeAll(tasks)
                .stream()
                .map(future -> {
                    try {
                        return future.get(timeOut, TimeUnit.SECONDS);
                    } catch (Exception e) {
                        throw new HistorianExtractorException(e);
                    }
                })
                .filter(Objects::nonNull)
                .collect(Collectors.toList());
        log.info("{} tasks(s) have been treated", extractionTimes.size());
        // liste des heures traitées
        Set<LocalDateTime> hours = extractionTimes
                .stream()
                .map(hour -> hour.truncatedTo(ChronoUnit.HOURS))
                .collect(Collectors.toSet());
        // taches de stat horaires
        hours.stream().forEach(h -> LogDAO.computeHourStat(server.getName(), h));
        log.info("{} hour(s) stats have been computed", hours.size());
        Set<LocalDate> days = hours
                .stream()
                .map(hour -> hour.truncatedTo(ChronoUnit.DAYS).toLocalDate())
                .collect(Collectors.toSet());
        days.stream().forEach(d -> LogDAO.computeDayStat(server.getName(), d));
        log.info("{} day(s) stats have been computed", days.size());
        return extractionTimes.size();
    }

    @Override
    public void postRunTask() {
        // on doit arrêter l'exécutor, sinon la tache ne se finit jamais !
        stop();
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }

    @Override
    public void stop() {
        executor.shutdown();
        try {
            if (!executor.awaitTermination(timeOut, TimeUnit.SECONDS)) {
                executor.shutdownNow();
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
        }
    }
}
