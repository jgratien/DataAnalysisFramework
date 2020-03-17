#include "gtest/gtest.h"
#include "historian.hpp"

#include "misc.hpp"

namespace historian
{
	TEST(LogTests, Macros)
	{
		LOG_DEBUG("Simple use of logger via macro LOG_DEBUG (level DEBUG)");
		LOG_INFO("Simple use of logger via macro LOG_INFO (level INFO)");
		LOG_WARN("Simple use of logger via macro LOG_WARN (level WARN)");
		LOG_ERROR("Simple use of logger via macro LOG_ERROR (level ERROR)");

		LOG_DEBUG("A", ' ', 'B', ' ', true, ' ', 1, ' ', 1.111);
		LOG_INFO("Param", 1, " = ", "Param1");
		LOG_WARN(1, 2, 3, 4);
		std::vector<double> v(10);
		std::iota(std::begin(v), std::end(v), 1);
		LOG_ERROR("vector = ", v);
	}

	TEST(MiscTests, GetEnv)
	{
		LOG_INFO("start of get env test");
		EXPECT_EQ(MiscUtils::get_env("SystemDrive"), "C:");
		EXPECT_EQ(MiscUtils::get_env("YopYop"), "");
		EXPECT_EQ(MiscUtils::get_env("YopYop", "Yop"), "Yop");
		LOG_INFO("end of get env test");
	}

	TEST(MiscTests, ToString)
	{
		LOG_INFO("start of toString test");
		EXPECT_EQ(MiscUtils::to_string("Yop"), "Yop");
		EXPECT_EQ(MiscUtils::to_string(10), "10");
		EXPECT_EQ(MiscUtils::to_string(3. / 2.), "1.5");
		EXPECT_EQ(MiscUtils::to_string(NULL), "0");
		EXPECT_EQ(MiscUtils::to_string("Yop", "Yop"), "YopYop");
		EXPECT_EQ(MiscUtils::to_string("A", ' ', 'B', ' ', true, ' ', 1, ' ', 1.111), "A B 1 1 1.111");
		EXPECT_EQ(MiscUtils::to_string(1, 2, 3, 4), "1234");
		std::vector<double> v(10);
		std::iota(std::begin(v), std::end(v), 1);
		EXPECT_EQ(MiscUtils::to_string(v), "[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]");
		LOG_INFO("end of toString test");
	}

	TEST(MiscTests, ToCStr)
	{
		LOG_INFO("start of toCStr test");
		EXPECT_EQ(TO_CSTR(std::string("")), nullptr);
		char* v = "abc";
		std::string s(v);
		EXPECT_EQ(strcmp(TO_CSTR(s), v), 0);
		LOG_INFO("end of toCStr test");
	}

	TEST(MiscTests, ToEpoch)
	{
		LOG_INFO("start of toEpoch test");
		EXPECT_EQ(MiscUtils::to_epoch(2019, 9, 11, 17, 53, 15), 1568217195);
		EXPECT_EQ(MiscUtils::to_epoch(2019, 9, 11, 17, 53, 15), MiscUtils::to_epoch("2019-09-11T17:53:15"));
		EXPECT_EQ(MiscUtils::to_epoch("2019-01-01T01:00:00") + 3600, MiscUtils::to_epoch("2019-01-01T02:00:00"));
		// au passage à l'heure d'hiver on perd 1 heure !
		EXPECT_EQ(MiscUtils::to_epoch("2019-10-27T01:00:00") + 7200, MiscUtils::to_epoch("2019-10-27T02:00:00"));
		EXPECT_EQ(MiscUtils::to_epoch("2019-10-27T02:00:00") + 3600, MiscUtils::to_epoch("2019-10-27T03:00:00"));
		// au passage à l'heure d'été on gagne 1 heure !
		EXPECT_EQ(MiscUtils::to_epoch("2019-03-31T01:00:00"), MiscUtils::to_epoch("2019-03-31T02:00:00"));
		EXPECT_EQ(MiscUtils::to_epoch("2019-03-31T02:00:00") + 3600, MiscUtils::to_epoch("2019-03-31T03:00:00"));
		LOG_INFO("end of toEpoch test");
	}

	TEST(MiscTests, FromEpoch)
	{
		std::string date = "2019-10-27T01:59:00";
		time_t epoch = MiscUtils::to_epoch(date);
		std::string date_from_epoch = MiscUtils::from_epoch(epoch, "%FT%T");

		LOG_INFO("start of fromEpoch test");
		EXPECT_EQ(epoch, 1572134340);
		EXPECT_EQ(date, date_from_epoch);
		EXPECT_EQ("2019-09-11 17:53:15", MiscUtils::from_epoch(1568217195, "%F %T"));
		EXPECT_EQ("2019-11-08 11:50:00", MiscUtils::from_epoch(MiscUtils::to_epoch("2019-11-08T11:50:00"), "%F %T"));
		LOG_INFO("end of fromEpoch test");
	}
}