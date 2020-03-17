package fr.ifpen.historian;

import com.google.common.base.Strings;
import com.google.common.collect.Lists;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.DataSource;
import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.tasks.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class Service implements Stoppable {
    private static final Logger log = LoggerFactory.getLogger(Service.class);
    private static final DateTimeFormatter DATETIME_ARGS_FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");

    private ScheduledExecutorService executor;
    private ServiceMode mode;
    private String server;
    private LocalDateTime start;
    private LocalDateTime end;
    private Boolean force = Boolean.FALSE;

    public Service(Application application) {
        mode = application.getMode();
        if (!Strings.isNullOrEmpty(application.getServer())) server = application.getServer();
        if (application.getForce() != null) force = application.getForce();
        if (!Strings.isNullOrEmpty(application.getStart())) {
            try {
                start = LocalDateTime.parse(application.getStart(), DATETIME_ARGS_FMT);
            } catch (DateTimeParseException e) {
                log.error("invalid start argument \"{}\", expected format: yyyy-MM-dd HH:mm", application.getStart());
            }
        }
        if (!Strings.isNullOrEmpty(application.getEnd())) {
            try {
                end = LocalDateTime.parse(application.getEnd(), DATETIME_ARGS_FMT);
            } catch (DateTimeParseException e) {
                log.error("invalid end argument \"{}\", expected format: yyyy-MM-dd HH:mm", application.getEnd());
            }
        }
    }

    public ServiceMode getMode() {
        return mode;
    }

    public String getServer() {
        return server;
    }

    public LocalDateTime getStart() {
        return start;
    }

    public LocalDateTime getEnd() {
        return end;
    }

    public Boolean getForce() {
        return force;
    }

    public boolean check() {
        boolean result = true;
        if (server != null) {
            if (mode == ServiceMode.DAEMON || mode == ServiceMode.CONSOLE) {
                log.error("setting server value has no meaning in \"{}\" mode", mode);
                result = false;
            } else {
                if (!Singleton.getInstance().serverExists(server)) {
                    log.error("server \"{}\" is not a valid Historian server (check \"historian.servers\" list in configuration)", server);
                    result = false;
                }
            }
        }

        if (start != null) {
            if (mode == ServiceMode.RETRIEVE && start.toLocalDate().isBefore(Singleton.getInstance().getConfiguration().getRetentionPeriods().lastDbDate())) {
                log.error("start date \"{}\" too old, first date allowed is {} (depends on \"retentionPeriods.db\" parameter)", start, Singleton.getInstance().getConfiguration().getRetentionPeriods().lastDbDate());
                result = false;
            } else if (mode == ServiceMode.FILE_TRANSFER && start.toLocalDate().isBefore(Singleton.getInstance().getConfiguration().getRetentionPeriods().lastFilesDate())) {
                log.error("start date \"{}\" too old, first date allowed is {} (depends on \"retentionPeriods.files\" parameter)", start, Singleton.getInstance().getConfiguration().getRetentionPeriods().lastFilesDate());
                result = false;
            }
        } else if (mode == ServiceMode.RETRIEVE || mode == ServiceMode.FILE_TRANSFER) {
            log.error("start argument is mandatory in \"{}\" mode", mode);
            result = false;
        }
        if (end != null) {
            if (start != null) {
                if (end.isBefore(start)) {
                    log.error("end argument \"{}\" must be posterior to start argument \"{}\"", end, start);
                    result = false;
                }
            }
        } else if (mode == ServiceMode.RETRIEVE || mode == ServiceMode.FILE_TRANSFER) {
            log.error("end argument is mandatory in \"{}\" mode", mode);
            result = false;
        }
        if (mode == ServiceMode.FILE_TRANSFER && !Singleton.getInstance().getConfiguration().isFtpEnabled()) {
            log.error("FTP is not active in configuration, \"{}\" mode is not available", mode);
            result = false;
        }
        return result;
    }

    public void execute() {
        // ----------------------------------------------------------------
        // Initialize datasource (h2 db connections)
        DataSource.getInstance().initialize(mode == ServiceMode.DAEMON);
        // execution mode
        switch (mode) {
            case DAEMON:
                daemon();
                break;
            case RETRIEVE:
                retrieve();
                break;
            case FILE_TRANSFER:
                transferFiles();
                break;
            case CONSOLE:
                startConsole();
                break;
        }
    }

    @Override
    public void stop() {
        if (executor == null) return;
        executor.shutdown();
        try {
            if (!executor.awaitTermination(Singleton.getInstance().getConfiguration().getHistorian().getBatchExtraction().getTimeOutExtract(), TimeUnit.SECONDS)) {
                executor.shutdownNow();
                log.warn("tasks have been shutdown violently, because they were not responding to stop command");
            }
        } catch (InterruptedException e) {
            executor.shutdownNow();
            log.error("tasks have been shutdown violently, because they were not responding to stop command and some have thrown exception: {}", e.getMessage());
        } finally {
            DataSource.getInstance().close();
            executor = null;
        }
    }

    private void daemon() {
        // stats and clean tasks are always presents
        List<Task> tasks = Lists.newArrayList(new DailyStatTask(), new HourlyStatTask(), new CleanTask());
        // ------- regular Historian data extraction tasks
        for (Server server : Singleton.getInstance().getServers()) {
            tasks.add(new ExtractTask(server));
        }
        // ------- automatics retrieve tasks
        if (Singleton.getInstance().getConfiguration().getAutomaticDataRetrieveDelay() > 0) {
            for (Server server : Singleton.getInstance().getServers()) {
                tasks.add(new BackgroundRetrieveTask(server));
            }
        }
        if (Singleton.getInstance().getConfiguration().getAutomaticFileTransferDelay() > 0) {
            for (Server server : Singleton.getInstance().getServers()) {
                tasks.add(new BackgroundFileTransferTask(server));
            }
        }

        // ------- Create ScheduledExecutor
        executor = Executors.newScheduledThreadPool(tasks.size());
        Runtime.getRuntime().addShutdownHook(new ShutdownExecutor(this));
        log.info("starting Historian Extractor in daemon mode");
        for (Task task : tasks) {
            executor.scheduleAtFixedRate(task, task.computeInitialDelay(), task.getPeriod(), task.getTimeUnit());
        }
    }

    private void retrieve() {
        try {
            if (server == null) {
                for (Server server : Singleton.getInstance().getServers()) {
                    new RetryExtractTask(server, start, end, force).run();
                }
            } else {
                new RetryExtractTask(Singleton.getInstance().getServer(server), start, end, force).run();
            }
        } catch (Exception e) {
            log.error("error met when retrieving data: {}", e.getMessage());
        } finally {
            DataSource.getInstance().close();
        }
    }

    private void transferFiles() {
        try {
            if (server == null) {
                for (Server server : Singleton.getInstance().getServers()) {
                    new RetryFileTransferTask(server, start, end, force).run();
                }
            } else {
                new RetryFileTransferTask(Singleton.getInstance().getServer(server), start, end, force).run();
            }
        } catch (Exception e) {
            log.error("error met when transferring files: {}", e.getMessage());
        } finally {
            DataSource.getInstance().close();
        }
    }

    private void startConsole() {
        try (Connection conn = DataSource.getInstance().getConnection()) {
            org.h2.tools.Server.startWebServer(conn);
        } catch (Exception e) {
            log.error("launching database console error: {}", e.getMessage());
        }
        DataSource.getInstance().close();
    }

    @Override
    public String toString() {
        return "Service{" +
                "mode=" + mode +
                ", server='" + server + '\'' +
                ", start=" + start +
                ", end=" + end +
                ", force=" + force +
                '}';
    }
}
