curl http://localhost:9003/query -s -X POST -d '{ "namespace": "default", "query": { "regexp": { "field": "city", "regexp": ".*" } }, "rangeStart": 0, "rangeEnd":'"$(date +"%s")"' }'
