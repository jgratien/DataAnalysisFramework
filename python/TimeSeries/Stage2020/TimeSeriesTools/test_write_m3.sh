curl http://localhost:9003/writetagged -s -X POST -d '{ "namespace": "default", "id": "foo", "tags": [ { "name": "__name__", "value": "user_login" }, { "name": "city", "value": "new_york" }, { "name": "endpoint", "value": "/request" } ], "datapoint": { "timestamp":'"$(date +"%s")"', "value": 42.123456789 } }'

