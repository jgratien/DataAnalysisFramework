#include "historian.hpp"
#include "batch_extractor.hpp"

int main(int argc, char *argv[])
{
	return historian::BatchExtractor().run(argc, argv);
}