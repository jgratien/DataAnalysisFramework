#include "data_query.hpp"
#include "connection.hpp"

namespace historian
{
	DataQuery::DataQuery(std::vector<std::string>& tags, std::time_t date_time, int duration) :
		m_tags(tags),
		m_values()
	{
		std::tm tm;
		localtime_s(&tm, &date_time);
		m_date_time = MiscUtils::from_epoch(date_time);
		if (IHU_TIMESTAMP_FromParts(tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday, tm.tm_hour, tm.tm_min, 0, 0, &m_start_time) != ihuSTATUS_OK) throw HISTORIAN_EXCEPTION("invalid date/time");
		m_start_time.Seconds--;
		memset(&m_end_time, 0, sizeof(IHU_TIMESTAMP));
		m_end_time.Seconds = m_start_time.Seconds + duration;
	}

	void DataQuery::retrieve_values() {
		long return_code(0);
		ihuErrorCode *tags_return_codes;

		if (m_tags.size() == 0) throw HISTORIAN_EXCEPTION("no tag set");

		std::vector<IHU_RETRIEVED_RAW_VALUES> rawData;
		rawData.resize(m_tags.size());
		for (size_t i = 0; i < m_tags.size(); i++) {
			rawData[i].Tagname = (char*)calloc(RV_TAGNAME_MAX_SIZE + 1, sizeof(char));
			strcpy_s(rawData[i].Tagname, RV_TAGNAME_MAX_SIZE, m_tags[i].c_str());
		}

		return_code = ihuReadMultiTagRawDataByTime(Connection::getInstance().getHandle(), rawData.size(), &m_start_time, &m_end_time, &tags_return_codes, rawData.data());
		if (return_code != ihuSTATUS_OK)
		{
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("error ", return_code, " met when retrieving data at ", m_date_time));
		}

		for (size_t i = 0; i < rawData.size(); i++)
		{
			if (tags_return_codes[i] != ihuSTATUS_OK)
			{
				LOG_ERROR("error ", tags_return_codes[i], " when retrieving data for tag ", m_tags[i], " at ", m_date_time);
				continue;
			}
			if (rawData[i].NumberOfValues == 0)
			{
				LOG_DEBUG("no data for ", rawData[i].Tagname, " at ", m_date_time);
				continue;
			}
			LOG_DEBUG(rawData[i].NumberOfValues, " data for ", rawData[i].Tagname, " at ", m_date_time);
			for (size_t v = 0; v < rawData[i].NumberOfValues; v++)
			{
				RawValue value(rawData[i].Tagname, rawData[i].ValueDataType, rawData[i].Values[v]);
				if (value.isValid()) {
					m_values.push_back(value);
				}
			}
			free(rawData[i].Tagname);
		}
	}
}