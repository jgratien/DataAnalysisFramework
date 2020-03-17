package fr.ifpen.historian.utils;

import com.google.common.base.Strings;
import com.jcraft.jsch.*;
import fr.ifpen.historian.config.Ftp;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Path;
import java.time.LocalDateTime;

public class FileTransfer {
    private Logger log = LoggerFactory.getLogger(FileTransfer.class);

    private Session session;
    private ChannelSftp sftpChannel;
    private Ftp configuration;

    public FileTransfer() {
    }

    public void connect(Ftp configuration) {
        this.configuration = configuration;
        if (!configuration.getEnabled())
            throw new HistorianExtractorException("Trying to make FTP connection with FTP disabled !");
        JSch jsch = new JSch();
        try {
            session = jsch.getSession(configuration.getUsername(), configuration.getHost(), configuration.getPort());
            session.setConfig("StrictHostKeyChecking", configuration.getStrictHostKeyChecking());
            session.setPassword(configuration.getPassword());
            session.connect();
            Channel channel = session.openChannel("sftp");
            channel.connect();
            sftpChannel = (ChannelSftp) channel;
        } catch (JSchException e) {
            throw new HistorianExtractorException(e);
        }
    }

    public void uploadFile(Path file, String server, LocalDateTime dateTime) {
        try (InputStream input = new FileInputStream(file.toFile())) {
            changeDir(server, dateTime);
            sftpChannel.put(input, file.getFileName().toString());
        } catch (FileNotFoundException e) {
            throw new HistorianExtractorException(e);
        } catch (IOException e) {
            throw new HistorianExtractorException(e);
        } catch (SftpException e) {
            throw new HistorianExtractorException(e);
        }
    }

    private void changeDir(String server, LocalDateTime dateTime) {
        if (configuration == null)
            throw new HistorianExtractorException("Trying upload file without any connection made !");
        Path hostBaseDirectory = configuration.hostBaseDirectoryAsPath();
        String fileDirectory = String.format(configuration.getHostDirectoryPattern(),
                Strings.isNullOrEmpty(server) ? "unknown_server" : server, dateTime == null ? LocalDateTime.now() : dateTime);
        try {
            sftpChannel.cd(hostBaseDirectory.toString().replace('\\', '/'));
        } catch (SftpException e) {
            log.error("unable to access remote directory {}: {}", hostBaseDirectory, e.getMessage());
            throw new HistorianExtractorException(e);
        }
        try {
            sftpChannel.cd(fileDirectory);
        } catch (SftpException e) {
            try {
                sftpChannel.mkdir(fileDirectory);
                sftpChannel.cd(fileDirectory);
            } catch (SftpException sftpe) {
                log.error("unable to create remote directory {}: {}", hostBaseDirectory.resolve(fileDirectory), sftpe.getMessage());
                throw new HistorianExtractorException(sftpe);
            }
        }
    }

    public void disconnect() {
        if (sftpChannel != null) {
            sftpChannel.exit();
            sftpChannel = null;
        }
        if (session != null && session.isConnected()) {
            session.disconnect();
        }
        session = null;
    }
}