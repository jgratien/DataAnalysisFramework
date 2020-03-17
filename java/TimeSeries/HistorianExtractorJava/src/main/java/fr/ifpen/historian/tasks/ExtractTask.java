package fr.ifpen.historian.tasks;

import com.google.common.collect.Lists;
import fr.ifpen.historian.config.Historian;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.utils.DateUtils;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;

public class ExtractTask extends AbstractTask<LocalDateTime> {
    protected Logger log = LoggerFactory.getLogger(ExtractTask.class);

    private Server server;
    private Report report;
    private LocalDateTime dateTime;
    private Integer timeOutExtract;
    private Integer extractionInterval;
    private Path dataDirectory;
    private ExtractMode mode;

    public ExtractTask(Server server, LocalDateTime dateTime, ExtractMode mode) {
        super();
        this.dateTime = dateTime;
        this.server = server;
        this.extractionInterval = Singleton.getInstance().getConfiguration().getExtractionInterval();
        this.timeOutExtract = Singleton.getInstance().getConfiguration().getHistorian().getBatchExtraction().getTimeOutExtract();
        this.dataDirectory = Singleton.getInstance().getConfiguration().dataDirectoryAsPath();
        this.mode = mode;
        log.debug("new {}", toString());
    }

    public ExtractTask(Server server) {
        this(server, null, ExtractMode.DAEMON);
    }

    public Report getReport() {
        return report;
    }

    @Override
    public LocalDateTime runTask() {
        LocalDateTime t0 = LocalDateTime.now();
        // initialize and check (date time, file, report)
        if (!initRun()) return null;
        // execute batch program
        boolean result = false;
        long duration = extractionInterval + 1;
        try {
            // compute batch command
            List<String> command = batchCommand();
            // run batch or simulate
            result = debug ? runDebug() : runBatch(command);
            // write report in DB
            writeExtractionLog(result);
            // manage number of tries
            manageTries(result);
            // send result file via FTP
            copyFile();
            duration = ChronoUnit.SECONDS.between(t0, LocalDateTime.now());
            if (result && duration > extractionInterval) {
                log.warn("{} take {} s, which is more than expected delay {} s", toString(), duration, extractionInterval);
            }
            log.info("{} completed in {} s with status {}", toString(), duration, result ? "OK" : "ERROR");
            return dateTime;
        } catch (IOException | InterruptedException e) {
            throw new HistorianExtractorException("unsuccessful " + toString() + " : " + e.getMessage());
        } finally {
            // en mode daemon, on renseigne si le serveur est accessible (s'il a bien répondu dans un délai raisonnable)
            if (mode == ExtractMode.DAEMON) {
                server.getHealth().set(result && duration <= extractionInterval);
            }
        }
    }

    private boolean initRun() {
        if (mode == ExtractMode.DAEMON) {
            // on traite l'intervalle précédent (il faut que les données soient disponibles dans Historian)
            LocalDateTime previousDateTime = DateUtils.previousExtractionDateTime();
            if (previousDateTime.equals(dateTime)) {
                return false;
            }
            dateTime = previousDateTime;
        }
        report = new Report(server.getName(), dateTime);
        // delete previous data
        deletePreviousDataFile();
        // return go !
        return true;
    }

    private List<String> batchCommand() {
        Historian historianConfig = Singleton.getInstance().getConfiguration().getHistorian();
        // command with args
        List<String> command = Lists.newArrayList(historianConfig.getBatchExtraction().programAsPath().toString(),
                "-s", server.getName(),
                "-t", DateTimeFormatter.ISO_LOCAL_DATE_TIME.format(dateTime),
                "-d", extractionInterval.toString(),
                "-o", dataDirectory.toString());

        if (historianConfig.getBatchExtraction().isLogFileSet()) {
            command.add("-l");
            command.add(historianConfig.getBatchExtraction().logFileAsPath().toString());
        }
        if (historianConfig.isUserSet()) {
            command.add("-u");
            command.add(historianConfig.getUserId());
        }
        if (historianConfig.isPasswordSet()) {
            command.add("-p");
            command.add(historianConfig.getPassword());
        }
        command.addAll(server.getTagsList().getBatchArguments());
        return command;
    }

