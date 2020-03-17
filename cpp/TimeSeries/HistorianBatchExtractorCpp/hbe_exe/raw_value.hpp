#pragma once

#include "historian.hpp"

namespace historian
{
	static constexpr int const RV_DATE_SIZE = 2 + 1 + 2 + 1 + 4 + 1 + 2 + 1 + 2 + 1 + 2; // 17/09/2019 15:30:58
	static constexpr int const RV_TAGNAME_MAX_SIZE = 100; // ça doit passer crème comme dirait ma fille
	static constexpr int const RV_VALUE_MAX_SIZE = 9 + 1 + 9; // 123456789.123456789, là aussi on est laaaarge
	static constexpr int const RV_QUALITY_MAX_SIZE = 3 + 1 + 1; // 100.0
	static constexpr int const RV_MAX_SIZE = RV_DATE_SIZE + 1 + 
											 RV_TAGNAME_MAX_SIZE + 1 +
											 RV_VALUE_MAX_SIZE + 1 +
											 RV_QUALITY_MAX_SIZE; // 17/09/2019 15:30:04;CRY.CENTRALE_SOLAIRE.CRY_act_prod_pow;27.000000000;100.0

	class RawValue
	{
	public:
		RawValue(std::string tagname, ihuDataType type, IHU_DATA_SAMPLE value);
		RawValue::~RawValue() {}

		std::string getTagname() {
			return m_tagname;
		}
		std::string getDateTime() {
			return MiscUtils::from_epoch(getEpoch());
		}
		time_t getEpoch() {
			return MiscUtils::to_epoch(m_year, m_month, m_day, m_hour, m_minutes, m_seconds);
		}
		double getValue() {
			return m_value;
		}
		double getQuality() {
			return m_quality;
		}
		bool isValid() {
			return m_valid;
		}

		std::string to_string() {
			char str[RV_MAX_SIZE + 1];
			sprintf_s(str, RV_MAX_SIZE, "%2.2d/%2.2d/%4.4d %2.2d:%2.2d:%2.2d;%.*s;%.9f;%.1f",
				m_day, m_month, m_year, m_hour, m_minutes, m_seconds,
				RV_TAGNAME_MAX_SIZE, m_tagname.c_str(), m_value, m_quality);
			return str;
		}

	private:
		std::string m_tagname;
		int m_year;
		int m_month;
		int m_day;
		int m_hour;
		int m_minutes;
		int m_seconds;
		long m_subsecond;
		double m_value;
		double m_quality;
		bool m_valid;
	};
}
