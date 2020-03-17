package fr.ifpen.historian;

import fr.ifpen.historian.tasks.Stoppable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// The ShutdownService is the thread we pass to the addShutdownHook method
public class ShutdownExecutor extends Thread {
    private static final Logger log = LoggerFactory.getLogger(ShutdownExecutor.class);
    private Stoppable stoppable = null;

    public ShutdownExecutor(Stoppable stoppable) {
        super();
        this.stoppable = stoppable;
    }

    public void run() {
        log.debug("shutdown requested for {}", stoppable);
        stoppable.stop();
        log.info("shutdown complete for {}", stoppable);
    }
}