package fr.ifpen.historian;

import fr.ifpen.historian.request.HistorianQuery;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.junit.Assert;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;

public class TestHistorianQuery {
    private static final Logger log = LoggerFactory.getLogger(TestHistorianQuery.class);

    private class SimpleTagRequest extends HistorianQuery<String> {

        public void runQuery() {
            execute("ISNTS35-N", "SELECT TOP 20 TAGNAME FROM ihTags ORDER BY TAGNAME");
        }

        @Override
        public List<String> getValues() {
            return super.getValues();
        }

        @Override
        protected String fromRecordset(Object[] values) {
            return values.length > 0 ? values[0].toString() : "";
        }
    }

    private class ErrorRequest extends HistorianQuery<String> {

        public void runQuery() {
            execute("ISNTS35-N", "SELECT UNKNOWN_FIELD FROM UNKNOWN_TABLE");
        }

        @Override
        protected String fromRecordset(Object[] values) {
            return values.length > 0 ? values[0].toString() : "";
        }
    }

    @Test
    public void testSimpleRequest() {
        SimpleTagRequest request = new SimpleTagRequest();
        request.runQuery();
        Assert.assertEquals(20, request.getValues().size());
    }

    @Test
    public void testErrorRequest() {
        try {
            ErrorRequest request = new ErrorRequest();
            request.runQuery();
            Assert.fail("Request is invalid we must have exception");
        } catch (HistorianExtractorException e) {
            log.info("historian error={}", e.getMessage());
            Assert.assertTrue(e.getMessage().contains("table n'existe pas"));
        }
    }
}
