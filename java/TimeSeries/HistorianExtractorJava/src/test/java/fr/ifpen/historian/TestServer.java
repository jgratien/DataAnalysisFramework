package fr.ifpen.historian;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.DataSource;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.domain.Server;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.List;
import java.util.Set;

/**
 * Created by IFPEN on 21/02/2019.
 */
public class TestServer {
    private static final Logger log = LoggerFactory.getLogger(TestServer.class);
    private static boolean canRun = true;
    private static final String db4Tests = "D:/tmp/historian_extractor";

    @BeforeClass
    public static void initializeDb() {
        if (Files.exists(Paths.get(db4Tests + ".mv.db"))) {
            Singleton.getInstance().getConfiguration().getDatabase().setUrl("jdbc:h2:file:" + db4Tests + ";AUTO_SERVER=true;DB_CLOSE_DELAY=60");
            DataSource.getInstance().close();
            LocalDateTime t0 = LocalDateTime.now();
            DataSource.getInstance().initialize(true);
            log.debug("database={} initialized in {}s", db4Tests, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        } else {
            log.debug("most of the tests can not be done, because you don't have the correct database (not committed because of its size > 230 Mo)");
            canRun = false;
        }
    }

    @AfterClass
    public static void closeDb() {
        if (canRun) DataSource.getInstance().close();
    }
    /**
     * This test works only with parameter extractionInterval set to 60 s
     * and parameter maxRetrieveRequests set to 50s
     */
    @Test
    public void testMaxRetrieveRange() {
        Server server = Singleton.getInstance().getServer("ISNTS35-N");
        log.debug("server={}, maxRetrieveRange={}", server, server.maxRetrieveRange());
        Assert.assertEquals(60*50, server.maxRetrieveRange());
    }

    @Test
    public void testFirstBadFileTransferDateTime() {
        if (!canRun) return;
        LocalDateTime t0 = LocalDateTime.now();
        List<Report> reports = LogDAO.listReports("ISNTS35-N", LocalDateTime.now().minusDays(25), LocalDateTime.now().minusDays(1));
        Report report = reports.get(0);
        report.setFileTransferSuccess(false);
        LogDAO.saveReport(report);
        Server server = Singleton.getInstance().getServer("ISNTS35-N");
        Singleton.getInstance().getConfiguration().getRetentionPeriods().setFiles(25);
        Report first = server.firstBadFileTransferReport();
        log.debug("server={}, firstBadFileTransferReport={}, computed in {}s", server, first, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        Assert.assertNotNull(first);
        Assert.assertTrue("Bad file transfer in DB", first.getDateTime().toLocalDateTime().isBefore(LocalDateTime.now()));
        Assert.assertEquals(report.getDateTime(), first.getDateTime());
    }

    @Test
    public void testFirstBadRetrieveDateTime() {
        if (!canRun) return;
        LocalDateTime t0 = LocalDateTime.now();
        Server server = Singleton.getInstance().getServer("ISNTS29-N");
        LocalDateTime first = server.firstBadRetrieveDateTime();
        log.debug("server={}, firstBadRetrieveDateTime={}, computed in {}s", server, first, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        Assert.assertNotNull(first);
        Assert.assertTrue("Bad retrieve in DB", first.isBefore(LocalDateTime.now()));
        Assert.assertEquals(LocalDateTime.of(2019, 10, 04, 10, 59, 0), first);
    }

    /**
     * This test works only with parameter extractionInterval set to 60 s
     */
    @Test
    public void testRetrieveDateTimes() {
        if (!canRun) return;
        LocalDateTime t0 = LocalDateTime.now();
        Server server = Singleton.getInstance().getServer("ISNTS29-N");
        LocalDateTime start = LocalDateTime.of(2019, 9, 17, 3, 30, 0);
        LocalDateTime end = start.plusHours(1);
        Set<LocalDateTime> dateTimes = server.retrieveDateTimes(start, end, false);
        log.debug("server={}, retrieveDateTimes={}, computed in {}s", server, dateTimes, ChronoUnit.SECONDS.between(t0, LocalDateTime.now()));
        Assert.assertNotNull(dateTimes);
        Assert.assertEquals(29, dateTimes.size());
        // limit à 50 via maxRetrieveRequest sinon on aurait 24 * 60
        dateTimes = server.retrieveDateTimes(start, end, true);
        Assert.assertEquals(50, dateTimes.size());
    }
}
