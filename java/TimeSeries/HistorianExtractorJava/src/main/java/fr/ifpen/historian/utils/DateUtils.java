package fr.ifpen.historian.utils;

import fr.ifpen.historian.config.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;

public class DateUtils {
    private static final Logger log = LoggerFactory.getLogger(DateUtils.class);

    public static final DateTimeFormatter QUERY_DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private DateUtils() {
    }

    public static LocalDateTime nextExtractionDateTime() {
        int interval = Singleton.getInstance().getConfiguration().getExtractionInterval();
        LocalDateTime nextExtraction = LocalDateTime.now().truncatedTo(ChronoUnit.MINUTES);
        while (nextExtraction.isBefore(LocalDateTime.now())) {
            nextExtraction = nextExtraction.plusSeconds(interval);
        }
        return nextExtraction;
    }

    public static LocalDateTime currentExtractionDateTime() {
        return nextExtractionDateTime().minusSeconds(Singleton.getInstance().getConfiguration().getExtractionInterval());
    }

    public static LocalDateTime previousExtractionDateTime() {
        return currentExtractionDateTime().minusSeconds(Singleton.getInstance().getConfiguration().getExtractionInterval());
    }

    public static Instant excelDateToInstant(double dateHistorian) {
        LocalDateTime date = LocalDateTime.of(1900, 1, 1, 0, 0);
        long days = Math.round(Math.floor(dateHistorian));
        date = date.plusDays(days).minusDays(2L);
        long seconds = Math.round((dateHistorian - (double) days) * 86400.0D);
        return date.plusSeconds(seconds).toInstant(ZoneOffset.ofHours(2));
    }

    public static LocalDateTime adjustSummerTime(String dateString, Instant instant) {
        if (dateString == null || instant == null) return null;
        return dateString.contains("CEST") ? LocalDateTime.ofInstant(instant, ZoneOffset.ofHours(2)) : LocalDateTime.ofInstant(instant, ZoneOffset.ofHours(1));
    }

    public static LocalDateTime formattedDisplayDateToLocalDateTime(String date) {
        try {
            return LocalDateTime.from(DateTimeFormatter.ISO_LOCAL_DATE_TIME.parse(date));
        } catch (Exception var4) {
            Instant i = Instant.from(DateTimeFormatter.ISO_INSTANT.parse(date));
            return LocalDateTime.ofInstant(i, ZoneId.systemDefault());
        }
    }

    public static boolean isMissingHistorianHour(LocalDateTime hour) {
        Timestamp ts = Timestamp.valueOf(hour);
        return !hour.equals(ts.toLocalDateTime());
    }

    public static String localDateTimeToHistorianQueryDate(LocalDateTime localDateTime) {
        return localDateTime == null ? null : QUERY_DATE_FORMAT.format(localDateTime);
    }
}
