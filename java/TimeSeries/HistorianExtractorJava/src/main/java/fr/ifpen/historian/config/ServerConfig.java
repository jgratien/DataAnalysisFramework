package fr.ifpen.historian.config;

import com.google.common.collect.Lists;
import fr.ifpen.historian.domain.TagsBatch;
import fr.ifpen.historian.domain.TagsList;
import fr.ifpen.historian.request.TagsQuery;
import fr.ifpen.historian.utils.HistorianExtractorException;

import java.io.Serializable;
import java.util.List;

import static fr.ifpen.historian.config.TagsMethod.C_API;

public class ServerConfig implements Serializable {
    private String name;
    private Integer checkTagsDelay;
    private TagsMethod tagsMethod;
    private List<String> tagsSelections;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Integer getCheckTagsDelay() {
        return checkTagsDelay;
    }

    public void setCheckTagsDelay(Integer checkTagsDelay) {
        this.checkTagsDelay = checkTagsDelay;
    }

    public TagsMethod getTagsMethod() {
        return tagsMethod;
    }

    public void setTagsMethod(TagsMethod tagsMethod) {
        this.tagsMethod = tagsMethod;
    }

    public List<String> getTagsSelections() {
        return tagsSelections == null ? Lists.newArrayList() : tagsSelections;
    }

    public void setTagsSelections(List<String> tagsSelections) {
        this.tagsSelections = tagsSelections;
    }

    public void check() {
        if (tagsSelections == null || tagsSelections.isEmpty()) {
            throw new HistorianExtractorException("you have to set at least one tag selection for server " + name);
        }
        if (tagsMethod == null) {
            throw new HistorianExtractorException("you have to set tags reading method. check 'tagsMethod' in configuration for server " + name);
        }
        if (tagsMethod == C_API && tagsSelections.size() > 1) {
            throw new HistorianExtractorException("in C_API mode, we can use only one tag selection. check configuration for server " + name);
        }
    }

    public TagsList createTagsList() {
        check();
        switch (tagsMethod) {
            case C_API:
                return new TagsBatch(this);
            case ODBC:
                return new TagsQuery(this);
        }
        throw new HistorianExtractorException("unable to create TagsList implementation, what the fuck the hell is this configuration " + toString());
    }

    @Override
    public String toString() {
        return "ServerConfig{" +
                "name='" + name + '\'' +
                ", checkTagsDelay=" + checkTagsDelay +
                ", tagMethod=" + tagsMethod +
                ", tagsSelections=" + tagsSelections +
                '}';
    }
}
