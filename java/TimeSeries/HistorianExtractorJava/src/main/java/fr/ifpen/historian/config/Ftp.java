package fr.ifpen.historian.config;

import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Created by IFPEN on 19/02/2019.
 */
public class Ftp {
    private Boolean enabled;
    private String host;
    private Integer port;
    private String username;
    private String password;
    private String hostBaseDirectory;
    private String hostDirectoryPattern;
    private String strictHostKeyChecking;

    public Ftp() {
    }

    public Boolean getEnabled() {
        return enabled;
    }

    public void setEnabled(Boolean enabled) {
        this.enabled = enabled;
    }

    public String getHost() {
        return host;
    }

    public void setHost(String host) {
        this.host = host;
    }

    public Integer getPort() {
        return port;
    }

    public void setPort(Integer port) {
        this.port = port;
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

    public String getHostBaseDirectory() {
        return hostBaseDirectory;
    }

    public void setHostBaseDirectory(String hostBaseDirectory) {
        this.hostBaseDirectory = hostBaseDirectory;
    }

    public Path hostBaseDirectoryAsPath() {
        return Paths.get(hostBaseDirectory);
    }

    public String getHostDirectoryPattern() {
        return hostDirectoryPattern;
    }

    public void setHostDirectoryPattern(String hostDirectoryPattern) {
        this.hostDirectoryPattern = hostDirectoryPattern;
    }

    public String getStrictHostKeyChecking() {
        return strictHostKeyChecking;
    }

    public void setStrictHostKeyChecking(String strictHostKeyChecking) {
        this.strictHostKeyChecking = strictHostKeyChecking;
    }

    @Override
    public String toString() {
        return "Ftp{" +
                "enabled=" + enabled +
                ", host='" + host + '\'' +
                ", port=" + port +
                ", username='" + username + '\'' +
                ", password='" + password + '\'' +
                ", hostBaseDirectory='" + hostBaseDirectory + '\'' +
                ", hostDirectoryPattern='" + hostDirectoryPattern + '\'' +
                ", strictHostKeyChecking='" + strictHostKeyChecking + '\'' +
                '}';
    }
}
