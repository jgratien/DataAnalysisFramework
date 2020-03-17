package fr.ifpen.historian.request;


import com.google.common.collect.Lists;
import fr.ifpen.historian.config.ServerConfig;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.domain.TagsList;
import fr.ifpen.historian.utils.HistorianExtractorException;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Request to get all Historian to be extracted
 * Depends on config and selection criteria
 * Tags are saved in text file for batch program
 * Created by IFPEN on 15/02/2019.
 */
public class TagsQuery extends HistorianQuery<String> implements TagsList {

    private static Integer maxTags = Singleton.getInstance().getConfiguration().getHistorian().getMaxTags();
    private static int maxQueries = Singleton.getInstance().getConfiguration().getHistorian().getMaxQueries();
    private String sql;
    private LocalDateTime nextCheck;
    private ServerConfig config;
    private List<String> tags = new ArrayList<>();
    private Boolean debug;
    private Path tagsFile;

    public TagsQuery(ServerConfig config) {
        this.sql = Singleton.getInstance().getConfiguration().getHistorian().getRequests().getTagList();
        this.sql = this.sql.replace("{MAX_TAGS}", maxTags.toString());
        this.config = config;
        this.nextCheck = LocalDateTime.now().minusDays(1);
        this.debug = Singleton.getInstance().getConfiguration().getDebug();
        this.tagsFile = TagsList.tagsFile(config.getName());
    }

    private String getServer() {
        return config.getName();
    }

    @Override
    public Path getTagsFile() {
        return tagsFile;
    }

    @Override
    public List<String> getBatchArguments() {
        // we need to read tags in order to save them in the tagsFile
        readTags();
        List<String> arguments = Lists.newArrayList("-f");
        arguments.add(tagsFile.toString());
        return arguments;
    }

    public void readTags() {
        if (nextCheck.isBefore(LocalDateTime.now()) || tags.isEmpty()) {
            try {
                if (debug) {
                    // permet de fournir une liste bidon de tags
                    debugTags();
                } else {
                    queryTags();
                }
                // we save them in file for use by C batch program
                Files.write(tagsFile, tags, StandardOpenOption.WRITE, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING);
            } catch (IOException e) {
                throw new HistorianExtractorException("error when trying to read and save Historian tags list for " + getServer() + " : " + e.getMessage());
            }
        }
        // si on a rien remonté on sort en erreur
        if (tags.isEmpty()) {
            throw new HistorianExtractorException("no active tag found, no data can be extracted on server " + getServer());
        }
    }

    private void queryTags() {
        tags.clear();
        // on récupère tous les tags correspondant à la config (demandée en paramétrage)
        for (String selection : config.getTagsSelections()) {
            // on vide les valeurs à chaque sélection
            values.clear();
            // on boucle au maximum maxQueries tous les maxTags pour obtenir l'ensemble des tags de la sélection
            String query = this.sql.replace("{TAGSELECT}", "TAGNAME like '" + selection + "' {LOOP}");
            long count = maxTags;
            for (int iter = 0; iter < maxQueries && count == maxTags; iter++) {
                count = execute(getServer(), query.replace("{LOOP}", iter == 0 ? "" : "AND TAGNAME > '" + values.get(values.size() - 1) + "' "));
            }
            // on ajoute tous les tags récupérés
            tags.addAll(values);
        }
        nextCheck = LocalDateTime.now().plusSeconds(config.getCheckTagsDelay());
    }

    private void debugTags() {
        tags.clear();
        int nbTags = getServer().contains("35") ? 2 : 10;
        for (int i = 0; i < nbTags; i++) {
            tags.add("TAG_" + i + "_" + getServer());
        }
        nextCheck = LocalDateTime.now().plusSeconds(config.getCheckTagsDelay());
    }

    @Override
    public List<String> getTags() {
        readTags();
        return tags;
    }

    @Override
    protected String fromRecordset(Object[] values) {
        return values.length > 0 ? values[0].toString() : "";
    }

    @Override
    public String toString() {
        return "TagsQuery{" +
                "nextCheck=" + nextCheck +
                ", config=" + config +
                ", debug=" + debug +
                '}';
    }
}
