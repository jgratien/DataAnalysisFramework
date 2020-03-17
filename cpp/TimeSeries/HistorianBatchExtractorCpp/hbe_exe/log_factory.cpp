#include "log_factory.hpp"
#include "misc.hpp"
#include <exception>
#include <filesystem>

#include <log4cpp/PropertyConfigurator.hh>
#include <log4cpp/OstreamAppender.hh>
#include <log4cpp/FileAppender.hh>
#include <log4cpp/BasicLayout.hh>
#include <log4cpp/PatternLayout.hh>

namespace historian
{
	bool LogFactory::m_initialized = false;
	std::string LogFactory::m_properties_file = "";

	//!	\brief		Log initialization
	//!	\details	Try to use log4cpp.properties to initialize log level and appenders.
	bool LogFactory::_initialize() {
		if (m_initialized) return true;

		m_initialized = true;

		// Log initialization
		if (MiscUtils::file_exists(m_properties_file))
		{
			try
			{
				log4cpp::PropertyConfigurator::configure(m_properties_file);
				return true;
			}
			catch (std::exception& e)
			{
				_default_properties();
				log4cpp::Category::getRoot().warn(e.what());
				return false;
			}
		}
		else
		{
			_default_properties();
			return m_properties_file.empty();
		}
	}

	//!	\brief		Get or create Logger
	//!	\details	Get a logger for writing (name [separated by .] creates hierarchical logger for hierarchical configuration).
	log4cpp::Category& LogFactory::getLogger(const char* name)
	{
		if (!_initialize()) {
			log4cpp::Category::getRoot().warn(MiscUtils::to_string("Invalid log properties file ", m_properties_file));
		}
		return log4cpp::Category::getInstance(std::string(name));
	}

	//!	\brief		Default log configuration
	//!	\details	If no log4cpp properties file found, initialize appender and priority.
	void LogFactory::_default_properties()
	{
		log4cpp::Appender* console_appender = new log4cpp::OstreamAppender("appender", &std::cout);
		log4cpp::Appender* console_error_appender = new log4cpp::OstreamAppender("appender", &std::cerr);
		log4cpp::Appender* error_file_appender = new log4cpp::FileAppender("errors", "./err.txt");
		log4cpp::Appender* info_file_appender = new log4cpp::FileAppender("infos", "./log.txt");

		log4cpp::PatternLayout* console_layout = new log4cpp::PatternLayout();
		console_layout->setConversionPattern("%m%n");
		console_appender->setLayout(console_layout);
		console_appender->setThreshold(log4cpp::Priority::INFO);

		log4cpp::PatternLayout* console_error_layout = new log4cpp::PatternLayout();
		console_error_layout->setConversionPattern("%m%n");
		console_error_appender->setLayout(console_error_layout);
		console_error_appender->setThreshold(log4cpp::Priority::ERROR);

		log4cpp::PatternLayout* error_layout = new log4cpp::PatternLayout();
		error_layout->setConversionPattern("%-5.5p %d{%Y-%m-%d %H:%M:%S,%l} %c: %m%n");

		error_file_appender->setLayout(error_layout);
		error_file_appender->setThreshold(log4cpp::Priority::ERROR);

		log4cpp::PatternLayout* info_layout = new log4cpp::PatternLayout();
		info_layout->setConversionPattern("%-5.5p %d{%Y-%m-%d %H:%M:%S,%l} %c: %m%n");

		info_file_appender->setLayout(info_layout);
		info_file_appender->setThreshold(log4cpp::Priority::INFO);

		log4cpp::Category& root = log4cpp::Category::getRoot();
		//priority order is: FATAL < ALERT < CRIT < ERROR < WARN < NOTICE < INFO < DEBUG
		root.setPriority(log4cpp::Priority::INFO);

		root.removeAllAppenders();
		root.addAppender(console_appender);
		root.addAppender(console_error_appender);
		root.addAppender(error_file_appender);
		root.addAppender(info_file_appender);
	}
}