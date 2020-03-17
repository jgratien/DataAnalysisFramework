package fr.ifpen.historian.domain;

import com.google.common.collect.Lists;
import fr.ifpen.historian.config.ServerConfig;
import fr.ifpen.historian.utils.HistorianExtractorException;

import java.nio.file.Path;
import java.util.List;

/**
 * TagsList class which transfer tags selection (only one currently)
 * to C batch program.
 * <p>
 * Created by IFPEN on 20/09/2019.
 */
public class TagsBatch implements TagsList {
    private ServerConfig config;

    public TagsBatch(ServerConfig config) {
        this.config = config;
    }

    @Override
    public List<String> getBatchArguments() {
        List<String> arguments = Lists.newArrayList("-c");
        arguments.addAll(config.getTagsSelections());
        return arguments;
    }

    @Override
    public Path getTagsFile() {
        throw new HistorianExtractorException("no tags file in C_API mode");
    }

    @Override
    public List<String> getTags() {
        throw new HistorianExtractorException("no tags file in C_API mode");
    }

    @Override
    public String toString() {
        return "TagsBatch{" +
                "config=" + config +
                '}';
    }
}
