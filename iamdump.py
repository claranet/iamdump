import json
import os
import socketserver
import sys
import threading
import time

service_map = {
    "applicationautoscaling": "application-autoscaling",
    "cloudWatchevents": "events",
    "elasticloadbalancingv2": "elasticloadbalancing",
}


def translate_service(service):
    """
    Translates a service string from the JSON message
    into a valid IAM service string.

    """

    service = service.lower().replace(" ", "")
    if service in service_map:
        service = service_map[service]
    return service


class MetricsHandler(socketserver.BaseRequestHandler):
    """
    Receives JSON messages from AWS SDKs, extracts the API call
    made by the SDK, and adds it to the global "api_calls" set.

    """

    api_calls = set()

    def handle(self):
        data = json.loads(self.request[0].strip())
        service = translate_service(data["Service"])
        api = data["Api"]
        api_call = "{}:{}".format(service, api)
        self.__class__.api_calls.add(api_call)

    @classmethod
    def iam_policy_json(cls):
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": sorted(cls.api_calls),
                        "Resource": "*",
                    }
                ],
            },
            indent=2,
        )


def cli():

    command = " ".join(sys.argv[1:])
    if not command:
        script = os.path.basename(sys.argv[0])
        sys.stderr.write("Usage: {} <command>\n".format(script))
        sys.exit(1)

    # Open a socket on port 0 to let the kernal assign a port.
    with socketserver.UDPServer(("localhost", 0), MetricsHandler) as server:

        # Run the server in a background thread.
        threading.Thread(target=server.serve_forever).start()

        # Tell AWS SDKs to send metrics to this server.
        os.environ["AWS_CSM_ENABLED"] = "true"
        os.environ["AWS_CSM_PORT"] = str(server.server_address[1])

        # Run the command that was passed in as arguments,
        # and stop the server after the command has finished.
        exit_code = os.system(command)
        server.shutdown()

    # This API call doesn't require an IAM policy so ignore it.
    MetricsHandler.api_calls.discard("ec2metadata:GetMetadata")

    if MetricsHandler.api_calls:
        sys.stderr.write("\n")
        sys.stderr.write(MetricsHandler.iam_policy_json())
        sys.stderr.write("\n")

    sys.exit(exit_code)


if __name__ == "__main__":
    cli()
