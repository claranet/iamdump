# iamdump

Like tcpdump for AWS IAM policies.

This relies on [AWS SDK Metrics](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch-Agent-SDK-Metrics.html). It should work for anything using the supported SDKs listed on that page.

## How it works

1. Starts a temporary UDP server on a random port.
2. Exports environment variables telling AWS SDKs to send metrics to that UDP server.
3. Runs the command that was passed to iamdump.
4. Prints a JSON policy for all API calls that the command made according to the AWS SDK metrics.

Note that the policy has `*` for the resource because information about resources is not sent by SDK metrics. Use this policy as a starting point only!

## Usage

Install:

```
pip install iamdump
```

Run:

```
iamdump <command>
```

## Example

```
$ iamdump aws s3 ls
2018-06-27 11:35:45 this-is-not-a-real-bucket
2018-04-30 10:44:20 neither-is-this-one
2018-04-30 11:00:56 nor-this

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBuckets"
      ],
      "Resource": "*"
    }
  ]
}
```

## Incorrect service names

Service names in AWS SDK Metrics don't match up with IAM policy actions, so iamdump has to translate them. This is a young project, so some services may not be mapped correctly yet. If you encounter a policy with the wrong service name, please submit an issue or pull request so we can fix it.
