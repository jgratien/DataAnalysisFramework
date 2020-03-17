package fr.ifpen.historian.domain;

import fr.ifpen.historian.config.Singleton;

import java.math.BigDecimal;
import java.nio.file.Path;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public class Report {
    private static final DateTimeFormatter FILE_DATE_TIME_FMT = DateTimeFormatter.ofPattern("yyyyMMddHHmmss");

    private String server;
    private Timestamp dateTime;
    private Timestamp start;
    private Timestamp end;
    private BigDecimal duration;
    private Integer nbTry;
    private Boolean extractionSuccess;
    private Boolean fileTransferSuccess;
    private String dataFile;

    public Report() {
    }

    public Report(String server, LocalDateTime dateTime) {
        this.server = server;
        this.dateTime = Timestamp.valueOf(dateTime);
        this.start = Timestamp.valueOf(LocalDateTime.now());
        this.extractionSuccess = Boolean.FALSE;
        this.fileTransferSuccess = Boolean.FALSE;
        this.nbTry = 0;
        this.dataFile = String.format("dataHistorian-%s-%s.csv", server, FILE_DATE_TIME_FMT.format(dateTime));
    }

    public String getServer() {
        return server;
    }

    public void setServer(String server) {
        this.server = server;
    }

    public Timestamp getDateTime() {
        return dateTime;
    }

    public void setDateTime(Timestamp dateTime) {
        this.dateTime = dateTime;
    }

    public Timestamp getStart() {
        return start;
    }

    public void setStart(Timestamp start) {
        this.start = start;
    }

    public Timestamp getEnd() {
        return end;
    }

    public void setEnd(Timestamp end) {
        this.end = end;
        if (this.end != null && this.start != null) {
            this.duration = BigDecimal.valueOf(ChronoUnit.SECONDS.between(this.start.toLocalDateTime(), this.end.toLocalDateTime()));
        }
    }

    public BigDecimal getDuration() {
        return duration;
    }

    public void setDuration(BigDecimal duration) {
        this.duration = duration;
    }

    public Integer getNbTry() {
        return nbTry;
    }

    public void setNbTry(Integer nbTry) {
        this.nbTry = nbTry;
    }

    public Boolean getExtractionSuccess() {
        return extractionSuccess;
    }

    public void setExtractionSuccess(Boolean extractionSuccess) {
        this.extractionSuccess = extractionSuccess;
    }

    public Boolean getFileTransferSuccess() {
        return fileTransferSuccess;
    }

    public void setFileTransferSuccess(Boolean fileTransferSuccess) {
        this.fileTransferSuccess = fileTransferSuccess;
    }

    public String getDataFile() {
        return dataFile;
    }

    public void setDataFile(String dataFile) {
        this.dataFile = dataFile;
    }

    public Path getDataFileFullPath() {
        Path localDir = Singleton.getInstance().getConfiguration().dataDirectoryAsPath();
        return localDir.resolve(dataFile);
    }

    public boolean isAbandoned(int maxTries) {
        return nbTry >= maxTries;
    }

    public List<String> getStatusMessages() {
        List<String> msgs = new ArrayList<>();
        msgs.add("   - last date/time treated : " + dateTime.toLocalDateTime());
        msgs.add("   - extraction success : " + extractionSuccess);
        msgs.add("   - in " + nbTry + (nbTry > 1 ? " tries" : " try"));
        msgs.add("   - data file : " + getDataFileFullPath());
        msgs.add("   - file transfer success : " + fileTransferSuccess);
        msgs.add("   - started at : " + start.toLocalDateTime());
        msgs.add("   - ended at : " + (end == null ? "<work in progress>" : end.toLocalDateTime()));
        msgs.add("   - duration (s) : " + (duration == null ? "-" : duration));
        msgs.add("");
        return msgs;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Report)) return false;
        Report that = (Report) o;
        return Objects.equals(server, that.server) &&
                Objects.equals(start, that.start);
    }

    @Override
    public int hashCode() {
        return Objects.hash(server, start);
    }

    @Override
    public String toString() {
        return "Report{" +
                "server='" + server + '\'' +
                ", dateTime=" + dateTime +
                ", start=" + start +
                ", end=" + end +
                ", duration=" + duration +
                ", extractionSuccess=" + extractionSuccess +
                ", fileTransferSuccess=" + fileTransferSuccess +
                ", dataFile='" + dataFile + '\'' +
                '}';
    }
}
