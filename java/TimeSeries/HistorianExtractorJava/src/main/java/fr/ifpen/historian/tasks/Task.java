package fr.ifpen.historian.tasks;

import java.util.concurrent.Callable;
import java.util.concurrent.TimeUnit;

/**
 * Created by IFPEN on 23/08/2019.
 */
public interface Task<T> extends Runnable, Callable<T> {
    long computeInitialDelay();

    long getPeriod();

    TimeUnit getTimeUnit();
}
