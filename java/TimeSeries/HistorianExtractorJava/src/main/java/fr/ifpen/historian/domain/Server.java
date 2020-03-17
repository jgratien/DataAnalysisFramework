package fr.ifpen.historian.domain;

import fr.ifpen.historian.config.RetentionPeriods;
import fr.ifpen.historian.config.ServerConfig;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.TreeSet;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;

public class Server {
    private Logger log = LoggerFactory.getLogger(Server.class);

    private String name;
    private ServerConfig config;
    private TagsList tagsList;
    private int extractionInterval;
    private int maxRetrieveRequests;
    private int maxExtractionRetry;
    private RetentionPeriods retentionPeriods;
    private AtomicBoolean health;

    public Server(ServerConfig config) {
        this.name = config.getName();
        this.config = config;
        this.tagsList = config.createTagsList();
        this.extractionInterval = Singleton.getInstance().getConfiguration().getExtractionInterval();
        this.maxRetrieveRequests = Singleton.getInstance().getConfiguration().getMaxRetrieveRequests();
        this.maxExtractionRetry = Singleton.getInstance().getConfiguration().getMaxExtractionRetry();
        this.retentionPeriods = Singleton.getInstance().getConfiguration().getRetentionPeriods();
        this.health = new AtomicBoolean(false);
    }

    public String getName() {
        return name;
    }

    public TagsList getTagsList() {
        return tagsList;
    }

    public ServerConfig getConfig() {
        return config;
    }

    public AtomicBoolean getHealth() {
        return health;
    }

    /**
     * Method to determine date/time to be extracted in retrieve mode
     *
     * @param start : start of range (included)
     * @param end   : end of range (excluded)
     * @param force : if true all extraction are made again, otherwise only missing ones
     * @return List of date/time to run extraction task on
     */
    public Set<LocalDateTime> retrieveDateTimes(LocalDateTime start, LocalDateTime end, boolean force) {
        // liste des extractions à rejouer !
        Set<LocalDateTime> result = new TreeSet<>();
        for (LocalDateTime dateTime = start; dateTime.isBefore(end); dateTime = dateTime.plusSeconds(extractionInterval)) {
            result.add(dateTime);
        }
        if (!force) {
            List<LocalDateTime> treated = LogDAO.listReports(name, start, end)
                    .stream()
                    .filter(Report::getExtractionSuccess)
                    .map(Report::getDateTime)
                    .map(Timestamp::toLocalDateTime)
                    .collect(Collectors.toList());
            log.debug("successful extractions date/times of the period {} / {} : {}", start, end, treated);
            result.removeAll(treated);
        }
        if (result.isEmpty()) {
            log.debug("no extraction date/time to retrieve, every data have been extracted and transferred");
        } else if (result.size() > maxRetrieveRequests) {
            log.warn("we find {} extractions date/times to make in the interval {} - {}, which is too important. We truncate the list at {} requests only",
                    result.size(), start, end, maxRetrieveRequests);
            result = result.stream().limit(maxRetrieveRequests).collect(Collectors.toSet());
        }
        log.debug("date/time to retrieve {}", result);
        return result;
    }

    /**
     * Computing first missing extraction
     * get first non completed hour (with error) and in it find first lack or error
     * if no hour in DB, returns null. But regular clean task will generate hour stats automatically
     *
     * @return date/time to play with or null if all data have been extracted
     */
    public LocalDateTime firstBadRetrieveDateTime() {
        LocalDateTime ceiling = LocalDateTime.now().minusMinutes(90);
        int nbTries = 0;
        while (nbTries < 3) {
            List<LogStat> badHours = LogDAO.listBadHourStat(name, ceiling, 1);
            if (badHours == null || badHours.isEmpty()) {
                log.debug("no stat hour with any error in db for server {} before {}", name, ceiling);
                return null;
            }
            LocalDateTime hour = badHours.get(0).getHour().toLocalDateTime();
            // on garde les rapports de l'heure qui sont OK pour les retirer de la liste des trous
            List<Report> reports = LogDAO.listReports(name, hour, hour.plusHours(1));
            List<LocalDateTime> validDateTimes = reports
                    .stream()
                    .filter(Report::getExtractionSuccess)
                    .map(Report::getDateTime)
                    .map(Timestamp::toLocalDateTime)
                    .collect(Collectors.toList());
            log.debug("{} reports with successful extraction for server {} at {}", validDateTimes.size(), name, hour);
            // on récupère les rapports qui ont déjà été lancés "maxExtractionRetry" foits pour les retirer de la liste des trous
            List<LocalDateTime> alreadyTriedDateTimes = reports
                    .stream()
                    .filter(r -> r.isAbandoned(maxExtractionRetry))
                    .map(Report::getDateTime)
                    .map(Timestamp::toLocalDateTime)
                    .collect(Collectors.toList());
            log.debug("{} reports in error but already tried to much for server {} at {}", alreadyTriedDateTimes.size(), name, hour);
            // find first extraction date/time in error (missing from validDateTimes
            for (LocalDateTime h = hour.plusHours(1).minusSeconds(extractionInterval); h.isAfter(hour.minusSeconds(1)); h = h.minusSeconds(extractionInterval)) {
                if (!validDateTimes.contains(h) && !alreadyTriedDateTimes.contains(h)) return h;
            }
            // if we arrive here, it means that hour stat is invalid (because all reports of the hour are valid)
            LogDAO.computeHourStat(name, hour);
            nbTries++;
            log.debug("incoherent stat for server {} at {} have been recomputed, {} try to find another date/time in error", name, hour, nbTries);
        }
        log.warn("many stats with incoherence between hour and reports for server {}, check stat computation", name);
        return null;
    }

    public Report firstBadFileTransferReport() {
        List<Report> badTransfers = LogDAO.listBadFileTransferReports(name, retentionPeriods.lastFilesDate(), 1);
        return (badTransfers == null || badTransfers.isEmpty()) ? null : badTransfers.get(0);
    }

    public int maxRetrieveRange() {
        return maxRetrieveRequests * extractionInterval;
    }

    @Override
    public String toString() {
        return "HistorianServer{" +
                "name='" + name + '\'' +
                ", tagsList=" + tagsList +
                '}';
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Server server = (Server) o;
        return Objects.equals(name, server.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name);
    }
}
