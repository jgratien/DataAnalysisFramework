#pragma once

#include <string>
#include <algorithm>
#include <cctype>
#include <locale>
#include <vector>
#include <iostream>
#include <sstream>
#include <initializer_list>

#define TO_CSTR(x) (x.size() == 0 ? nullptr : const_cast<char*>(x.c_str()))

namespace historian
{
	//!	\class		MiscUtils
	//!	\brief		Miscellanous utils function
	//!	\details	Env var access
	class MiscUtils
	{
	public:
		//!	\brief		get environment variable
		//!	\details	return environment variable if exists or NULL.
		static const std::string get_env(const char* varName);
		//!	\brief		get environment variable
		//!	\details	return environment variable if exists or default value.
		static const std::string get_env(const char* varName, const std::string defaultValue);

		static time_t to_epoch(int year, int month, int day, int hour, int minute, int second);
		static time_t to_epoch(std::string date_time);
		static std::string from_epoch(time_t date_time, std::string format = "%FT%T");

		// trim from start (in place)
		static inline void ltrim(std::string &s) {
			s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int ch) {
				return !std::isspace(ch);
			}));
		}

		// trim from end (in place)
		static inline void rtrim(std::string &s) {
			s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch) {
				return !std::isspace(ch);
			}).base(), s.end());
		}

		// trim from both ends (in place)
		static inline void trim(std::string &s) {
			ltrim(s);
			rtrim(s);
		}

		// trim from start (copying)
		static inline std::string ltrim_copy(std::string s) {
			ltrim(s);
			return s;
		}

		// trim from end (copying)
		static inline std::string rtrim_copy(std::string s) {
			rtrim(s);
			return s;
		}

		// trim from both ends (copying)
		static inline std::string trim_copy(std::string s) {
			trim(s);
			return s;
		}

		template <typename T>
		static const std::string to_string(T t)
		{
			std::ostringstream strs;
			strs << t;
			return strs.str();
		}

		template<typename T, typename... Args>
		static const std::string to_string(T t, Args... args) // recursive variadic function
		{
			std::ostringstream strs;
			strs << t;
			strs << to_string(args...);
			return strs.str();
		}

		template <typename T>
		static const std::string to_string(std::vector<T> v)
		{
			std::ostringstream strs;
			strs << "[";
			for (size_t i = 0; i < (v.size() - 1); ++i)
			{
				strs << to_string(v[i], ", ");
			}
			strs << to_string(v.back()) << "]";
			return strs.str();
		}

		template <typename T, typename... Args>
		static const std::string to_string(std::vector<T> v, Args... args)
		{
			std::ostringstream strs;
			strs << to_string(v);
			strs << to_string(args...);
			return strs.str();
		}

		static bool file_exists(std::string file);
		static bool delete_file(std::string file, bool error_if_absent = false);
		static bool check_or_create_directory(std::string directory);

		// Private
		//**********************************************************************************************************//
	private:
		//!	\brief		The MiscUtils class constructor
		//!	\details	Private, only static functions in this class.
		MiscUtils() {}
	};
}