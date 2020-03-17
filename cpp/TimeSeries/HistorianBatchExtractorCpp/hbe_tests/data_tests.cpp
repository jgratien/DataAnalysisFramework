#include "gtest/gtest.h"
#include "historian.hpp"

#include "connection.hpp"
#include "data_query.hpp"

namespace historian
{
	TEST(DataTests, DataQuery)
	{
		LOG_INFO("start of data query test");

		Connection::getInstance().initialize("ISNTS35-N");
		std::vector<std::string> tags;
		tags.push_back("CRY.CENTRALE_SOLAIRE.CRY_act_prod_pow");
		DataQuery dataQuery(tags, MiscUtils::to_epoch("2019-09-17T15:30:00"), 60);
		std::vector<RawValue>& data(dataQuery.getValues());
		ASSERT_EQ(data.size(), 4);
		EXPECT_EQ(data[0].getValue(), 27.);
		EXPECT_EQ(data[1].getValue(), 28.);
		EXPECT_EQ(data[2].getValue(), 27.);
		EXPECT_EQ(data[3].getValue(), 26.);
		Connection::getInstance().close();

		LOG_INFO("end of data query test");
	}
}