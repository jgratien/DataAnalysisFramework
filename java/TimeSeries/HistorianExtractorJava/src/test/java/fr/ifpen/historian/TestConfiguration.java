package fr.ifpen.historian;

import fr.ifpen.historian.config.Configuration;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.junit.Assert;
import org.junit.Test;

/**
 * Created by IFPEN on 21/02/2019.
 */
public class TestConfiguration {

    @Test
    public void testClasspathLoad() {
        Configuration cfg = Singleton.getInstance().getConfiguration();
        Assert.assertEquals("TEST CONFIGURATION For Historian Extractor", cfg.getWelcomeMessage());
        Assert.assertEquals(120, cfg.getHistorian().getBatchExtraction().getTimeOutExtract().intValue());
        Assert.assertEquals(false, cfg.getDebug());
        int extractionInterval = cfg.getExtractionInterval().intValue();
        Assert.assertEquals(60, extractionInterval);
        Assert.assertEquals(1, cfg.nbExtractionsPerMinute());
        cfg.setExtractionInterval(30);
        Assert.assertEquals(2, cfg.nbExtractionsPerMinute());
        cfg.setExtractionInterval(20);
        Assert.assertEquals(3, cfg.nbExtractionsPerMinute());
        cfg.setExtractionInterval(15);
        Assert.assertEquals(4, cfg.nbExtractionsPerMinute());
        cfg.setExtractionInterval(10);
        Assert.assertEquals(6, cfg.nbExtractionsPerMinute());
        try {
            cfg.setExtractionInterval(70);
            Assert.fail("extraction interval should be in error");
        } catch (HistorianExtractorException e) {
            Assert.assertEquals("extraction interval must be between 10 and 60 s", e.getMessage());
        }
        try {
            cfg.setExtractionInterval(5);
            Assert.fail("extraction interval should be in error");
        } catch (HistorianExtractorException e) {
            Assert.assertEquals("extraction interval must be between 10 and 60 s", e.getMessage());
        }
        try {
            cfg.setExtractionInterval(45);
            Assert.fail("extraction interval should be in error");
        } catch (HistorianExtractorException e) {
            Assert.assertEquals("60 must be a multiple of extraction interval (30, 20, 15, 12, 10)", e.getMessage());
        }
        try {
            cfg.setExtractionInterval(21);
            Assert.fail("extraction interval should be in error");
        } catch (HistorianExtractorException e) {
            Assert.assertEquals("60 must be a multiple of extraction interval (30, 20, 15, 12, 10)", e.getMessage());
        }
        cfg.setExtractionInterval(extractionInterval);
    }
}
