#include "tags_file.hpp"
#include <fstream>
#include <filesystem>

namespace historian
{
	void TagsFile::retrieve_tags() {
		if (!MiscUtils::file_exists(m_file_name))
		{
			throw HISTORIAN_EXCEPTION(MiscUtils::to_string("trying to read tags from invalid file ", m_file_name));
		}
		std::ifstream file(m_file_name);
		std::string tag;
		if (file.is_open())
		{
			while (file >> tag) {
				if (tag.size() > 0) {
					m_tags.push_back(tag);
				}
			}
			file.close();
		}
		LOG_DEBUG("We get ", m_tags.size(), " tags from ", m_file_name);
	}
}