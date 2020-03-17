#include "raw_value.hpp"

namespace historian
{
	RawValue::RawValue(std::string tagname, ihuDataType type, IHU_DATA_SAMPLE value) :
		m_valid(true),
		m_quality(0.0)
	{
		IHU_TIMESTAMP_ToParts(&(value.TimeStamp), &m_year, &m_month, &m_day, &m_hour, &m_minutes, &m_seconds, &m_subsecond);
		m_tagname = tagname;
		switch (type)
		{
		case ihuShort:
			m_value = value.Value.Short;
			break;
		case ihuInteger:
			m_value = value.Value.Integer;
			break;
		case ihuFloat:
			m_value = value.Value.Float;
			break;
		case ihuDoubleFloat:
			m_value = value.Value.DoubleFloat;
			break;
		case ihuInt64:
			m_value = (double)value.Value.Int64;
			break;
		case ihuUInt64:
			m_value = (double)value.Value.UInt64;
			break;
		case ihuUInt32:
			m_value = value.Value.UInt32;
			break;
		case ihuUInt16:
			m_value = value.Value.UInt16;
			break;
		case ihuByte:
			m_value = value.Value.Byte;
			break;
		case ihuBool:
			m_value = value.Value.Bool;
			break;
		case ihuTime:
			m_value = value.Value.Time.Seconds + value.Value.Time.Nanoseconds * 1e-9;
			break;
		case ihuString:
			//		m_value = value.Value.String;
			//		break;
		case ihuBlob:
			//		m_value = value.Value.Blob;
			//		break;
		case ihuMultiField:
			//		m_value = value.Value.MultiField;
			//		break;
		case ihuArray:
			//		m_value = value.Value.Array;
			//		break;
		case ihuMaxDataType:
		case ihuScaled:
		case ihuDataTypeUndefined:
		default:
			m_valid = false;
			break;
		}
		m_quality = value.Quality.QualityStatus == ihuOPCGood ? 100. : 0.;
	}
}