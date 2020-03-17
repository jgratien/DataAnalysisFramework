package fr.ifpen.historian.config;

import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.yaml.snakeyaml.Yaml;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URL;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

public class Singleton {
    private static final Logger log = LoggerFactory.getLogger(Singleton.class);

    private static final Singleton instance = new Singleton();
    private Configuration configuration;
    private List<Server> servers;

    private Singleton() {
        Yaml yaml = new Yaml();
        try (InputStream in = applicationYml()) {
            configuration = yaml.loadAs(in, Configuration.class);
            log.debug(configuration.toString());
        } catch (IOException e) {
            log.error("unable to load application.yml : {}", e.getCause());
        }
    }

    public static Singleton getInstance() {
        return instance;
    }

    public Configuration getConfiguration() {
        return configuration;
    }

    public List<Server> getServers() {
        if (servers == null) {
            servers = configuration.getHistorian().getServers()
                    .stream()
                    .map(c -> new Server(c))
                    .collect(Collectors.toList());
        }
        return servers;
    }

    public boolean serverExists(String serverName) {
        return getServers().stream().anyMatch(s -> s.getName().equalsIgnoreCase(serverName));
    }

    public Optional<Server> findServer(String serverName) {
        return getServers()
                .stream()
                .filter(s -> s.getName().equalsIgnoreCase(serverName))
                .findFirst();
    }

    public Server getServer(String serverName) {
        return findServer(serverName).orElseThrow(() -> new HistorianExtractorException("unknown server " + serverName));

    }

    private InputStream applicationYml() {
        List<Path> roots = getResourcesDirectories();
        log.debug("directories for looking for configuration {}", roots);
        for (Path root : roots) {
            try {
                File yml = root.resolve("application.yml").toFile();
                log.debug("looking for configuration file {}", yml.getAbsolutePath());
                if (yml.exists() && yml.isFile()) {
                    log.debug("using configuration file {}", yml.getAbsolutePath());
                    return new FileInputStream(yml);
                }
            } catch (Exception e) {
                log.debug("no file application.yml in {}", root);
            }
        }
        log.debug("using configuration file application.yml from Classpath");
        return Singleton.class.getResourceAsStream("/application.yml");
    }

    private List<Path> getResourcesDirectories() {
        List<Path> paths = new ArrayList<>();
        try {
            // on regarde d'abord si on est dans un jar
            Path classPath = Paths.get(Singleton.class.getProtectionDomain().getCodeSource().getLocation().toURI());
            log.debug("classPath=[{}], end with .jar={}, file=[{}], parent=[{}]",
                    classPath, classPath.toString().endsWith(".jar"), classPath.getFileName(), classPath.getParent());
            if (classPath.toString().endsWith(".jar")) {
                paths.add(classPath.getParent());
            }
            // sinon on regarde dans le classpath du thread
            for (URL root : Collections.list(Thread.currentThread().getContextClassLoader().getResources(""))) {
                log.debug("classloader context={}", root);
                paths.add(Paths.get(root.toURI()));
            }
            // on ajoute le path des resources en dernier
            if (!classPath.toString().endsWith(".jar")) {
                paths.add(classPath);
            }
        } catch (Exception e) {
            log.error("error met when looking for classpath: {}", e.getMessage());
        }
        return paths;
    }
}
