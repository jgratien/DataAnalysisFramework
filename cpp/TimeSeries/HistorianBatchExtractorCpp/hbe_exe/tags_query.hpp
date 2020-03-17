#pragma once

#include "historian.hpp"
#include "tags_extractor.hpp"

namespace historian
{
	class TagsQuery : public TagsExtractor
	{
	public:
		TagsQuery(std::string criteria) : 
			TagsExtractor(), 
			m_criteria(criteria)
		{
		}

		~TagsQuery()
		{
		}

	protected:
		virtual void retrieve_tags();
		std::string m_criteria;
	};
}
