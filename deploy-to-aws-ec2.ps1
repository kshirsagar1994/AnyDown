[CmdletBinding()]
param (
    [string]$Region = "",
    [string]$InstanceType = "t3.small",
    [string]$ExistingIp = "",
    [string]$KeyPath = ""
)

$ErrorActionPreference = "Stop"

if ($Region) { $env:AWS_DEFAULT_REGION = $Region }
if ($InstanceType) { $env:ANYDOWN_INSTANCE_TYPE = $InstanceType }

& python "$PSScriptRoot\deploy_aws.py"
