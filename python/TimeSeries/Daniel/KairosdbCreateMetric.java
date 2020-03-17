
import java.io.IOException;
import java.util.HashMap;
import java.util.zip.DataFormatException;

import org.kairosdb.client.HttpClient;
import org.kairosdb.client.builder.Metric;
import org.kairosdb.client.builder.MetricBuilder;

public class KairosdbCreateMetric {
	private static String SANDBOX_KAIROS = "http://islin-hdpmas1.ifp.fr:8888/";
	private static String TEST_METRIC = "testMetric";

	private static long STEP = 60000l; // one minute
	private HashMap<String, String> TAGS = new HashMap<>();

	public void createMetric(boolean clean) throws DataFormatException, IOException {
		HttpClient client = new HttpClient(SANDBOX_KAIROS);
		// Clean if required
		if (clean) {
			client.deleteMetric(TEST_METRIC);
		}
		TAGS.put("Site", "Rueil");
		TAGS.put("User", "JoeDalton");
		long startTimestamp = 1512086400000l;
		long endTimestamp = 1517443200000l;
		long currentTimeStamp = startTimestamp;
		// New metric to be created
		MetricBuilder metricBuilder = MetricBuilder.getInstance();
		Metric testMetric = metricBuilder.addMetric(TEST_METRIC);
		addTags(testMetric, TAGS);
		while (currentTimeStamp < endTimestamp) {
			testMetric.addDataPoint(currentTimeStamp, Math.random()*100.);
			currentTimeStamp = Math.min(currentTimeStamp + STEP, endTimestamp);
		}
		client.pushMetrics(metricBuilder);
		client.close();
	}

	private void addTags(Metric metric, HashMap<String, String> tags) {
		tags.forEach((k,v) -> metric.addTag(k, v));
	}

	public static void main(String[] args) {
		KairosdbCreateMetric kairosTester = new KairosdbCreateMetric();
		try {
			kairosTester.createMetric(true);
		} catch (DataFormatException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
	}


}
