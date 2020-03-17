#pragma once

#include <log4cpp\Category.hh>
#include "log_factory.hpp"
#include "misc.hpp"

// hack in order to have real line number
// cf https://stackoverflow.com/questions/19343205/c-concatenating-file-and-line-macros#19343239 
#define LINE_HACK(x) #x
#define LINE_INDIRECT(x) LINE_HACK(x)

#define LOG_CATEGORY __FUNCTION__

#define LOG_MSG(...) historian::MiscUtils::to_string(__VA_ARGS__, " --->>> ", __FILE__, " [", LINE_INDIRECT(__LINE__), "]")

typedef log4cpp::Category& LOG;

#define LOG_CREATE historian::LogFactory::getLogger(LOG_CATEGORY)

#if _DEBUG
#define LOG_DEBUG(...) LOG_CREATE.debug(historian::MiscUtils::to_string(__VA_ARGS__))
#else
#define LOG_DEBUG(...)
#endif  // _DEBUG

#define LOG_INFO(...) LOG_CREATE.info(historian::MiscUtils::to_string(__VA_ARGS__))
#define LOG_WARN(...) LOG_CREATE.warn(historian::MiscUtils::to_string(__VA_ARGS__))
#define LOG_ERROR(...) LOG_CREATE.error(historian::MiscUtils::to_string(__VA_ARGS__))
