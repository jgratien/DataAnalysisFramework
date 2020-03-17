#include "tags_query.hpp"
#include "connection.hpp"
#include <fstream>

namespace historian
{
	void TagsQuery::retrieve_tags() {
		int num_tags(0);
		char tag_name[200];

		// intialize the tag
		ihuTagClearProperties();

		char criteria[200];
		strcpy_s(criteria, 200, m_criteria.c_str());
		ihuTagCacheCriteriaSetStringProperty(ihutagpropTagname, criteria);

		ihuFetchTagCacheEx(Connection::getInstance().getHandle(), &num_tags);
		// cache
		ihuTagCacheCriteriaClear();
		// Iterate through the all the tags in the cache.
		// while there are tags left
		int tag_idx(0);
		// Note we do all calls by index because it is much faster
		while ((ihuGetStringTagPropertyByIndex(tag_idx, ihutagpropTagname, tag_name, 200) == ihuSTATUS_OK))
		{
			std::string tag(tag_name);
			m_tags.push_back(tag);
			tag_idx++;
		}
		ihuCloseTagCache();
		LOG_DEBUG("We get ", tag_idx, " tags");
	}
}