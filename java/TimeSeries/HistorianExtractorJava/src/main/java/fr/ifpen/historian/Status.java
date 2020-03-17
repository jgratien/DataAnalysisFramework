package fr.ifpen.historian;

import fr.ifpen.historian.db.DataSource;
import fr.ifpen.historian.db.ExtractionKey;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.LogStat;
import fr.ifpen.historian.domain.Report;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by IFPEN on 21/03/2019.
 */
public class Status {
    private static final Logger log = LoggerFactory.getLogger(Status.class);

    private Map<String, List<String>> status = new HashMap<>();
    private int nbHours;
    private int nbDays;

    public Status(Integer nbDays, Integer nbHours) {
        this.nbDays = nbDays == null ? 3 : nbDays;
        this.nbHours = nbHours == null ? 3 : nbHours;
    }

    public void display() {
        DataSource.getInstance().initialize(false);
        List<ExtractionKey> extractions;
        try {
            extractions = LogDAO.lastExtractions();
            if (extractions.isEmpty()) {
                log.warn("no stat available in database, please wait for at least one minute to check status again");
            } else {
                // add last minute treated information for each server
                addMinuteStatus(extractions);
                // from the server list obtained gather last <nbHours> hour stat
                addHourStatus();
                // from the server list obtained gather last <nbDays> days stat
                addDayStatus();
                // display stats to the screen
                displayStatus();
            }
        } catch (Exception e) {
            log.error("impossible to get status: {}", e.getMessage());
        } finally {
            DataSource.getInstance().close();
        }
    }

    private List<String> getMessages(String server) {
        if (!status.containsKey(server)) {
            status.put(server, new ArrayList<>());
        }
        return status.get(server);
    }

    private void addMessage(String server, String message) {
        getMessages(server).add(message);
    }

    private void addMessage(String server, List<String> messages) {
        getMessages(server).addAll(messages);
    }

    private void addSectionHeader(String server, String sectionTitle) {
        addMessage(server, "____________________ " + server + " ______________________________");
        addMessage(server, sectionTitle);
        addMessage(server, "");
    }

    private void addMinuteStatus(List<ExtractionKey> extractions) {
        for (ExtractionKey mm : extractions) {
            String server = mm.getServer();
            addSectionHeader(server, "Last extraction :");
            List<Report> lastReports = LogDAO.listReports(server, mm.getDateTime().toLocalDateTime());
            if (lastReports.isEmpty()) {
                addMessage(server, "No log in database for server " + server);
                addMessage(server, "");
            } else {
                // last minute informations
                for (Report report : lastReports) {
                    addMessage(server, report.getStatusMessages());
                }
            }
        }
    }

    private void addHourStatus() {
        for (Map.Entry<String, List<String>> entry : status.entrySet()) {
            String server = entry.getKey();
            addSectionHeader(server, "Last " + (nbHours > 1 ? "hours" : "hour") + " :");
            LocalDateTime hour = LocalDateTime.now().truncatedTo(ChronoUnit.HOURS);
            List<LogStat> lastHours = LogDAO.listHourStat(server, hour, nbHours);
            if (lastHours.isEmpty()) {
                addMessage(server, "No stat for last hour " + hour + " in database for server " + server);
                addMessage(server, "");
            }
            for (LogStat stat : lastHours) {
                addMessage(server, stat.getStatusMessages());
            }
        }
    }

    private void addDayStatus() {
        for (Map.Entry<String, List<String>> entry : status.entrySet()) {
            String server = entry.getKey();
            addSectionHeader(server, "Last " + (nbDays > 1 ? "days" : "day") + " :");
            LocalDate from = LocalDate.now().minusDays(5);
            List<LogStat> lastDays = LogDAO.listDayStat(server, from, nbDays);
            if (lastDays.isEmpty()) {
                addMessage(server, "No stat between " + from + " and today in database for server " + server);
                addMessage(server, "");
            }
            for (LogStat stat : lastDays) {
                addMessage(server, stat.getStatusMessages());
            }
        }
    }

    private void displayStatus() {
        for (Map.Entry<String, List<String>> entry : status.entrySet()) {
            entry.getValue().stream().forEach(log::info);
        }
    }
}
