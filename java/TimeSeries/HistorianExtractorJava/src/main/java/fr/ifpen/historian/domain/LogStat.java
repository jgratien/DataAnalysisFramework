package fr.ifpen.historian.domain;

import fr.ifpen.historian.config.Singleton;

import java.sql.Date;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Created by IFPEN on 19/02/2019.
 */
public class LogStat {
    private String server;
    private Timestamp hour;
    private Date day;
    private Integer nbExtractionSuccess;
    private Integer nbExtractionError;
    private Integer nbExtractionMissing;
    private Integer nbFileTransferSuccess;
    private Integer nbFileTransferError;
    private Integer nbExtractionAbandoned;

    public LogStat() {
        this.nbExtractionError = 0;
        this.nbExtractionSuccess = 0;
        this.nbExtractionMissing = 0;
        this.nbFileTransferError = 0;
        this.nbFileTransferSuccess = 0;
        this.nbExtractionAbandoned = 0;
    }

    public LogStat(String server, Date day) {
        this();
        this.server = server;
        this.day = day;
    }

    public LogStat(String server, LocalDateTime hour) {
        this();
        this.server = server;
        this.hour = Timestamp.valueOf(hour);
    }

    public String getServer() {
        return server;
    }

    public void setServer(String server) {
        this.server = server;
    }

    public Timestamp getHour() {
        return hour;
    }

    public void setHour(Timestamp hour) {
        this.hour = hour;
    }

    public Date getDay() {
        return day;
    }

    public void setDay(Date day) {
        this.day = day;
    }

    public Integer getNbExtractionSuccess() {
        return nbExtractionSuccess;
    }

    public void setNbExtractionSuccess(Integer nbExtractionSuccess) {
        this.nbExtractionSuccess = nbExtractionSuccess;
    }

    public void incrementExtractionSuccess() {
        this.nbExtractionSuccess++;
    }

    public Integer getNbExtractionError() {
        return nbExtractionError;
    }

    public void setNbExtractionError(Integer nbExtractionError) {
        this.nbExtractionError = nbExtractionError;
    }

    public void incrementExtractionError() {
        this.nbExtractionError++;
    }

    public Integer getNbExtractionMissing() {
        return nbExtractionMissing;
    }

    public void setNbExtractionMissing(Integer nbExtractionMissing) {
        this.nbExtractionMissing = nbExtractionMissing;
    }

    public Integer getNbExtractionAbandoned() {
        return nbExtractionAbandoned;
    }

    public void setNbExtractionAbandoned(Integer nbExtractionAbandoned) {
        this.nbExtractionAbandoned = nbExtractionAbandoned;
    }

    public void incrementExtractionAbandoned() {
        this.nbExtractionAbandoned++;
    }

    public void computeMissing() {
        // nb extraction per hour
        int nbExtractionPerPeriod = Singleton.getInstance().getConfiguration().nbExtractionsPerHour();
        // if we treat day stat we have to multiply by 24
        if (day != null) nbExtractionPerPeriod *= 24;
        // extraction missing is the number of extraction of the period minus the extractions made (simply tried)
        nbExtractionMissing = nbExtractionPerPeriod - (nbExtractionSuccess + nbExtractionError + nbExtractionAbandoned);
    }

    public Integer getNbFileTransferSuccess() {
        return nbFileTransferSuccess;
    }

    public void setNbFileTransferSuccess(Integer nbFileTransferSuccess) {
        this.nbFileTransferSuccess = nbFileTransferSuccess;
    }

    public void incrementFileTransferSuccess() {
        this.nbFileTransferSuccess++;
    }

    public Integer getNbFileTransferError() {
        return nbFileTransferError;
    }

    public void setNbFileTransferError(Integer nbFileTransferError) {
        this.nbFileTransferError = nbFileTransferError;
    }

    public void incrementFileTransferError() {
        this.nbFileTransferError++;
    }

    public void addCounters(LogStat other) {
        this.nbExtractionSuccess += other.nbExtractionSuccess;
        this.nbExtractionError += other.nbExtractionError;
        this.nbExtractionMissing += other.nbExtractionMissing;
        this.nbExtractionAbandoned += other.nbExtractionAbandoned;
        this.nbFileTransferSuccess += other.nbFileTransferSuccess;
        this.nbFileTransferError += other.nbFileTransferError;
    }

    public List<String> getStatusMessages() {
        List<String> msgs = new ArrayList<>();
        if (day == null) {
            msgs.add("   - hour treated : " + hour.toLocalDateTime());
        } else {
            msgs.add("   - day treated : " + day.toLocalDate());
        }
        msgs.add("   - extraction success : " + nbExtractionSuccess);
        msgs.add("   - extraction error : " + nbExtractionError);
        msgs.add("   - extraction missing : " + nbExtractionMissing);
        msgs.add("   - extraction abandoned : " + nbExtractionAbandoned);
        msgs.add("   - file transfer success : " + nbFileTransferSuccess);
        msgs.add("   - file transfer error : " + nbFileTransferError);
        msgs.add("");
        return msgs;
    }

    @Override
    public String toString() {
        return "LogStat{" +
                "server='" + server + '\'' +
                ", hour=" + hour +
                ", day=" + day +
                ", nbExtractionSuccess=" + nbExtractionSuccess +
                ", nbExtractionError=" + nbExtractionError +
                ", nbExtractionMissing=" + nbExtractionMissing +
                ", nbExtractionAbandoned=" + nbExtractionAbandoned +
                ", nbFileTransferSuccess=" + nbFileTransferSuccess +
                ", nbFileTransferError=" + nbFileTransferError +
                '}';
    }
}
