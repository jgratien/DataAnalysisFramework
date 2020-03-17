package fr.ifpen.historian.config;

import com.google.common.base.Strings;
import fr.ifpen.historian.utils.HistorianExtractorException;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

/**
 * Created by IFPEN on 25/09/2019.
 */
public class BatchExtraction {
    private String program;
    private String logFile;
    private Path programPath;
    private Integer timeOutExtract;

    public String getProgram() {
        return program;
    }

    public void setProgram(String program) {
        this.program = program;
    }

    public String getLogFile() {
        return logFile;
    }

    public void setLogFile(String logFile) {
        this.logFile = logFile;
    }

    public Path programAsPath() {
        if (programPath == null) {
            if (Strings.isNullOrEmpty(program)) {
                throw new HistorianExtractorException("You have to set historian batch extractor in configuration \"historian.batchExtraction.program\"");
            }
            programPath = Paths.get(program);
            if (!Files.exists(programPath)) {
                throw new HistorianExtractorException("Historian batch extractor " + program + " is not a valid executable file");
            }
        }
        return programPath;
    }

    public boolean isLogFileSet() {
        return !Strings.isNullOrEmpty(logFile) && Files.exists(logFileAsPath());
    }

    public Path logFileAsPath() {
        return Paths.get(logFile);
    }

    public Integer getTimeOutExtract() {
        return timeOutExtract;
    }

    public void setTimeOutExtract(Integer timeOutExtract) {
        this.timeOutExtract = timeOutExtract;
    }

    @Override
    public String toString() {
        return "BatchExtraction{" +
                "program='" + program + '\'' +
                ", logFile='" + logFile + '\'' +
                ", timeOutExtract=" + timeOutExtract +
                '}';
    }
}
