import sys
import json
import time
import random

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout_sec=10.0):
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time = 0
        self.total_requests = 0

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
        return {"state": self.state, "message": "Circuit restored to CLOSED"}

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        return {"state": self.state, "failures": self.failure_count}

    def allow_request(self):
        self.total_requests += 1
        if self.state == "CLOSED":
            return True, "CLOSED"
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True, "HALF_OPEN"
            return False, "OPEN"
        if self.state == "HALF_OPEN":
            return True, "HALF_OPEN"
        return False, "UNKNOWN"

    def status(self):
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "recovery_timeout_sec": self.recovery_timeout,
            "last_failure_time": self.last_failure_time,
            "total_requests": self.total_requests
        }

breakers = {}

def get_breaker(service_name):
    if service_name not in breakers:
        breakers[service_name] = CircuitBreaker()
    return breakers[service_name]

def handle_rpc(request):
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params", {})

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "check_execution_allowed",
                        "description": "Check whether circuit breaker allows an execution to proceed.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service": {"type": "string", "default": "default"}
                            }
                        }
                    },
                    {
                        "name": "report_result",
                        "description": "Report execution outcome (success or failure) to update breaker state.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service": {"type": "string", "default": "default"},
                                "success": {"type": "boolean"}
                            },
                            "required": ["success"]
                        }
                    },
                    {
                        "name": "get_breaker_state",
                        "description": "Get current state and health metrics of a service breaker.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service": {"type": "string", "default": "default"}
                            }
                        }
                    }
                ]
            }
        }

    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        service = args.get("service", "default")
        cb = get_breaker(service)

        if name == "check_execution_allowed":
            allowed, state = cb.allow_request()
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps({"allowed": allowed, "state": state})}]}}
        elif name == "report_result":
            succ = args.get("success", True)
            if succ:
                res = cb.record_success()
            else:
                res = cb.record_failure()
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}
        elif name == "get_breaker_state":
            res = cb.status()
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res)}]}}

    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()
