package fr.ifpen.historian.domain;

import fr.ifpen.historian.config.Singleton;

import java.nio.file.Path;
import java.util.List;

/**
 * Created by IFPEN on 20/09/2019.
 */
public interface TagsList {
    static Path tagsFile(String server) {
        return Singleton.getInstance().getConfiguration().dataDirectoryAsPath().resolve("tags-" + server + ".txt");
    }

    List<String> getBatchArguments();

    Path getTagsFile();

    List<String> getTags();
}
