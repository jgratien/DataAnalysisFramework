#pragma once

#include "historian.hpp"

namespace historian {

	class TagsExtractor {
	public:
		TagsExtractor() : m_tags()
		{
		}

		virtual ~TagsExtractor()
		{
		}

		std::vector<std::string>& getTags() {
			if (m_tags.size() == 0) retrieve_tags();
			return m_tags;
		}

	protected:
		virtual void retrieve_tags() = 0;

		std::vector<std::string> m_tags;
	};

}
