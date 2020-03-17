package fr.ifpen.historian;

import fr.ifpen.historian.config.ServerConfig;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.DataSource;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.tasks.ExtractTask;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

import static fr.ifpen.historian.config.TagsMethod.C_API;
import static fr.ifpen.historian.config.TagsMethod.ODBC;

public class TestServerExtract {
    private static final Logger log = LoggerFactory.getLogger(TestServerExtract.class);

    private class ExtractResult {
        private List<String> values = new ArrayList<>();
        private Path fileName;
        private Boolean success;
        private String server;

        ExtractResult(Report report) {
            this.fileName = report.getDataFileFullPath();
            this.success = report.getExtractionSuccess();
            this.server = report.getServer();
            if (this.success) {
                try {
                    this.values = Files.readAllLines(this.fileName);
                } catch (IOException e) {
                    log.error(e.getMessage());
                }
            } else {
                log.warn("result not successful");
            }
        }

        public List<String> getValues() {
            return values;
        }

        public Path getFileName() {
            return fileName;
        }

        public Boolean getSuccess() {
            return success;
        }

        public String getServer() {
            return server;
        }

        @Override
        public String toString() {
            return "Extraction " +
                    "server='" + server + '\'' +
                    ", success=" + success +
                    ", nb values=" + values.size() +
                    ", fileName=" + fileName;
        }
    }

    @BeforeClass
    public static void initializeDb() {
        DataSource.getInstance().initialize(true);
    }

    @Test
    public void testExtractionForISNTS35() throws Exception {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(0);
        Assert.assertEquals(C_API, config.getTagsMethod());
        Server server = new Server(config);
        Assert.assertEquals("ISNTS35-N", server.getName());
        ExtractTask extract = new ExtractTask(server, LocalDateTime.now().minusHours(1).truncatedTo(ChronoUnit.MINUTES), ExtractTask.ExtractMode.BACKGROUND_RETRIEVE);
        extract.call();
        ExtractResult result = new ExtractResult(extract.getReport());
        log.info("{}", result);
        Assert.assertEquals("ISNTS35-N", result.getServer());
        Assert.assertTrue("More than 1000 Values in ISNTS35-N", result.getValues().size() > 1000);

        // second run in tags query (ODBC) mode
        ServerConfig otherConfig = Tools.copy(config);
        otherConfig.setTagsMethod(ODBC);
        server = new Server(otherConfig);
        Assert.assertTrue("Tags query config", server.getTagsList().getClass().getSimpleName().equals("TagsQuery"));
        extract = new ExtractTask(server, LocalDateTime.now().minusHours(1).minusMinutes(5).truncatedTo(ChronoUnit.MINUTES), ExtractTask.ExtractMode.BACKGROUND_RETRIEVE);
        extract.call();
        result = new ExtractResult(extract.getReport());
        log.info("{}, tags file={}", result, server.getTagsList().getTagsFile());
        Assert.assertEquals("ISNTS35-N", result.getServer());
        Assert.assertTrue("More than 1000 Values in ISNTS35-N", result.getValues().size() > 1000);
        Assert.assertTrue("Tags File has been created", Files.exists(server.getTagsList().getTagsFile()));
    }

    @Test
    public void testExtractionForISNTS29() throws Exception {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(1);
        Assert.assertEquals(ODBC, config.getTagsMethod());
        Server server = new Server(config);
        Assert.assertEquals("ISNTS29-N", server.getName());
        ExtractTask extract = new ExtractTask(server, LocalDateTime.now().minusHours(1).truncatedTo(ChronoUnit.MINUTES), ExtractTask.ExtractMode.BACKGROUND_RETRIEVE);
        extract.call();
        ExtractResult result = new ExtractResult(extract.getReport());
        log.info("{}", result);
        Assert.assertEquals("ISNTS29-N", result.getServer());
        Assert.assertTrue("More than 1000 Values in ISNTS29-N", result.getValues().size() > 1000);
    }
}
