#include "gtest/gtest.h"
#include "historian.hpp"

#include "connection.hpp"
#include "tags_query.hpp"
#include "tags_file.hpp"

namespace historian
{
	TEST(TagsTests, TagsQuery)
	{
		LOG_INFO("start of tags query test");

		Connection::getInstance().initialize("ISNTS35-N");
		TagsQuery tagsQuery("CR*");
		std::vector<std::string>& tags(tagsQuery.getTags());
		EXPECT_EQ(tags.size(), 7);
		Connection::getInstance().close();

		LOG_INFO("end of tags query test");
	}

	TEST(TagsTests, TagsFile)
	{
		LOG_INFO("start of tags file test");

		TagsFile tagsFile("..\\..\\..\\resources\\tags29.txt");
		std::vector<std::string>& tags(tagsFile.getTags());
		EXPECT_EQ(tags.size(), 10);

		LOG_INFO("end of tags file test");
	}

	TEST(TagsTests, TagsFileInvalid)
	{
		LOG_INFO("start of tags file invalid file test");

		TagsFile tagsFile("what_the_fuck_tag_file.txt");
		try
		{
			EXPECT_THROW(tagsFile.getTags(), Exception);
			//ADD_FAILURE();
		}
		catch (Exception e) 
		{
			SUCCEED();
		}

		LOG_INFO("end of tags file invalid file test");
	}
}