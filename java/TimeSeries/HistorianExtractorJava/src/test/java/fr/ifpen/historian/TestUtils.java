package fr.ifpen.historian;

import fr.ifpen.historian.utils.DateUtils;
import org.junit.Assert;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.time.LocalDateTime;
import java.time.Year;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

import static fr.ifpen.historian.utils.DateUtils.*;

/**
 * Created by IFPEN on 21/02/2019.
 */
public class TestUtils {
    private static final Logger log = LoggerFactory.getLogger(TestUtils.class);

    /**
     * This test works only with parameter extractionInterval set to 60 s
     */
    @Test
    public void testCurrentInterval() {
        LocalDateTime dt = currentExtractionDateTime();
        LocalDateTime expected = LocalDateTime.now().truncatedTo(ChronoUnit.MINUTES);
        log.debug("Current interval calculated={}, expected={}, now={}", dt, expected, LocalDateTime.now());
        Assert.assertEquals(expected, dt);
    }

    /**
     * This test works only with parameter extractionInterval set to 60 s
     */
    @Test
    public void testNextInterval() {
        LocalDateTime dt = nextExtractionDateTime();
        LocalDateTime expected = LocalDateTime.now().truncatedTo(ChronoUnit.MINUTES).plusMinutes(1);
        log.debug("Next interval calculated={}, expected={}, now={}", dt, expected, LocalDateTime.now());
        Assert.assertEquals(expected, dt);
    }

    /**
     * This test works only with parameter extractionInterval set to 60 s
     */
    @Test
    public void testPreviousInterval() {
        LocalDateTime dt = previousExtractionDateTime();
        LocalDateTime expected = LocalDateTime.now().truncatedTo(ChronoUnit.MINUTES).minusMinutes(1);
        log.debug("Previous interval calculated={}, expected={}, now={}", dt, expected, LocalDateTime.now());
        Assert.assertEquals(expected, dt);
    }

    @Test
    public void testMissingHour() {
        List<LocalDateTime> missingHours = new ArrayList<>();
        LocalDateTime start = Year.now().atDay(1).atStartOfDay();
        for (LocalDateTime hour = start; hour.isBefore(start.plusYears(1)); hour = hour.plusHours(1)) {
            if (DateUtils.isMissingHistorianHour(hour)) {
                missingHours.add(hour);
            }
        }
        log.debug("missingHours={}", missingHours);
        Assert.assertEquals(1, missingHours.size());
    }
}
