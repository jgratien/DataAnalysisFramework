package fr.ifpen.historian.db;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.domain.LogStat;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.utils.DateUtils;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.apache.commons.dbutils.QueryRunner;
import org.apache.commons.dbutils.ResultSetHandler;
import org.apache.commons.dbutils.handlers.BeanListHandler;
import org.apache.commons.dbutils.handlers.ScalarHandler;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.Date;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;

public class LogDAO {
    /**
     * Cached scalar result set handler.
     */
    private static final ResultSetHandler<?> SCALAR_HANDLER = new ScalarHandler();
    private static Logger log = LoggerFactory.getLogger(LogDAO.class);

    public static void saveReport(Report report) {
        try (Connection conn = DataSource.getInstance().getConnection()) {
            if (count(conn, "select count(*) from log_extraction where server = ? and dateTime = ?", report.getServer(), report.getDateTime()) > 0) {
                update(conn, report);
            } else {
                insert(conn, report);
            }
        } catch (SQLException e) {
            log.error("SQL error when trying to save report {} : {} - {} [{}]", report, e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    private static long count(Connection conn, String sql, Object... params) {
        QueryRunner queryRunner = new QueryRunner();
        List result;
        try {
            result = queryRunner.execute(conn, sql, SCALAR_HANDLER, params);
        } catch (SQLException e) {
            log.error("SQL error when trying to count database rows: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
        if (result == null || result.isEmpty() || result.get(0) == null) {
            return 0;
        } else {
            Object count = result.get(0);
            if (count instanceof Long) {
                return (Long) result.get(0);
            } else if (count instanceof Integer) {
                return ((Integer) result.get(0)).longValue();
            } else {
                return Long.valueOf(count.toString());
            }
        }
    }

    private static void insert(Connection conn, Report report) {
        QueryRunner queryRunner = new QueryRunner();
        try {
            int insertedRecords = queryRunner.update(conn,
                    "insert into log_extraction(server, dateTime, start, end, duration, nbtry, dataFile, extractionSuccess, fileTransferSuccess) values (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    report.getServer(), report.getDateTime(), report.getStart(), report.getEnd(), report.getDuration(), report.getNbTry(), report.getDataFile(), report.getExtractionSuccess(), report.getFileTransferSuccess());
            log.debug("{} event inserted in db {}", insertedRecords, report);
        } catch (SQLException e) {
            log.error("SQL error when trying to insert log entry: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    private static void update(Connection conn, Report report) {
        QueryRunner queryRunner = new QueryRunner();
        try {
            // beware : no update of nbTry => to dangerous, in most cases we don't read existing report to update it
            int updatedRecords = queryRunner.update(conn,
                    "update log_extraction set start = ?, end = ?, duration = ?, dataFile = ?, extractionSuccess = ?, fileTransferSuccess = ? where server = ? and dateTime = ?",
                    report.getStart(), report.getEnd(), report.getDuration(), report.getDataFile(), report.getExtractionSuccess(), report.getFileTransferSuccess(), report.getServer(), report.getDateTime());
            log.debug("{} event updated in db {}", updatedRecords, report);
        } catch (SQLException e) {
            log.error("SQL error when trying to update log entry: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static void addTry(Report report) {
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            int updatedRecords = queryRunner.update(conn,
                    "update log_extraction set nbtry = nbtry + 1 where server = ? and dateTime = ?", report.getServer(), report.getDateTime());
            log.debug("{} report nb try updated in db {}", updatedRecords, report);
        } catch (SQLException e) {
            log.error("SQL error when trying to update report nb try : {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<ExtractionKey> lastExtractions() {
        ResultSetHandler<List<ExtractionKey>> listHandler = new BeanListHandler<>(ExtractionKey.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            return queryRunner.query(conn, "select server, max(dateTime) as dateTime from log_extraction group by server", listHandler);
        } catch (SQLException e) {
            log.error("SQL error when trying to get last log: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<Report> listReports(String server, LocalDateTime start) {
        ResultSetHandler<List<Report>> listHandler = new BeanListHandler<>(Report.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            return queryRunner.query(conn, "select * from log_extraction where server = ? and dateTime = ?",
                    listHandler, server, Timestamp.valueOf(start));
        } catch (SQLException e) {
            log.error("SQL error when trying to get reports from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<Report> listReports(String server, LocalDateTime start, LocalDateTime end) {
        ResultSetHandler<List<Report>> listHandler = new BeanListHandler<>(Report.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            return queryRunner.query(conn, "select * from log_extraction where server = ? and dateTime >= ? and dateTime < ? order by dateTime desc",
                    listHandler, server, Timestamp.valueOf(start), Timestamp.valueOf(end));
        } catch (SQLException e) {
            log.error("SQL error when trying to get logs from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<Report> listBadFileTransferReports(String server, LocalDate lastDate, int nbReports) {
        ResultSetHandler<List<Report>> listHandler = new BeanListHandler<>(Report.class);
        QueryRunner queryRunner = new QueryRunner();
        Timestamp timestamp = Timestamp.valueOf(lastDate.atStartOfDay());
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            return queryRunner.query(conn, "select top ? * from log_extraction where server = ? and dateTime >= ? and fileTransferSuccess = ? order by dateTime desc",
                    listHandler, nbReports, server, timestamp, false);
        } catch (SQLException e) {
            log.error("SQL error when trying to get bad file transfer logs from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<LogStat> listBadHourStat(String server, LocalDateTime end, int nbStats) {
        ResultSetHandler<List<LogStat>> listHandler = new BeanListHandler<>(LogStat.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            return queryRunner.query(conn, "select top ? * from log_hour where server = ? and hour < ? and (nbExtractionError > 0 or nbExtractionMissing > 0) order by hour desc",
                    listHandler, nbStats, server, Timestamp.valueOf(end));
        } catch (SQLException e) {
            log.error("SQL error when trying to get bad hourly stats from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<LogStat> listHourStat(String server, LocalDateTime end, int nbStats) {
        ResultSetHandler<List<LogStat>> listHandler = new BeanListHandler<>(LogStat.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            return queryRunner.query(conn, "select top ? * from log_hour where server = ? and hour < ? order by hour desc",
                    listHandler, nbStats, server, Timestamp.valueOf(end));
        } catch (SQLException e) {
            log.error("SQL error when trying to get hourly stats from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static List<LogStat> listDayStat(String server, LocalDate start, int nbStats) {
        ResultSetHandler<List<LogStat>> listHandler = new BeanListHandler<>(LogStat.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            return queryRunner.query(conn, "select top ? * from log_day where server = ? and day >= ? order by day desc",
                    listHandler, nbStats, server, Timestamp.valueOf(start.atStartOfDay()));
        } catch (SQLException e) {
            log.error("SQL error when trying to get hourly stats from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static void computeHourStat(String server, LocalDateTime hour) {
        if (DateUtils.isMissingHistorianHour(hour)) {
            // for the hours lost in transition from winter to summer time (31/03 at 02h00)
            return;
        }
        ResultSetHandler<List<Report>> listHandler = new BeanListHandler<>(Report.class);
        QueryRunner queryRunner = new QueryRunner();
        LocalDateTime exactHour = hour.truncatedTo(ChronoUnit.HOURS);
        int maxExtractionRetry = Singleton.getInstance().getConfiguration().getMaxExtractionRetry();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            List<Report> reports = queryRunner.query(conn, "select * from log_extraction where server = ? and dateTime >= ? and dateTime < ?",
                    listHandler, server, Timestamp.valueOf(exactHour), Timestamp.valueOf(exactHour.plusHours(1)));
            LogStat stat = new LogStat(server, exactHour);
            for (Report report : reports) {
                if (report.getExtractionSuccess()) {
                    stat.incrementExtractionSuccess();
                } else if (report.isAbandoned(maxExtractionRetry)) {
                    stat.incrementExtractionAbandoned();
                } else {
                    stat.incrementExtractionError();
                }
                if (report.getFileTransferSuccess()) {
                    stat.incrementFileTransferSuccess();
                } else {
                    stat.incrementFileTransferError();
                }
            }
            // compute quantities
            stat.computeMissing();
            log.debug("computeHourStat hour={}, stat={}", exactHour, stat);
            // update in DB
            updateOrInsert(conn, stat, ChronoUnit.HOURS);
        } catch (SQLException e) {
            log.error("SQL error when trying to compute hourly stats from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static void computeDayStat(String server, LocalDate day) {
        ResultSetHandler<List<LogStat>> listHandler = new BeanListHandler<>(LogStat.class);
        QueryRunner queryRunner = new QueryRunner();
        try (Connection conn = DataSource.getInstance().getConnection()) {
            // create
            List<LogStat> hourlyStats = queryRunner.query(conn, "select * from log_hour where server = ? and hour >= ? and hour < ?",
                    listHandler, server, Timestamp.valueOf(day.atStartOfDay()), Timestamp.valueOf(day.plusDays(1).atStartOfDay()));
            LogStat stat = new LogStat(server, Date.valueOf(day));
            for (LogStat hourlyStat : hourlyStats) {
                stat.addCounters(hourlyStat);
            }
            // compute quantities
            stat.computeMissing();
            log.debug("computeDayStat day={}, stat={}", day, stat);
            // update in DB
            updateOrInsert(conn, stat, ChronoUnit.DAYS);
        } catch (SQLException e) {
            log.error("SQL error when trying to compute daily stats from database: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    public static void deleteStats(LocalDate date) {
        QueryRunner queryRunner = new QueryRunner();
        Timestamp timestamp = Timestamp.valueOf(date.atStartOfDay());
        try (Connection conn = DataSource.getInstance().getConnection()) {
            int deletedRecords = queryRunner.update(conn, "DELETE from log_extraction WHERE dateTime < ?", timestamp);
            log.debug("{} reports deleted in db anterior to {}", deletedRecords, timestamp);
            deletedRecords = queryRunner.update(conn, "DELETE from log_hour WHERE hour < ?", timestamp);
            log.debug("{} hourly logs deleted in db anterior to {}", deletedRecords, timestamp);
            deletedRecords = queryRunner.update(conn, "DELETE from log_day WHERE day < ?", timestamp);
            log.debug("{} daily logs deleted in db anterior to {}", deletedRecords, timestamp);
        } catch (SQLException e) {
            log.error("SQL error when trying to delete log entry: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    private static void updateOrInsert(Connection conn, LogStat stat, ChronoUnit unit) {
        String table = unit == ChronoUnit.HOURS ? "log_hour" : "log_day";
        String column = unit == ChronoUnit.HOURS ? "hour" : "day";
        if (count(conn, "select count(*) from " + table + " where server = ? and " + column + " = ?",
                stat.getServer(), unit == ChronoUnit.HOURS ? stat.getHour() : stat.getDay()) > 0) {
            update(conn, stat, unit);
        } else {
            insert(conn, stat, unit);
        }
    }

    private static void insert(Connection conn, LogStat stat, ChronoUnit unit) {
        String table = unit == ChronoUnit.HOURS ? "log_hour" : "log_day";
        String column = unit == ChronoUnit.HOURS ? "hour" : "day";
        QueryRunner queryRunner = new QueryRunner();
        try {
            int insertedRecords = queryRunner.update(conn,
                    "insert into " + table + "(server, " + column + ", nbExtractionSuccess, nbExtractionError, nbExtractionMissing, nbExtractionAbandoned, nbFileTransferSuccess, nbFileTransferError) values (?, ?, ?, ?, ?, ?, ?, ?)",
                    stat.getServer(), unit == ChronoUnit.HOURS ? stat.getHour() : stat.getDay(), stat.getNbExtractionSuccess(), stat.getNbExtractionError(), stat.getNbExtractionMissing(), stat.getNbExtractionAbandoned(), stat.getNbFileTransferSuccess(), stat.getNbFileTransferError());
            log.debug("{} stat inserted in db {}", insertedRecords, stat);
        } catch (SQLException e) {
            log.error("SQL error when trying to insert stat entry: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }

    private static void update(Connection conn, LogStat stat, ChronoUnit unit) {
        String table = unit == ChronoUnit.HOURS ? "log_hour" : "log_day";
        String column = unit == ChronoUnit.HOURS ? "hour" : "day";
        QueryRunner queryRunner = new QueryRunner();
        try {
            int updatedRecords = queryRunner.update(conn,
                    "update " + table + " set nbExtractionSuccess = ?, nbExtractionError = ?, nbExtractionMissing = ?, nbExtractionAbandoned = ?, nbFileTransferSuccess = ?, nbFileTransferError = ? where server = ? and " + column + " = ?",
                    stat.getNbExtractionSuccess(), stat.getNbExtractionError(), stat.getNbExtractionMissing(), stat.getNbExtractionAbandoned(), stat.getNbFileTransferSuccess(), stat.getNbFileTransferError(), stat.getServer(), unit == ChronoUnit.HOURS ? stat.getHour() : stat.getDay());
            log.debug("{} stat updated in db {}", updatedRecords, stat);
        } catch (SQLException e) {
            log.error("SQL error when trying to update stat entry: {} - {} [{}]", e.getMessage(), e.getSQLState(), e.getErrorCode());
            throw new HistorianExtractorException(e);
        }
    }
}
