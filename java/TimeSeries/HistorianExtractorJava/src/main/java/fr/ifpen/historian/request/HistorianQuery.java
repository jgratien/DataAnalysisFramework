package fr.ifpen.historian.request;

import com.google.common.base.Strings;
import com.jacob.com.ComFailException;
import com.jacob.com.ComThread;
import com.jacob.com.Variant;
import fr.ifpen.historian.com.Fields;
import fr.ifpen.historian.com.Recordset;
import fr.ifpen.historian.config.Historian;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.utils.ComUtils;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.List;

public abstract class HistorianQuery<T> implements Serializable {

    protected final Logger log = LoggerFactory.getLogger(HistorianQuery.class);

    protected List<String> headers = new ArrayList<>();
    protected List<T> values = new ArrayList<>();
    protected String connectionString;

    protected HistorianQuery() {
    }

    protected long execute(String server, String sql) {
        ComThread.InitMTA();
        Recordset rs = null;
        try {
            rs = getRS(server, sql);
            return readRecordset(rs);
        } catch (ComFailException e) {
            // in case of ComFail we better stop the service !!!
            if (Singleton.getInstance().getConfiguration().getKillOnCOMException()) {
                System.exit(-1);
                // May be more efficient way to test (kill the JVM)
                //Runtime.getRuntime().halt(-1);
            } else {
                throw new HistorianExtractorException(e);
            }
        } catch (Exception e) {
            throw new HistorianExtractorException(e);
        } finally {
            if (rs != null) rs.Close();
            ComThread.Release();
        }
        return 0L;
    }

    protected List<String> getHeaders() {
        return headers;
    }

    protected List<T> getValues() {
        return values;
    }

    protected abstract T fromRecordset(Object[] values);

    // simple request (SQL fourni par le client), pas de traitement spécifique
    protected long readRecordset(Recordset rs) {
        Fields fields = rs.getFields();
        int columnCount = fields.getCount();
        for (int i = 0; headers.isEmpty() && i < columnCount; i++) {
            headers.add(fields.getItem(i).getName());
        }
        Object[] objects = new Object[columnCount];
        long count = 0;
        if (!rs.getEOF()) rs.MoveFirst();
        while (!rs.getEOF()) {
            for (int i = 0; i < columnCount; i++) {
                objects[i] = ComUtils.variantToObject(fields.getItem(i).getValue());
            }
            values.add(fromRecordset(objects));
            count++;
            rs.MoveNext();
        }
        return count;
    }

    // open temp recordset directly
    protected Recordset getRS(String server, String query) {
        log.debug("recordset getRS, query={}", query);
        Recordset rs = new Recordset();
        rs.Open(new Variant(query), new Variant(connectString(server)));
        return rs;
    }


    protected String connectString(String server) {
        if (connectionString == null) {
            Historian historian = Singleton.getInstance().getConfiguration().getHistorian();
            connectionString = "Provider=" + Strings.nullToEmpty(historian.getProvider()) +
                    ";Persist Security Info=" + historian.getPersistSecurityInfo() +
                    ";USER ID=" + Strings.nullToEmpty(historian.getUserId()) +
                    ";Password=" + Strings.nullToEmpty(historian.getPassword()) +
                    ";Data source=" + server +
                    ";Mode=" + Strings.nullToEmpty(historian.getMode());
            log.debug(connectionString);
        }
        return connectionString;
    }
}