    private boolean runBatch(List<String> command) throws IOException, InterruptedException {
        log.debug("running HBE with command {}", command);
        ProcessBuilder pb = new ProcessBuilder(command);
        pb.directory(dataDirectory.toFile());
        pb.redirectErrorStream(true);
        Process process = pb.start();
        BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        String line;
        while ((line = reader.readLine()) != null) {
            log.info("HBE: {}", line);
        }
        boolean result = process.waitFor(timeOutExtract, TimeUnit.SECONDS);
        if (!result) {
            //timeout - kill the process.
            log.error("{} doesn't respond in {}s, so we kill it", toString(), timeOutExtract);
            process.destroyForcibly(); // consider using destroyForcibly instead
        }
        return result && Files.exists(report.getDataFileFullPath());
    }

    private boolean runDebug() {
        // Test nb try
//        if (server.getName().contains("29")) {
//            // toutes les taches bakcground du 29 seront en erreur
//            if (mode == ExtractMode.BACKGROUND_RETRIEVE) return false;
//            // on simule une bad health toutes les 7 minutes
//            if (dateTime.getMinute() % 7 == 0) return false;
//        }
        DateTimeFormatter dtf = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
        Random random = new Random();
        int nbValues = server.getName().contains("35") ? 250 : 4500;
        List<String> values = new ArrayList<>(nbValues + 1);
        int nbTags = server.getName().contains("35") ? 2 : 10;
        // timestamp;tagname;value;quality
        // 19/12/2018 07:30:30;1C08.P1_TC01;17.791919708;100.0
        for (int i = 0; i < nbValues; i++) {
            for (int j = 0; j < nbTags; j++) {
                values.add(String.format("%s;TAG_%d_%s;%f;%f",
                        dtf.format(dateTime),
                        j, server.getName(),
                        random.nextDouble() * 50.0 + 15.0,
                        (j % 157) == 0 ? 0.0 : 100.0));
            }
        }
        // write file
        try {
            Files.write(report.getDataFileFullPath(), values, StandardOpenOption.WRITE, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            int wait = server.getName().contains("35") ?
                    (random.nextInt(3000) + 1000) :
                    (random.nextInt(8000) + 5000);
            Thread.sleep(wait);
        } catch (Exception e) {
            log.error("triple fuck {}", e.getMessage());
        }
        return true;
    }

    private void copyFile() {
        if (report.getExtractionSuccess()) {
            new FileTransfer(report).execute();
        }
    }

    private void deletePreviousDataFile() {
        // suppression fichier de resultat
        try {
            Files.deleteIfExists(report.getDataFileFullPath());
        } catch (IOException e) {
            log.error("file {} already exists and can not be deleted : {}", report.getDataFileFullPath(), e.getMessage());
            throw new HistorianExtractorException(e);
        }
    }

    private void writeExtractionLog(boolean result) {
        report.setEnd(Timestamp.valueOf(LocalDateTime.now()));
        report.setExtractionSuccess(result);
        log.debug("write report in database {}", report);
        LogDAO.saveReport(report);
    }

    private void manageTries(boolean result) {
        // update number of try (not in manual update)
        if (mode != ExtractMode.RETRY) {
            LogDAO.addTry(report);
        }
        // in case of error, we wait at least one daemon period to be sure not to
        // set tries at max in background (which run almost every second and does not set health)
        // when daemon extraction runs every minute (and can set health to bad)
        if (!result && mode == ExtractMode.BACKGROUND_RETRIEVE) {
            log.error("{} in error, waiting {}s to try again", toString(), getPeriod());
            try {
                // waiting for a moment to limit number of preceding log
                Thread.sleep(TimeUnit.MILLISECONDS.convert(getPeriod(), getTimeUnit()));
            } catch (InterruptedException e) {
                log.error("{} wait to recover good health has been interrupted, reason {}", toString(), e.getMessage());
            }
        }
    }

    @Override
    public String toString() {
        switch (mode) {
            case DAEMON:
                return "extraction data task in background for server " + server.getName();
            case BACKGROUND_RETRIEVE:
                return "automatic retrieve data task in background for server " + server.getName() + " at " + dateTime;
            case RETRY:
                return "manual retrieve data task for server " + server.getName() + " at " + dateTime;
        }
        return "extraction data task for server " + server.getName();
    }

    @Override
    public long computeInitialDelay() {
        LocalDateTime nextExtraction = DateUtils.nextExtractionDateTime().plusSeconds(Singleton.getInstance().getConfiguration().getExtractionRunDelay());
        return ChronoUnit.SECONDS.between(LocalDateTime.now(), nextExtraction);
    }

    @Override
    public long getPeriod() {
        return Singleton.getInstance().getConfiguration().getExtractionInterval();
    }

    @Override
    public TimeUnit getTimeUnit() {
        return TimeUnit.SECONDS;
    }

    public enum ExtractMode {DAEMON, BACKGROUND_RETRIEVE, RETRY}
}
