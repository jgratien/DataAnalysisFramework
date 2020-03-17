#pragma once

#include "historian.hpp"
#include "tags_extractor.hpp"
#include "data_query.hpp"
#include "raw_value.hpp"

namespace historian {

	class BatchExtractor
	{
	public:
		BatchExtractor() = default;
		~BatchExtractor() = default;

		int run(int argc, char *argv[]) noexcept;

	private:
		void parse_args(int argc, char *argv[]);
		void write_data(std::vector<RawValue>& data);

		std::unique_ptr<TagsExtractor> mp_tags_extractor;
		std::unique_ptr<DataQuery> mp_data_query;
		std::string m_server;
		std::string m_user;
		std::string m_pwd;
		std::string m_tags_file;
		std::string m_tags_criteria;
		time_t m_start_time;
		std::string m_date_time;
		int m_duration;
		std::string m_out_dir;
		std::string m_out_file;
	};

}
