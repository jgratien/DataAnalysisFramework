package fr.ifpen.historian.config;

import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

public class Configuration {
    Logger log = LoggerFactory.getLogger(Configuration.class);

    private String welcomeMessage;
    private String dataDirectory;
    private Path dataDirectoryPath;
    private Integer extractionInterval;
    private Integer extractionRunDelay;
    private Integer maxExtractionRetry;
    private Integer automaticDataRetrieveDelay;
    private Integer automaticFileTransferDelay;
    private Integer maxRetrieveRequests;
    private Integer parallelRetrieveRequests;
    private Database database = new Database();
    private Historian historian = new Historian();
    private List<Ftp> ftps = new ArrayList<>();
    private Boolean debug;
    private Boolean killOnCOMException;
    private RetentionPeriods retentionPeriods;

    public Configuration() {
    }

    public String getWelcomeMessage() {
        return welcomeMessage;
    }

    public void setWelcomeMessage(String welcomeMessage) {
        this.welcomeMessage = welcomeMessage;
    }

    public String getDataDirectory() {
        return dataDirectory;
    }

    public void setDataDirectory(String dataDirectory) {
        this.dataDirectory = dataDirectory;
    }

    public Path dataDirectoryAsPath() {
        if (dataDirectoryPath == null) {
            dataDirectoryPath = Paths.get(this.dataDirectory);
            if (!Files.exists(dataDirectoryPath)) {
                try {
                    Files.createDirectory(dataDirectoryPath);
                } catch (IOException e) {
                    throw new HistorianExtractorException(e);
                }
            } else if (!Files.isDirectory(dataDirectoryPath)) {
                throw new HistorianExtractorException("path for data files " + this.dataDirectory + " is not a valid directory");
            }
        }
        return dataDirectoryPath;
    }

    public Integer getExtractionInterval() {
        return extractionInterval;
    }

    public void setExtractionInterval(Integer extractionInterval) {
        if (extractionInterval > 60 || extractionInterval < 10) {
            throw new HistorianExtractorException("extraction interval must be between 10 and 60 s");
        } else if (60 % extractionInterval != 0) {
            throw new HistorianExtractorException("60 must be a multiple of extraction interval (30, 20, 15, 12, 10)");
        }
        this.extractionInterval = extractionInterval;
    }

    public Integer getExtractionRunDelay() {
        return extractionRunDelay;
    }

    public void setExtractionRunDelay(Integer extractionRunDelay) {
        this.extractionRunDelay = extractionRunDelay;
    }

    public int nbExtractionsPerMinute() {
        return 60 / extractionInterval;
    }

    public int nbExtractionsPerHour() {
        return 60 * nbExtractionsPerMinute();
    }

    public Integer getMaxExtractionRetry() {
        return maxExtractionRetry;
    }

    public void setMaxExtractionRetry(Integer maxExtractionRetry) {
        this.maxExtractionRetry = maxExtractionRetry;
    }

    public Integer getAutomaticDataRetrieveDelay() {
        return automaticDataRetrieveDelay;
    }

    public void setAutomaticDataRetrieveDelay(Integer automaticDataRetrieveDelay) {
        this.automaticDataRetrieveDelay = automaticDataRetrieveDelay;
    }

    public Integer getAutomaticFileTransferDelay() {
        if (automaticFileTransferDelay > 0 && !isFtpEnabled()) {
            log.warn("incoherent configuration, automatic file transfer is activated and FTP is disabled. Check your configuration file");
            log.warn("disabling automatic file transfer");
            automaticFileTransferDelay = 0;
        }
        return automaticFileTransferDelay;
    }

    public void setAutomaticFileTransferDelay(Integer automaticFileTransferDelay) {
        this.automaticFileTransferDelay = automaticFileTransferDelay;
    }

    public Integer getMaxRetrieveRequests() {
        return maxRetrieveRequests;
    }

    public void setMaxRetrieveRequests(Integer maxRetrieveRequests) {
        this.maxRetrieveRequests = maxRetrieveRequests;
    }

    public Integer getParallelRetrieveRequests() {
        return parallelRetrieveRequests;
    }

    public void setParallelRetrieveRequests(Integer parallelRetrieveRequests) {
        this.parallelRetrieveRequests = parallelRetrieveRequests;
    }

    public Database getDatabase() {
        return database;
    }

    public void setDatabase(Database database) {
        this.database = database;
    }

    public Historian getHistorian() {
        return historian;
    }

    public void setHistorian(Historian historian) {
        this.historian = historian;
    }

    public List<Ftp> getFtps() {
        return ftps;
    }

    public void setFtps(List<Ftp> ftps) {
        this.ftps = ftps;
    }

    public List<Ftp> activeFtps() {
        return ftps.stream().filter(Ftp::getEnabled).collect(Collectors.toList());
    }

    public boolean isFtpEnabled() {
        return ftps.stream().anyMatch(Ftp::getEnabled);
    }

    public Boolean getKillOnCOMException() {
        return killOnCOMException;
    }

    public void setKillOnCOMException(Boolean killOnCOMException) {
        this.killOnCOMException = killOnCOMException;
    }

    public Boolean getDebug() {
        return debug;
    }

    public void setDebug(Boolean debug) {
        this.debug = debug;
    }

    public RetentionPeriods getRetentionPeriods() {
        return retentionPeriods;
    }

    public void setRetentionPeriods(RetentionPeriods retentionPeriods) {
        this.retentionPeriods = retentionPeriods;
    }

    @Override
    public String toString() {
        return "Configuration{" +
                "welcomeMessage='" + welcomeMessage + '\'' +
                ", dataDirectory='" + dataDirectory + '\'' +
                ", extractionInterval=" + extractionInterval +
                ", extractionRunDelay=" + extractionRunDelay +
                ", dataDirectoryPath=" + dataDirectoryPath +
                ", automaticDataRetrieveDelay=" + automaticDataRetrieveDelay +
                ", automaticFileTransferDelay=" + automaticFileTransferDelay +
                ", maxRetrieveRequests=" + maxRetrieveRequests +
                ", parallelRetrieveRequests=" + parallelRetrieveRequests +
                ", database=" + database +
                ", historian=" + historian +
                ", ftps=" + ftps +
                ", killOnCOMException=" + killOnCOMException +
                ", debug=" + debug +
                ", retentionPeriods=" + retentionPeriods +
                '}';
    }
}
