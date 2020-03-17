package fr.ifpen.historian.tasks;

import fr.ifpen.historian.config.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Created by IFPEN on 20/02/2019.
 */
public abstract class AbstractTask<T> implements Task<T> {
    protected Logger log = LoggerFactory.getLogger(AbstractTask.class);

    protected boolean debug;

    protected AbstractTask() {
        this.debug = Singleton.getInstance().getConfiguration().getDebug();
    }

    public abstract T runTask() throws Exception;

    public void postRunTask() {
    }

    @Override
    public void run() {
        try {
            runTask();
        } catch (Exception e) {
            log.error("error met on {} : {}", toString(), e.getMessage());
        } finally {
            postRunTask();
        }
    }

    @Override
    public T call() throws Exception {
        try {
            return runTask();
        } catch (Exception e) {
            log.error("error met on {} : {}", toString(), e.getMessage());
            return null;
        } finally {
            postRunTask();
        }
    }
}
