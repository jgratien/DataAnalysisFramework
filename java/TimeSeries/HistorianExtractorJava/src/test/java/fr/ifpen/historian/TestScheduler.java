package fr.ifpen.historian;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import static java.lang.System.err;
import static java.lang.System.out;

/**
 * Created by IFPEN on 19/09/2019.
 */
public class TestScheduler {
    private static class TestSchedulerRunner implements Runnable {
        static DateTimeFormatter DTF = DateTimeFormatter.ofPattern("mm:ss");
        private int number;
        private int wait;
        private String msg;
        private int runNumber;

        public TestSchedulerRunner(int number, int wait) {
            this.number = number + 1;
            this.runNumber = 1;
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
            msg = "T" + number + ", S=" + LocalDateTime.now().format(DTF);
            try {
                Thread.sleep(wait * 1000);
                msg += ", E=" + LocalDateTime.now().format(DTF);
            } catch (InterruptedException e) {
                err.println(e.getMessage());
                msg += ", I=" + LocalDateTime.now().format(DTF);
            }
            msg += ", run n°=" + runNumber;
            out.println(msg);
            // test d'une runtimeexception
            if (runNumber % 4 == 0) {
                err.println("exception rised on T" + number);
                runNumber++;
                throw new RuntimeException("exception rised");
            }
            runNumber++;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int poolSize = 2;
        int duration = 5;
        int period = 2;
        int nbThread = 2;
        out.print("nb thread=" + nbThread + " / ");
        out.print("pool size=" + poolSize + ", ");
        out.print("thread duration=1s T1 et " + duration + "s T2/ ");
        out.println("period=" + period + "s");
        ScheduledExecutorService executor = Executors.newScheduledThreadPool(poolSize);
        for (int index = 0; index < nbThread; index++) {
            executor.scheduleAtFixedRate(new TestSchedulerRunner(index, index == 0 ? 1 : duration),
                    index * 100, period * 1000, TimeUnit.MILLISECONDS);
        }
        System.out.println("end of main");
    }
}
