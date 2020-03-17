package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Ftp;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.db.LogDAO;
import fr.ifpen.historian.domain.Report;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * Created by IFPEN on 20/02/2019.
 */
public class FileTransfer {
    private Logger log = LoggerFactory.getLogger(FileTransfer.class);

    protected boolean debug;
    private Report report;

    protected FileTransfer(Report report) {
        this.debug = Singleton.getInstance().getConfiguration().getDebug();
        this.report = report;
        log.debug("new {}", toString());
    }

    public LocalDateTime execute() {
        if (!Singleton.getInstance().getConfiguration().isFtpEnabled() || !Files.exists(report.getDataFileFullPath()))
            return null;
        if (debug) {
            return transferDebug();
        } else {
            return transferFile();
        }
    }

    private LocalDateTime transferFile() {
        if (!Files.exists(report.getDataFileFullPath())) {
            log.warn("unable to transfer file {} which is no more present in data directory {}", report.getDataFile(), Singleton.getInstance().getConfiguration().getDataDirectory());
            return null;
        }
        // pour chaque rapport, on créé une tâche qui copie le fichier et met à jour la bd
        boolean result = true;
        for (Ftp ftp : Singleton.getInstance().getConfiguration().activeFtps()) {
            fr.ifpen.historian.utils.FileTransfer fileTransfer = new fr.ifpen.historian.utils.FileTransfer();
            try {
                fileTransfer.connect(ftp);
                fileTransfer.uploadFile(report.getDataFileFullPath(), report.getServer(), report.getDateTime().toLocalDateTime());
            } catch (Exception e) {
                result = false;
                log.warn("unable to transfer file {} : {}", report.getDataFile(), e.getMessage());
            } finally {
                fileTransfer.disconnect();
            }
        }
        if (result) {
            // FIXME: need to change DB model in order to save which transfer is ok (we can have many FTP servers now)
            // Attention il faudra changer le modèle de base, les procédures de retrieve
            report.setFileTransferSuccess(Boolean.TRUE);
            LogDAO.saveReport(report);
        }
        return report.getDateTime().toLocalDateTime();
    }

    private LocalDateTime transferDebug() {
        log.info("debug mode, simulation of file transfer {}, for server {} at {}", report.getDataFileFullPath(), report.getServer(), report.getDateTime().toLocalDateTime());
        return report.getDateTime().toLocalDateTime();
    }

    @Override
    public String toString() {
        return "file transfer task for file " + report.getDataFile();
    }

    public AbstractTask<LocalDateTime> toTask() {
        return new FileTransferTask(this);
    }

    private class FileTransferTask extends AbstractTask<LocalDateTime> {

        private FileTransfer fileTransfer;

        public FileTransferTask(FileTransfer fileTransfer) {
            this.fileTransfer = fileTransfer;
        }

        @Override
        public LocalDateTime runTask() throws Exception {
            return fileTransfer.execute();
        }

        @Override
        public long computeInitialDelay() {
            throw new HistorianExtractorException("not implemented, not needed");
        }

        @Override
        public long getPeriod() {
            throw new HistorianExtractorException("not implemented, not needed");
        }

        @Override
        public TimeUnit getTimeUnit() {
            throw new HistorianExtractorException("not implemented, not needed");
        }
    }
}
