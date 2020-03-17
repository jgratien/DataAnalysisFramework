package fr.ifpen.historian;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import static java.lang.System.err;
import static java.lang.System.out;

/**
 * Created by IFPEN on 19/09/2019.
 */
public class TestEmpilement {
    private static class TestStandardRunner implements Runnable {
        static DateTimeFormatter DTF = DateTimeFormatter.ofPattern("mm:ss");
        private int number;
        private int wait;
        private String msg;
        private int runNumber;
        private AtomicBoolean health;

        public TestStandardRunner(int number, int wait, AtomicBoolean health) {
            this.number = number + 1;
            this.runNumber = 1;
            this.wait = wait;
            this.health = health;
        }

        @Override
        public void run() {
            try {
                runThread();
            } catch (Exception e) {
                err.println("catch fucking exception: " + e.getMessage());
            }
        }

        private void runThread() {
            msg = "Std " + number + ", Start=" + LocalDateTime.now().format(DTF);
            try {
                Thread.sleep(wait);
                // stop background
                if (runNumber % 4 == 0) {
                    health.set(false);
                    msg += ", sleeping for " + (5 * wait / 1000) + "s";
                    Thread.sleep(5 * wait);
                }
            } catch (InterruptedException e) {
                err.println(e.getMessage());
                health.set(false);
            }
            msg += ", run n°=" + runNumber;
            out.println(msg);
            health.set(true);
            runNumber++;
        }
    }

    private static class TestBackgroundRunner implements Runnable {
        static DateTimeFormatter DTF = DateTimeFormatter.ofPattern("mm:ss");
        private int number;
        private int runNumber;
        private int wait;
        private String msg;
        private AtomicBoolean health;

        public TestBackgroundRunner(int number, int wait, AtomicBoolean health) {
            this.number = number + 1;
            this.runNumber = 1;
            this.health = health;
            this.wait = wait;
        }

        @Override
        public void run() {
            try {
                runThread();
            } catch (Exception e) {
                err.println("catch fucking exception: " + e.getMessage());
            }
        }

        private void runThread() {
            msg = "Back" + number + ", Start=" + LocalDateTime.now().format(DTF);
            try {
                if (!health.get()) {
                    msg += ", run n°=" + runNumber;
                    msg += ", health bad cancel";
                    runNumber++;
                    out.println(msg);
                    return;
                }
                Thread.sleep(wait);
            } catch (InterruptedException e) {
                err.println(e.getMessage());
            }
            msg += ", run n°=" + runNumber;
            runNumber++;
            out.println(msg);
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int poolSize = 2;
        int duration = 5;
        int period = 2;
        AtomicBoolean health = new AtomicBoolean(true);
        //int nbThread = 2;
        //out.print("nb thread=" + nbThread + " / ");
        //out.print("pool size=" + poolSize + ", ");
        //out.print("thread duration=1s T1 et " + duration + "s T2/ ");
        //out.println("period=" + period + "s");
        ScheduledExecutorService executor = Executors.newScheduledThreadPool(poolSize);
        executor.scheduleAtFixedRate(new TestStandardRunner(1, 2000, health), 100, 5000, TimeUnit.MILLISECONDS);
        executor.scheduleAtFixedRate(new TestBackgroundRunner(1, 500, health), 2500, 2000, TimeUnit.MILLISECONDS);
//        for (int index = 0; index < nbThread; index++) {
//            executor.scheduleAtFixedRate(new TestSchedulerRunner(index, index == 0 ? 1 : duration),
//                    index * 100, period * 1000, TimeUnit.MILLISECONDS);
//        }
        out.println("end of main");
    }
}
