package fr.ifpen.historian;

import com.google.common.collect.Lists;
import fr.ifpen.historian.config.ServerConfig;
import fr.ifpen.historian.config.Singleton;
import fr.ifpen.historian.config.TagsMethod;
import fr.ifpen.historian.db.DataSource;
import fr.ifpen.historian.domain.Server;
import fr.ifpen.historian.utils.HistorianExtractorException;
import org.junit.Assert;
import org.junit.BeforeClass;
import org.junit.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.List;
import java.util.function.Predicate;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

import static fr.ifpen.historian.config.TagsMethod.C_API;
import static fr.ifpen.historian.config.TagsMethod.ODBC;

public class TestTagRequest {
    private static final Logger log = LoggerFactory.getLogger(TestTagRequest.class);

    @BeforeClass
    public static void initializeDb() {
        DataSource.getInstance().initialize(true);
    }

    @Test
    public void testAllTags35Request() {
        ServerConfig config = Tools.copy(Singleton.getInstance().getConfiguration().getHistorian().getServers().get(0));
        config.setTagsMethod(TagsMethod.ODBC);
        Assert.assertEquals("ISNTS35-N", config.getName());
        // gettings all ISNTS35 tags
        Server server = new Server(config);
        Assert.assertTrue("Tags query config", server.getTagsList().getClass().getSimpleName().equals("TagsQuery"));
        // force request launch
        List<String> tags = server.getTagsList().getTags();
        int nbTags = tags.size();
        log.info("Nb tags={}, first tag={}, last tag={}",
                nbTags, tags.get(0), tags.get(nbTags - 1));
        Assert.assertTrue("More than 1000 active tags in ISNTS35-N", nbTags > 1000);
        Assert.assertEquals("067_PI01", tags.get(0));
        Assert.assertTrue("Last tag of last selection is one from VEBP", tags.get(nbTags - 1).startsWith("VEBP"));
        Assert.assertTrue("Tags File has been created", Files.exists(server.getTagsList().getTagsFile()));

        // check file contains all tags
        ServerConfig originalConfig = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(0);
        Assert.assertEquals(C_API, originalConfig.getTagsMethod());
        Server batch = new Server(originalConfig);
        Assert.assertTrue("Tags batch config", batch.getTagsList().getClass().getSimpleName().equals("TagsBatch"));
        Assert.assertEquals("-c", batch.getTagsList().getBatchArguments().get(0));
    }

    @Test
    public void testTags29Request() {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(1);
        Assert.assertEquals(ODBC, config.getTagsMethod());
        Assert.assertEquals("ISNTS29-N", config.getName());
        Server server = new Server(config);
        // force request launch
        List<String> tags = server.getTagsList().getTags();
        log.info("ISNTS29 TAGS => {}", tags);
        log.info("Nb tags={}, first tag={}, last tag={}",
                tags.size(), tags.get(0), tags.get(tags.size() - 1));
        Assert.assertTrue("More than 1000 active tags in ISNTS29-N", tags.size() > 1000);
        Assert.assertEquals("U204.FC02CALC.F_CV", tags.get(0));
        Assert.assertTrue("Last tag of last selection is one from U875", tags.get(tags.size() - 1).startsWith("U875"));
    }

    @Test
    public void testInvalidTagsSelectionRequest() {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(1);
        Assert.assertEquals("ISNTS29-N", config.getName());
        // forcing  C API method
        ServerConfig otherConfig = Tools.copy(config);
        otherConfig.setTagsMethod(TagsMethod.C_API);
        try {
            Server server = new Server(otherConfig);
            Assert.fail("We must have exception because of incoherence between multiple tags selections adn C_API method");
        } catch (HistorianExtractorException e) {
            log.info("Erreur Historian={}", e.getMessage());
            Assert.assertTrue(e.getMessage().startsWith("in C_API mode, we can use only one tag selection"));
        }
    }

    @Test
    public void testPredicateConstitution() {
        List<String> liste = Lists.newArrayList("A1", "B1", "C1", "A2", "B2", "C2", "ZZ", "YY", "WW.A");
        List<String> regExpr = Lists.newArrayList("^A", "^B");
        log.info("Initial list={}", liste);
        List<Predicate<String>> exclusions = regExpr.stream()
                .map(Pattern::compile) // RegExpr to matcher
                .map(Pattern::asPredicate) // matcher to predicate
                .map(Predicate::negate) // negate to have exclusion not selection
                .collect(Collectors.toList());
        for (int i = 0; i < regExpr.size(); i++) {
            log.info("Applying exclusion of [{}] => list={}", regExpr.get(i), liste.stream().filter(exclusions.get(i)).collect(Collectors.toList()));
        }
        Predicate<String> tagExclusions = exclusions.stream().reduce(Predicate::and).orElse(x->true);
        log.info("All predicates together = {}", liste.stream().filter(tagExclusions).collect(Collectors.toList()));
    }

    @Test
    public void testTags35Batch() {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(0);
        Assert.assertEquals(C_API, config.getTagsMethod());
        Assert.assertEquals("ISNTS35-N", config.getName());
        Server server = new Server(config);
        Assert.assertTrue("Tags batch config", server.getTagsList().getClass().getSimpleName().equals("TagsBatch"));
        Assert.assertEquals(2, server.getTagsList().getBatchArguments().size());
        Assert.assertEquals("-c", server.getTagsList().getBatchArguments().get(0));
        log.info("tags batch arguments: {} / Data directory: {}", server.getTagsList().getBatchArguments(), Singleton.getInstance().getConfiguration().getDataDirectory());
        Assert.assertEquals("*", server.getTagsList().getBatchArguments().get(1));
   }

    @Test
    public void testTags29Query() {
        ServerConfig config = Singleton.getInstance().getConfiguration().getHistorian().getServers().get(1);
        Assert.assertEquals(ODBC, config.getTagsMethod());
        Assert.assertEquals("ISNTS29-N", config.getName());
        Server server = new Server(config);
        Assert.assertTrue("Tags query config", server.getTagsList().getClass().getSimpleName().equals("TagsQuery"));
        Assert.assertEquals(2, server.getTagsList().getBatchArguments().size());
        Assert.assertEquals("-f", server.getTagsList().getBatchArguments().get(0));
        log.info("tags batch arguments: {} / Data directory: {}", server.getTagsList().getBatchArguments(), Singleton.getInstance().getConfiguration().getDataDirectory());
        Assert.assertTrue("Tags file in correct directory", Paths.get(server.getTagsList().getBatchArguments().get(1)).startsWith(Singleton.getInstance().getConfiguration().dataDirectoryAsPath()));
        Assert.assertTrue("Tags file has txt extension", server.getTagsList().getBatchArguments().get(1).endsWith(".txt"));
    }
}
