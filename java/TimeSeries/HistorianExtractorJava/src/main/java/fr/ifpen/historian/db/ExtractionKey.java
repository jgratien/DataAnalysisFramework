package fr.ifpen.historian.db;

import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.Objects;

/**
 * Created by IFPEN on 22/02/2019.
 */
public class ExtractionKey {
    private String server;
    private Timestamp dateTime;

    public ExtractionKey() {
    }

    public ExtractionKey(String server, LocalDateTime dateTime) {
        this.server = server;
        this.dateTime = Timestamp.valueOf(dateTime);
    }

    public ExtractionKey(String server, Timestamp timestamp) {
        this.server = server;
        this.dateTime = timestamp;
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

    @Override
    public String toString() {
        return "ExtractionKey{" +
                "server='" + server + '\'' +
                ", dateTime=" + dateTime +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        ExtractionKey that = (ExtractionKey) o;
        return Objects.equals(server, that.server) &&
                Objects.equals(dateTime, that.dateTime);
    }

    @Override
    public int hashCode() {
        return Objects.hash(server, dateTime);
    }
}
