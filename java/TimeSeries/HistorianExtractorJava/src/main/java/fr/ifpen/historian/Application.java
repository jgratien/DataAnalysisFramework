package fr.ifpen.historian;

import org.kohsuke.args4j.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;

public class Application {
    private static final Logger log = LoggerFactory.getLogger(Application.class);

    @Option(name = "-mode", required = true, usage = "Service mode :\n" +
            "DAEMON: service extracting every data from historian regularly\n" +
            "STATUS: gives information about extraction succeeded and extractions errors or missing\n" +
            "RETRIEVE: run the extraction between two date/time retrieving missing extractions\n" +
            "FILE_TRANSFER: transfer data files produced between two date/time\n" +
            "CONSOLE: start and display H2 DB console in a browser\n" +
            "USAGE: display the launching options")
    private ServiceMode mode;

    @Option(name = "-start", usage = "Start of date/time range for extracting missing data or transferring missing data files (in RETRIEVE or FILE_TRANSFER mode)\n" +
            "Format : yyyy-MM-dd HH:mm (for example : \"2019-08-07 15:00\")")
    private String start;

    @Option(name = "-end", usage = "End of date/time range for extracting missing data or transferring missing data files (in RETRIEVE or FILE_TRANSFER mode)\n" +
            "Format : yyyy-MM-dd HH:mm (for example : \"2019-08-07 16:00\")")
    private String end;

    @Option(name = "-server", usage = "historian server concerned by extracting missing data in RETRIEVE mode")
    private String server;

    @Option(name = "-force", usage = "Force the treatment for extracting data or transferring files (in RETRIEVE or FILE_TRANSFER mode)")
    private Boolean force;

    @Option(name = "-hours", usage = "Number of hours listed in STATUS mode")
    private Integer hours;

    @Option(name = "-days", usage = "Number of days listed in STATUS mode")
    private Integer days;

    // receives other command line parameters than options
    @Argument
    private List<String> arguments = new ArrayList<String>();

    public static void main(String[] args) {
        new Application().doMain(args);
    }

    public ServiceMode getMode() {
        return mode;
    }

    public String getStart() {
        return start;
    }

    public String getEnd() {
        return end;
    }

    public String getServer() {
        return server;
    }

    public Boolean getForce() {
        return force;
    }

    public List<String> getArguments() {
        return arguments;
    }

    private void doMain(String[] args) {
        ParserProperties properties = ParserProperties.defaults();
        properties.withOptionSorter(null);
        CmdLineParser parser = new CmdLineParser(this, properties);
        //noinspection deprecation
        parser.setUsageWidth(150);
        try {
            // parse the arguments.
            parser.parseArgument(args);
            if (mode == null) {
                log.error("mode argument must be supplied");
                mode = ServiceMode.USAGE;
            }
            switch (mode) {
                case STATUS:
                    status();
                    break;
                case USAGE:
                    parser.printUsage(System.out);
                    break;
                default:
                    Service service = new Service(this);
                    // check arguments
                    if (!service.check()) {
                        parser.printUsage(System.out);
                        return;
                    }
                    service.execute();
                    break;
            }
        } catch (CmdLineException e) {
            // if there's a problem in the command line,
            // you'll get this exception. this will report
            // an error message.
            log.error(e.getMessage());

            // print the list of available options
            parser.printUsage(System.out);

            // print option sample. This is useful some time
            log.error("  example: java -jar historian-extractor.jar " + parser.printExample(OptionHandlerFilter.ALL));
        }
    }

    private void status() {
        Status status = new Status(days, hours);
        status.display();
    }
}
