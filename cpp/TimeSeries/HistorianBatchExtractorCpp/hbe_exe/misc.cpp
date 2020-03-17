#include "misc.hpp"
#include "log.hpp"
#include "exception.hpp"
#include <filesystem>

namespace historian
{
	//!	\brief		get environment variable
	//!	\details	return environment variable if exists or NULL.
	const std::string MiscUtils::get_env(const char* varName) {
		std::string result("");
		char* envVar(NULL);
		size_t envVarSize;

		getenv_s(&envVarSize, NULL, 0, varName);
		if (envVarSize != 0)
		{
			envVar = (char*)malloc(envVarSize * sizeof(char));
			// Get the value of the SWIFT_DIR environment variable.  
			getenv_s(&envVarSize, envVar, envVarSize, varName);
			result = envVar;
			free(envVar);
		}
		return result;
	}

	//!	\brief		get environment variable
	//!	\details	return environment variable if exists or defalut value.
	const std::string MiscUtils::get_env(const char* varName, const std::string defaultValue) {
		std::string result(get_env(varName));
		return result.empty() ? defaultValue : result;
	}

	time_t MiscUtils::to_epoch(int year, int month, int day, int hour, int minute, int second) {
		struct tm timeinfo;
		// mode heure été / hiver : Flag indiquant "Is DST on?" 1 = yes, 0 = no, -1 = unknown
		timeinfo.tm_isdst = -1;
		timeinfo.tm_year = year - 1900;
		timeinfo.tm_mon = month - 1;
		timeinfo.tm_mday = day;
		timeinfo.tm_hour = hour;
		timeinfo.tm_min = minute;
		timeinfo.tm_sec = second;

		return mktime(&timeinfo);
	}

	time_t MiscUtils::to_epoch(std::string date_time) {
		int year, month, day, hour, minute, second;
		if (sscanf_s(date_time.c_str(), "%d-%d-%dT%d:%d:%d", &year, &month, &day, &hour, &minute, &second) != 6) {
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("invalid date/time ", date_time, ", expected format : yyyy-mm-ddThh:mm:ss"));
		}
		return to_epoch(year, month, day, hour, minute, second);
	}

	std::string MiscUtils::from_epoch(time_t date_time, std::string format) {
		char buffer[80];
		std::tm tm;
		localtime_s(&tm, &date_time);
		strftime(buffer, 80, format.c_str(), &tm);
		return buffer;
	}

	bool MiscUtils::file_exists(std::string file)
	{
		return !file.empty() && std::experimental::filesystem::is_regular_file(file) && std::experimental::filesystem::exists(file);
	}

	bool MiscUtils::delete_file(std::string file, bool error_if_absent)
	{
		if (!file_exists(file)) {
			if (error_if_absent) throw HISTORIAN_EXCEPTION(to_string("impossible to delete non existing file ", file));
			return false;
		}
		return std::experimental::filesystem::remove(file);
	}

	bool MiscUtils::check_or_create_directory(std::string directory)
	{
		if (MiscUtils::trim_copy(directory).empty()) {
			throw HISTORIAN_EXCEPTION("directory can't be empty");
		}
		try
		{
			// Check if folder exists
			if (!std::experimental::filesystem::is_directory(directory) || !std::experimental::filesystem::exists(directory))
			{
				if (!std::experimental::filesystem::create_directory(directory)) { // create folder
					throw HISTORIAN_EXCEPTION(MiscUtils::to_string("unable to create directory ", directory));
				}
				LOG_INFO("directory ", directory, " created");
			}
		}
		catch (std::exception& e)
		{
			// Output the error message.
			throw HISTORIAN_EXCEPTION(e.what());
		}
		return true;
	}
}