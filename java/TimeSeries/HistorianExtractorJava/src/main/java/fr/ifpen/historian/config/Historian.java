package fr.ifpen.historian.config;

import com.google.common.base.Strings;

import java.util.ArrayList;
import java.util.List;

public class Historian {

    private String provider;
    private Boolean persistSecurityInfo;
    private String userId;
    private String password;
    private List<ServerConfig> servers = new ArrayList<>();
    private String mode;
    private HistorianRequests requests = new HistorianRequests();
    private Integer maxTags;
    private Integer maxQueries;
    private BatchExtraction batchExtraction;

    public Historian() {
    }

    public String getProvider() {
        return provider;
    }

    public void setProvider(String provider) {
        this.provider = provider;
    }

    public Boolean getPersistSecurityInfo() {
        return persistSecurityInfo;
    }

    public void setPersistSecurityInfo(Boolean persistSecurityInfo) {
        this.persistSecurityInfo = persistSecurityInfo;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public boolean isUserSet() {
        return !Strings.isNullOrEmpty(userId);
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public boolean isPasswordSet() {
        return !Strings.isNullOrEmpty(password);
    }

    public List<ServerConfig> getServers() {
        return servers;
    }

    public void setServers(List<ServerConfig> servers) {
        this.servers = servers;
    }

    public String getMode() {
        return mode;
    }

    public void setMode(String mode) {
        this.mode = mode;
    }

    public HistorianRequests getRequests() {
        return requests;
    }

    public void setRequests(HistorianRequests requests) {
        this.requests = requests;
    }

    public Integer getMaxTags() {
        return maxTags;
    }

    public void setMaxTags(Integer maxTags) {
        this.maxTags = maxTags;
    }

    public Integer getMaxQueries() {
        return maxQueries;
    }

    public void setMaxQueries(Integer maxQueries) {
        this.maxQueries = maxQueries;
    }

    public BatchExtraction getBatchExtraction() {
        return batchExtraction;
    }

    public void setBatchExtraction(BatchExtraction batchExtraction) {
        this.batchExtraction = batchExtraction;
    }

    @Override
    public String toString() {
        return "Historian{" +
                "provider='" + provider + '\'' +
                ", persistSecurityInfo=" + persistSecurityInfo +
                ", userId='" + userId + '\'' +
                ", password='" + password + '\'' +
                ", servers=" + servers +
                ", mode='" + mode + '\'' +
                ", requests=" + requests +
                ", maxTags=" + maxTags +
                ", maxQueries=" + maxQueries +
                ", batchExtraction=" + batchExtraction +
                '}';
    }
}
