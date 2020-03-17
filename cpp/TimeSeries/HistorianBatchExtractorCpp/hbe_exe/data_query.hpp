#pragma once

#include "historian.hpp"
#include "raw_value.hpp"

namespace historian
{
	class DataQuery
	{
	public:
		DataQuery(std::vector<std::string>& tags, std::time_t date_time, int duration);
		~DataQuery() {}

		std::vector<RawValue>& getValues() {
			if (m_values.size() == 0) retrieve_values();
			return m_values;
		}

	private:
		void retrieve_values();

		IHU_TIMESTAMP m_start_time;
		IHU_TIMESTAMP m_end_time;
		std::string m_date_time;
		std::vector<RawValue> m_values;
		std::vector<std::string>& m_tags;
	};
}