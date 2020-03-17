package fr.ifpen.historian.config;

public class Database {
    private String url;
    private String username;
    private String password;
    private Integer prepStmtCacheSize;
    private Integer prepStmtCacheSqlLimit;
    private Boolean cachePrepStmts;

    public Database() {
    }

    public String getUrl() {
        return url;
    }

    public void setUrl(String url) {
        this.url = url;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public Integer getPrepStmtCacheSize() {
        return prepStmtCacheSize;
    }

    public void setPrepStmtCacheSize(Integer prepStmtCacheSize) {
        this.prepStmtCacheSize = prepStmtCacheSize;
    }

    public Integer getPrepStmtCacheSqlLimit() {
        return prepStmtCacheSqlLimit;
    }

    public void setPrepStmtCacheSqlLimit(Integer prepStmtCacheSqlLimit) {
        this.prepStmtCacheSqlLimit = prepStmtCacheSqlLimit;
    }

    public Boolean getCachePrepStmts() {
        return cachePrepStmts;
    }

    public void setCachePrepStmts(Boolean cachePrepStmts) {
        this.cachePrepStmts = cachePrepStmts;
    }

    @Override
    public String toString() {
        return "Database{" +
                "url='" + url + '\'' +
                ", username='" + username + '\'' +
                ", password='" + password + '\'' +
                ", prepStmtCacheSize=" + prepStmtCacheSize +
                ", prepStmtCacheSqlLimit=" + prepStmtCacheSqlLimit +
                ", cachePrepStmts=" + cachePrepStmts +
                '}';
    }
}
