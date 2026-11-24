"""Emit a synthetic local event and verify it can be retrieved from Loki."""
import json
import time
import urllib.parse
import urllib.request
import uuid

BASE="http://127.0.0.1:3100"
def run():
    for _ in range(40):
        try:
            with urllib.request.urlopen(BASE+"/ready",timeout=3) as r:
                if r.status == 200:
                    break
        except OSError:
            pass
        time.sleep(2)
    else:
        raise SystemExit("Loki not ready")
    event="synthetic demo event "+uuid.uuid4().hex
    stamp=time.time_ns()
    data=json.dumps({"streams":[{"stream":{"app":"potato-demo","environment":"local"},
                                "values":[[str(stamp),event]]}]}).encode()
    req=urllib.request.Request(BASE+"/loki/api/v1/push",data=data,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=5) as r:
        if r.status != 204:
            raise SystemExit("Push failed")
    for _ in range(20):
        params=urllib.parse.urlencode({"query":'{app="potato-demo"}',"start":str(stamp-1000000000),"end":str(time.time_ns()),"limit":"100"})
        with urllib.request.urlopen(BASE+"/loki/api/v1/query_range?"+params,timeout=5) as r:
            result=json.load(r)
        if any(value[1]==event for stream in result["data"]["result"] for value in stream["values"]):
            print("Synthetic event pushed and retrieved")
            return
        time.sleep(1)
    raise SystemExit("Event missing from Loki")
if __name__=="__main__":
    run()
