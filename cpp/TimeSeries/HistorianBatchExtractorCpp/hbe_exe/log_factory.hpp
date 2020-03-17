#pragma once

#include <log4cpp\Category.hh>

namespace historian
{
	//!	\class		LogFactory
	//!	\brief		Logger configuration and creation
	class LogFactory
	{
	public:
		//!	\brief		Get or create Logger
		//!	\details	Get a logger for writing (name [separated by .] creates hierarchical logger for hierarchical configuration).
		static log4cpp::Category& getLogger(const char* name);

		static void setPropertiesFile(std::string file) {
			m_initialized = false;
			m_properties_file = file;
		}

	private:
		LogFactory() {}
		//!	\brief		Log initialization
		//!	\details	Try to use log4cpp.properties to initialize log level and appenders.
		static bool _initialize();

		//!	\brief		Default log configuration
		//!	\details	If no log4cpp properties file found, initialze appender and priority.
		static void _default_properties();

		// members 

		// static members
		static bool m_initialized;
		static std::string m_properties_file;
	};
}