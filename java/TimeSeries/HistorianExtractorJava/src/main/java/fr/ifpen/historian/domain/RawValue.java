package fr.ifpen.historian.domain;

import fr.ifpen.historian.utils.ComUtils;
import fr.ifpen.historian.utils.HistorianExtractorException;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Locale;

/**
 * Created by IFPEN on 08/02/2019.
 */
public class RawValue {
    private static final DateTimeFormatter TIMESTAMP_CSV = DateTimeFormatter.ofPattern("dd/MM/yyyy HH:mm:ss");
    private LocalDateTime timestamp;
    private String tagname;
    private Double value;
    private Double quality;

    public RawValue() {
    }

    public RawValue(LocalDateTime timestamp, String tagname, Double value, Double quality) {
        this.timestamp = timestamp;
        this.tagname = tagname;
        this.value = value;
        this.quality = quality;
    }

    public static RawValue fromRecordSet(Object[] values) {
        RawValue v = new RawValue();
        if (values.length < 4) throw new HistorianExtractorException("Invalid recordset !!!");
        v.timestamp = ComUtils.objectToLocalDateTime(values[0]);
        v.tagname = ComUtils.objectToString(values[1]);
        v.value = ComUtils.objectToDouble(values[2]);
        v.quality = ComUtils.objectToDouble(values[3]);
        return v;
    }

    public static String csvHeader() {
        return "timestamp;tagname;value;quality\n";
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public String getTagname() {
        return tagname;
    }

    public Double getValue() {
        return value;
    }

    public Double getQuality() {
        return quality;
    }

    public String toCsv() {
        // Locale.ROOT is used to force decimal separator to "."
        return String.format(Locale.ROOT, "%s;%s;%f;%f\n", TIMESTAMP_CSV.format(timestamp), tagname, value, quality);
    }
}
