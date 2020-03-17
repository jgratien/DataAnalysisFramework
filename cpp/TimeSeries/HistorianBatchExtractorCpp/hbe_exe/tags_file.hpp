#pragma once

#include "historian.hpp"
#include "tags_extractor.hpp"

namespace historian
{
	class TagsFile : public TagsExtractor
	{
	public:
		TagsFile(std::string file_name) : 
			TagsExtractor(), 
			m_file_name(file_name)
		{
		}

		~TagsFile()
		{
		}

	protected:
		virtual void retrieve_tags();
		std::string m_file_name;
	};
}
