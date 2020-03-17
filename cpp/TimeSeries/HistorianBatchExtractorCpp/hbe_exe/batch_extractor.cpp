#include "batch_extractor.hpp"
#include "connection.hpp"
#include "tags_query.hpp"
#include "tags_file.hpp"
#include "data_query.hpp"
#include <filesystem>
#include <iostream>
#include <fstream>

#include "tclap/CmdLine.h"
#include "tclap/ValueArg.h"
#include "tclap/SwitchArg.h"

namespace historian {

	int BatchExtractor::run(int argc, char *argv[]) noexcept {
		int return_code = 0;
		time_t t0 = std::time(nullptr);
		try
		{
			// checks program arguments
			parse_args(argc, argv);
			// log
			LOG_DEBUG(m_server, " >>> ", m_date_time, " >>> start of historian extraction");
			// connect to historian server
			Connection::getInstance().initialize(m_server, m_user, m_pwd);
			// get tags list
			std::vector<std::string>& tags = mp_tags_extractor->getTags();
			// get data
			mp_data_query = std::make_unique<DataQuery>(tags, m_start_time, m_duration);
			std::vector<RawValue>& data = mp_data_query->getValues();
			// write data file
			write_data(data);
		}
		catch (TCLAP::ArgException& e)
		{
			return_code = 1;
			LOG_ERROR(e.error(), e.argId());
		}
		catch (Exception &e)
		{
			return_code = -1;
			LOG_ERROR("exception met during execution: ", e.getFullMessage());
		}
		catch (std::exception &e)
		{
			return_code = -1;
			LOG_ERROR("exception met during execution: ", e.what());
		}
		catch (...)
		{
			return_code = -100;
			LOG_ERROR("catch unknown exception");
		}
		Connection::getInstance().close();
		time_t duration = std::time(nullptr) - t0;
		LOG_DEBUG(m_server, " >>> ", m_date_time, " >>> duration = ", duration, "s >>> end of historian extraction");
		LOG_INFO("extraction for ", m_server, " at ", m_date_time, " successfully completed in ", duration, "s");
		return return_code;
	}

	void BatchExtractor::parse_args(int argc, char *argv[]) {
		TCLAP::ValueArg<std::string> server("s", "server", "historian server", true, "", "string");
		TCLAP::ValueArg<std::string> user("u", "user", "historian user login", false, "", "string");
		TCLAP::ValueArg<std::string> pwd("p", "password", "historian user password", false, "", "string");
		TCLAP::ValueArg<std::string> tags_file("f", "tags_file", "file containing tags list", false, "", "string");
		TCLAP::ValueArg<std::string> tags_criteria("c", "tags_criteria", "tags selection criteria, for example: U*", false, "*", "string");
		TCLAP::ValueArg<std::string> start_time("t", "start_time", "start time format yyyy-mm-ddThh:mm:ss", true, "", "string");
		TCLAP::ValueArg<int> duration("d", "duration", "duration in seconds", false, 60, "int");
		TCLAP::ValueArg<std::string> log_properties("l", "log_configuration", "log properties configuration file", false, "", "string");
		TCLAP::ValueArg<std::string> out_dir("o", "out_dir", "output directory for historian data file", false, "./", "string");

		TCLAP::CmdLine cmd("Historian Batch Extractor", ' ', "1.0.0");
		cmd.add(server);
		cmd.add(user);
		cmd.add(pwd);
		cmd.add(tags_file);
		cmd.add(tags_criteria);
		cmd.add(start_time);
		cmd.add(duration);
		cmd.add(log_properties);
		cmd.add(out_dir);

		// Parse the args.
		cmd.parse(argc, argv);
		LogFactory::setPropertiesFile(log_properties.getValue());

		m_server = MiscUtils::trim_copy(server.getValue());
		if (m_server.empty()) {
			throw HISTORIAN_EXCEPTION("historian server is mandatory");
		}
		m_user = MiscUtils::trim_copy(user.getValue());
		m_pwd = MiscUtils::trim_copy(pwd.getValue());

		m_tags_file = MiscUtils::trim_copy(tags_file.getValue());
		m_tags_criteria = MiscUtils::trim_copy(tags_criteria.getValue());
		if (!m_tags_file.empty() && tags_criteria.isSet()) {
			throw HISTORIAN_EXCEPTION("you can not set both tags_file and tags_criteria options");
		}
		if (!m_tags_file.empty())
		{
			mp_tags_extractor = std::make_unique<TagsFile>(m_tags_file);
		}
		else
		{
			mp_tags_extractor = std::make_unique<TagsQuery>(m_tags_criteria);
		}

		m_start_time = MiscUtils::to_epoch(start_time.getValue());
		m_date_time = MiscUtils::from_epoch(m_start_time, "%F %T");
		m_duration = duration.getValue();
		if (m_duration <= 0) {
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("invalid duration ", m_duration, ", duration must be > 0s"));
		}

		m_out_dir = MiscUtils::trim_copy(out_dir.getValue());
		if (!MiscUtils::check_or_create_directory(m_out_dir)) {
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("invalid or inaccessible directory ", m_out_dir));
		}
		if (m_out_dir.back() != '/' && m_out_dir.back() != '\\') {
			m_out_dir += '/';
		}
		m_out_file = m_out_dir;
		m_out_file += "dataHistorian-";
		m_out_file += m_server;
		m_out_file += '-';
		m_out_file += MiscUtils::from_epoch(m_start_time, "%Y%m%d%H%M%S");
		m_out_file += ".csv";
		LOG_DEBUG("output file=", m_out_file);
	}

	void BatchExtractor::write_data(std::vector<RawValue>& data) {
		if (data.empty())
		{
			LOG_INFO("no data to write in ", m_out_file, " file");
		} 
		else
		{
			LOG_DEBUG(data.size(), " rows to write in ", m_out_file, " file");
		}
		// delete existing file
		MiscUtils::delete_file(m_out_file);
		std::ofstream out_file(m_out_file, std::ios::out | std::ios::trunc);
		if (out_file.is_open())
		{
			// header
			out_file << "timestamp;tagname;value;quality" << std::endl;
			// data
			for (RawValue value : data) {
				out_file << value.to_string() << std::endl;
				LOG_DEBUG(value.to_string());
			}
			out_file.close();
		}
		else
		{
			LOG_ERROR("unable to open file ", m_out_file, " no data can be written");
		}
	}
}
