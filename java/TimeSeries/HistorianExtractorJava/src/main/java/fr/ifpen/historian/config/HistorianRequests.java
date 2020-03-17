package fr.ifpen.historian.config;

public class HistorianRequests {
    private String tagList;

    public HistorianRequests() {
    }

    public String getTagList() {
        return tagList;
    }

    public void setTagList(String tagList) {
        this.tagList = tagList;
    }

    @Override
    public String toString() {
        return "HistorianRequests{" +
                "tagList='" + tagList + '\'' +
                '}';
    }
}
