package fr.ifpen.historian;

import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.utils.FileTransfer;
import org.junit.Assert;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.LocalDateTime;

/**
 * Created by IFPEN on 21/02/2019.
 */
public class TestFTP {
    private static final Logger log = LoggerFactory.getLogger(TestFTP.class);

    @Test
    public void testFileTransfer() throws IOException {
        Path localDir = Singleton.getInstance().getConfiguration().dataDirectoryAsPath();
        Path dataTest = localDir.resolve("dataTest.csv");
        Files.deleteIfExists(dataTest);
        FileTransfer fileTransfer = new FileTransfer();
        Files.createFile(dataTest);
        Files.write(dataTest, LocalDateTime.now().toString().getBytes());
        log.info("temporary file: {}", dataTest.toFile().getAbsolutePath());
        Assert.assertEquals("dataTest.csv", dataTest.getFileName().toString());
        Assert.assertTrue("temp data file not created", Files.exists(dataTest));
        try {
            fileTransfer.connect(Singleton.getInstance().getConfiguration().activeFtps().get(0));
            fileTransfer.uploadFile(dataTest, "ISNTS-TEST", LocalDateTime.now());
            fileTransfer.disconnect();
        } catch (Exception e) {
            log.warn("unable to transfer file: {}", e.getMessage());
        } finally {
            fileTransfer.disconnect();
        }
    }
}
