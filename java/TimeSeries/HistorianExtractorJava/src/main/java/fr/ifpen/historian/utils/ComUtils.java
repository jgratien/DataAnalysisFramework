package fr.ifpen.historian.utils;

import com.jacob.com.Variant;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;

/**
 * Created by IFPEN on 28/08/2018.
 */
public class ComUtils {
    private ComUtils() {
    }

    public static Object variantToObject(Variant v) {
        switch (v.getvt()) {
            case Variant.VariantDouble:
                return v.getDouble();
            case Variant.VariantBoolean:
                return v.getBoolean();
            case Variant.VariantInt:
                return v.getInt();
//            case Variant.VariantArray:
//                return v.getVariantArray();
            case Variant.VariantByte:
                return v.getByte();
            case Variant.VariantCurrency:
                return v.getCurrency();
            case Variant.VariantDate:
                Instant instant = DateUtils.excelDateToInstant(v.getDate());
                return DateUtils.adjustSummerTime(v.toString(), instant);
            case Variant.VariantDecimal:
                return v.getDecimal();
            case Variant.VariantDispatch:
                return v.getDispatch();
            case Variant.VariantError:
                return v.getError();
            case Variant.VariantFloat:
                return v.getFloat();
            case Variant.VariantLongInt:
                return v.getLong();
            case Variant.VariantShort:
                return v.getShort();
            default:
                return v.toString();
        }
    }

    public static String objectToString(Object object) {
        return object == null ? "" : object.toString();
    }

    public static Double objectToDouble(Object object) {
        if (object == null) return 0.;
        if (object instanceof Double) return (Double) object;
        if (object instanceof Float) return ((Float) object).doubleValue();
        try {
            return Double.valueOf(object.toString());
        } catch (Exception e) {
            return 0.;
        }
    }

    public static LocalDateTime objectToLocalDateTime(Object object) {
        if (object == null) return null;
        if (object instanceof LocalDateTime) {
            return (LocalDateTime) object;
        }
        if (object instanceof Instant) {
            return LocalDateTime.ofInstant((Instant) object, ZoneId.systemDefault());
        }
        return DateUtils.formattedDisplayDateToLocalDateTime(object.toString());
    }
}
